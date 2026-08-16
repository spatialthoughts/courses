"""Filter City of London Police 2024 crime data to theft-family categories.

Loads all 12 monthly CSVs from data/london_crime_2024/, keeps only the 7
theft-family Crime types, drops columns that are constant or entirely empty,
drops rows with any remaining missing value, and writes one merged CSV.
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/london_crime_2024")
OUT_DIR = Path("outputs/london_crime_2024_theft")
OUT_PATH = OUT_DIR / "london_theft_crimes_2024.csv"

THEFT_TYPES = [
    "Other theft",
    "Shoplifting",
    "Theft from the person",
    "Burglary",
    "Bicycle theft",
    "Robbery",
    "Vehicle crime",
]

# Reported by / Falls within are constant ("City of London Police") across the
# whole dataset, and Context is 100% empty — none carry information.
DROP_COLUMNS = ["Reported by", "Falls within", "Context"]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(DATA_DIR.glob("*/*.csv"))
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    print(f"Loaded {len(df):,} rows from {len(files)} files")

    theft = df[df["Crime type"].isin(THEFT_TYPES)].copy()
    print(f"Filtered to theft-family categories: {len(theft):,} rows")

    theft = theft.drop(columns=DROP_COLUMNS)
    print(f"Dropped columns: {DROP_COLUMNS}")

    before = len(theft)
    theft = theft.dropna()
    print(f"Dropped {before - len(theft):,} rows with missing data "
          f"(missing Longitude/Latitude/LSOA code/LSOA name)")

    theft.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(theft):,} rows x {len(theft.columns)} columns to {OUT_PATH}")
    print()
    print("Crime type counts in final file:")
    print(theft["Crime type"].value_counts().to_string())


if __name__ == "__main__":
    main()
