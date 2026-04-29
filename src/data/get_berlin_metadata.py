from owslib.wfs import WebFeatureService
import pandas as pd
import os

def get_berlin_gw_metadata():
    url = "https://gdi.berlin.de/services/wfs/gwm"
    
    print("Connecting to WFS...")
    wfs = WebFeatureService(url=url, version='2.0.0')
    
    print("Available layers:")
    print(list(wfs.contents))
    
    # Usually the layer is fis:s_grundwasser or similar
    # Let's try to get all features for the first content
    layer_name = list(wfs.contents)[0]
    print(f"Fetching features from layer: {layer_name}")
    
    # Request features as JSON if possible for easier parsing
    response = wfs.getfeature(typename=layer_name, outputFormat='application/json')
    
    import json
    data = json.loads(response.read())
    
    # Parse GeoJSON to DataFrame
    features = data['features']
    rows = []
    for f in features:
        props = f['properties']
        geom = f['geometry']
        props['lon'] = geom['coordinates'][0]
        props['lat'] = geom['coordinates'][1]
        rows.append(props)
        
    df = pd.DataFrame(rows)
    
    output_path = 'data/raw/Berlin_wells/berlin_gw_metadata.csv'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved metadata for {len(df)} stations to {output_path}")
    print("\nColumns found:")
    print(df.columns.tolist())
    
    # Print first few IDs to verify
    # Look for 'messstellennummer' or similar
    id_cols = [col for col in df.columns if 'nummer' in col.lower() or 'id' in col.lower()]
    print("\nPotential ID columns:", id_cols)
    if id_cols:
        print(df[id_cols].head())

if __name__ == "__main__":
    get_berlin_gw_metadata()
