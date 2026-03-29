from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

DATA_FILE = Path("data/airport-cgn.csv")
RESULTS_DIR = Path("results")
VALID_YEARS = list(range(2020, 2025))


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
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Data file not found: {DATA_FILE}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    weather_df = pd.read_csv(DATA_FILE)
    weather_df["date"] = pd.to_datetime(weather_df[["year", "month", "day"]], errors="coerce")

    year = ask_year()
    df_year = weather_df[weather_df["date"].dt.year == year].copy()

    if df_year.empty:
        raise SystemExit(f"Keine Daten für das Jahr {year} gefunden.")

    # 1) Niederschlag pro Monat
    prcp_by_month = df_year.groupby(df_year["date"].dt.month)["prcp"].sum()
    plt.figure(figsize=(10, 4))
    prcp_by_month.plot(kind="bar")
    plt.title(f"Niederschlag pro Monat in {year}")
    plt.xlabel("Monat")
    plt.ylabel("Niederschlag (mm)")
    plt.grid(axis="y")
    plt.tight_layout()
    out1 = RESULTS_DIR / f"niederschlag_pro_monat_{year}.png"
    plt.savefig(out1, dpi=150)
    plt.close()

    # 2) Temperaturstatistik
    df_year["tavg"] = pd.to_numeric(df_year["tavg"], errors="coerce")
    df_year["tmin"] = pd.to_numeric(df_year["tmin"], errors="coerce")
    df_year["tmax"] = pd.to_numeric(df_year["tmax"], errors="coerce")

    temp_stats = df_year.groupby(df_year["date"].dt.month).agg(
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
    out2 = RESULTS_DIR / f"temperaturen_pro_monat_{year}.png"
    plt.savefig(out2, dpi=150)
    plt.close()

    # 3) Luftdruck vs Niederschlag
    df_year["pres"] = pd.to_numeric(df_year["pres"], errors="coerce")
    df_year["prcp"] = pd.to_numeric(df_year["prcp"], errors="coerce")

    plt.figure(figsize=(10, 4))
    plt.scatter(df_year["pres"], df_year["prcp"], alpha=0.5)
    plt.title(f"Luftdruck vs. Niederschlag in {year}")
    plt.xlabel("Luftdruck (hPa)")
    plt.ylabel("Niederschlag (mm)")
    plt.grid(True)
    plt.tight_layout()
    out3 = RESULTS_DIR / f"luftdruck_vs_niederschlag_{year}.png"
    plt.savefig(out3, dpi=150)
    plt.close()

    print("[+] Diagramme gespeichert:")
    print(f"    - {out1}")
    print(f"    - {out2}")
    print(f"    - {out3}")


if __name__ == "__main__":
    run()