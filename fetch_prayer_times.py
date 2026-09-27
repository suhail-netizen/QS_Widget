"""
Regenerates the local prayer-time JSON files (makkah_*.json, madinah_*.json)
used by Quran_TV.html and Sunnah_TV.html.

Requires internet access and the `requests` package (pip install requests).
Run this once, offline from the broadcast machine, whenever the bundled
Hijri years run out (currently covers 1448-1449 / 2026-06-16 to 2028-05-24).

Usage:
    python fetch_prayer_times.py            # regenerates 1448 and 1449
    python fetch_prayer_times.py 1450 1451  # regenerates specific years
"""

import requests
import json
import time
import sys

METHOD = 4  # Umm Al-Qura University, Makkah

CITIES = {
    "makkah": {"lat": 21.4225, "lon": 39.8262},
    "madinah": {"lat": 24.4672, "lon": 39.6112},
}

DEFAULT_YEARS = [1448, 1449]
KEYS = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]

def clean_time(s):
    # "04:10 (+03)" -> "04:10"
    return s.split(" ")[0]

def fetch_month(lat, lon, year, month):
    url = f"https://api.aladhan.com/v1/hijriCalendar/{year}/{month}"
    params = {"latitude": lat, "longitude": lon, "method": METHOD}
    for attempt in range(3):
        try:
            r = requests.get(url, params=params, timeout=30)
            r.raise_for_status()
            return r.json()["data"]
        except Exception as e:
            print(f"  retry {attempt+1} for {year}-{month:02d}: {e}", file=sys.stderr)
            time.sleep(2)
    raise RuntimeError(f"Failed to fetch {year}-{month:02d}")

def main():
    # Usage: python fetch_prayer_times.py [hijri_year ...]
    # e.g. python fetch_prayer_times.py 1450 1451
    years = [int(y) for y in sys.argv[1:]] or DEFAULT_YEARS

    for city, coords in CITIES.items():
        for year in years:
            out = {}
            for month in range(1, 13):
                print(f"Fetching {city} {year}-{month:02d}...")
                days = fetch_month(coords["lat"], coords["lon"], year, month)
                for d in days:
                    g = d["date"]["gregorian"]
                    # DD-MM-YYYY -> YYYY-MM-DD
                    dd, mm, yyyy = g["date"].split("-")
                    key = f"{yyyy}-{mm}-{dd}"
                    weekday_en = g["weekday"]["en"]
                    t = d["timings"]
                    out[key] = {
                        "weekday": weekday_en,
                        "Fajr": clean_time(t["Fajr"]),
                        "Dhuhr": clean_time(t["Dhuhr"]),
                        "Asr": clean_time(t["Asr"]),
                        "Maghrib": clean_time(t["Maghrib"]),
                        "Isha": clean_time(t["Isha"]),
                    }
                time.sleep(0.3)
            fname = f"{city}_{year}.json"
            with open(fname, "w", encoding="utf-8") as f:
                json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)
            print(f"Wrote {fname} with {len(out)} days")

if __name__ == "__main__":
    main()
