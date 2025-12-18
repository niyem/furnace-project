import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ==========================================
# CONFIGURATION
# ==========================================
# Adjust this filename if needed
INPUT_FILE = os.path.join('data', 'raw', 'Final_Modified.xlsx')
OUTPUT_DIR = os.path.join('outputs', 'efficiency_stats')

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set plot style for publication quality
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['savefig.dpi'] = 300

def load_and_prep_data(filepath):
    """
    Loads data and ensures efficiency columns are percentages (0-100).
    """
    print(f"[Info] Loading data from: {filepath}")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    if filepath.endswith('.xlsx'):
        df = pd.read_excel(filepath, engine='openpyxl')
    else:
        df = pd.read_csv(filepath)

    # Standardize Column Names
    rename_map = {
        'ThermalEffCold': 'Cold Start',
        'ThermalEffHot': 'Hot Start',
        'Thermal efficiency(%)  LOW POWER(SIMMER)': 'Simmer',
        'ThermalEffSimmer': 'Simmer' # Handle case if already renamed
    }
    df.rename(columns=rename_map, inplace=True)

    # Helper to fix percentages
    def fix_pct(col_name):
        if col_name in df.columns:
            # If max value < 1.0, it's a decimal (0.25), so multiply by 100
            if df[col_name].max() < 1.0:
                df[col_name] = df[col_name] * 100
            return df[col_name]
        return None

    # Apply fixes
    df['Cold Start'] = fix_pct('Cold Start')
    df['Hot Start'] = fix_pct('Hot Start')
    
    # Simmer usually comes as 0-100, but let's check
    if 'Simmer' in df.columns:
        if df['Simmer'].max() < 1.0:
            df['Simmer'] = df['Simmer'] * 100
    
    # Calculate Combined Average
    # We use nanmean to handle cases where a phase might be missing
    df['Combined Average'] = df[['Cold Start', 'Hot Start', 'Simmer']].mean(axis=1)

    return df

def print_stats(df):
    """
    Prints a formatted statistical summary table.
    """
    metrics = ['Cold Start', 'Hot Start', 'Simmer', 'Combined Average']
    valid_metrics = [m for m in metrics if m in df.columns]
    
    stats = df[valid_metrics].describe().T
    stats['CV (%)'] = (stats['std'] / stats['mean']) * 100 # Coefficient of Variation
    
    print("\n" + "="*60)
    print("      THERMAL EFFICIENCY STATISTICS (%)")
    print("="*60)
    print(f"{'Metric':<20} | {'Mean':<8} | {'StdDev':<8} | {'Min':<8} | {'Max':<8} | {'CV%':<6}")
    print("-" * 75)
    
    for index, row in stats.iterrows():
        print(f"{index:<20} | {row['mean']:<8.2f} | {row['std']:<8.2f} | {row['min']:<8.2f} | {row['max']:<8.2f} | {row['CV (%)']:<6.1f}")
    print("="*60 + "\n")

    # Save CSV report
    report_path = os.path.join(OUTPUT_DIR, 'efficiency_descriptive_stats.csv')
    stats.to_csv(report_path)
    print(f"[Info] Stats saved to: {report_path}")

def plot_distributions(df):
    """
    Generates distribution plots.
    """
    metrics = ['Cold Start', 'Hot Start', 'Simmer', 'Combined Average']
    valid_metrics = [m for m in metrics if m in df.columns]
    
    # Melt data for categorical plotting
    df_melt = pd.melt(df, value_vars=valid_metrics, var_name='Phase', value_name='Efficiency (%)')

    # --- FIG A: Kernel Density Estimate (Distribution curves) ---
    plt.figure(figsize=(10, 6))
    for col in valid_metrics:
        sns.kdeplot(df[col], fill=True, label=col, alpha=0.3)
    plt.title('Distribution of Thermal Efficiencies (All Phases)')
    plt.xlabel('Thermal Efficiency (%)')
    plt.ylabel('Density')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'FigA_Efficiency_Distributions.png'))
    plt.close()

    # --- FIG B: Box Plot with Jitter ---
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Phase', y='Efficiency (%)', data=df_melt, palette='Set2', showfliers=False)
    sns.stripplot(x='Phase', y='Efficiency (%)', data=df_melt, color='black', alpha=0.2, size=3)
    plt.title('Comparison of Efficiency Ranges')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'FigB_Efficiency_Boxplots.png'))
    plt.close()

    # --- FIG C: Violin Plot ---
    plt.figure(figsize=(10, 6))
    sns.violinplot(x='Phase', y='Efficiency (%)', data=df_melt, palette='Pastel1', inner='quartile')
    plt.title('Efficiency Density Profiles (Violin Plot)')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'FigC_Efficiency_Violin.png'))
    plt.close()

    # --- FIG D: Correlation Heatmap ---
    if len(valid_metrics) > 1:
        plt.figure(figsize=(8, 6))
        corr = df[valid_metrics].corr()
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", square=True)
        plt.title('Correlation Between Efficiency Phases')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'FigD_Efficiency_Correlation.png'))
        plt.close()

    print(f"[Info] All figures saved to: {OUTPUT_DIR}/")

def main():
    try:
        df = load_and_prep_data(INPUT_FILE)
        print_stats(df)
        plot_distributions(df)
        print("[Done] Analysis complete.")
    except Exception as e:
        print(f"[Error] {e}")

if __name__ == "__main__":
    main()