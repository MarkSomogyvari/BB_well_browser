import pandas as pd
import numpy as np
import os
import glob
from scipy.signal import lombscargle
import matplotlib.pyplot as plt
from tqdm import tqdm

def run_spectral_analysis():
    # Paths
    index_path = 'data/processed/well_cluster_index.csv'
    quality_path = 'data/processed/timeseries_quality_summary_2000_2025.csv'
    cluster_base_dir = 'data/interim/timeseries_by_cluster'
    output_dir = 'reports/spectral_analysis'
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'figures'), exist_ok=True)

    print("Loading indices and quality summaries...")
    df_index = pd.read_csv(index_path)
    df_quality = pd.read_csv(quality_path)
    
    # Filter for high-quality wells only
    hq_ids = df_quality[df_quality['Flagged'] == False]['ID'].astype(str).tolist()
    df_hq = df_index[df_index['well_id'].astype(str).isin(hq_ids)].copy()
    
    print(f"Analyzing {len(df_hq)} high-quality wells across {len(df_hq['cluster_id'].unique())} clusters.")

    # Frequency range for Lomb-Scargle (units: cycles per week)
    # Periods from 4 weeks (0.25 year) to 10 years (520 weeks)
    periods = np.linspace(4, 520, 500) # periods in weeks
    freqs = 2 * np.pi / periods # angular frequencies for scipy
    
    cluster_psds = {}

    # Process cluster by cluster
    clusters = sorted(df_hq['cluster_id'].unique())
    
    for cluster_id in clusters:
        print(f"Processing Cluster {int(cluster_id)}...")
        cluster_wells = df_hq[df_hq['cluster_id'] == cluster_id]
        
        all_psds = []
        
        for _, row in cluster_wells.iterrows():
            well_id = str(int(float(row['well_id'])))
            prefix = "BB" if row['source'] == 'Brandenburg' else "BE"
            file_path = os.path.join(cluster_base_dir, f"cluster_{int(cluster_id)}", f"{prefix}_{well_id}_weekly.csv")
            
            if not os.path.exists(file_path):
                continue
                
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'])
            df = df.dropna()
            
            if len(df) < 52: # Minimum 1 year of data
                continue
            
            # Time in weeks from start
            t = (df['date'] - df['date'].min()).dt.days / 7.0
            y = df['gw_level'].values
            
            # Normalize y (detrend and scale)
            y = (y - np.mean(y)) / np.std(y)
            
            # Calculate Lomb-Scargle
            pgram = lombscargle(t, y, freqs, normalize=True)
            all_psds.append(pgram)
            
        if all_psds:
            # Average PSD for the cluster
            avg_psd = np.mean(all_psds, axis=0)
            cluster_psds[int(cluster_id)] = avg_psd
            
            # Plot individual cluster signature
            plt.figure(figsize=(10, 6))
            plt.plot(periods / 52.18, avg_psd) # Convert weeks to years for X-axis
            plt.title(f"Mean Spectral Signature: Cluster {int(cluster_id)}")
            plt.xlabel("Period (Years)")
            plt.ylabel("Normalized Power")
            plt.grid(True, alpha=0.3)
            plt.savefig(os.path.join(output_dir, 'figures', f"cluster_{int(cluster_id)}_spectrum.png"))
            plt.close()

    # Create Comparison Plot
    print("Generating comparison plot...")
    plt.figure(figsize=(12, 8))
    for cid, psd in cluster_psds.items():
        plt.plot(periods / 52.18, psd, label=f"Cluster {cid}", alpha=0.6)
    
    plt.title("Cluster Comparison: Groundwater Level Power Spectra")
    plt.xlabel("Period (Years)")
    plt.ylabel("Normalized Power")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', ncol=2)
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(output_dir, 'figures', "all_clusters_comparison.png"), bbox_inches='tight')
    plt.close()

    # Generate Report
    print("Generating report...")
    with open(os.path.join(output_dir, 'spectral_summary.md'), 'w', encoding='utf-8') as f:
        f.write("# Cluster-Scale Spectral Analysis Report\n\n")
        f.write("## Objective\n")
        f.write("Identify dominant groundwater level periodicities (e.g., annual, multi-annual) within each spatial cluster using the Lomb-Scargle periodogram on high-quality timeseries (2000-2025).\n\n")
        
        f.write("## Methodology\n")
        f.write("1. **Data Selection:** Only 'High Quality' wells (max gaps < 8 weeks) were included.\n")
        f.write("2. **Normalization:** Individual timeseries were detrended (mean removed) and variance-normalized before analysis.\n")
        f.write("3. **Spectrum:** Calculated Lomb-Scargle Power Spectral Density (PSD) for periods between 0.1 and 10 years.\n")
        f.write("4. **Aggregation:** Averaged normalized PSDs across all wells in a cluster to extract the regional signal.\n\n")
        
        f.write("## Key Findings\n")
        f.write("| Cluster ID | Dominant Period (Years) | Max Power | Interpretation |\n")
        f.write("|------------|-------------------------|-----------|----------------|\n")
        
        for cid, psd in cluster_psds.items():
            max_idx = np.argmax(psd)
            dom_period = periods[max_idx] / 52.18
            max_power = psd[max_idx]
            
            interp = "Annual/Seasonal" if 0.8 < dom_period < 1.2 else "Multi-annual"
            f.write(f"| {cid} | {dom_period:.2f} | {max_power:.3f} | {interp} |\n")
            
        f.write("\n## Comparative Visualization\n")
        f.write("![All Clusters Comparison](figures/all_clusters_comparison.png)\n")

    print(f"Spectral analysis complete. Report at {output_dir}/spectral_summary.md")

if __name__ == "__main__":
    run_spectral_analysis()
