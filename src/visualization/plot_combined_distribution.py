import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
import os
from shapely.geometry import Point

def plot_combined_distribution():
    # Paths
    bb_path = 'data/processed/topmost_aquifer_wells.csv'
    be_path = 'data/processed/berlin_topmost_identification.csv'
    be_meta_path = 'data/raw/Berlin_wells/berlin_gw_metadata.csv'
    output_plot = 'reports/figures/combined_well_map.png'

    print("Loading datasets...")
    df_bb = pd.read_csv(bb_path)
    df_be = pd.read_csv(be_path)
    df_be_meta = pd.read_csv(be_meta_path)

    # 1. Process Brandenburg (already has x, y in EPSG:25833)
    gdf_bb = gpd.GeoDataFrame(
        df_bb, 
        geometry=gpd.points_from_xy(df_bb.x, df_bb.y), 
        crs="EPSG:25833"
    )
    gdf_bb['region'] = 'Brandenburg'

    # 2. Process Berlin
    # Merge be identification with coordinates from WFS meta
    # Note: be_path ID is string, be_meta 'invhyas' is numeric in CSV
    df_be['ID'] = pd.to_numeric(df_be['ID'], errors='coerce')
    df_be_combined = pd.merge(df_be, df_be_meta, left_on='ID', right_on='invhyas')
    
    # The WFS metadata has xcoord and ycoord (UTM 33N / EPSG:25833 based on inspection)
    gdf_be = gpd.GeoDataFrame(
        df_be_combined,
        geometry=gpd.points_from_xy(df_be_combined.xcoord, df_be_combined.ycoord),
        crs="EPSG:25833"
    )
    gdf_be['region'] = 'Berlin'

    # 3. Combine
    combined_gdf = pd.concat([
        gdf_bb[['ID', 'is_topmost', 'region', 'geometry']], 
        gdf_be[['ID', 'is_topmost', 'region', 'geometry']]
    ])

    # 4. Plot
    print(f"Plotting {len(combined_gdf)} total wells...")
    fig, ax = plt.subplots(figsize=(15, 12))
    
    # Plot deep wells
    combined_gdf[combined_gdf['is_topmost'] == False].plot(
        ax=ax, color='red', markersize=5, label='Deep Aquifer / Mismatch', alpha=0.5
    )
    
    # Plot topmost wells
    combined_gdf[combined_gdf['is_topmost'] == True].plot(
        ax=ax, color='blue', markersize=5, label='Topmost Aquifer', alpha=0.7
    )

    # Add OSM basemap
    print("Adding OpenStreetMap basemap...")
    cx.add_basemap(ax, crs=combined_gdf.crs.to_string(), source=cx.providers.OpenStreetMap.Mapnik)

    ax.set_title('Combined Groundwater Well Distribution: Brandenburg & Berlin\nTopmost Aquifer Identification', fontsize=16)
    ax.legend(loc='upper right', frameon=True, facecolor='white')
    ax.set_axis_off()

    os.makedirs(os.path.dirname(output_plot), exist_ok=True)
    plt.savefig(output_plot, dpi=300, bbox_inches='tight')
    print(f"Combined map saved to {output_plot}")

    # Summary
    print("\nSummary Results:")
    print(combined_gdf.groupby(['region', 'is_topmost']).size().unstack(fill_value=0))

if __name__ == "__main__":
    plot_combined_distribution()
