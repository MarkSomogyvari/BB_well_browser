# Brandenburg Groundwater Project Mandates

This file contains foundational instructions that take absolute precedence over general agent defaults.

## Project Goal
- Analyze groundwater level trends in the Brandenburg region.
- Build predictive models for future groundwater availability.

## Data Integrity & Management
- **Raw Data:** Files in `data/raw/` are **immutable**. Never modify them directly.
- **Reproducibility:** All data transformations must be scripted in `src/data/` or `src/features/`. 
- **Intermediate Storage:** Store cleaned data in `data/interim/` and modeling-ready features in `data/processed/`.

## Engineering Standards
- **Language:** Python 3.x.
- **Style:** Follow PEP 8 for scripts in `src/`.
- **Notebooks:** Use `notebooks/` for exploration only. Move stable logic to `src/` to keep notebooks clean and importable.
- **Documentation:** Every function in `src/` must have a docstring (Google style) explaining parameters and return values.

## Project Maintenance
- **Logging:** Maintain a comprehensive `LOG.md` file. Every significant task, script creation, data transformation, or milestone must be documented there with a date and a brief summary of results.
- **Environment:** Use the Anaconda `raven` environment for all Python scripts. The executable path is stored in memory.

## Verification & Validation
- **Unit Tests:** All scripts in `src/` must have corresponding tests in a `tests/` directory (to be created as needed).
- **Data Validation:** Check for null values, outliers, and coordinate system consistency (e.g., EPSG:25833 for Brandenburg) during the ETL process.

## Domain Specifics
- **Spatial Resolution:** Brandenburg-wide, but be aware of local hydrological variations.
- **Temporal Resolution:** Monthly or daily averages depending on available sensor data.
