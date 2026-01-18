import pandas as pd

CSV_PATH = "/home/hebertsouza/etl_ctl_financeiro/src/etl/Extrato_2025-12-19_a_2026-01-17_03379339105.csv"

def extract():
    print("📥 Extraindo CSV...")
    return pd.read_csv(CSV_PATH)
