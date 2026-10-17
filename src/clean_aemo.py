import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CLEANED_DATA_DIR = DATA_DIR / "cleaned"
RAW_DATA_DIR = DATA_DIR / "raw"

CLEANED_DATA_DIR.mkdir(parents=True, exist_ok=True)

def clean_aemo():
    print("Cleaning AEMO data...")
    aemo_path = RAW_DATA_DIR / "aemo_nsw_2013.csv"
    df = pd.read_csv(aemo_path)

    print("Selecting relevant columns and converting timestamps...")
    df = df[['SETTLEMENTDATE', 'RRP', 'TOTALDEMAND']]
    df['SETTLEMENTDATE'] = pd.to_datetime(df['SETTLEMENTDATE'])
    
    print("Renaming columns to its metric units...")
    # Standardize column naming and metric measurement units
    df = df.rename(columns={
        'SETTLEMENTDATE': 'DATETIME_30MIN',
        'RRP': 'PRICE_AUD_MWH',
        'TOTALDEMAND': 'DEMAND_MW'
    })
    
    print("Dropping N/A values...")
    df = df.dropna()

    out_path = CLEANED_DATA_DIR / "aemo_cleaned.csv"
    
    print(f"Saving cleaned AEMO data to {out_path}...")
    df.to_csv(out_path, index=False)

    print(f"Cleaned AEMO saved to {out_path}")

if __name__ == "__main__":
    clean_aemo()