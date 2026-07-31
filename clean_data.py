"""
Data Cleaning & Transformation
------------------------------
Cleans a messy raw customer/order export and produces an analysis-ready CSV.

Issues handled:
  - Inconsistent name casing/whitespace
  - Inconsistent region casing/whitespace, missing values
  - Inconsistent date formats
  - Inconsistent / missing status values
  - Missing or invalid quantity and price values
  - Exact duplicate rows
  - Missing emails

Usage:
    python clean_data.py
Reads:  ../data/raw_customer_orders.csv
Writes: ../data/cleaned_customer_orders.csv
"""

import pandas as pd
from pathlib import Path

RAW_PATH = Path(__file__).resolve().parent.parent / "data" / "raw_customer_orders.csv"
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "cleaned_customer_orders.csv"


def load_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str)


def clean_names(df: pd.DataFrame) -> pd.DataFrame:
    df["customer_name"] = (
        df["customer_name"]
        .str.strip()
        .str.title()
        .str.replace(r"\s+", " ", regex=True)
    )
    return df


def clean_region(df: pd.DataFrame) -> pd.DataFrame:
    df["region"] = df["region"].fillna("").str.strip().str.title()
    df.loc[df["region"] == "", "region"] = "Unknown"
    return df


def clean_status(df: pd.DataFrame) -> pd.DataFrame:
    df["status"] = df["status"].fillna("").str.strip().str.title()
    df.loc[df["status"] == "", "status"] = "Unknown"
    return df


def clean_dates(df: pd.DataFrame) -> pd.DataFrame:
    # Try multiple known formats until one parses successfully per row
    df["signup_date"] = df["signup_date"].apply(_parse_date)
    return df


def _parse_date(value):
    if pd.isna(value) or value == "":
        return pd.NaT
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return pd.to_datetime(value, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT


def clean_numeric_fields(df: pd.DataFrame) -> pd.DataFrame:
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

    # Invalid quantities (negative or zero) treated as missing, then imputed with median
    df.loc[df["quantity"] <= 0, "quantity"] = pd.NA
    df["quantity"] = df["quantity"].fillna(df["quantity"].median())

    # Missing prices imputed with median price
    df["unit_price"] = df["unit_price"].fillna(df["unit_price"].median())

    df["quantity"] = df["quantity"].astype(int)
    df["unit_price"] = df["unit_price"].round(2)
    return df


def clean_email(df: pd.DataFrame) -> pd.DataFrame:
    df["email"] = df["email"].fillna("").str.strip().str.lower()
    df.loc[df["email"] == "", "email"] = "unknown@missing.com"
    return df


def drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(subset=[c for c in df.columns if c != "record_id"])
    after = len(df)
    print(f"Removed {before - after} duplicate rows")
    return df


def main():
    df = load_data(RAW_PATH)
    print(f"Loaded {len(df)} raw rows")

    df = clean_names(df)
    df = clean_region(df)
    df = clean_status(df)
    df = clean_dates(df)
    df = clean_numeric_fields(df)
    df = clean_email(df)
    df = drop_duplicates(df)

    df["revenue"] = (df["quantity"] * df["unit_price"]).round(2)

    df.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(df)} cleaned rows to {OUT_PATH}")


if __name__ == "__main__":
    main()
