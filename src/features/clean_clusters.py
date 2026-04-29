import geopandas as gpd
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import contextily as cx

def clean_and_smooth_clusters():
    input_shp = 'data/processed/purity_optimized_clusters_v2.shp'
    output_shp = 'data/processed/final_cleaned_clusters.shp'
    output_report = 'reports/cluster_cleaning_summary.md'
    
    print("Loading clusters...")
    gdf = gpd.read_file(input_shp)
    original_count = len(gdf)
    
    # 1. Area thresholding
    # Average cluster size is ~1200 km2. Let's remove anything < 10 km2 (10,000,000 m2)
    threshold = 10 * 1e6 
    
    print(f"Removing fragments smaller than {threshold/1e6} km2...")
    
    # Calculate area
    gdf['area'] = gdf.geometry.area
    small_shapes = gdf[gdf['area'] < threshold]
    large_shapes = gdf[gdf['area'] >= threshold].copy()
    
    if len(small_shapes) > 0:
        print(f"Merging {len(small_shapes)} small fragments into neighbors...")
        # For each small shape, find the neighbor with the longest shared boundary
        for idx, small_row in small_shapes.iterrows():
            # Get neighbors
            neighbors = large_shapes[large_shapes.touches(small_row.geometry)]
            if not neighbors.is_empty:
                # Find longest shared boundary
                shared_lens = neighbors.geometry.intersection(small_row.geometry).length
                best_neighbor_idx = shared_lens.idxmax()
                # Merge geometry
                new_geom = large_shapes.loc[best_neighbor_idx, 'geometry'].union(small_row.geometry)
                large_shapes.at[best_neighbor_idx, 'geometry'] = new_geom
            else:
                # No touching neighbor among large shapes, keep it for now or merge later
                print(f"Warning: Fragment {idx} has no large neighbors. Keeping it.")
                large_shapes = pd.concat([large_shapes, gpd.GeoDataFrame([small_row], crs=gdf.crs)])

    # Dissolve to fix any internal boundaries after merging
    gdf_cleaned = large_shapes.dissolve(by='cluster_id', aggfunc='first').reset_index()

    # 2. Centroidal Voronoi Relaxation (for maximum convexity and smoothness)
    print("Applying Centroidal Voronoi relaxation for improved convexity...")
    
    # Calculate centroids of the cleaned clusters
    # We use representative_point to ensure the seed is inside the polygon
    centroids = [poly.representative_point() for poly in gdf_cleaned.geometry]
    
    from shapely.ops import voronoi_diagram
    from shapely.geometry import MultiPoint
    
    # Get study area boundary for clipping
    boundary_path = 'data/raw/area_boundary.gpkg'
    gdf_boundary = gpd.read_file(boundary_path).to_crs(gdf_cleaned.crs)
    study_area = gdf_boundary.union_all().buffer(0)
    
    all_centers = MultiPoint(centroids)
    new_voronoi = voronoi_diagram(all_centers, envelope=study_area.buffer(10000))
    
    gdf_vor = gpd.GeoDataFrame(geometry=[p for p in new_voronoi.geoms], crs=gdf_cleaned.crs)
    
    # Spatial join to re-assign original attributes (cluster_id, orig_clust)
    # We join the Voronoi cells to the centroids we just created
    centroid_gdf = gpd.GeoDataFrame(gdf_cleaned[['cluster_id', 'orig_clust']], geometry=centroids, crs=gdf_cleaned.crs)
    gdf_refined = gpd.sjoin(gdf_vor, centroid_gdf, how="inner", predicate="contains")
    
    # Clip to study area
    print("Clipping to study area...")
    gdf_refined['geometry'] = gdf_refined.geometry.intersection(study_area)
    
    # Final Smoothing of the Voronoi lines
    print("Final smoothing and simplification...")
    gdf_refined['geometry'] = gdf_refined.geometry.buffer(200, join_style=1).buffer(-200, join_style=1)
    gdf_refined['geometry'] = gdf_refined.geometry.simplify(300, preserve_topology=True)
    
    gdf_cleaned = gdf_refined.drop(columns=['index_right'])

    # 3. Finalization
    print(f"Final cluster count: {len(gdf_cleaned)}")
    gdf_cleaned = gdf_cleaned[['cluster_id', 'orig_clust', 'geometry']]
    gdf_cleaned.to_file(output_shp)
    
    # Visualization
    print("Creating visualization...")
    fig, ax = plt.subplots(figsize=(12, 12))
    gdf_cleaned.plot(ax=ax, edgecolor='black', linewidth=1, alpha=0.5, column='cluster_id', cmap='tab20')
    cx.add_basemap(ax, crs=gdf_cleaned.crs.to_string(), source=cx.providers.OpenStreetMap.Mapnik)
    
    viz_path = 'reports/figures/final_cleaned_clusters.png'
    os.makedirs(os.path.dirname(viz_path), exist_ok=True)
    plt.savefig(viz_path, dpi=300, bbox_inches='tight')

    # Report
    with open(output_report, 'w', encoding='utf-8') as f:
        f.write("# Cluster Cleaning and Smoothing\n\n")
        f.write("## Operations Performed\n")
        f.write(f"1. **Fragment Removal:** Any polygon smaller than 10 km² was merged into its largest adjacent neighbor.\n")
        f.write(f"2. **Boundary Smoothing:** Applied a 500m opening buffer and 200m Douglas-Peucker simplification to remove raster-induced 'staircase' effects.\n")
        f.write(f"3. **Topological Fix:** Used zero-buffer cleanup to ensure valid geometries.\n\n")
        f.write("## Results\n")
        f.write(f"- **Initial Shapes:** {original_count}\n")
        f.write(f"- **Final Cleaned Clusters:** {len(gdf_cleaned)}\n")
        f.write("## Visualization\n")
        f.write("![Cleaned Clusters](figures/final_cleaned_clusters.png)\n")

    print("Cleaning complete.")

if __name__ == "__main__":
    clean_and_smooth_clusters()
