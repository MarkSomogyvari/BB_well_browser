import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import os
import glob

def analyze_spectra():
    # File paths
    processed_meta_path = 'data/processed/topmost_aquifer_wells.csv'
    timeseries_dir = 'data/raw/Brandenburg_wells/GWData_BB_all_prepro_lv1/'
    output_plot = 'reports/figures/spectral_comparison.png'

    print("Loading classification results...")
    df_meta = pd.read_csv(processed_meta_path)
    
    # Select subsets
    n_samples = 50 # Increase if needed
    topmost_ids = df_meta[df_meta['is_topmost'] == True]['ID'].sample(n_samples, random_state=42).tolist()
    deep_ids = df_meta[df_meta['is_topmost'] == False]['ID'].sample(min(n_samples, df_meta['is_topmost'].value_counts()[False]), random_state=42).tolist()

    def get_psd(well_id):
        # Construct filename
        fname = os.path.join(timeseries_dir, f"BB_{well_id}_GW-Data.csv")
        if not os.path.exists(fname):
            return None
        
        # Read CSV: delimiter is ';', decimal is ','
        try:
            ts = pd.read_csv(fname, sep=';', decimal=',', quotechar='"', parse_dates=['Zeitpunkt'], dayfirst=True)
            ts = ts.rename(columns={'Zeitpunkt': 'date', 'Wasserstand(NHN) [mNHN]': 'h'})
            
            # Remove duplicates and sort
            ts = ts.drop_duplicates('date').sort_values('date')
            ts = ts.set_index('date')
            
            # Resample to monthly to handle irregular sampling and fill gaps
            ts_resampled = ts['h'].resample('ME').mean().interpolate(method='linear')
            
            # If still too many NaNs or too short, skip
            if ts_resampled.isna().any() or len(ts_resampled) < 60: # at least 5 years
                return None
            
            # Detrend for spectral analysis
            data = signal.detrend(ts_resampled.values)
            
            # Welch's method for Power Spectral Density
            # fs = 1.0 (monthly frequency)
            freqs, psd = signal.welch(data, fs=1.0, nperseg=60) # 5-year window
            return freqs, psd
        except Exception as e:
            return None

    print(f"Analyzing {len(topmost_ids)} topmost and {len(deep_ids)} deep wells...")
    
    psd_topmost = []
    for wid in topmost_ids:
        res = get_psd(wid)
        if res: psd_topmost.append(res[1])
        
    psd_deep = []
    for wid in deep_ids:
        res = get_psd(wid)
        if res:
            freqs = res[0] # assuming same freqs for all since same fs and nperseg
            psd_deep.append(res[1])

    # Calculate means
    mean_psd_topmost = np.mean(psd_topmost, axis=0)
    mean_psd_deep = np.mean(psd_deep, axis=0)

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.loglog(freqs, mean_psd_topmost, label='Shallow (Topmost) Aquifer', color='blue', linewidth=2)
    plt.loglog(freqs, mean_psd_deep, label='Deep Aquifer / Mismatch', color='red', linewidth=2)
    
    # Annotate seasonal peak (1/12 months = 0.083)
    plt.axvline(1/12, color='green', linestyle='--', alpha=0.5, label='Annual Cycle (12m)')
    
    plt.title('Average Power Spectral Density of Groundwater Levels')
    plt.xlabel('Frequency [cycles/month]')
    plt.ylabel('Power Spectral Density [m²/cycle]')
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.3)
    
    os.makedirs(os.path.dirname(output_plot), exist_ok=True)
    plt.savefig(output_plot, dpi=300, bbox_inches='tight')
    print(f"Spectral comparison plot saved to {output_plot}")

    # Analysis Summary
    print("\nSpectral Summary:")
    print(f"Avg Power (Topmost): {np.sum(mean_psd_topmost):.4f}")
    print(f"Avg Power (Deep): {np.sum(mean_psd_deep):.4f}")
    
    # High frequency power (periods < 6 months -> freq > 0.16)
    hf_idx = freqs > 0.16
    print(f"High Freq Power (Topmost): {np.sum(mean_psd_topmost[hf_idx]):.4f}")
    print(f"High Freq Power (Deep): {np.sum(mean_psd_deep[hf_idx]):.4f}")

if __name__ == "__main__":
    analyze_spectra()
