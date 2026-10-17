import pandas as pd
import numpy as np
from pathlib import Path

RANDOM_SEED = 123

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CLEANED_DATA_DIR = DATA_DIR / "cleaned"
RAW_DATA_DIR = DATA_DIR / "raw"

CLEANED_DATA_DIR.mkdir(parents=True, exist_ok=True)

def clean_sgsc(sample_size=1500):
    print("Cleaning SGSC interval data...")
    sgsc_path = RAW_DATA_DIR / "ClusteredSGSC" / "interval load data" / "data_3_groups.csv"
    
    print(f"Reading SGSC data from {sgsc_path}...")
    # Read the wide-format dataset
    df = pd.read_csv(sgsc_path)

    if sample_size is not None:
        print(f"Sampling {sample_size} random buildings...")
        # All columns except 'timestamp' are customer IDs
        customer_cols = [col for col in df.columns if col != 'timestamp']
        
        # Randomly select the desired number of customer columns
        np.random.seed(RANDOM_SEED)
        actual_size = min(sample_size, len(customer_cols))
        sampled_customers = np.random.choice(customer_cols, size=actual_size, replace=False).tolist()
        
        # Keep only the timestamp and the sampled customers to reduce melt overhead
        df = df[['timestamp'] + sampled_customers]

    print("Changing data from wide to long format...")
    # Melt unpivots the data from wide to long format
    long_df = df.melt(
        id_vars=['timestamp'], 
        var_name='CUSTOMER_ID', 
        value_name='KWH_READING'
    )
    
    print("Renaming columns and downcasting data types...")
    long_df = long_df.rename(columns={'timestamp': 'READING_DATETIME'})
    
    # Downcast data types to significantly reduce file size and RAM usage
    long_df['CUSTOMER_ID'] = long_df['CUSTOMER_ID'].astype(np.int32)
    long_df['KWH_READING'] = long_df['KWH_READING'].astype(np.float32)
    
    print("Converting timestamps to 30-minute intervals...")
    # Convert to datetime and round to 30 mins to align with AEMO
    long_df['READING_DATETIME'] = pd.to_datetime(long_df['READING_DATETIME'])
    long_df['DATETIME_30MIN'] = long_df['READING_DATETIME'].dt.round('30min')
    long_df = long_df.drop(columns=['READING_DATETIME'])
    
    print("Dropping N/A values in KWH readings...")
    # Drop empty readings
    long_df = long_df.dropna(subset=['KWH_READING'])
    
    out_path = CLEANED_DATA_DIR / "sgsc_cleaned.csv"
    print(f"Saving cleaned SGSC data to {out_path}...")
    long_df.to_csv(out_path, index=False)
    
    print(f"Cleaned SGSC saved to {out_path}")

if __name__ == "__main__":
    # You can pass sample_size=None to process the entire dataset
    clean_sgsc(sample_size=1500)