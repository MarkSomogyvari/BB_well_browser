import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import time

def download_berlin_data():
    output_dir = 'data/raw/Berlin_wells/timeseries'
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Scrape the station IDs from the Wasserportal website (more reliable than WFS for public data)
    print("Scraping station list from Wasserportal...")
    url_list = "https://wasserportal.berlin.de/start.php?anzeige=tabelle_gw&messanzeige=ms_gw_berlin"
    try:
        r_list = requests.get(url_list)
        soup = BeautifulSoup(r_list.text, 'html.parser')
        # Find the first table
        table = soup.find('table')
        if not table:
            print("Error: Could not find station table.")
            return
        
        # Extract station IDs (first column of the table)
        station_ids = []
        for row in table.find_all('tr')[1:]: # Skip header
            cols = row.find_all('td')
            if cols:
                sid = cols[0].text.strip()
                if sid.isdigit():
                    station_ids.append(sid)
        
        print(f"Found {len(station_ids)} station IDs on the website.")
    except Exception as e:
        print(f"Error scraping station list: {e}")
        return

    # 2. Download timeseries
    url_post = 'https://wasserportal.berlin.de/station.php'
    today = datetime.now().strftime('%d.%m.%Y')
    
    success_count = 0
    error_count = 0
    
    print(f"Starting download for {len(station_ids)} stations...")
    
    for sid in station_ids:
        dest_file = os.path.join(output_dir, f"station_{sid}.csv")
        
        # Skip if already downloaded and valid
        if os.path.exists(dest_file) and os.path.getsize(dest_file) > 2000:
            continue
            
        payload = {
            'anzeige': 'd',
            'station': sid,
            'sreihe': 'wa',
            'smode': 'c',
            'thema': 'gws',
            'exportthema': 'gw',
            'sdatum': '01.01.1850',
            'senddatum': today
        }
        
        try:
            r = requests.post(url_post, data=payload, timeout=30)
            # Check if it contains actual data rows (e.g. check for a date pattern or semicolon count)
            if r.status_code == 200 and len(r.text) > 1000 and "Datum;" in r.text:
                with open(dest_file, 'w', encoding='utf-8') as f:
                    f.write(r.text)
                success_count += 1
                if success_count % 50 == 0:
                    print(f"Progress: {success_count} downloaded...")
            else:
                error_count += 1
        except Exception as e:
            error_count += 1
            
        time.sleep(0.1)
        
    print(f"Completed. Successfully downloaded {success_count} stations. {error_count} failed/skipped.")

if __name__ == "__main__":
    download_berlin_data()
