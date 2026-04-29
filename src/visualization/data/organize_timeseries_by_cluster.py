import pandas as pd
import shutil
import os
import glob

def organize_timeseries():
    # Paths
    index_path = 'data/processed/well_cluster_index.csv'
    source_dir = 'data/interim/timeseries_weekly'
    base_target_dir = 'data/interim/timeseries_by_cluster'
    
    print("Loading well-cluster index...")
    df_index = pd.read_csv(index_path)
    
    # Ensure target base directory exists
    if os.path.exists(base_target_dir):
        shutil.rmtree(base_target_dir)
    os.makedirs(base_target_dir, exist_ok=True)
    
    # Create cluster subfolders
    clusters = sorted(df_index['cluster_id'].unique())
    for cluster_id in clusters:
        os.makedirs(os.path.join(base_target_dir, f"cluster_{int(cluster_id)}"), exist_ok=True)
    
    print(f"Organizing {len(df_index)} wells into {len(clusters)} cluster folders...")
    
    copy_count = 0
    missing_count = 0
    
    for _, row in df_index.iterrows():
        # Ensure well_id is a clean string (no .0 if it was float)
        try:
            well_id_clean = str(int(float(row['well_id'])))
        except:
            well_id_clean = str(row['well_id'])
            
        source = row['source']
        cluster_id = int(row['cluster_id'])
        
        prefix = "BB" if source == "Brandenburg" else "BE"
        filename = f"{prefix}_{well_id_clean}_weekly.csv"
        source_path = os.path.join(source_dir, filename)
        
        target_path = os.path.join(base_target_dir, f"cluster_{cluster_id}", filename)
        
        if os.path.exists(source_path):
            shutil.copy2(source_path, target_path)
            copy_count += 1
        else:
            # Try searching for the file if the naming convention varies
            search_pattern = os.path.join(source_dir, f"*{well_id_clean}*_weekly.csv")
            found_files = glob.glob(search_pattern)
            if found_files:
                shutil.copy2(found_files[0], target_path)
                copy_count += 1
            else:
                missing_count += 1
    
    print(f"Done. Successfully copied {copy_count} files.")
    if missing_count > 0:
        print(f"Warning: {missing_count} wells from the index were not found in the source directory.")

if __name__ == "__main__":
    organize_timeseries()
