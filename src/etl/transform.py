import pandas as pd

def transform(df: pd.DataFrame) -> pd.DataFrame:
    print("🔄 Transformando dados...")
    print(df.columns)
    # Padroniza nomes das colunas
    #df.columns = [c.lower().strip() for c in df.columns]

    df = df.drop(columns=["Unnamed: 4"], errors="ignore")
    df = df.drop(columns=["Unnamed: 7"], errors="ignore")
    df = df.drop(columns=["Unnamed: 0"], errors="ignore")
    df = df.drop(columns=["Unnamed: 5"], errors="ignore")
    df = df.drop(columns=["Unnamed: 8"], errors="ignore")
    df = df.drop(columns=["Unnamed: 9"], errors="ignore")
    #df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    #df["Data"] = df["Data"].astype(str)
    df["Data"] = pd.to_datetime(
    df["Data"],
    format="%d/%m/%Y %H:%M",
    errors="coerce"
)
    df["Descrição"] = df["Descrição"].str.lower().str.strip()
    df["Categoria"] = df["Categoria"].str.strip()
    df["Transação"] = df["Transação"].str.lower().str.strip()
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    df["Conta"] = "Conta BTG Pactual"
    df["Tipo"] = df["Valor"].apply(lambda x: "saida" if x < 0 else "entrada")

    print(df)
    qtd = df.isna().any(axis=1).sum()
    print("A quantidade de linhas com valores nulos é:", qtd)

    df = df.dropna(subset=["Data", "Valor", "Transação", "Categoria", "Descrição", "Conta"])

    return df
