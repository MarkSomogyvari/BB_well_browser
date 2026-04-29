# Groundwater Trend Analysis Summary (2000-2025)

## Overview
This report summarizes the results of a long-term trend analysis of groundwater levels for **1,289 high-quality wells** screening the topmost aquifer in Brandenburg and Berlin. The analysis covers the 25-year period from 2000 to 2025.

## Methodology
- **Dataset:** 1,289 wells identified as "High Quality" (Flagged=False in the 2000-2025 assessment).
- **Trend Estimator:** Theil-Sen Slope (robust to outliers and non-normal distributions).
- **Significance Test:** Mann-Kendall test (via `scipy.stats.kendalltau`).
- **Resolution:** Weekly mean timeseries.

## Key Findings

### Statistical Summary
| Metric | Value |
| :--- | :--- |
| **Total Wells Analyzed** | 1,289 |
| **Wells with Significant Trends (p < 0.05)** | 1,192 (92.5%) |
| **Mean Trend (All Wells)** | -0.87 cm/year |
| **Median Trend (All Wells)** | -0.66 cm/year |
| **Average Total Change (25 years)** | -22.5 cm |
| **Max Decline Observed** | -28.9 cm/year |
| **Max Increase Observed** | +31.1 cm/year |

### Spatial Patterns
The majority of the study area exhibits a significant **decline** in groundwater levels. 
- **Widespread Decline:** Over 90% of significant trends are negative, indicating a systemic regional reduction in groundwater storage.
- **Regional Variation:** While the decline is widespread, some areas show stable or even slightly rising levels, potentially due to local recharge conditions or reduced extraction.

## Visualizations

### Trend Magnitude Map
The map below shows the spatial distribution of trends. Red circles indicate falling levels, while blue circles indicate rising levels. The size and color intensity reflect the magnitude of the annual change.

![Groundwater Trends Map](../figures/groundwater_trends_map.png)

### Distribution of Trends
The histogram below shows the distribution of annual trend magnitudes. The clear shift of the distribution to the left of the zero line (red dashed) highlights the regional decline.

![Groundwater Trends Histogram](../figures/groundwater_trends_hist.png)

## Conclusion
The analysis confirms a statistically significant and widespread decline in surface-near groundwater levels across Brandenburg and Berlin over the last 25 years. This trend is likely driven by a combination of changing climatic patterns (increased potential evaporation, altered precipitation timing) and anthropogenic factors. These findings will serve as the baseline for the subsequent predictive modeling phase.

## Next Steps
1. **Climate Integration:** Correlate these trends with ERA5-Land climate data (Precipitation, Temperature, Evaporation) once the download is complete.
2. **Feature Engineering:** Calculate drought indices (e.g., SPI, SPEI) and other predictors.
3. **Model Development:** Train models to predict future groundwater levels based on various climate scenarios.
