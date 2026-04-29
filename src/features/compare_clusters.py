import geopandas as gpd
import pandas as pd
import rasterio
from rasterio.features import rasterize
import numpy as np
import matplotlib.pyplot as plt
import os

def compare_clusters():
    raster_path = 'data/raw/clusters.tif'
    clusters_shp = 'data/processed/new_clusters.shp'
    output_report = 'reports/cluster_comparison_analysis.md'
    output_fig = 'reports/figures/cluster_overlap_matrix.png'

    print("Loading data...")
    gdf_new = gpd.read_file(clusters_shp)
    
    with rasterio.open(raster_path) as src:
        raster_data = src.read(1)
        raster_crs = src.crs
        raster_transform = src.transform
        # Filter out nodata (assuming 0 or 255 if not specified, but let's check)
        nodata = src.nodata if src.nodata is not None else 0

    print(f"Raster CRS: {raster_crs}")
    print(f"New Clusters CRS: {gdf_new.crs}")

    if gdf_new.crs != raster_crs:
        gdf_new = gdf_new.to_crs(raster_crs)

    # 1. Manually calculate zonal statistics using rasterio.mask or rasterize
    print("Calculating zonal statistics using rasterio...")
    overlap_data = []
    
    with rasterio.open(raster_path) as src:
        nodata = src.nodata if src.nodata is not None else 0
        
        for idx, row in gdf_new.iterrows():
            # Mask the raster with the current polygon
            from rasterio.mask import mask
            try:
                out_image, out_transform = mask(src, [row.geometry], crop=True)
                data = out_image[0]
                
                # Get unique values and counts, excluding nodata
                values, counts = np.unique(data, return_counts=True)
                
                # Filter out nodata
                mask_valid = (values != nodata)
                values = values[mask_valid]
                counts = counts[mask_valid]
                
                total_pixels = counts.sum()
                if total_pixels > 0:
                    for v, c in zip(values, counts):
                        overlap_data.append({
                            'new_cluster_id': row['cluster_id'],
                            'orig_cluster_id': int(v),
                            'pixel_count': c,
                            'percentage': (c / total_pixels) * 100
                        })
            except ValueError:
                # This happens if the polygon is outside the raster extent
                print(f"Warning: Cluster {row['cluster_id']} is outside raster extent.")
                continue

    df_overlap = pd.DataFrame(overlap_data)
    
    # Pivot for heatmap
    pivot_pct = df_overlap.pivot(index='new_cluster_id', columns='orig_cluster_id', values='percentage').fillna(0)

    # 3. Analyze Purity (Certainty)
    # How much does the dominant original cluster represent the new cluster?
    purity = pivot_pct.max(axis=1)
    dominant_orig = pivot_pct.idxmax(axis=1)
    
    gdf_new['dominant_orig_cluster'] = dominant_orig
    gdf_new['purity_score'] = purity

    # 4. Visualization
    print("Generating heatmap...")
    fig, ax = plt.subplots(figsize=(14, 10))
    im = ax.imshow(pivot_pct, cmap="YlGnBu")
    
    # Add colorbar
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("% Overlap", rotation=-90, va="bottom")

    # Show all ticks and label them with the respective list entries
    ax.set_xticks(np.arange(len(pivot_pct.columns)))
    ax.set_yticks(np.arange(len(pivot_pct.index)))
    ax.set_xticklabels(pivot_pct.columns.astype(int))
    ax.set_yticklabels(pivot_pct.index.astype(int))

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(len(pivot_pct.index)):
        for j in range(len(pivot_pct.columns)):
            text = ax.text(j, i, f"{pivot_pct.iloc[i, j]:.0f}",
                           ha="center", va="center", color="black" if pivot_pct.iloc[i, j] < 50 else "white")

    ax.set_title("Spatial Relationship: New Clusters vs. Original Raster Clusters\n(Cell value = % of New Cluster area covered by Original Cluster)")
    ax.set_xlabel("Original Cluster ID (from Raster)")
    ax.set_ylabel("New Cluster ID (Voronoi)")
    fig.tight_layout()
    
    os.makedirs(os.path.dirname(output_fig), exist_ok=True)
    plt.savefig(output_fig, dpi=300, bbox_inches='tight')

    # 5. Generate Report
    print(f"Generating report at {output_report}...")
    with open(output_report, 'w', encoding='utf-8') as f:
        f.write("# Cluster Comparison Analysis\n\n")
        f.write("## Objective\n")
        f.write("Evaluate how the new Voronoi-based clusters (Task 5) relate to the original `clusters.tif` classification.\n\n")
        
        f.write("## Summary Statistics\n")
        f.write(f"- **Mean Purity Score:** {purity.mean():.1f}%\n")
        f.write(f"- **Max Purity Score:** {purity.max():.1f}%\n")
        f.write(f"- **Min Purity Score:** {purity.min():.1f}%\n\n")
        
        f.write("## Interpretation\n")
        f.write("- **High Purity (>70%):** The new cluster closely matches one original cluster. These are likely stable regions where well distribution aligns with the raster logic.\n")
        f.write("- **Low Purity (<40%):** The new cluster spans multiple original clusters. This is expected since the new clusters are contiguous and based on well density, whereas the raster may have been fragmented.\n\n")
        
        f.write("## Overlap Matrix (Heatmap)\n")
        f.write("![Cluster Overlap Matrix](figures/cluster_overlap_matrix.png)\n\n")
        
        f.write("## Detailed Mapping\n")
        f.write("| New Cluster ID | Dominant Original Cluster | Purity (%) |\n")
        f.write("|----------------|---------------------------|------------|\n")
        for idx, row in gdf_new.iterrows():
            f.write(f"| {int(row['cluster_id'])} | {int(row['dominant_orig_cluster'])} | {row['purity_score']:.1f} |\n")

    print("Done.")

if __name__ == "__main__":
    compare_clusters()
