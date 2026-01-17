import pandas as pd

def transform(df: pd.DataFrame) -> pd.DataFrame:
    print("🔄 Transformando dados...")

    df.columns = [c.lower().strip() for c in df.columns]

    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df["tipo"] = df["tipo"].str.lower().str.strip()
    df["categoria"] = df["categoria"].str.strip()
    df["conta"] = df["conta"].str.strip()

    df = df.dropna(subset=["data", "valor", "tipo", "categoria", "conta"])

    return df
