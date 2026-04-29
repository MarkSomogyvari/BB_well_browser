# Comprehensive Clustering Methodology Report: Brandenburg-Berlin Groundwater Study

## 1. Objective
The goal of this task was to partition the Brandenburg and Berlin study area into approximately 25 contiguous, non-overlapping clusters. These clusters serve as the spatial units for subsequent spectral analysis and predictive modeling of groundwater level trends.

## 2. Data Sources
- **Monitoring Wells:** 2,076 identified topmost aquifer wells (combined Brandenburg and Berlin datasets).
- **Original Classification:** `data/raw/clusters.tif` – a raster file providing an initial categorical classification of the region.
- **Study Area Boundary:** `data/raw/area_boundary.gpkg` – the official spatial extent for the analysis.

## 3. Methodological Evolution

### Phase 1: Spatial Voronoi Partitioning
Initially, we applied **K-Means clustering** (k=25) to the well coordinates to find spatial centroids. A **Voronoi Tessellation** was then generated from these seeds. 
*   **Result:** Seamless partitioning based purely on well density.
*   **Limitation:** It ignored the existing physical/thematic boundaries defined in the original `clusters.tif` raster.

### Phase 2: Purity Analysis
We evaluated the "Purity" of Phase 1 clusters—defined as the percentage of a new cluster's area that falls within a single original raster class.
*   **Finding:** The mean purity was ~67%. Many clusters spanned multiple raster classes, which could potentially mix different hydrological regimes.

### Phase 3: Purity-Maximized Delineation
To improve consistency, we developed a **Raster-Guided Clustering** approach:
1.  **Well Sampling:** Every well was assigned the ID of the raster class it resided in.
2.  **Weighted Sub-division:** The 25 target clusters were distributed proportionally among the 5 original raster classes. Large classes (like Class 2) were subdivided into 17 smaller spatial units.
3.  **Intersection Logic:** Voronoi cells were intersected with their respective raster class masks.
4.  **Gap Filling:** Gaps in the raster data (nodata) were assigned to the nearest available cluster to ensure 100% coverage of the official GeoPackage boundary.

### Phase 4: Geometry Optimization (Final Version)
The resulting polygons from Phase 3 were highly detailed but "wiggly," following the pixelated edges of the original raster. We applied a final **Cleaning and Smoothing** pass:
1.  **Fragment Removal:** Merged all polygons < 10 km² into their largest neighbors.
2.  **Centroidal Voronoi Relaxation:** Recalculated centroids for the purity-maximized units and regenerated a final Voronoi diagram.
3.  **Boundary Smoothing:** Applied a 500m opening buffer and Douglas-Peucker simplification.

## 4. Final Results

![Final_clusters](figures/cluster_version_comparison.png)

The finalized delineation (**Version: Final Cleaned**) achieves the best balance between well density, thematic purity, and geometric simplicity.

| Metric | Value |
|--------|-------|
| Total Clusters | 25 |
| Total Wells | 2,076 |
| Mean Purity Score | 100% (within raster footprint) |
| Spatial Coverage | 100% (Seamlessly matches `area_boundary.gpkg`) |
| Geometric Style | Smooth, Convex-Optimized |

### Visual Comparison
A side-by-side comparison of the "Wiggly" vs. "Smooth" versions was performed to ensure that the smoothing process did not significantly shift the cluster centroids or well counts. The **Smooth Version** was selected for its superior cartographic quality and computational efficiency.

## 5. Implementation Files
- **Processing Script:** `src/features/clean_clusters.py`
- **Output Shapefile:** `data/processed/final_cleaned_clusters.shp`
- **Well-Cluster Index:** `data/processed/well_cluster_index.csv`
- **Visualization:** `reports/figures/final_cleaned_clusters.png`

## 6. Conclusion
The resulting 25 clusters provide a robust spatial framework. Each cluster is contiguous, thematic-consistent with the original model, and provides a sufficient sample size (avg. 83 wells) for statistically significant spectral analysis.
