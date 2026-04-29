import pandas as pd
import numpy as np
import os

def aggregate_climate_to_weekly():
    """
    Aggregates daily climate data to weekly resolution to match groundwater levels.
    Calculates net water balance (P - PET).
    """
    input_path = 'data/interim/climate_at_wells/daily_climate_at_wells.csv'
    output_path = 'data/processed/weekly_climate_features.csv'
    
    if not os.path.exists(input_path):
        print("Daily climate data not found.")
        return

    df = pd.read_csv(input_path)
    df['date'] = pd.to_datetime(df['date'])
    
    # Sort to ensure correct rolling calculations later
    df = df.sort_values(['well_id', 'date'])
    
    # Weekly Aggregation
    # Note: 'W' in pandas is weekly ending Sunday.
    # We use 'W-SUN' to be explicit, matching our GW upscaling logic.
    
    df_weekly = df.groupby('well_id').resample('W', on='date').agg({
        'temp_2m_c': 'mean',
        'precip_mm': 'sum',
        'evap_mm': 'sum',
        'pot_evap_mm': 'sum'
    }).reset_index()
    
    # Calculate Net Water Balance (P - PET)
    # PET is usually negative in ERA5-Land (evaporation from surface), 
    # but pot_evap_mm is also negative.
    # We want P - |PET| or P + PET if PET is negative.
    df_weekly['net_balance_mm'] = df_weekly['precip_mm'] + df_weekly['pot_evap_mm']
    
    # Cumulative balances for different time scales (e.g., 3-month, 6-month, 12-month)
    # This is useful for capturing delayed groundwater response.
    # Note: These will only be useful once we have enough months of data.
    for months in [3, 6, 12]:
        weeks = months * 4 # Approximation
        df_weekly[f'cum_balance_{months}m_mm'] = df_weekly.groupby('well_id')['net_balance_mm'].transform(
            lambda x: x.rolling(window=weeks, min_periods=1).sum()
        )

    df_weekly.to_csv(output_path, index=False)
    print(f"Weekly climate features saved to {output_path}")
    print(df_weekly.head())

if __name__ == "__main__":
    aggregate_climate_to_weekly()
