import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import os

# --- Path Handling ---
# Since this script is in src/visualization/, we go up two levels to reach the project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

def get_path(rel_path):
    """Helper to join the project root with a relative data path."""
    return os.path.join(BASE_DIR, rel_path)

# Set page config
st.set_page_config(page_title="Brandenburg & Berlin Groundwater Explorer", layout="wide")

st.title("💧 Groundwater Data Exploration Tool")
st.markdown("""
Explore groundwater levels across Brandenburg and Berlin. 
**Select a well on the map** to view its weekly timeseries (2000-2025).
""")

# --- Data Loading ---

@st.cache_data
def load_well_data():
    # 1. Load Index
    df_index = pd.read_csv(get_path('data/processed/well_cluster_index.csv'), dtype={'well_id': str})
    df_index['well_id'] = df_index['well_id'].str.replace(r'\.0$', '', regex=True)
    
    # 2. Load Brandenburg Coords
    df_bb_coords = pd.read_csv(get_path('data/processed/topmost_aquifer_wells.csv'), dtype={'ID': str})[['ID', 'x', 'y']]
    df_bb_coords.columns = ['well_id', 'x', 'y']
    df_bb_coords['well_id'] = df_bb_coords['well_id'].str.replace(r'\.0$', '', regex=True)
    
    # 3. Load Berlin Coords
    df_be_coords = pd.read_csv(get_path('data/raw/Berlin_wells/berlin_gw_metadata.csv'), dtype={'invhyas': str})[['invhyas', 'xcoord', 'ycoord']]
    df_be_coords.columns = ['well_id', 'x', 'y']
    df_be_coords['well_id'] = df_be_coords['well_id'].str.replace(r'\.0$', '', regex=True)
    
    # Merge coords
    df_coords = pd.concat([df_bb_coords, df_be_coords])
    df_combined = pd.merge(df_index, df_coords, on='well_id', how='left')
    
    # 4. Load Quality Flags
    df_quality = pd.read_csv(get_path('data/processed/timeseries_quality_summary_2000_2025.csv'), dtype={'ID': str})[['ID', 'Flagged', 'Pct_Missing']]
    df_quality.columns = ['well_id', 'flagged', 'pct_missing']
    df_quality['well_id'] = df_quality['well_id'].str.replace(r'\.0$', '', regex=True)
    df_combined = pd.merge(df_combined, df_quality, on='well_id', how='left')
    
    # 5. Load Trends
    df_trends = pd.read_csv(get_path('data/processed/groundwater_trends_2000_2025.csv'), dtype={'well_id': str})
    df_trends['well_id'] = df_trends['well_id'].str.replace(r'\.0$', '', regex=True)
    df_combined = pd.merge(df_combined, df_trends, on='well_id', how='left')
    
    # 6. Convert CRS (EPSG:25833 to WGS84)
    gdf = gpd.GeoDataFrame(
        df_combined, 
        geometry=gpd.points_from_xy(df_combined.x, df_combined.y), 
        crs="EPSG:25833"
    ).to_crs("EPSG:4326")
    
    df_combined['lat'] = gdf.geometry.y
    df_combined['lon'] = gdf.geometry.x
    
    return df_combined

@st.cache_data
def load_cluster_trends():
    return pd.read_csv(get_path('data/processed/cluster_trend_summary.csv'))

@st.cache_data
def load_timeseries(well_id, source):
    prefix = "BB" if source == "Brandenburg" else "BE"
    # Ensure ID is formatted correctly for filename matching
    str_id = str(int(float(well_id)))
    file_path = get_path(f"data/interim/timeseries_weekly/{prefix}_{str_id}_weekly.csv")
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['date'])
        return df