from __future__ import annotations

import csv
import socket
from pathlib import Path
from typing import Dict, Tuple, Any

HOST = "127.0.0.1"
PORT = 5026
DATA_FILE = Path("data/airport-cgn.csv")

DateKey = Tuple[int, int, int]
WeatherRow = Dict[str, Any]


def _to_float(value: str) -> float | None:
    if value is None:
        return None
    value = value.strip()
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _to_int(value: str) -> int | None:
    if value is None:
        return None
    value = value.strip()
    if value == "":
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def load_data(filename: Path) -> Dict[DateKey, WeatherRow]:
    if not filename.exists():
        raise FileNotFoundError(f"Data file not found: {filename}")

    data: Dict[DateKey, WeatherRow] = {}

    with filename.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = _to_int(row.get("year", ""))
            month = _to_int(row.get("month", ""))
            day = _to_int(row.get("day", ""))

            if year is None or month is None or day is None:
                continue

            key: DateKey = (year, month, day)
            data[key] = {
                "year": year,
                "month": month,
                "day": day,
                "tavg": _to_float(row.get("tavg", "")),
                "tmin": _to_float(row.get("tmin", "")),
                "tmax": _to_float(row.get("tmax", "")),
                "prcp": _to_float(row.get("prcp", "")),
                "snow": _to_float(row.get("snow", "")),
                "wdir": _to_int(row.get("wdir", "")),
                "wspd": _to_float(row.get("wspd", "")),
                "wpgt": _to_float(row.get("wpgt", "")),
                "pres": _to_float(row.get("pres", "")),
                "tsun": _to_int(row.get("tsun", "")),
            }

    return data


def format_value(value: Any, unit: str = "") -> str:
    if value is None:
        return "n/v"
    if isinstance(value, int):
        return f"{value}{unit}"
    if isinstance(value, float):
        return f"{value:.1f}{unit}"
    return f"{value}{unit}"


def build_response(key: DateKey, record: WeatherRow | None) -> str:
    day, month, year = key[2], key[1], key[0]

    if record is None:
        return f"Keine Wetterdaten für den {day:02d}.{month:02d}.{year:04d} gefunden."

    return (
        f"Hier sind die Wetterdaten des {day:02d}.{month:02d}.{year:04d}:\n"
        f"Temp (min/o/max): {format_value(record['tmin'], ' C')} / "
        f"{format_value(record['tavg'], ' C')} / "
        f"{format_value(record['tmax'], ' C')}\n"
        f"Niederschlag: {format_value(record['prcp'], ' mm')}, "
        f"Schnee: {format_value(record['snow'], ' mm')}\n"
        f"Luftdruck: {format_value(record['pres'], ' hPa')}\n"
        f"Sonnenscheindauer: {format_value(record['tsun'], ' min')}"
    )


def run_server() -> None:
    data = load_data(DATA_FILE)
    print(f"[+] {len(data)} Tageswerte geladen aus {DATA_FILE}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[+] Server lauscht auf {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"[+] Verbunden mit {addr}")
                raw = conn.recv(1024)
                if not raw:
                    continue

                date_str = raw.decode("utf-8").strip()
                try:
                    parts = date_str.split(".")
                    if len(parts) != 3:
                        raise ValueError

                    day = int(parts[0])
                    month = int(parts[1])
                    year = int(parts[2])
                    key = (year, month, day)

                    response = build_response(key, data.get(key))
                except (ValueError, IndexError):
                    response = "Ungültiges Datumsformat. Bitte im Format DD.MM.YYYY angeben."

                conn.sendall(response.encode("utf-8"))


if __name__ == "__main__":
    try:
        run_server()
    except FileNotFoundError as e:
        print(f"[-] {e}")