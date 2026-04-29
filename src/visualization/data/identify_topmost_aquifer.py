import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os

def identify_topmost_wells():
    # File paths
    meta_path = 'data/raw/Brandenburg_wells/well_meta_data/BB_GW_wells_metadata_coords_1.csv'
    shp_path = 'data/raw/Groundwater_distance/MuB/GW_Maechtigk_ungesaettigte_BZ.shp'
    output_path = 'data/processed/topmost_aquifer_wells.csv'

    print("Loading well metadata...")
    # Read metadata, handle German decimal separator
    df = pd.read_csv(meta_path, decimal=',')
    
    # Create GeoDataFrame from x, y (UTM 33N - EPSG:25833)
    print("Creating GeoDataFrame from well locations...")
    geometry = [Point(xy) for xy in zip(df['x'], df['y'])]
    wells_gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:25833")

    # Drop index_right if it exists to avoid conflicts in sjoin
    if 'index_right' in wells_gdf.columns:
        wells_gdf = wells_gdf.drop(columns=['index_right'])

    print("Loading groundwater distance shapefile...")
    # Shapefile is large (~800MB), using sample or reading efficiently
    dist_gdf = gpd.read_file(shp_path)
    
    print("Performing spatial join...")
    joined = gpd.sjoin(wells_gdf, dist_gdf, how="left", predicate="within")

    print("Calculating metrics...")
    # Clean up column names and convert to numeric
    joined['z_terrain'] = pd.to_numeric(joined['Gelaendehoehe (in Meter HS)'], errors='coerce')
    joined['h_measured'] = pd.to_numeric(joined['MW - Mittlerer Wasserstand [m ue. NHN]'], errors='coerce')
    joined['unsat_thickness_shp'] = pd.to_numeric(joined['WERT'], errors='coerce')
    
    # Groundwater distance below ground (measured)
    # MW Januar [cm uGOK] etc. are monthly means, MW - Mittlerer Wasserstand [cm u. GOK] is the long term mean
    # Let's check if the column name matches exactly what we saw in read_file
    # 'MW - Mittlerer Wasserstand [cm u. GOK]'
    
    col_cm_gok = 'MW - Mittlerer Wasserstand [cm u. GOK]'
    if col_cm_gok in joined.columns:
        joined['dist_measured_cm'] = pd.to_numeric(joined[col_cm_gok], errors='coerce')
        joined['dist_measured_m'] = joined['dist_measured_cm'] / 100.0
    else:
        # Fallback to elevation difference
        joined['dist_measured_m'] = joined['z_terrain'] - joined['h_measured']

    # Calculated groundwater level from shapefile (assuming WERT is in meters)
    joined['h_calculated'] = joined['z_terrain'] - joined['unsat_thickness_shp']
    
    # Difference between measured and calculated groundwater levels
    joined['h_diff'] = (joined['h_measured'] - joined['h_calculated']).abs()
    
    # Threshold for "topmost aquifer"
    threshold = 1.5  # meters
    joined['is_topmost'] = (joined['h_diff'] <= threshold)
    
    print(f"Identification complete.")
    print(f"Total wells: {len(joined)}")
    print(f"Wells with distance data: {joined['unsat_thickness_shp'].notna().sum()}")
    print(f"Wells identified as topmost: {joined['is_topmost'].sum()}")
    
    # Save results
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    joined.to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    identify_topmost_wells()
