 Gemini
Streamlit Deployment Dependency Errors
Conversation with Gemini

I am trying to deploy a streamlit app from github, but getting this error: : Unable to locate package 1

E: Unable to locate package 2

E: Unable to locate package 3

[15:25:15] ❗️ installer returned a non-zero exit code

[15:25:15] ❗️ Error during processing dependencies! Please fix the error and push an update, or try restarting the app.

It looks like Streamlit is trying to treat the contents of your requirements file as actual package names. When you see errors like Unable to locate package 1, it usually means the installer is misreading a list or a configuration file.

This specific error typically happens because of one of three common hiccups in your repository setup.
1. The packages.txt vs. requirements.txt Confusion

Streamlit Sharing uses two different files for dependencies:

    requirements.txt: For Python libraries (e.g., pandas, streamlit, plotly).

    packages.txt: For Linux/system level dependencies (e.g., libgomp1, ffmpeg).

The Fix:
If you accidentally listed your Python libraries inside a file named packages.txt, the installer thinks they are Linux system packages. Since pandas or matplotlib aren't in the Debian system repository, it fails.

    Rename your file to requirements.txt if it contains Python libraries.

2. Invalid Formatting in packages.txt

If you actually need system packages and have a packages.txt file, ensure it doesn't have:

    Version numbers (e.g., use libgl1, not libgl1=1.2).

    Comments on the same line as a package.

    Hidden characters or weird encoding (ensure it is UTF-8).

3. "Numbered" List Error

The error Unable to locate package 1 strongly suggests that your dependency file looks like this:

    pandas

    streamlit

    numpy

The Fix:
Remove any numbering or bullet points. Your requirements.txt (or packages.txt) should be a plain text list with one package per line:
Plaintext

pandas
streamlit
scikit-learn

How to resolve it right now:

    Check your file names: Ensure your Python dependencies are in requirements.txt.

    Check the content: Open the file in GitHub and make sure there are no numbers (1, 2, 3) at the start of the lines.

    Commit and Push: Once you fix the filename or the text inside, commit the changes. Streamlit will automatically try to reboot the app.

    Pro Tip: If the app still hangs after the fix, click on "Manage app" in the bottom right of your Streamlit Cloud dashboard and select "Reboot app" to clear the cache.

this is my requirements:   1 streamlit

   2 pandas

   3 geopandas

   4 plotly

   5 xarray

   6 cfgrib

   7 numpy<2.0.0

There is the culprit! The error is occurring because you have line numbers inside your file.

When the Streamlit installer reads your file, it doesn't see "streamlit"; it sees "1 streamlit" and thinks "1" is the name of the package you want to install. Since there is no package named "1" in the repository, it fails with Unable to locate package 1.
The Fix

You need to remove the numbers and the extra indentation. Your requirements.txt file should look exactly like this:
Plaintext

streamlit
pandas
geopandas
plotly
xarray
cfgrib
numpy<2.0.0

Why geopandas and cfgrib might need more help

Once you fix the numbers, you might run into a second error. Both geopandas and cfgrib often require system-level libraries (like libgdal or eccodes) that can't be installed via Python's requirements.txt.

If the app fails again after you remove the numbers, you will need to create a second file in your main folder called packages.txt and add these system dependencies:

File: packages.txt
Plaintext

libgdal-dev
g++
libeccodes-dev

To-do list:

    Edit requirements.txt to remove the numbers.

    Commit and push to GitHub.

    If it still fails, add the packages.txt file mentioned above.

Does your app specifically use GRIB files (weather data), or are you just using standard CSV/Excel files?

FileNotFoundError:

This app has encountered an error. The original error message is

redacted to prevent data leaks. Full error details have been recorded in

the logs (if you're on Streamlit Cloud, click on 'Manage app' in the

lower right of your app).

Traceback:


File "/mount/src/bb_well_browser/src/visualization/exploration_dashboard.py", line 80, in <module>

df_all = load_well_data()

File "/home/adminuser/venv/lib/python3.14/site-packages/streamlit/runtime/caching/cache_utils.py", line 280, in __call__

return self._get_or_create_cached_value(args, kwargs, spinner_message)

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

File "/home/adminuser/venv/lib/python3.14/site-packages/streamlit/runtime/caching/cache_utils.py", line 325, in _get_or_create_cached_value

return self._handle_cache_miss(cache, value_key, func_args, func_kwargs)

~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

File "/home/adminuser/venv/lib/python3.14/site-packages/streamlit/runtime/caching/cache_utils.py", line 384, in _handle_cache_miss

computed_value = self._info.func(*func_args, **func_kwargs)

File "/mount/src/bb_well_browser/src/visualization/exploration_dashboard.py", line 21, in load_well_data

df_index = pd.read_csv('data/processed/well_cluster_index.csv', dtype={'well_id': str})

File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/io/parsers/readers.py", line 1026, in read_csv

return _read(filepath_or_buffer, kwds)

File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/io/parsers/readers.py", line 620, in _read

parser = TextFileReader(filepath_or_buffer, **kwds)

File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/io/parsers/readers.py", line 1620, in __init__

self._engine = self._make_engine(f, self.engine)

~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^

File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/io/parsers/readers.py", line 1880, in _make_engine

self.handles = get_handle(

~~~~~~~~~~^

f,

^^

...<6 lines>...

storage_options=self.options.get("storage_options", None),

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

)

^

File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/io/common.py", line 873, in get_handle

handle = open(

handle,

...<3 lines>...

newline="",

)

