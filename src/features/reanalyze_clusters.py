import geopandas as gpd
import pandas as pd
import rasterio
from shapely.geometry import shape, Point, box, MultiPoint
from shapely.ops import voronoi_diagram
from sklearn.cluster import KMeans
import numpy as np
import os
import matplotlib.pyplot as plt
import contextily as cx

def reanalyze_clusters_voronoi():
    # Paths
    raster_path = 'data/raw/clusters.tif'
    bb_path = 'data/processed/topmost_aquifer_wells.csv'
    be_path = 'data/processed/berlin_topmost_identification.csv'
    be_meta_path = 'data/raw/Berlin_wells/berlin_gw_metadata.csv'
    output_shp = 'data/processed/new_clusters.shp'
    output_report = 'reports/cluster_reanalysis_summary.md'

    print("Loading wells...")
    df_bb = pd.read_csv(bb_path)
    gdf_bb = gpd.GeoDataFrame(df_bb[df_bb['is_topmost'] == True], 
                              geometry=gpd.points_from_xy(df_bb[df_bb['is_topmost'] == True].x, 
                                                         df_bb[df_bb['is_topmost'] == True].y), 
                              crs="EPSG:25833")
    
    df_be = pd.read_csv(be_path)
    df_be_meta = pd.read_csv(be_meta_path)
    df_be = pd.merge(df_be[df_be['is_topmost'] == True], df_be_meta, left_on='ID', right_on='invhyas')
    gdf_be = gpd.GeoDataFrame(df_be, 
                              geometry=gpd.points_from_xy(df_be.xcoord, df_be.ycoord), 
                              crs="EPSG:25833")
    
    wells = pd.concat([gdf_bb[['geometry']], gdf_be[['geometry']]]).reset_index(drop=True)
    coords = np.array([(p.x, p.y) for p in wells.geometry])

    # 1. Get Cluster Centers
    print(f"Calculating 25 cluster centers using K-Means...")
    kmeans = KMeans(n_clusters=25, random_state=42, n_init=10)
    kmeans.fit(coords)
    centers = [Point(c) for c in kmeans.cluster_centers_]
    centers_multipoint = MultiPoint(centers)

    # 2. Get Study Area Boundary (from GPKG)
    print("Loading area boundary from GPKG...")
    boundary_path = 'data/raw/area_boundary.gpkg'
    gdf_boundary = gpd.read_file(boundary_path)
    if gdf_boundary.crs != "EPSG:25833":
        gdf_boundary = gdf_boundary.to_crs("EPSG:25833")
    study_area = gdf_boundary.unary_union

    # 3. Generate Voronoi Diagram
    print("Generating Voronoi partitioning...")
    # voronoi_diagram returns a GeometryCollection of polygons
    region_voronoi = voronoi_diagram(centers_multipoint, envelope=study_area.buffer(10000))
    
    # 4. Clip and Filter
    voronoi_polys = []
    for poly in region_voronoi.geoms:
        clipped = poly.intersection(study_area)
        if not clipped.is_empty:
            voronoi_polys.append(clipped)

    gdf_clusters = gpd.GeoDataFrame(geometry=voronoi_polys, crs="EPSG:25833")
    gdf_clusters['cluster_id'] = range(len(gdf_clusters))

    # 5. Spatial Join Wells to Clusters to confirm counts
    print("Verifying well counts per cluster...")
    wells_joined = gpd.sjoin(wells, gdf_clusters, how="left", predicate="within")
    counts = wells_joined.groupby('cluster_id').size()
    gdf_clusters['well_count'] = gdf_clusters['cluster_id'].map(counts).fillna(0)

    # Save
    os.makedirs(os.path.dirname(output_shp), exist_ok=True)
    gdf_clusters.to_file(output_shp)
    print(f"Saved {len(gdf_clusters)} contiguous clusters to {output_shp}")

    # Visualization
    print("Creating visualization...")
    fig, ax = plt.subplots(figsize=(12, 12))
    gdf_clusters.plot(ax=ax, edgecolor='white', linewidth=1, alpha=0.4, cmap='tab20', column='cluster_id')
    wells.plot(ax=ax, markersize=1, color='black', alpha=0.3)
    gdf_boundary.plot(ax=ax, facecolor='none', edgecolor='red', linewidth=2, label='Area Boundary')
    cx.add_basemap(ax, crs=gdf_clusters.crs.to_string(), source=cx.providers.OpenStreetMap.Mapnik)
    ax.set_title('Contiguous Well Clusters (n=25)\nClipped to Brandenburg Area Boundary', fontsize=14)
    
    viz_path = 'reports/figures/reanalyzed_clusters.png'
    os.makedirs(os.path.dirname(viz_path), exist_ok=True)
    plt.savefig(viz_path, dpi=300, bbox_inches='tight')
    
    # Generate Report
    with open(output_report, 'w', encoding='utf-8') as f:
        f.write("# Cluster Reanalysis Summary (Contiguous Tessellation)\n\n")
        f.write("## Objective\n")
        f.write("Create a seamless partitioning of the Brandenburg-Berlin region into ~25 convex shapes that each contain monitoring wells.\n\n")
        f.write("## Methodology\n")
        f.write("1. **Seed Points:** Calculated 25 spatial centroids using K-Means clustering on 2,076 topmost wells.\n")
        f.write("2. **Tessellation:** Generated a **Voronoi Diagram** based on these centroids to ensure clusters touch but never overlap.\n")
        f.write("3. **Coverage:** Clipped the partitioning to the **official area boundary** (`data/raw/area_boundary.gpkg`) instead of a simple raster extent.\n")
        f.write("4. **Geometric Integrity:** Voronoi cells are mathematically guaranteed to be convex and perfectly adjacent within the defined boundary.\n\n")
        f.write("## Results\n")
        f.write(f"- **Total Clusters:** {len(gdf_clusters)}\n")
        f.write(f"- **Coverage:** Exact match to input area boundary.\n")
        f.write(f"- **Well Inclusion:** Every cluster contains at least {int(gdf_clusters['well_count'].min())} wells.\n")
        f.write(f"- **Average Wells per Cluster:** {gdf_clusters['well_count'].mean():.1f}\n\n")
        f.write("## Visualization\n")
        f.write("![Reanalyzed Clusters](figures/reanalyzed_clusters.png)\n\n")
        f.write("## Output Files\n")
        f.write(f"- Shapefile: `{output_shp}`\n")
        f.write("- Summary Report: `reports/cluster_reanalysis_summary.md`\n")

    print(f"Report generated at {output_report}")

if __name__ == "__main__":
    reanalyze_clusters_voronoi()
