import pandas as pd

CSV_PATH = "data.csv"

def extract():
    print("📥 Extraindo CSV...")
    return pd.read_csv(CSV_PATH)
