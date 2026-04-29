import cdsapi
import os
import time

def test_era5_daily_stats():
    """
    Benchmarks the download speed of daily-statistics ERA5-Land data.
    """
    c = cdsapi.Client()
    output_dir = 'data/raw/external/ERA5_Land'
    os.makedirs(output_dir, exist_ok=True)
    
    target_file = os.path.join(output_dir, 'era5_land_daily_stats_test_2023.grib')
    
    # Brandenburg/Berlin bounds
    area = [53.75, 10.9, 51.1, 15.1]
    
    # Note: Precipitation and Evaporation are NOT in this dataset
    variables = [
        '2m_temperature'
    ]

    print(f"Requesting 1 month of Daily Statistics ERA5-Land data (GRIB) for {area}...")
    start_time = time.time()
    try:
        c.retrieve(
            'derived-era5-land-daily-statistics',
            {
                'format': 'grib',
                'variable': variables,
                'year': '2023',
                'month': '01',
                'day': [f"{d:02d}" for d in range(1, 32)],
                'daily_statistic': 'daily_mean',
                'time_zone': 'utc+00:00',
                'frequency': '1_hourly',
                'area': area,
            },
            target_file
        )
        end_time = time.time()
        print(f"Success! Daily statistics saved to {target_file}")
        print(f"Download took {end_time - start_time:.2f} seconds.")
    except Exception as e:
        print(f"Daily statistics download failed: {e}")

if __name__ == "__main__":
    test_era5_daily_stats()
