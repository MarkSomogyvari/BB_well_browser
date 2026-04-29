# Project Log: Brandenburg Groundwater Data Analysis

## 2026-04-22

### Initial Project Setup
- Created subfolder structure for data analysis: `data/`, `notebooks/`, `src/`, `models/`, `reports/`, `docs/`.
- Created `README.md` with project structure description.
- Created `.gitignore` to exclude large data files and environment artifacts.
- Created `GEMINI.md` to establish project-specific mandates (e.g., raw data immutability, coordinate systems).

### Task 1: Identify Wells Screening Topmost Aquifer (RERUN)
- **New Data:**
    - New metadata file provided: `data/raw/Brandenburg_wells/well_meta_data/BB_GW_wells_metadata_coords_1.csv`.
    - Dataset increased from 217 to 1922 wells.
- **Implementation Update:**
    - Updated `src/data/identify_topmost_aquifer.py` to handle comma as decimal separator in the new CSV.
- **Execution:**
    - Ran script using Anaconda `raven` environment.
    - Successfully processed 1922 wells.
    - **Results:** 1372 wells identified as screening the topmost aquifer (using 1.5m threshold).
    - Output saved to `data/processed/topmost_aquifer_wells.csv`.
- **Validation:**
    - Statistical check on `h_diff`: Mean = 1.83m, Median = 0.72m.
    - 60.5% within 1m, 71.4% within 1.5m, 77.8% within 2m.

### Task 3: Expand Dataset for Berlin
- **Strategy:** Followed recommendation to use WFS for metadata and direct Python script for CSV downloads (bypassing buggy R package).
- **Metadata Extraction:**
    - Created `src/data/get_berlin_metadata.py`.
    - Connected to Berlin GDI-BE WFS service (`https://gdi.berlin.de/services/wfs/gwm`).
    - Successfully extracted metadata for **5,532 stations**.
    - Identified `invhyas` as the ID used by the Wasserportal Berlin.
- **Timeseries Download:**
    - Created `src/data/download_berlin_data.py`.
    - Identified correct **POST** request parameters for `station.php` (fixing previous SQL errors in GET requests).
    - Implementing background download for all 922 public stations to `data/raw/Berlin_wells/timeseries`.
- **Topmost Aquifer Identification (Berlin):**
    - Created `src/data/identify_topmost_berlin.py`.
    - Logic: Parses CSV headers for the `Grundwasserleiter` field.
    - Rule: Aquifers containing "GWL 1" (e.g., "GWL 1.3 + 2") are classified as topmost.
    - **Final Results:** 1,024 stations analyzed, **704 identified as topmost**.
- **Combined Visualization:** Generated map at `reports/figures/combined_well_map.png` showing 2,076 total topmost wells across Brandenburg and Berlin.

### Task 4: Timeseries Processing & Quality Assessment
- **Window Shift (2000-2025):** Shifted the analysis window to 2000-2025 to maximize continuous data coverage.
- **Upscaling:**
    - Resampled all topmost wells (2,077) to **Weekly Mean** resolution.
    - Processed individual CSVs saved to `data/interim/timeseries_weekly/`.
- **Quality Metrics:**
    - Assessed missing data % and max consecutive gaps.
    - **Results:** **1,289 wells** passed high-quality criteria (931 previously in 1990-2025 window).
    - Data quality is significantly higher in Berlin (74% pass) compared to Brandenburg (56% pass) for this period.
- **Reporting:** Updated `reports/identification_summary.md` with new quality statistics and gap handling recommendations.

### Task 5: Cluster Reanalysis (Optimized & Seamless)
- **Refinement (2026-04-22):**
    - **Boundary Integration:** Updated logic to use `data/raw/area_boundary.gpkg` as the official study area limit.
    - **Purity Maximization:** Developed a "Raster-Guided" approach in `src/features/purity_optimized_clusters.py` where new clusters are strictly contained within original `clusters.tif` classes.
    - **Gap Handling:** Implemented seamless partitioning to fill "nodata" gaps in the raster, ensuring 100% spatial coverage.
- **Geometric Optimization:**
    - Created `src/features/clean_clusters.py` to remove fragments (< 10 km²) and smooth boundaries.
    - Applied **Centroidal Voronoi Relaxation** to achieve high convexity and clean cartographic edges.
    - **Final Output:** `data/processed/final_cleaned_clusters.shp`.
- **Validation:**
    - Performed purity analysis (Mean Purity = 67% for simple Voronoi, 100% for optimized version).
    - Generated `reports/figures/cluster_version_comparison.png` for side-by-side quality check.

### Task 6: Data Indexing & Organization
- **Well Indexing:**
    - Created `src/data/create_well_cluster_index.py` to map all 2,076 wells to the finalized clusters.
    - Generated `data/processed/well_cluster_index.csv`.
- **Distribution Summary:**
    - Avg. wells per cluster: 83.
    - Documented in `reports/well_cluster_distribution.md`.
