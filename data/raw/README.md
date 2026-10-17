# Raw Data Guide

Datasets:
- Clustered SGSC: https://www.doi.org/10.17632/zm4f727vvr.1
- AEMO: https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/data-nem/aggregated-data

This folder stores the source datasets before any cleaning or feature engineering is applied. The project assumes the raw files are kept here so the scripts in `src/` can load them consistently.

## Usage instructions

1. Download the raw AEMO data:
   ```bash
   # from the root of the project
   python src/fetch_aemo.py
   ```
   This writes the raw AEMO CSV into `data/raw/`.

2. Keep source files in the expected folders:
   - AEMO raw market data should be downloaded to `data/raw/aemo_nsw_2013.csv`.
   - SGSC data should be downloaded and unzipped into `data/raw/sgsc/`.
     - SGSC raw interval-load data should remain under `data/raw/sgsc/interval load data/data_3_groups.csv`.
     - Supporting SGSC index files should remain under `data/raw/sgsc/index files/`.

## Expected file tree

```text
data_processing/
├── data/
│   └── raw/
│       ├── aemo_nsw_2013.csv
│       └── sgsc/
│           ├── index files/
│           │   ├── cluster_index.csv
│           │   ├── Column Mappings.csv
│           │   └── demographic_lookup_3_groups.csv
│           └── interval load data/
│               └── data_3_groups.csv
└── src/
    ├── clean_aemo.py
    ├── clean_sgsc.py
    ├── fetch.py
    └── unify.py
```