import cdsapi
import os
import time
import zipfile
import shutil

def download_era5_land_monthly(start_year, end_year):
    """
    Downloads ERA5-Land data in monthly chunks to stay within CDS API size limits.
    Handles the ZIP format returned by newer CDS infrastructure.
    """
    c = cdsapi.Client()
    output_dir = 'data/raw/external/ERA5_Land'
    os.makedirs(output_dir, exist_ok=True)
    
    # Study area bounds for Brandenburg/Berlin: [North, West, South, East]
    area = [53.75, 10.9, 51.1, 15.1]
    
    variables = [
        '2m_temperature',
        'total_precipitation',
        'total_evaporation',
        'potential_evaporation'
    ]

    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            target_file_grib = os.path.join(output_dir, f'era5_land_{year}_{month:02d}.grib')
            target_file_nc = os.path.join(output_dir, f'era5_land_{year}_{month:02d}.nc')
            
            if os.path.exists(target_file_grib) or os.path.exists(target_file_nc):
                print(f"File for {year}-{month:02d} already exists (.grib or .nc), skipping.")
                continue
                
            print(f"Requesting ERA5-Land data (GRIB) for {year}-{month:02d}...")
            temp_zip = target_file_grib + ".zip"
            try:
                c.retrieve(
                    'reanalysis-era5-land',
                    {
                        'variable': variables,
                        'year': str(year),
                        'month': f"{month:02d}",
                        'day': [f"{d:02d}" for d in range(1, 32)],
                        'time': [f"{h:02d}:00" for h in range(0, 24)],
                        'area': area,
                        'format': 'grib',
                    },
                    temp_zip
                )
                
                # Extract GRIB from ZIP
                with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                    if 'data.grib' in zip_ref.namelist():
                        zip_ref.extract('data.grib', output_dir)
                        os.rename(os.path.join(output_dir, 'data.grib'), target_file_grib)
                        print(f"Successfully downloaded and extracted {year}-{month:02d}.")
                    else:
                        print(f"Warning: data.grib not found in ZIP for {year}-{month:02d}")
                
                os.remove(temp_zip)
                
                # Wait 10 seconds between months to be respectful to the API
                time.sleep(10)
            except Exception as e:
                print(f"Error downloading {year}-{month:02d}: {e}")
                if os.path.exists(temp_zip):
                    os.remove(temp_zip)
                # Wait longer on error (e.g., rate limit)
                time.sleep(60)

if __name__ == "__main__":
    # Coverage for the study period (2000-2025)
    download_era5_land_monthly(2000, 2025)
