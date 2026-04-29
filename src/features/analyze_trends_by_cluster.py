import pandas as pd
import numpy as np

def analyze_trends_by_cluster():
    """
    Summarizes groundwater trends for each spatial cluster.
    """
    trends_path = 'data/processed/groundwater_trends_2000_2025.csv'
    cluster_index_path = 'data/processed/well_cluster_index.csv'
    output_path = 'data/processed/cluster_trend_summary.csv'

    # Load data
    df_trends = pd.read_csv(trends_path)
    df_trends['well_id'] = df_trends['well_id'].astype(str)
    
    df_clusters = pd.read_csv(cluster_index_path)
    df_clusters['well_id'] = df_clusters['well_id'].astype(str)
    # Handle the .0 in well_id if present (common for Berlin IDs in cluster index)
    df_clusters['well_id'] = df_clusters['well_id'].apply(lambda x: x[:-2] if x.endswith('.0') else x)

    # Merge
    df_merged = pd.merge(df_trends, df_clusters, on='well_id', how='left')
    
    # Group by cluster
    cluster_summary = df_merged.groupby('cluster_id').agg({
        'well_id': 'count',
        'slope_m_per_year': ['mean', 'median', 'std'],
        'p_value': lambda x: (x < 0.05).mean(), # % significant
        'total_change_est': 'mean'
    }).reset_index()

    # Flatten columns
    cluster_summary.columns = [
        'cluster_id', 'well_count', 
        'mean_slope', 'median_slope', 'std_slope', 
        'pct_significant', 'mean_total_change'
    ]

    cluster_summary.to_csv(output_path, index=False)
    print(f"Cluster trend summary saved to {output_path}")
    print(cluster_summary.head())

if __name__ == "__main__":
    analyze_trends_by_cluster()
