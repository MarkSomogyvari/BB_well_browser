import cdsapi
import os

def test_era5_download():
    c = cdsapi.Client()
    
    output_dir = 'data/raw/external/ERA5_Land'
    os.makedirs(output_dir, exist_ok=True)
    
    target_file = os.path.join(output_dir, 'era5_land_test_2024.nc')
    
    # Study area bounds: [North, West, South, East]
    area = [53.75, 10.9, 51.1, 15.1]
    
    print(f"Requesting test data for {area}...")
    
    try:
        c.retrieve(
            'reanalysis-era5-land',
            {
                'variable': [
                    'total_precipitation', 
                    'total_evaporation',
                    '2m_temperature'
                ],
                'year': '2024',
                'month': '01',
                'day': '01',
                'time': [
                    '00:00', '06:00', '12:00', '18:00'
                ],
                'area': area,
                'format': 'netcdf',
            },
            target_file
        )
        print(f"Success! Test file saved to {target_file}")
    except Exception as e:
        print(f"Download failed: {e}")

if __name__ == "__main__":
    test_era5_download()
