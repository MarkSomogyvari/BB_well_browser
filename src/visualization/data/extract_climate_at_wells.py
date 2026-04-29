import xarray as xr
import pandas as pd
import numpy as np
import os
from tqdm import tqdm

def extract_climate_at_wells():
    """
    Extracts ERA5-Land climate variables at well locations from GRIB files.
    """
    trends_coords_path = 'data/processed/groundwater_trends_with_coords.csv'
    grib_dir = 'data/raw/external/ERA5_Land'
    output_dir = 'data/interim/climate_at_wells'
    os.makedirs(output_dir, exist_ok=True)

    # 1. Load Well Locations
    df_wells = pd.read_csv(trends_coords_path)
    # Filter for high quality and valid coordinates
    df_wells = df_wells.dropna(subset=['x', 'y'])
    
    # 2. Get available GRIB files
    grib_files = sorted([f for f in os.listdir(grib_dir) if f.endswith('.grib') and 'test' not in f and 'monthly_means' not in f])
    
    if not grib_files:
        print("No GRIB files found for extraction.")
        return

    # Convert well coordinates to WGS84 for extraction (ERA5 is in WGS84)
    import geopandas as gpd
    gdf_wells = gpd.GeoDataFrame(
        df_wells, 
        geometry=gpd.points_from_xy(df_wells.x, df_wells.y), 
        crs="EPSG:25833"
    ).to_crs("EPSG:4326")
    
    lats = xr.DataArray(gdf_wells.geometry.y.values, dims="well")
    lons = xr.DataArray(gdf_wells.geometry.x.values, dims="well")
    well_ids = gdf_wells['well_id'].values

    all_data = []

    print(f"Extracting climate data from {len(grib_files)} files for {len(well_ids)} wells...")

    for grib_file in tqdm(grib_files):
        file_path = os.path.join(grib_dir, grib_file)
        
        try:
            # Open dataset
            ds = xr.open_dataset(file_path, engine='cfgrib')
            
            # Extract points (nearest neighbor)
            # ERA5-Land variables in GRIB: t2m, tp, e, pev
            subset = ds.sel(latitude=lats, longitude=lons, method='nearest')
            
            # Convert to DataFrame
            # The structure might have 'time' and 'step', we want 'valid_time'
            df_subset = subset.to_dataframe()
            
            # Reset index to get well dimension and time/step
            df_subset = df_subset.reset_index()
            
            # Use valid_time as the primary timestamp
            if 'valid_time' in df_subset.columns:
                df_subset['date'] = df_subset['valid_time']
            else:
                # Fallback if valid_time is not a coordinate
                df_subset['date'] = df_subset['time'] + df_subset['step']
            
            # Add well_id
            df_subset['well_id'] = well_ids[df_subset['well'].astype(int)]
            
            # Select and rename columns
            cols_to_keep = ['well_id', 'date', 't2m', 'tp', 'e', 'pev']
            df_subset = df_subset[cols_to_keep]
            
            all_data.append(df_subset)
            ds.close()
            
        except Exception as e:
            print(f"Error processing {grib_file}: {e}")

    if all_data:
        df_final = pd.concat(all_data)
        
        # Aggregate to Daily or Weekly to save space?
        # Let's aggregate to Daily first
        df_final['date_only'] = df_final['date'].dt.date
        df_daily = df_final.groupby(['well_id', 'date_only']).agg({
            't2m': 'mean',
            'tp': 'sum',
            'e': 'sum',
            'pev': 'sum'
        }).reset_index()
        
        df_daily.columns = ['well_id', 'date', 'temp_2m_k', 'precip_m', 'evap_m', 'pot_evap_m']
        
        # Conversions
        df_daily['temp_2m_c'] = df_daily['temp_2m_k'] - 273.15
        df_daily['precip_mm'] = df_daily['precip_m'] * 1000
        df_daily['evap_mm'] = df_daily['evap_m'] * 1000
        df_daily['pot_evap_mm'] = df_daily['pot_evap_m'] * 1000
        
        output_path = os.path.join(output_dir, 'daily_climate_at_wells.csv')
        df_daily.to_csv(output_path, index=False)
        print(f"Extraction complete. Daily data saved to {output_path}")
    else:
        print("No data extracted.")

if __name__ == "__main__":
    extract_climate_at_wells()
