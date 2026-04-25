"""Test simple sans import circulaire"""
import sys
sys.path.insert(0, 'c:/Users/gjacquet/Workspace/Coding/WindAnalysis')

import pandas as pd
from src.wind_turbine_analytics.application.utils.load_data import load_csv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("TEST SIMPLIFIE : Calcul puissance nominale")
print("=" * 80)

# Charger données
df = load_csv(
    'experiments/real_run_test/DATA/E1/'
    'tenMinTimeSeries-01WEA95986-Mean-1260206142049.csv'
)

# Filtrer période
test_start = pd.to_datetime('27.01.2026 15:30:00', dayfirst=True)
test_end = pd.to_datetime('31.01.2026 23:50:00', dayfirst=True)
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)

mask = (df['Date'] >= test_start) & (df['Date'] <= test_end)
df_filtered = df[mask].copy()

print(f"Donnees dans periode: {len(df_filtered)} points")

# Seuil 98% de 3780 kW
P_nom = 3780
threshold_percent = 98
threshold = (threshold_percent / 100.0) * P_nom

print(f"P_nom: {P_nom} kW")
print(f"Seuil: {threshold_percent}% = {threshold:.2f} kW")
print()

# Compter points au-dessus
above = df_filtered[
    df_filtered['01WEA95986 GRD ActivePower'] >= threshold
]

# Intervalle
interval_hours = (
    df_filtered['Date'].diff().dt.total_seconds().median() / 3600
)

print(f"Intervalle de mesure: {interval_hours * 60:.1f} minutes")
print(f"Points >= seuil: {len(above)}")
print(f"Duree totale: {len(above) * interval_hours:.2f}h")
print()

# Critère
required_hours = 3
criterion_met = (len(above) * interval_hours) >= required_hours

print(f"Critere requis: {required_hours}h")
print(f"Critere satisfait: {criterion_met}")
print()

# Valeurs maximales
max_power = df_filtered['01WEA95986 GRD ActivePower'].max()
max_power_idx = df_filtered['01WEA95986 GRD ActivePower'].idxmax()
max_power_time = df_filtered.loc[max_power_idx, 'Date']

max_wind = df_filtered['01WEA95986 MET Wind Speed'].max()
max_wind_idx = df_filtered['01WEA95986 MET Wind Speed'].idxmax()
max_wind_time = df_filtered.loc[max_wind_idx, 'Date']

print(f"Puissance max observee: {max_power:.2f} kW le {max_power_time}")
print(
    f"Vitesse vent max observee: {max_wind:.2f} m/s "
    f"le {max_wind_time}"
)
print()

print("Echantillon des points >= seuil:")
print(
    above[['Date', '01WEA95986 GRD ActivePower']].head(10)
)
print("=" * 80)
