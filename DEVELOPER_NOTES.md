# Developer Notes: Brandenburg & Berlin Groundwater Analysis

This file documents the environment configuration and technical strategies that successfully worked for this project.

## Python Environment
- **Path:** `C:\Users\Mark\anaconda3\envs\raven\python.exe`
- **Key Libraries:** `pandas`, `geopandas`, `shapely`, `contextily`, `owslib`, `scipy`, `matplotlib`.
- **Critical Dependency Note:** 
    - `numpy` **must be < 2.0.0** (specifically version `1.26.4` is verified).
    - Higher versions (2.x) cause `ImportError: numpy.core.multiarray failed to import` in `shapely` and `geopandas` within this specific Anaconda environment.

## R Environment (Fallback/Alternative)
- **Path:** `C:\Program Files\R\R-4.3.2\bin\R.exe`
- **Package Note:** The `wasserportal` package may have dependency issues with `xml2` binaries. A robust alternative is the direct Python download script.

## Data Acquisition (Berlin Wasserportal)
- **Metadata:** Use the GDI-BE WFS service: `https://gdi.berlin.de/services/wfs/gwm`.
- **Station IDs:** Use the `invhyas` field from the WFS metadata to match the public portal.
- **Timeseries Download:** Must use a **POST** request to `https://wasserportal.berlin.de/station.php`.
    - **Required Payload:**
        ```python
        {
            'anzeige': 'd',
            'station': sid,
            'sreihe': 'wa',
            'smode': 'c',
            'thema': 'gws',
            'exportthema': 'gw',
            'sdatum': '01.01.1850',
            'senddatum': 'current_date'
        }
        ```
    - *Note:* Standard GET requests or the `download.php` endpoint resulted in SQL errors or 404s.

## Aquifer Identification Logic
- **Brandenburg:** Compare well measurements with the regional `Groundwater_distance` shapefile. A threshold of `|h_measured - h_calculated| <= 1.5m` effectively identifies the topmost aquifer.
- **Berlin:** Parse CSV headers for the `Grundwasserleiter` field. Any string containing **"GWL 1"** (e.g., "GWL 1.3 + 2") indicates the topmost layer.
