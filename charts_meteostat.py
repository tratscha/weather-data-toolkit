from __future__ import annotations

from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from meteostat import Point, Daily

RESULTS_DIR = Path("results")
VALID_YEARS = list(range(2000, 2024))

# Flughafen Köln/Bonn
CGN = Point(50.8659, 7.1427, 91)


def ask_year() -> int:
    max_attempts = 3
    attempt = 0

    while attempt < max_attempts:
        try:
            year_input = input("Die Wetterdaten welches Jahrs soll ich darstellen? ").strip()
            year = int(year_input)
            if year in VALID_YEARS:
                return year
            print(f"Ungültiges Jahr! Bitte ein Jahr zwischen {VALID_YEARS[0]} und {VALID_YEARS[-1]} eingeben.")
        except ValueError:
            print("Ungültige Eingabe! Bitte eine Zahl eingeben.")
        attempt += 1

    raise SystemExit("Zu viele ungültige Versuche. Das Programm wird beendet.")


def run() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    year = ask_year()

    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31)

    df = Daily(CGN, start, end).fetch()

    if df.empty:
        raise SystemExit(f"Keine Wetterdaten für das Jahr {year} verfügbar.")

    df = df.reset_index()
    df["month"] = df["time"].dt.month

    # 1) Niederschlag pro Monat
    prcp_by_month = df.groupby("month")["prcp"].sum()
    plt.figure(figsize=(10, 4))
    prcp_by_month.plot(kind="bar")
    plt.title(f"Niederschlag pro Monat in {year}")
    plt.xlabel("Monat")
    plt.ylabel("Niederschlag (mm)")
    plt.grid(axis="y")
    plt.tight_layout()
    out1 = RESULTS_DIR / f"meteostat_niederschlag_pro_monat_{year}.png"
    plt.savefig(out1, dpi=150)
    plt.close()

    # 2) Temperaturverlauf
    df["tavg"] = pd.to_numeric(df["tavg"], errors="coerce")
    df["tmin"] = pd.to_numeric(df["tmin"], errors="coerce")
    df["tmax"] = pd.to_numeric(df["tmax"], errors="coerce")

    temp_stats = df.groupby("month").agg(
        {"tmin": "min", "tavg": "mean", "tmax": "max"}
    )

    plt.figure(figsize=(10, 4))
    plt.plot(temp_stats.index, temp_stats["tmin"], label="Min", marker="o")
    plt.plot(temp_stats.index, temp_stats["tavg"], label="Ø Mittelwert", marker="o")
    plt.plot(temp_stats.index, temp_stats["tmax"], label="Max", marker="o")
    plt.title(f"Temperaturen pro Monat in {year}")
    plt.xlabel("Monat")
    plt.ylabel("Temperatur (°C)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    out2 = RESULTS_DIR / f"meteostat_temperaturen_pro_monat_{year}.png"
    plt.savefig(out2, dpi=150)
    plt.close()

    # 3) Luftdruck vs Niederschlag
    df["pres"] = pd.to_numeric(df["pres"], errors="coerce")
    df["prcp"] = pd.to_numeric(df["prcp"], errors="coerce")

    plt.figure(figsize=(10, 4))
    plt.scatter(df["pres"], df["prcp"], alpha=0.5)
    plt.title(f"Luftdruck vs. Niederschlag in {year}")
    plt.xlabel("Luftdruck (hPa)")
    plt.ylabel("Niederschlag (mm)")
    plt.grid(True)
    plt.tight_layout()
    out3 = RESULTS_DIR / f"meteostat_luftdruck_vs_niederschlag_{year}.png"
    plt.savefig(out3, dpi=150)
    plt.close()

    print("[+] Diagramme gespeichert:")
    print(f"    - {out1}")
    print(f"    - {out2}")
    print(f"    - {out3}")


if __name__ == "__main__":
    run()