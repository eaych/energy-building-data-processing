"""Download raw AEMO market data for a specified year and region.

Input:
year: integer year to fetch, such as 2013.
region: AEMO region code, defaulting to NSW1.

Output:
data/aemo_nsw_2013.csv: raw AEMO price and demand export saved from the public API.

aemo_nsw_2013.csv:

 Column            Description
 REGION            The region of the National Electricity Market (NEM) the data applies to. The NEM is divided  
                   into five regions: NSW, VIC, QLD, SA, and TAS.                                             
 SETTLEMENTDATE    The date and time for which the data is recorded, typically in 30-minute intervals.         
 TOTALDEMAND       The total electricity consumption in a region, measured in megawatts (MW).               
 RRP               The wholesale electricity price for each region in the NEM, calculated every 5 minutes and 
                   then averaged over 30-minute intervals.                                                 
 PERIODTYPE        Indicates whether the data corresponds to a normal trading period (TRADE) or an          
                   exceptional circumstance such as a system restart (NON-TRADE).                          
"""

# Downloads AEMO data for a specified year and region, saving it to a CSV file in ../data/

import requests
import pandas as pd
import time
import io
from pathlib import Path

# Resolve absolute paths based on the script's location
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def retrieve_aemo_subset(year, region="NSW1"):
    aemo_frames = []

    # required otherwise AEMO will return Error 403
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    }
    
    for month in range(1, 13):
        url = f"https://aemo.com.au/aemo/data/nem/priceanddemand/PRICE_AND_DEMAND_{year}{month:02d}_{region}.csv"
        try:
            print(f"Downloading AEMO data from {url}...")
            response = requests.get(url, headers=headers)
            response.raise_for_status() 
            df = pd.read_csv(io.StringIO(response.text))
            aemo_frames.append(df)
            time.sleep(1) 
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            
    return pd.concat(aemo_frames, ignore_index=True) if aemo_frames else pd.DataFrame()

if __name__ == "__main__":
    aemo_df = retrieve_aemo_subset(year=2013, region="NSW1")
    if not aemo_df.empty:
        output_path = DATA_DIR / "aemo_nsw_2013.csv"
        aemo_df.to_csv(output_path, index=False)
        print(f"AEMO data downloaded to {output_path}")