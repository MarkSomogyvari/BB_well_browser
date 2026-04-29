import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
import os

def compare_versions():
    wiggly_path = 'data/processed/purity_optimized_clusters_v2.shp'
    smooth_path = 'data/processed/final_cleaned_clusters.shp'
    output_fig = 'reports/figures/cluster_version_comparison.png'

    print("Loading both versions...")
    gdf_wiggly = gpd.read_file(wiggly_path)
    gdf_smooth = gpd.read_file(smooth_path)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 12))

    # Plot Wiggly Version
    print("Plotting wiggly version...")
    gdf_wiggly.plot(ax=ax1, edgecolor='white', linewidth=0.5, alpha=0.6, column='cluster_id', cmap='tab20')
    ax1.set_title("Version A: Raster-Aligned (Wiggly)\nHigh Purity, Follows Pixel Boundaries", fontsize=16)
    cx.add_basemap(ax1, crs=gdf_wiggly.crs.to_string(), source=cx.providers.OpenStreetMap.Mapnik)

    # Plot Smooth Version
    print("Plotting smooth version...")
    gdf_smooth.plot(ax=ax2, edgecolor='black', linewidth=1, alpha=0.6, column='cluster_id', cmap='tab20')
    ax2.set_title("Version B: Convex-Optimized (Smooth)\nHigh Convexity, Simplified Boundaries", fontsize=16)
    cx.add_basemap(ax2, crs=gdf_smooth.crs.to_string(), source=cx.providers.OpenStreetMap.Mapnik)

    for ax in [ax1, ax2]:
        ax.set_axis_off()

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_fig), exist_ok=True)
    plt.savefig(output_fig, dpi=300, bbox_inches='tight')
    print(f"Comparison saved to {output_fig}")

if __name__ == "__main__":
    compare_versions()
