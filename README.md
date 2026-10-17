## Data Dictionary

The training, validation, and test files created by `src/unify.py` are the primary datasets. Each contains the same schema, with rows split by customer group.

### `data_learn.csv`, `data_finetune.csv`, `data_test.csv`

| Column | Description |
| --- | --- |
| `DATETIME_30MIN` | Timestamp for the 30-minute interval shared across the SGSC and AEMO datasets. |
| `CUSTOMER_ID` | Unique identifier for the customer or building in the SGSC dataset. |
| `KWH_READING` | Electricity consumption for that customer during the interval, measured in kWh. |
| `PRICE_AUD_MWH` | Regional reference price in Australian dollars per megawatt-hour. |
| `DEMAND_MW` | Total regional electricity demand in megawatts. |
| `HOUR` | Hour of the day (0 to 23) for the interval. |
| `DAY_OF_WEEK` | Day of the week index where Monday = 0 and Sunday = 6. |
| `IS_WEEKEND` | Binary flag indicating whether the interval falls on a weekend (1) or weekday (0). |
| `MONTH` | Month of the year (1 to 12). |
| `KWH_LAG_1HR` | Energy consumption from 1 hour earlier, used as a short-term lag feature. |
| `KWH_LAG_3DAYS` | Energy consumption from 3 days earlier, used as a medium-range lag feature. |
| `KWH_LAG_1WEEK` | Energy consumption from 1 week earlier, used as a longer-term lag feature. |

## Requirements

The project uses Python 3 and depends on the following packages:

- pandas
- numpy
- requests

Install dependencies with:

```bash
pip install pandas numpy requests
```

## Usage

1. Download source AEMO and SGSC data
   ```bash
   python src/fetch_aemo.py
   ```
   This fetches monthly AEMO price-and-demand CSVs and saves the raw output to `data/raw/aemo_nsw_2013.csv`.

   Download the SGSC Dataset: https://data.mendeley.com/datasets/zm4f727vvr/1
    - SGSC data should be downloaded and unzipped into `data/raw/sgsc/`.
        - SGSC raw interval-load data should remain under `data/raw/sgsc/interval load data/data_3_groups.csv`.
        - Supporting SGSC index files should remain under `data/raw/sgsc/index files/`.
   
2. Clean the AEMO dataset
   ```bash
   python src/clean_aemo.py
   ```
   This keeps only the relevant columns, converts times to a standard format, renames fields, and writes the cleaned output to `data/cleaned/aemo_cleaned.csv`.

3. Clean the SGSC dataset
   ```bash
   python src/clean_sgsc.py
   ```
   This reshapes the wide customer table into a long-form consumer dataset and writes `data/cleaned/sgsc_cleaned.csv`.

4. Merge and prepare modelling data
   ```bash
   python src/unify.py
   ```
   This joins SGSC and AEMO records, adds temporal and lag features, drops incomplete rows, and exports `data_learn.csv`, `data_finetune.csv`, and `data_test.csv`.

## Script summary

- `src/fetch_aemo.py`: downloads raw AEMO market datasets for a selected year and region.
- `src/clean_aemo.py`: cleans the raw AEMO CSV into a compact, analysis-ready table.
- `src/clean_sgsc.py`: converts SGSC wide-form interval data into long-form per-customer readings.
- `src/unify.py`: merges both sources, engineers features, and creates train/validation/test output files.

## Data sources and attribution

This project uses and adapts publicly available datasets from the following sources:

- Smart Grid Smart City (SGSC) data: Roberts, Mike; Haghdadi, Navid; Bruce, Anna; MacGill, Iain (2019), “Clustered residential electricity load profiles from Smart Grid Smart City dataset”, Mendeley Data, V1, doi: 10.17632/zm4f727vvr.1
  - License: Creative Commons Attribution 4.0 International (CC BY 4.0)
  - Source: [Mendeley Data](https://data.mendeley.com/datasets/zm4f727vvr/1)

- AEMO price and demand data: historical 30-minute interval regional reference prices and total demand for the NSW region from the Australian Energy Market Operator (AEMO).

## Folder structure

```text
root/
├── data/
│   ├── cleaned/
│   │   ├── aemo_cleaned.csv
│   │   ├── data_finetune.csv
│   │   ├── data_learn.csv
│   │   ├── data_test.csv
│   │   └── sgsc_cleaned.csv
│   └── raw/
│       ├── README.md
│       ├── aemo_nsw_2013.csv
│       └── sgsc/
│           ├── index files/
│           │   ├── Column Mappings.csv
│           │   ├── cluster_index.csv
│           │   └── demographic_lookup_3_groups.csv
│           └── interval load data/
│               └── data_3_groups.csv
├── src/
│   ├── clean_aemo.py
│   ├── clean_sgsc.py
│   ├── fetch.py
│   └── unify.py
├── .gitignore
├── LICENSE
└── README.md
```