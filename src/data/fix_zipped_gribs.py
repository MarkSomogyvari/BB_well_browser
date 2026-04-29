import os
import zipfile
import shutil

def fix_zipped_gribs():
    output_dir = 'data/raw/external/ERA5_Land'
    files = [f for f in os.listdir(output_dir) if f.endswith('.grib')]
    
    for filename in files:
        file_path = os.path.join(output_dir, filename)
        
        # Check if it's a zip file
        with open(file_path, 'rb') as f:
            magic = f.read(2)
            
        if magic == b'PK':
            print(f"Fixing zipped GRIB: {filename}")
            temp_zip = file_path + ".zip"
            os.rename(file_path, temp_zip)
            
            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                # Assuming the file inside is always data.grib
                if 'data.grib' in zip_ref.namelist():
                    zip_ref.extract('data.grib', output_dir)
                    os.rename(os.path.join(output_dir, 'data.grib'), file_path)
                else:
                    print(f"Warning: data.grib not found in {filename}")
            
            os.remove(temp_zip)
        else:
            print(f"File {filename} is already a valid GRIB (or not a zip).")

if __name__ == "__main__":
    fix_zipped_gribs()
