import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os

def plot_groundwater_trends():
    """
    Plots the spatial distribution of groundwater trends.
    """
    trends_path = 'data/processed/groundwater_trends_with_coords.csv'
    boundary_path = 'data/raw/area_boundary.gpkg'
    output_map_path = 'reports/figures/groundwater_trends_map.png'
    output_hist_path = 'reports/figures/groundwater_trends_hist.png'
    os.makedirs('reports/figures', exist_ok=True)

    # Load trend data
    df = pd.read_csv(trends_path)
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.x, df.y), crs="EPSG:25833"
    )

    # Load boundary
    boundary = gpd.read_file(boundary_path)
    if boundary.crs != gdf.crs:
        boundary = boundary.to_crs(gdf.crs)

    # 1. Plot Map
    fig, ax = plt.subplots(figsize=(12, 10))
    boundary.plot(ax=ax, color='lightgrey', edgecolor='grey', alpha=0.5)
    
    # Scale points by significance and color by slope
    # Filter for significant trends for clearer visualization
    sig_gdf = gdf[gdf['p_value'] < 0.05]
    non_sig_gdf = gdf[gdf['p_value'] >= 0.05]
    
    # Plot non-significant trends as small grey dots
    non_sig_gdf.plot(ax=ax, color='grey', markersize=2, alpha=0.3, label='Not significant')
    
    # Plot significant trends
    scatter = ax.scatter(
        sig_gdf.geometry.x, sig_gdf.geometry.y,
        c=sig_gdf['slope_m_per_year'] * 100, # Convert to cm/year
        cmap='RdBu',
        vmin=-5, vmax=5, # Limit range for better contrast
        s=20,
        edgecolor='black', linewidth=0.5,
        label='Significant Trend'
    )
    
    plt.colorbar(scatter, label='Trend Magnitude (cm/year)')
    ax.set_title('Groundwater Level Trends (2000-2025)\nSurface-near Aquifers (Brandenburg & Berlin)', fontsize=14)
    ax.set_axis_off()
    
    plt.savefig(output_map_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Trend map saved to {output_map_path}")

    # 2. Plot Histogram
    plt.figure(figsize=(10, 6))
    plt.hist(df['slope_m_per_year'] * 100, bins=50, color='skyblue', edgecolor='black')
    plt.axvline(0, color='red', linestyle='--')
    plt.xlabel('Trend Magnitude (cm/year)')
    plt.ylabel('Frequency (Number of Wells)')
    plt.title('Distribution of Groundwater Level Trends (2000-2025)')
    plt.grid(axis='y', alpha=0.3)
    
    plt.savefig(output_hist_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Trend histogram saved to {output_hist_path}")

if __name__ == "__main__":
    plot_groundwater_trends()
