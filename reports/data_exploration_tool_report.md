# Report: Groundwater Data Exploration Tool

## Overview
The **Brandenburg & Berlin Groundwater Explorer** is an interactive web-based dashboard designed to facilitate the rapid exploration of spatiotemporal groundwater trends. It bridges the gap between raw data processing and formal modeling by providing a "live" window into the study area's hydrological network.

## Technical Architecture
- **Backend:** Python 3.x (Anaconda `raven` environment).
- **Framework:** Streamlit for UI and state management.
- **Visualization Engine:** Plotly Express for Mapbox basemaps and interactive line charts.
- **Data Integration:** 
    - Merges spatial cluster indices with regional coordinate metadata.
    - **Trend Integration:** Joins 25-year Theil-Sen slope results directly into the spatial index for real-time visualization.
    - Robust ID handling to resolve format mismatches between Berlin and Brandenburg datasets.
    - Leverages Streamlit caching (`@st.cache_data`) for high-performance data loading and filtering.

## Core Features
1. **Interactive Spatial Mapping:** 
    - Displays 2,076 wells across the study region.
    - **Dual Color Modes:** Toggle between "Cluster View" (spatial organization) and "Trend View" (quantified decline in cm/year).
    - Hover tooltips provide metadata (Well ID, Source, Cluster, Trend Magnitude).
2. **Dynamic Timeseries & Metrics:**
    - Selection of a map point triggers an immediate load of the weekly mean groundwater levels (2000-2025).
    - **Trend Metrics:** Displays quantified slope (cm/yr), statistical significance (p-value), and estimated total 25-year change (m) for the selected well.
3. **Cluster Analysis Dashboard:**
    - Dedicated tab summarizing groundwater trends aggregated by spatial clusters.
    - Sortable table identifying depletion hotspots (e.g., Clusters 18, 16, 19).
4. **Advanced Research Filtering:**
    - Filter by region (Berlin vs. Brandenburg).
    - Filter by specific hydrological clusters.
    - High-quality subset toggle (shows only the 1,289 wells passing strict gap criteria).

## Performance Optimization
The tool handles > 2,000 points on a vector basemap with zero lag by utilizing optimized Plotly WebGL rendering and efficient CRS transformations (EPSG:25833 to WGS84) performed once at startup.

## Status & Access
The tool is fully operational and integrated into the project's source control at `src/visualization/exploration_dashboard.py`.
