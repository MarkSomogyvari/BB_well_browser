# Brandenburg Groundwater Data Analysis Project

## Project Structure

- `data/`:
    - `raw/`: Original, immutable data.
    - `interim/`: Intermediate data that has been transformed.
    - `processed/`: The final, canonical data sets for modeling.
    - `external/`: Data from third party sources.
- `notebooks/`: Jupyter notebooks for exploratory analysis and visualization.
- `src/`: Source code for use in this project.
    - `data/`: Scripts to download or generate data.
    - `features/`: Scripts to turn raw data into features for modeling.
    - `models/`: Scripts to train models and make predictions.
    - `visualization/`: Scripts to create visualizations.
- `models/`: Trained and serialized models, model predictions, or model summaries.
- `reports/`: Generated analysis as HTML, PDF, LaTeX, etc.
    - `figures/`: Generated graphics and figures for reporting.
- `docs/`: Documentation for the project.
- `requirements.txt`: Requirements file for reproducing the analysis environment.
