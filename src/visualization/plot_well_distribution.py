import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
import os

def plot_wells():
    # File paths
    gpkg_path = 'data/processed/topmost_wells_viz.gpkg'
    output_path = 'reports/figures/well_distribution_map.png'
    
    if not os.path.exists(gpkg_path):
        print(f"Error: {gpkg_path} not found.")
        return

    print("Loading GeoPackage data...")
    gdf = gpd.read_file(gpkg_path)

    # Create the plot
    fig, ax = plt.subplots(figsize=(15, 12))
    
    print("Plotting wells...")
    # Plot 'Deep' wells first
    gdf[gdf['is_topmost'] == False].plot(
        ax=ax, color='red', markersize=8, label='Deep Aquifer / Mismatch', alpha=0.7, edgecolor='white', linewidth=0.5
    )
    
    # Plot 'Topmost' wells
    gdf[gdf['is_topmost'] == True].plot(
        ax=ax, color='blue', markersize=8, label='Topmost Aquifer', alpha=0.7, edgecolor='white', linewidth=0.5
    )

    # Add OpenStreetMap basemap
    print("Adding OpenStreetMap basemap...")
    # EPSG:25833 is what we used for the GDF
    cx.add_basemap(ax, crs=gdf.crs.to_string(), source=cx.providers.OpenStreetMap.Mapnik)

    # Formatting
    ax.set_title('Spatial Distribution of Groundwater Wells in Brandenburg\nBasemap: OpenStreetMap', fontsize=16)
    ax.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.8)
    ax.set_axis_off()

    # Save the figure
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved to {output_path}")

if __name__ == "__main__":
    plot_wells()
