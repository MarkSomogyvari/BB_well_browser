import pandas as pd
import numpy as np
import os
from scipy.stats import theilslopes, kendalltau
from tqdm import tqdm

def analyze_groundwater_trends():
    """
    Analyzes long-term trends in groundwater levels for high-quality wells.
    Calculates Theil-Sen slope and Kendall significance.
    """
    quality_summary_path = 'data/processed/timeseries_quality_summary_2000_2025.csv'
    timeseries_dir = 'data/interim/timeseries_weekly'
    output_path = 'data/processed/groundwater_trends_2000_2025.csv'

    # Load quality summary and filter for high-quality wells
    df_quality = pd.read_csv(quality_summary_path)
    high_quality_wells = df_quality[df_quality['Flagged'] == False].copy()
    
    print(f"Analyzing trends for {len(high_quality_wells)} high-quality wells...")

    results = []

    for _, row in tqdm(high_quality_wells.iterrows(), total=len(high_quality_wells)):
        well_id = str(row['ID'])
        region = row['Region']
        
        # Construct filename
        prefix = 'BB_' if region == 'Brandenburg' else 'BE_'
        filename = f"{prefix}{well_id}_weekly.csv"
        file_path = os.path.join(timeseries_dir, filename)
        
        if not os.path.exists(file_path):
            # Try without .0 for Berlin wells if needed (though IDs in quality summary should match filenames)
            if well_id.endswith('.0'):
                well_id = well_id[:-2]
                filename = f"{prefix}{well_id}_weekly.csv"
                file_path = os.path.join(timeseries_dir, filename)
        
        if not os.path.exists(file_path):
            continue

        try:
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'])
            df = df.dropna(subset=['gw_level'])
            
            if len(df) < 52: # Minimum 1 year of data points
                continue
                
            # Convert dates to numeric (days since start) for slope calculation
            days = (df['date'] - df['date'].min()).dt.days.values
            levels = df['gw_level'].values
            
            # Theil-Sen Estimator
            slope, intercept, low_slope, high_slope = theilslopes(levels, days)
            
            # Convert slope from m/day to m/year
            slope_m_per_year = slope * 365.25
            
            # Kendall's Tau for significance
            tau, p_value = kendalltau(days, levels)
            
            # Basic stats
            mean_level = np.mean(levels)
            std_level = np.std(levels)
            total_change = slope_m_per_year * (days.max() / 365.25)
            
            results.append({
                'well_id': well_id,
                'region': region,
                'slope_m_per_year': slope_m_per_year,
                'p_value': p_value,
                'tau': tau,
                'mean_level': mean_level,
                'std_level': std_level,
                'total_change_est': total_change,
                'count': len(df),
                'start_date': df['date'].min().strftime('%Y-%m-%d'),
                'end_date': df['date'].max().strftime('%Y-%m-%d')
            })
            
        except Exception as e:
            print(f"Error analyzing well {well_id}: {e}")

    # Save results
    df_results = pd.DataFrame(results)
    df_results.to_csv(output_path, index=False)
    print(f"Trend analysis complete. Results saved to {output_path}")

if __name__ == "__main__":
    analyze_groundwater_trends()
