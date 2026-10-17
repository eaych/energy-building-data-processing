"""Merge the clean AEMO and SGSC datasets, add time and lag features, and split them for model training.

Input:
data/cleaned/sgsc_cleaned.csv: customer energy readings by timestamp and customer.
data/cleaned/aemo_cleaned.csv: market price and demand data by timestamp.

Output:
data/cleaned/data_learn.csv: learning split for model training.
data/cleaned/data_finetune.csv: tuning split for validation.
data/cleaned/data_test.csv: hold-out split for final evaluation.

data_learn.csv / data_finetune.csv / data_test.csv:

 Column            Description
 DATETIME_30MIN    timestamp aligned across market and customer readings       
 CUSTOMER_ID       customer or building identifier                             
 KWH_READING       customer electricity usage in kWh                           
 PRICE_AUD_MWH     regional price in AUD per MWh                               
 DEMAND_MW         total national demand in MW                                 
 HOUR              hour of day                                                  
 DAY_OF_WEEK       day of week (0 = Monday, 6 = Sunday)                       
 IS_WEEKEND        weekend flag (1 = weekend, 0 = weekday)                     
 MONTH             month of year                                                
 KWH_LAG_1HR       consumption from one hour earlier                             
 KWH_LAG_3DAYS     consumption from three days earlier                          
 KWH_LAG_1WEEK     consumption from one week earlier                            
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CLEANED_DATA_DIR = DATA_DIR / "cleaned"

def unify_and_prep():
    print("Loading cleaned datasets...")
    meter_df = pd.read_csv(CLEANED_DATA_DIR / "sgsc_cleaned.csv", parse_dates=['DATETIME_30MIN'])
    aemo_df = pd.read_csv(CLEANED_DATA_DIR / "aemo_cleaned.csv", parse_dates=['DATETIME_30MIN'])
    
    print("Merging datasets...")
    merged_df = pd.merge(meter_df, aemo_df, on='DATETIME_30MIN', how='inner')
    
    print("Building time-based clues...")
    merged_df['HOUR'] = merged_df['DATETIME_30MIN'].dt.hour
    merged_df['DAY_OF_WEEK'] = merged_df['DATETIME_30MIN'].dt.dayofweek
    merged_df['IS_WEEKEND'] = merged_df['DAY_OF_WEEK'].isin([5, 6]).astype(int)
    merged_df['MONTH'] = merged_df['DATETIME_30MIN'].dt.month
    
    print("Building lag clues...")
    merged_df = merged_df.sort_values(by=['CUSTOMER_ID', 'DATETIME_30MIN'])
    
    # 1 Hour ago (2 x 30min intervals)
    merged_df['KWH_LAG_1HR'] = merged_df.groupby('CUSTOMER_ID')['KWH_READING'].shift(2)
    # 3 Days ago (144 x 30min intervals)
    merged_df['KWH_LAG_3DAYS'] = merged_df.groupby('CUSTOMER_ID')['KWH_READING'].shift(144)
    # 1 Week ago (336 x 30min intervals)
    merged_df['KWH_LAG_1WEEK'] = merged_df.groupby('CUSTOMER_ID')['KWH_READING'].shift(336)
    
    merged_df = merged_df.dropna()
    
    print("Splitting buildings into Learn, Fine-Tune, and Test...")
    unique_buildings = merged_df['CUSTOMER_ID'].unique()
    np.random.shuffle(unique_buildings)
    
    n = len(unique_buildings)
    learn_idx = int(n * 0.7)
    tune_idx = int(n * 0.85)
    
    learn_buildings = unique_buildings[:learn_idx]
    tune_buildings = unique_buildings[learn_idx:tune_idx]
    test_buildings = unique_buildings[tune_idx:]
    
    learn_df = merged_df[merged_df['CUSTOMER_ID'].isin(learn_buildings)]
    tune_df = merged_df[merged_df['CUSTOMER_ID'].isin(tune_buildings)]
    test_df = merged_df[merged_df['CUSTOMER_ID'].isin(test_buildings)]

    print("Downcasting data types to save memory...")
    # Convert time/boolean clues to 8-bit integers
    int8_cols = ['HOUR', 'DAY_OF_WEEK', 'IS_WEEKEND', 'MONTH']
    merged_df[int8_cols] = merged_df[int8_cols].astype(np.int8)
    
    # Convert numerical readings and prices to 32-bit floats
    float_cols = ['KWH_READING', 'PRICE_AUD_MWH', 'DEMAND_MW', 
                  'KWH_LAG_1HR', 'KWH_LAG_3DAYS', 'KWH_LAG_1WEEK']
    merged_df[float_cols] = merged_df[float_cols].astype(np.float32)
    
    # Convert Customer ID to 32-bit integer
    merged_df['CUSTOMER_ID'] = merged_df['CUSTOMER_ID'].astype(np.int32)
    
    print("Saving datasets...")
    learn_df.to_csv(CLEANED_DATA_DIR / 'data_learn.csv', index=False)
    tune_df.to_csv(CLEANED_DATA_DIR / 'data_finetune.csv', index=False)
    test_df.to_csv(CLEANED_DATA_DIR / 'data_test.csv', index=False)
    
    print(f"Learn: {len(learn_buildings)} | Tune: {len(tune_buildings)} | Test: {len(test_buildings)}")

if __name__ == "__main__":
    unify_and_prep()