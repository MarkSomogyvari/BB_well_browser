import os
import pandas as pd
import glob
import re

def identify_berlin_topmost():
    timeseries_dir = 'data/raw/Berlin_wells/timeseries'
    output_path = 'data/processed/berlin_topmost_identification.csv'
    
    csv_files = glob.glob(os.path.join(timeseries_dir, 'station_*.csv'))
    print(f"Analyzing {len(csv_files)} Berlin stations...")
    
    results = []
    
    for fpath in csv_files:
        try:
            # Read only the header part (first 20 lines should be enough)
            with open(fpath, 'r', encoding='utf-8') as f:
                header_lines = [f.readline().strip() for _ in range(20)]
            
            data = {}
            for line in header_lines:
                if ';' in line:
                    parts = line.split(';', 1)
                    key = parts[0].strip('"')
                    value = parts[1].strip('"')
                    data[key] = value
            
            # Extract relevant fields
            sid = data.get('Messstellennummer')
            aquifer = data.get('Grundwasserleiter', '')
            pressure = data.get('Grundwasserdruckfläche', '') # Note: may have encoding issues
            # Alternative key if encoding differs
            if not pressure:
                pressure = data.get('Grundwasserdruckfl\xe4che', '')
            
            # Identification logic
            # Rule: "GWL 1.3 + 2" or contains "GWL 1"
            is_topmost = False
            if "GWL 1" in aquifer:
                is_topmost = True
            
            # Store
            results.append({
                'ID': sid,
                'Grundwasserleiter': aquifer,
                'Grundwasserdruckflaeche': pressure,
                'is_topmost': is_topmost,
                'file_path': fpath
            })
            
        except Exception as e:
            print(f"Error processing {fpath}: {e}")
            
    df = pd.DataFrame(results)
    
    # Save results
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"Berlin identification complete.")
    print(f"Total stations analyzed: {len(df)}")
    print(f"Identified as topmost: {df['is_topmost'].sum()}")
    
    # Show some examples of what was excluded
    print("\nExamples of excluded aquifers:")
    print(df[df['is_topmost'] == False]['Grundwasserleiter'].unique()[:10])

if __name__ == "__main__":
    identify_berlin_topmost()
