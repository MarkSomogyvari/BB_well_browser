# Cluster Reanalysis Summary (Contiguous Tessellation)

## Objective
Create a seamless partitioning of the Brandenburg-Berlin region into ~25 convex shapes that each contain monitoring wells.

## Methodology
1. **Seed Points:** Calculated 25 spatial centroids using K-Means clustering on 2,076 topmost wells.
2. **Tessellation:** Generated a **Voronoi Diagram** based on these centroids to ensure clusters touch but never overlap.
3. **Coverage:** Clipped the partitioning to the **official area boundary** (`data/raw/area_boundary.gpkg`) instead of a simple raster extent.
4. **Geometric Integrity:** Voronoi cells are mathematically guaranteed to be convex and perfectly adjacent within the defined boundary.

## Results
- **Total Clusters:** 25
- **Coverage:** Exact match to input area boundary.
- **Well Inclusion:** Every cluster contains at least 30 wells.
- **Average Wells per Cluster:** 83.0

## Visualization
![Reanalyzed Clusters](figures/reanalyzed_clusters.png)

## Output Files
- Shapefile: `data/processed/new_clusters.shp`
- Summary Report: `reports/cluster_reanalysis_summary.md`
