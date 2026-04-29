import geopandas as gpd
import pandas as pd
import os

def create_well_cluster_index():
    # Paths
    wells_bb_path = 'data/processed/topmost_aquifer_wells.csv'
    wells_be_path = 'data/processed/berlin_topmost_identification.csv'
    be_meta_path = 'data/raw/Berlin_wells/berlin_gw_metadata.csv'
    clusters_path = 'data/processed/final_cleaned_clusters.shp'
    
    output_csv = 'data/processed/well_cluster_index.csv'
    output_report = 'reports/well_cluster_distribution.md'

    print("Loading data...")
    # 1. Load and merge wells
    df_bb = pd.read_csv(wells_bb_path)
    gdf_bb = gpd.GeoDataFrame(df_bb[df_bb['is_topmost'] == True], 
                              geometry=gpd.points_from_xy(df_bb[df_bb['is_topmost'] == True].x, 
                                                         df_bb[df_bb['is_topmost'] == True].y), 
                              crs="EPSG:25833")[['geometry']]
    gdf_bb['well_id'] = df_bb[df_bb['is_topmost'] == True]['ID']
    gdf_bb['source'] = 'Brandenburg'

    df_be = pd.read_csv(wells_be_path)
    df_be_meta = pd.read_csv(be_meta_path)
    df_be = pd.merge(df_be[df_be['is_topmost'] == True], df_be_meta, left_on='ID', right_on='invhyas')
    gdf_be = gpd.GeoDataFrame(df_be, 
                              geometry=gpd.points_from_xy(df_be.xcoord, df_be.ycoord), 
                              crs="EPSG:25833")[['geometry', 'ID']]
    gdf_be.columns = ['geometry', 'well_id']
    gdf_be['source'] = 'Berlin'

    wells = pd.concat([gdf_bb, gdf_be]).reset_index(drop=True)

    # 2. Load Clusters
    clusters = gpd.read_file(clusters_path)

    # 3. Spatial Join
    print("Performing spatial join...")
    joined = gpd.sjoin(wells, clusters, how="left", predicate="within")
    
    # Handle wells that might be slightly outside due to smoothing (assign to nearest)
    if joined['cluster_id'].isnull().any():
        print(f"Assigning {joined['cluster_id'].isnull().sum()} outlier wells to nearest cluster...")
        unassigned_indices = joined[joined['cluster_id'].isnull()].index
        for idx in unassigned_indices:
            well_geom = joined.loc[idx, 'geometry']
            distances = clusters.distance(well_geom)
            nearest_cluster_idx = distances.idxmin()
            joined.loc[idx, 'cluster_id'] = clusters.loc[nearest_cluster_idx, 'cluster_id']
            joined.loc[idx, 'orig_clust'] = clusters.loc[nearest_cluster_idx, 'orig_clust']

    # 4. Save Index Table
    result = joined[['well_id', 'source', 'cluster_id', 'orig_clust']].sort_values(['cluster_id', 'well_id'])
    result.to_csv(output_csv, index=False)
    print(f"Index table saved to {output_csv}")

    # 5. Generate Summary Report
    summary = result.groupby('cluster_id').agg(
        total_wells=('well_id', 'count'),
        bb_wells=('source', lambda x: (x == 'Brandenburg').sum()),
        be_wells=('source', lambda x: (x == 'Berlin').sum())
    ).reset_index()

    with open(output_report, 'w', encoding='utf-8') as f:
        f.write("# Well-Cluster Distribution Index\n\n")
        f.write("## Summary Statistics\n")
        f.write(f"- **Total Wells:** {len(result)}\n")
        f.write(f"- **Total Clusters:** {len(summary)}\n")
        f.write(f"- **Avg Wells per Cluster:** {summary['total_wells'].mean():.1f}\n\n")
        
        f.write("## Cluster Membership Table\n")
        f.write("| Cluster ID | Total Wells | Brandenburg | Berlin |\n")
        f.write("|------------|-------------|-------------|--------|\n")
        for _, row in summary.iterrows():
            f.write(f"| {int(row['cluster_id'])} | {int(row['total_wells'])} | {int(row['bb_wells'])} | {int(row['be_wells'])} |\n")
        
        f.write("\n\n*Full mapping is available in `data/processed/well_cluster_index.csv`*")

    print(f"Report generated at {output_report}")

if __name__ == "__main__":
    create_well_cluster_index()
