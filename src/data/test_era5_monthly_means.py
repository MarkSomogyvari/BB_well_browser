import cdsapi
import os
import time

def test_era5_monthly_means():
    """
    Benchmarks the download speed of monthly-averaged ERA5-Land data.
    """
    c = cdsapi.Client()
    output_dir = 'data/raw/external/ERA5_Land'
    os.makedirs(output_dir, exist_ok=True)
    
    target_file = os.path.join(output_dir, 'era5_land_monthly_means_test_2023.grib')
    
    # Brandenburg/Berlin bounds
    area = [53.75, 10.9, 51.1, 15.1]
    
    variables = [
        '2m_temperature',
        'total_precipitation',
        'total_evaporation',
        'potential_evaporation'
    ]

    print(f"Requesting 1 year of Monthly-Averaged ERA5-Land data (GRIB) for {area}...")
    start_time = time.time()
    try:
        c.retrieve(
            'reanalysis-era5-land-monthly-means',
            {
                'format': 'grib',
                'product_type': 'monthly_averaged_reanalysis',
                'variable': variables,
                'year': '2023',
                'month': [f"{m:02d}" for m in range(1, 13)],
                'time': '00:00',
                'area': area,
            },
            target_file
        )
        end_time = time.time()
        print(f"Success! Monthly means saved to {target_file}")
        print(f"Download took {end_time - start_time:.2f} seconds.")
        print(f"File size: {os.path.getsize(target_file) / 1024:.2f} KB")
    except Exception as e:
        print(f"Monthly means download failed: {e}")

if __name__ == "__main__":
    test_era5_monthly_means()