Progress! You've cleared the dependency hurdle, and now you're facing a classic pathing issue.

The error FileNotFoundError at line 21 tells us that your Python script is looking for data/processed/well_cluster_index.csv, but it can't find it relative to where the app is running.

On Streamlit Cloud, the "current working directory" is usually the root of your GitHub repository.
Why this is happening

Looking at your traceback, your script is located here:
/mount/src/bb_well_browser/src/visualization/exploration_dashboard.py

When you call pd.read_csv('data/processed/...'), Python looks for a folder named data inside the visualization folder (where the script is), rather than at the root of your project.
The Fix: Use Absolute Pathing

The most robust way to fix this in Streamlit is to define the path relative to the file itself. Update your load_well_data function in exploration_dashboard.py like this:
Python

import pandas as pd
import os

def load_well_data():
    # Get the directory that this script is in
    base_path = os.path.dirname(__file__)
    
    # Construct the path to the data folder
    # We use "../../" to go up two levels from 'visualization' to 'src', then 'bb_well_browser'
    # Adjust the number of "../" depending on your exact folder structure
    file_path = os.path.join(base_path, "../../data/processed/well_cluster_index.csv")
    
    df_index = pd.read_csv(file_path, dtype={'well_id': str})
    return df_index

Alternatively: The Quick "Root" Fix

If your data folder is at the very top level of your GitHub repo, you can sometimes just point to the absolute root of the Streamlit mount:
Python

df_index = pd.read_csv('/mount/src/bb_well_browser/data/processed/well_cluster_index.csv', dtype={'well_id': str})

Double-Check Your Repo

Make sure that:

    The file well_cluster_index.csv is actually pushed to GitHub. (Check if it's accidentally in your .gitignore).

    The folder names are exactly the same case (Linux is case-sensitive, so Data is not the same as data).

Quick question: Is your data folder at the same level as the src folder, or is it inside src? (Knowing this will help me give you the exact string for the path!)

the streamlit file runs from the /src/visualization subfolder, this is the file: import streamlit as st

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

Because your script is located in src/visualization/ but your data is in a separate data/ folder at the project root, the relative paths like pd.read_csv('data/processed/...') are failing. When Streamlit runs, it's looking for a data folder inside the visualization folder.

Here is the updated code with a robust path-handling helper. I’ve replaced your manual string paths with a dynamic get_path function that ensures the script always finds the root directory, regardless of where it's being executed.
Updated Script
Python

import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import os

# --- Path Helper ---
# This finds the absolute path to the project root (bb_well_browser)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

def get_path(relative_path):
    """Joins the relative path with the project root directory."""
    return os.path.join(BASE_DIR, relative_path)

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
    df_index['well_id'] = df_index['well_id'].str.replace('\.0$', '', regex=True)
    
    # 2. Load Brandenburg Coords
    df_bb_coords = pd.read_csv(get_path('data/processed/topmost_aquifer_wells.csv'), dtype={'ID': str})[['ID', 'x', 'y']]
    df_bb_coords.columns = ['well_id', 'x', 'y']
    df_bb_coords['well_id'] = df_bb_coords['well_id'].str.replace('\.0$', '', regex=True)
    
    # 3. Load Berlin Coords
    df_be_coords = pd.read_csv(get_path('data/raw/Berlin_wells/berlin_gw_metadata.csv'), dtype={'invhyas': str})[['invhyas', 'xcoord', 'ycoord']]
    df_be_coords.columns = ['well_id', 'x', 'y']
    df_be_coords['well_id'] = df_be_coords['well_id'].str.replace('\.0$', '', regex=True)
    
    # Merge coords
    df_coords = pd.concat([df_bb_coords, df_be_coords])
    df_combined = pd.merge(df_index, df_coords, on='well_id', how='left')
    
    # 4. Load Quality Flags
    df_quality = pd.read_csv(get_path('data/processed/timeseries_quality_summary_2000_2025.csv'), dtype={'ID': str})[['ID', 'Flagged', 'Pct_Missing']]
    df_quality.columns = ['well_id', 'flagged', 'pct_missing']
    df_quality['well_id'] = df_quality['well_id'].str.replace('\.0$', '', regex=True)
    df_combined = pd.merge(df_combined, df_quality, on='well_id', how='left')
    
    # 5. Load Trends
    df_trends = pd.read_csv(get_path('data/processed/groundwater_trends_2000_2025.csv'), dtype={'well_id': str})
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
    return pd.read_csv(get_path('data/processed/cluster_trend_summary.csv'))

@st.cache_data
def load_timeseries(well_id, source):
    prefix = "BB" if source == "Brandenburg" else "BE"
    str_id = str(int(float(well_id)))
    file_path = get_path(f"data/interim/timeseries_weekly/{prefix}_{str_id}_weekly.csv")
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['date'])
        return df
    return None

# ... (The rest of your UI code remains exactly the same)

Why this works:

    os.path.dirname(__file__): Gets the path to the folder containing your script (.../src/visualization).

    ../../: Moves up two levels to the root of your project.

    get_path(): Combines that root path with the actual data subfolders. This ensures that whether you run the app locally or on Streamlit Cloud, it always finds the absolute location of your files.

One final check: Ensure that your data folder and all its contents were actually committed and pushed to GitHub. Large CSV files are sometimes caught by .gitignore or require Git LFS if they are over 25MB–100MB.


Gemini is AI and can make mistakes, including about people. Your privacy and GeminiOpens in a new window
