import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import os

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
    df_index = pd.read_csv('data/processed/well_cluster_index.csv', dtype={'well_id': str})
    df_index['well_id'] = df_index['well_id'].str.replace('\.0$', '', regex=True)
    
    # 2. Load Brandenburg Coords
    df_bb_coords = pd.read_csv('data/processed/topmost_aquifer_wells.csv', dtype={'ID': str})[['ID', 'x', 'y']]
    df_bb_coords.columns = ['well_id', 'x', 'y']
    df_bb_coords['well_id'] = df_bb_coords['well_id'].str.replace('\.0$', '', regex=True)
    
    # 3. Load Berlin Coords
    df_be_coords = pd.read_csv('data/raw/Berlin_wells/berlin_gw_metadata.csv', dtype={'invhyas': str})[['invhyas', 'xcoord', 'ycoord']]
    df_be_coords.columns = ['well_id', 'x', 'y']
    df_be_coords['well_id'] = df_be_coords['well_id'].str.replace('\.0$', '', regex=True)
    
    # Merge coords
    df_coords = pd.concat([df_bb_coords, df_be_coords])
    df_combined = pd.merge(df_index, df_coords, on='well_id', how='left')
    
    # 4. Load Quality Flags
    df_quality = pd.read_csv('data/processed/timeseries_quality_summary_2000_2025.csv', dtype={'ID': str})[['ID', 'Flagged', 'Pct_Missing']]
    df_quality.columns = ['well_id', 'flagged', 'pct_missing']
    df_quality['well_id'] = df_quality['well_id'].str.replace('\.0$', '', regex=True)
    df_combined = pd.merge(df_combined, df_quality, on='well_id', how='left')
    
    # 5. Load Trends
    df_trends = pd.read_csv('data/processed/groundwater_trends_2000_2025.csv', dtype={'well_id': str})
    df_trends['well_id'] = df_trends['well_id'].str.replace('\.0$', '', regex=True)
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
    return pd.read_csv('data/processed/cluster_trend_summary.csv')

@st.cache_data
def load_timeseries(well_id, source):
    prefix = "BB" if source == "Brandenburg" else "BE"
    # Note: IDs might be floats in the CSV index, convert to int/str carefully
    str_id = str(int(float(well_id)))
    file_path = f"data/interim/timeseries_weekly/{prefix}_{str_id}_weekly.csv"
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['date'])
        return df
    return None

# --- Sidebar Filters ---

df_all = load_well_data()
df_clusters = load_cluster_trends()

st.sidebar.header("Map Settings")

# Color Mode
color_mode = st.sidebar.radio("Color Map By:", ["Cluster", "Trend (cm/year)"])

st.sidebar.divider()
st.sidebar.header("Filters")

# Filter by Region
region_options = df_all['source'].unique().tolist()
selected_regions = st.sidebar.multiselect("Select Regions", region_options, default=region_options)

# Filter by Cluster
cluster_options = sorted(df_all['cluster_id'].unique().tolist())
selected_clusters = st.sidebar.multiselect("Select Clusters", cluster_options, default=cluster_options)

# Filter by Quality
only_high_quality = st.sidebar.toggle("Show only High Quality wells", value=False)

# Apply Filters
df_filtered = df_all[
    (df_all['source'].isin(selected_regions)) & 
    (df_all['cluster_id'].isin(selected_clusters))
]
if only_high_quality:
    df_filtered = df_filtered[df_filtered['flagged'] == False]

st.sidebar.info(f"Showing **{len(df_filtered)}** wells out of {len(df_all)}.")

# --- Main Tabs ---

tab1, tab2 = st.tabs(["📍 Well Exploration", "📊 Cluster Analysis"])

