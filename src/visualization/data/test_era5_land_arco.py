import cdsapi
import os
import time

def test_era5_download_arco():
    c = cdsapi.Client()
    
    output_dir = 'data/raw/external/ERA5_Land'
    os.makedirs(output_dir, exist_ok=True)
    
    # Updated dataset name for 2026 ARCO-optimized time-series
    dataset = 'reanalysis-era5-land-hourly-time-series'
    target_file = os.path.join(output_dir, 'era5_land_test_arco_2024.nc')
    
    # Berlin/Brandenburg coordinates [Longitude, Latitude]
    location = ['13.4', '52.5']
    
    print(f"Requesting ARCO-optimized time-series for {location}...")
    
    start_time = time.time()
    try:
        c.retrieve(
            dataset,
            {
                'variable': [
                    '2m_temperature',
                    'total_precipitation'
                ],
                'location': location,
                'date': ['2024-01-01', '2024-01-31'],
                'data_format': 'netcdf',
            },
            target_file
        )
        end_time = time.time()
        print(f"Success! ARCO Test file saved to {target_file}")
        print(f"Download took {end_time - start_time:.2f} seconds.")
    except Exception as e:
        print(f"ARCO Download failed: {e}")

if __name__ == "__main__":
    test_era5_download_arco()
