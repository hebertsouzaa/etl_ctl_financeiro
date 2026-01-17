import psycopg2
from psycopg2.extras import execute_batch
from config.database import DB_CONFIG

def load(df):
    print("📤 Carregando dados no PostgreSQL...")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Inserir contas
    contas = df["conta"].unique()
    cur.executemany(
        """
        INSERT INTO contas (nome)
        VALUES (%s)
        ON CONFLICT (nome) DO NOTHING
        """,
        [(c,) for c in contas]
    )

    # Inserir categorias
    categorias = df[["categoria", "tipo"]].drop_duplicates()
    cur.executemany(
        """
        INSERT INTO categorias (nome, tipo)
        VALUES (%s, %s)
        ON CONFLICT (nome) DO NOTHING
        """,
        categorias.values.tolist()
    )

    # Buscar IDs
    cur.execute("SELECT id, nome FROM contas")
    contas_map = {nome: id for id, nome in cur.fetchall()}

    cur.execute("SELECT id, nome FROM categorias")
    categorias_map = {nome: id for id, nome in cur.fetchall()}

    # Inserir transações
    transacoes = [
        (
            row["data"],
            row["descricao"],
            abs(row["valor"]),
            row["tipo"],
            contas_map[row["conta"]],
            categorias_map[row["categoria"]]
        )
        for _, row in df.iterrows()
    ]

    sql = """
        INSERT INTO transacoes
        (data, descricao, valor, tipo, conta_id, categoria_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    execute_batch(cur, sql, transacoes, page_size=1000)

    conn.commit()
    cur.close()
    conn.close()

    print(f"✅ {len(transacoes)} transações carregadas com sucesso!")