with tab1:
    # --- Map Selection ---
    
    # Determine color column and scale
    if color_mode == "Cluster":
        df_filtered['color_val'] = df_filtered['cluster_id'].astype(str)
        color_scale = px.colors.qualitative.Alphabet
        color_label = "Cluster ID"
    else:
        df_filtered['color_val'] = df_filtered['slope_m_per_year'] * 100 # cm/year
        color_scale = "RdBu"
        color_label = "Trend (cm/year)"

    fig_map = px.scatter_mapbox(
        df_filtered,
        lat="lat",
        lon="lon",
        color="color_val",
        hover_name="well_id",
        custom_data=["well_id"],
        hover_data={"lat": False, "lon": False, "source": True, "cluster_id": True, "slope_m_per_year": ":.4f"},
        color_discrete_sequence=color_scale if color_mode == "Cluster" else None,
        color_continuous_scale=color_scale if color_mode == "Trend (cm/year)" else None,
        range_color=[-5, 5] if color_mode == "Trend (cm/year)" else None,
        zoom=7,
        height=600,
        mapbox_style="carto-positron"
    )

    fig_map.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0}, 
        showlegend=(color_mode == "Cluster"),
        coloraxis_colorbar=dict(title=color_label) if color_mode == "Trend (cm/year)" else None
    )

    # Display the map and capture selection
    selected_points = st.plotly_chart(fig_map, use_container_width=True, on_select="rerun")

    # --- Timeseries View ---
    st.divider()

    if selected_points and "selection" in selected_points and len(selected_points["selection"]["points"]) > 0:
        well_id = selected_points["selection"]["points"][0]["customdata"][0]
        selected_well = df_filtered[df_filtered['well_id'] == well_id].iloc[0]
        source = selected_well['source']
        
        st.subheader(f"📈 Timeseries for Well: {well_id} ({source})")
        
        cols = st.columns([1, 1, 4])
        with cols[0]:
            st.metric("Cluster", int(selected_well['cluster_id']))
            st.metric("Quality Status", "High" if not selected_well['flagged'] else "Flagged")
            st.metric("Missing Data", f"{selected_well['pct_missing']:.1f}%")
        
        with cols[1]:
            if not pd.isna(selected_well['slope_m_per_year']):
                slope_cm = selected_well['slope_m_per_year'] * 100
                st.metric("Trend Magnitude", f"{slope_cm:.2f} cm/yr", delta=f"{slope_cm:.2f}", delta_color="inverse")
                sig = "Significant" if selected_well['p_value'] < 0.05 else "Not Significant"
                st.metric("Significance", sig)
                st.metric("Total Est. Change", f"{selected_well['total_change_est']:.2f} m")
            else:
                st.info("Trend analysis not available for this well.")
            
        with cols[2]:
            df_ts = load_timeseries(well_id, source)
            if df_ts is not None:
                fig_ts = px.line(
                    df_ts, 
                    x="date", 
                    y="gw_level", 
                    title=f"Weekly Mean Groundwater Level (2000-2025)",
                    labels={"gw_level": "Groundwater Level (m)"}
                )
                fig_ts.update_traces(line_color='#1f77b4')
                fig_ts.update_layout(hovermode="x unified")
                st.plotly_chart(fig_ts, use_container_width=True)
            else:
                st.error(f"Timeseries file not found for well {well_id}.")
    else:
        st.info("👆 Click on a well on the map to explore its data trends.")

with tab2:
    st.subheader("📊 Spatial Cluster Trend Summary")
    st.markdown("This table summarizes the groundwater level trends aggregated by spatial clusters.")
    
    # Format the table for display
    df_clusters_disp = df_clusters.copy()
    df_clusters_disp['mean_slope'] = df_clusters_disp['mean_slope'] * 100
    df_clusters_disp['median_slope'] = df_clusters_disp['median_slope'] * 100
    df_clusters_disp['pct_significant'] = df_clusters_disp['pct_significant'] * 100
    
    df_clusters_disp.columns = [
        "Cluster ID", "Wells", "Mean Slope (cm/yr)", 
        "Median Slope (cm/yr)", "Std Slope (cm/yr)", 
        "% Significant", "Mean Total Change (m)"
    ]
    
    st.dataframe(
        df_clusters_disp.sort_values("Mean Slope (cm/yr)"),
        use_container_width=True,
        hide_index=True
    )
    
    st.info("Hotspots of groundwater decline (lowest Mean Slope) are prioritized in the sorted table.")

# --- Footer ---
st.caption("Data Source: Brandenburg LfU & Berlin Wasserportal. Period: 2000-2025.")
