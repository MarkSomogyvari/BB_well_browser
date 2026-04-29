import pandas as pd
import numpy as np

def combine_trends_with_coords():
    """
    Combines trend analysis results with spatial coordinates for mapping.
    """
    trends_path = 'data/processed/groundwater_trends_2000_2025.csv'
    bb_coords_path = 'data/processed/topmost_aquifer_wells.csv'
    be_coords_path = 'data/raw/Berlin_wells/berlin_gw_metadata.csv'
    output_path = 'data/processed/groundwater_trends_with_coords.csv'

    # Load trends
    df_trends = pd.read_csv(trends_path)
    df_trends['well_id'] = df_trends['well_id'].astype(str)

    # Load Brandenburg coordinates
    df_bb = pd.read_csv(bb_coords_path)
    df_bb = df_bb[['ID', 'east_25833', 'north_25833']].rename(columns={
        'ID': 'well_id',
        'east_25833': 'x',
        'north_25833': 'y'
    })
    df_bb['well_id'] = df_bb['well_id'].astype(str)
    # Remove duplicates in BB coords (might have multiple rows per ID if joined with something)
    df_bb = df_bb.drop_duplicates(subset=['well_id'])

    # Load Berlin coordinates
    df_be = pd.read_csv(be_coords_path)
    df_be = df_be[['invhyas', 'xcoord', 'ycoord']].rename(columns={
        'invhyas': 'well_id',
        'xcoord': 'x',
        'ycoord': 'y'
    })
    df_be['well_id'] = df_be['well_id'].astype(str)
    # IDs in Berlin metadata might have multiple entries (e.g., for different filters)
    df_be = df_be.drop_duplicates(subset=['well_id'])

    # Combine coords
    df_coords = pd.concat([df_bb, df_be], ignore_index=True)

    # Merge with trends
    df_merged = pd.merge(df_trends, df_coords, on='well_id', how='left')

    # Check for missing coordinates
    missing_coords = df_merged['x'].isna().sum()
    if missing_coords > 0:
        print(f"Warning: {missing_coords} wells are missing coordinates.")
        # Try a fuzzy match or check for .0 issues if needed
        # (Though we already handled .0 in analyze_trends.py)

    df_merged.to_csv(output_path, index=False)
    print(f"Combined data saved to {output_path}")

if __name__ == "__main__":
    combine_trends_with_coords()
