# Cluster Cleaning and Smoothing

## Operations Performed
1. **Fragment Removal:** Any polygon smaller than 10 km² was merged into its largest adjacent neighbor.
2. **Boundary Smoothing:** Applied a 500m opening buffer and 200m Douglas-Peucker simplification to remove raster-induced 'staircase' effects.
3. **Topological Fix:** Used zero-buffer cleanup to ensure valid geometries.

## Results
- **Initial Shapes:** 25
- **Final Cleaned Clusters:** 25
## Visualization
![Cleaned Clusters](figures/final_cleaned_clusters.png)
