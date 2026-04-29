
import pandas as pd
import os
import numpy as np
from pathlib import Path

def process_timeseries():
    # Define paths
    base_dir = Path(r"D:\Research_AI\Brandenburg_groundwater")
    bb_id_file = base_dir / "data" / "processed" / "topmost_aquifer_wells.csv"
    be_id_file = base_dir / "data" / "processed" / "berlin_topmost_identification.csv"
    output_dir = base_dir / "data" / "interim" / "timeseries_weekly"
    quality_summary_file = base_dir / "data" / "processed" / "timeseries_quality_summary_2000_2025.csv"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Target time range (2000-2025)
    start_date = '2000-01-01'
    end_date = '2025-12-31'
    target_index = pd.date_range(start=start_date, end=end_date, freq='W')
    
    # Load Brandenburg IDs
    bb_df = pd.read_csv(bb_id_file, dtype={'ID': str})
    # Ensure is_topmost is boolean
    if bb_df['is_topmost'].dtype == 'O':
        bb_df['is_topmost'] = bb_df['is_topmost'].map({'True': True, 'False': False, True: True, False: False})
    bb_topmost_ids = bb_df[bb_df['is_topmost'] == True]['ID'].tolist()
    
    # Load Berlin IDs
    be_df = pd.read_csv(be_id_file, dtype={'ID': str})
    if be_df['is_topmost'].dtype == 'O':
        be_df['is_topmost'] = be_df['is_topmost'].map({'True': True, 'False': False, True: True, False: False})
    be_topmost_ids = be_df[be_df['is_topmost'] == True]['ID'].tolist()
    
    quality_records = []
    
    # Process Brandenburg
    bb_raw_dir = base_dir / "data" / "raw" / "Brandenburg_wells" / "GWData_BB_all_prepro_lv1"
    for well_id in bb_topmost_ids:
        file_path = bb_raw_dir / f"BB_{well_id}_GW-Data.csv"
        if not file_path.exists():
            continue
            
        try:
            df = pd.read_csv(file_path, sep=';', decimal=',', quotechar='"')
            df['Zeitpunkt'] = pd.to_datetime(df['Zeitpunkt'], dayfirst=True)
            df = df.rename(columns={'Zeitpunkt': 'date', 'Wasserstand(NHN) [mNHN]': 'gw_level'})
            df = df[['date', 'gw_level']]
            
            # Resample and QA
            stats = process_well_data(df, target_index, well_id, 'Brandenburg', output_dir)
            quality_records.append(stats)
        except Exception as e:
            print(f"Error processing Brandenburg well {well_id}: {e}")

    # Process Berlin
    be_raw_dir = base_dir / "data" / "raw" / "Berlin_wells" / "timeseries"
    for well_id in be_topmost_ids:
        file_path = be_raw_dir / f"station_{well_id}.csv"
        if not file_path.exists():
            continue
            
        try:
            # Find the line where data starts
            with open(file_path, 'r', encoding='latin-1') as f:
                lines = f.readlines()
                skiprows = 0
                for i, line in enumerate(lines):
                    if line.startswith("Datum;"):
                        skiprows = i
                        break
            
            df = pd.read_csv(file_path, sep=';', decimal=',', skiprows=skiprows, encoding='latin-1')
            df = df.rename(columns={'Datum': 'date', df.columns[1]: 'gw_level'})
            df['date'] = pd.to_datetime(df['date'], dayfirst=True)
            df = df[['date', 'gw_level']]
            
            # Resample and QA
            stats = process_well_data(df, target_index, well_id, 'Berlin', output_dir)
            quality_records.append(stats)
        except Exception as e:
            print(f"Error processing Berlin well {well_id}: {e}")

    # Save quality summary
    summary_df = pd.DataFrame(quality_records)
    summary_df.to_csv(quality_summary_file, index=False)
    
    # Print summary
    total_wells = len(summary_df)
    passing_wells = len(summary_df[summary_df['Flagged'] == False])
    print(f"Total wells processed: {total_wells}")
    print(f"Wells passing quality check (<= 20% missing AND gap <= 52 weeks): {passing_wells}")
    print(f"Quality summary saved to {quality_summary_file}")

def process_well_data(df, target_index, well_id, region, output_dir):
    df = df.sort_values('date')
    df = df.set_index('date')
    
    # Resample to weekly mean
    df_weekly = df['gw_level'].resample('W').mean().reindex(target_index)
    
    # QA Metrics
    total_weeks = len(target_index)
    missing_count = df_weekly.isna().sum()
    pct_missing = (missing_count / total_weeks) * 100
    
    # Largest consecutive gap
    is_missing = df_weekly.isna()
    # Consecutive group trick
    gaps = is_missing.groupby((is_missing != is_missing.shift()).cumsum()).sum()
    # Filter only for True values (gaps)
    # The trick above counts consecutive True as group and sums them.
    # But it also counts consecutive False. We only want the True groups.
    # Corrected gap calculation:
    max_gap = 0
    if is_missing.any():
        # mask = is_missing == True
        # gaps = mask.groupby((mask != mask.shift()).cumsum()).sum()
        # This is slightly wrong because it sums booleans.
        # Let's use a more robust way:
        gaps = (is_missing != is_missing.shift()).cumsum()
        max_gap = is_missing.groupby(gaps).sum().max()
    
    flag = (pct_missing > 20) or (max_gap > 52)
    
    # Save processed CSV
    prefix = 'BB' if region == 'Brandenburg' else 'BE'
    output_file = output_dir / f"{prefix}_{well_id}_weekly.csv"
    df_weekly.to_csv(output_file, header=['gw_level'], index_label='date')
    
    return {
        'ID': well_id,
        'Region': region,
        'Pct_Missing': pct_missing,
        'Max_Gap_Weeks': max_gap,
        'Flagged': flag
    }

if __name__ == "__main__":
    process_timeseries()