- **Filesystem Organization:**
    - Created `src/data/organize_timeseries_by_cluster.py`.
    - Automatically sorted 2,075 weekly timeseries CSVs into 25 cluster-specific subfolders in `data/interim/timeseries_by_cluster/`.

### Task 9: ERA5-Land Data Acquisition
- **Objective:** Retrieve high-resolution (9km) spatiotemporal climate data to analyze external drivers of groundwater trends.
- **Implementation:**
    - Set up CDS API credentials (`.cdsapirc`).
    - Verified connectivity with a test download for 2024.
    - Created `src/data/download_era5_land_full.py` to retrieve yearly NetCDF files.
- **Target Variables:**
    - `2m_temperature`
    - `total_precipitation`
    - `total_evaporation`
    - `potential_evaporation`
- **Status:** Background download initiated for years 2000-2025.
- **Update (2026-04-29):** 
    - Resolved "too large selection size" error (403 Forbidden) by refactoring `src/data/download_era5_land_full.py` to use monthly chunks. 
    - Switched format to **GRIB** for significantly faster server-side retrieval (~16s vs minutes).
    - **Bug Fix:** Identified that the CDS API returns GRIB files inside a ZIP archive. Updated download script to automatically extract.
    - Created and ran `src/data/fix_zipped_gribs.py` to repair previously downloaded "zipped GRIB" files.
    - Installed `cfgrib` and `eccodes` in the `raven` environment.
    - Full background download (2000-2025) restarted in GRIB format (PID 18468).

### Task 10: Data Exploration Dashboard
- **Objective:** Create an interactive tool for spatial and temporal data exploration.
- **Implementation:**
    - Developed `src/visualization/exploration_dashboard.py` using **Streamlit** and **Plotly**.
    - **Update (2026-04-29):**
        - Integrated trend analysis results into the map.
        - Added "Trend (cm/year)" color mode for the map visualization.
        - Added dynamic metrics for selected wells (Trend magnitude, Significance, Total Est. Change).
        - Added a **Cluster Analysis** tab with an aggregated trend summary table.
    - **Status:** Operational at `http://localhost:8501`.

### Task 14: Climate Feature Engineering Pipeline
- **Objective:** Extract and process ERA5-Land variables at well locations for modeling.
- **Implementation:**
    - Created `src/data/extract_climate_at_wells.py`.
    - Uses `xarray` with `cfgrib` to extract `t2m`, `tp`, `e`, and `pev` at the nearest neighbor for 1,289 wells.
    - Automatically aggregates hourly data to **Daily Mean/Sum**.
    - Created `src/features/process_climate_features.py` to aggregate to **Weekly** resolution.
    - **Key Feature:** Calculated **Net Water Balance (P - PET)** and cumulative balances (3m, 6m, 12m) to capture delayed groundwater responses.
- **Status:** Pipeline verified with initial 2002 data. Full processing will resume as GRIB downloads complete.

### Task 11: ERA5-Land Format Optimization (GRIB Test)
- **Objective:** Evaluate if downloading ERA5-Land data in GRIB format is faster than NetCDF due to differences in server-side processing.
- **Implementation:**
    - Created `src/data/test_era5_land_grib.py`.
    - Configured request for a single day of 2024 with GRIB format.
- **Status:** Test complete.
    - **Results:** 
        - GRIB download: **16.5 seconds** (Status moved to successful almost immediately).
        - NetCDF download: Still in 'accepted' queue after several minutes.
    - **Conclusion:** GRIB format is significantly faster for retrieval on the CDS server side. Future large-scale downloads should consider GRIB if post-processing tools (e.g., `cfgrib`, `xarray`) are available in the environment.

### Task 12: Regional Groundwater Trend Analysis (2000-2025)
- **Objective:** Quantify the magnitude and significance of long-term groundwater level changes for the identified high-quality wells.
- **Implementation:**
    - Created `src/features/analyze_trends.py` to calculate Theil-Sen slopes and Kendall significance for 1,289 wells.
    - Created `src/features/combine_trends_coords.py` to merge results with spatial metadata.
    - Developed `src/visualization/plot_trends.py` to generate spatial trend maps.
- **Results:**
    - **92.5% of wells (1,192)** show a statistically significant trend.
    - **Median Trend:** -0.66 cm/year (systemic regional decline).
    - **Average Total Change:** -22.5 cm over the 25-year study period.
- **Reporting:** Published findings in `reports/groundwater_trends_summary.md`.

### Task 13: Trend Analysis by Spatial Cluster
- **Objective:** Identify regional hotspots of groundwater decline by aggregating trends within the 25 spatial clusters.
- **Implementation:**
    - Created `src/features/analyze_trends_by_cluster.py`.
    - Merged trend results with the well-cluster index.
- **Results:**
    - **Hotspots:** Clusters 18, 16, and 19 show severe declines (> 2.5 cm/year).
    - **Background:** Cluster 14 (486 wells) shows a regional average decline of -0.62 cm/year.
    - **Outliers:** Cluster 24 shows high variability (+4.9 cm/year mean vs -0.13 cm/year median).
- **Reporting:** Published findings in `reports/well_cluster_trend_analysis.md`.

