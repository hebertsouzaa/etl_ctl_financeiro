import psycopg2
from psycopg2.extras import execute_batch
from src.config.database import DB_CONFIG

def load(df):
    print("📤 Carregando dados no PostgreSQL...")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Inserir contas
    contas = df["Conta"].unique()
    cur.executemany(
        """
        INSERT INTO tb_contas (nome)
        VALUES (%s)
        ON CONFLICT (nome) DO NOTHING
        """,
        [(c,) for c in contas]
    )

    # Inserir categorias
    categorias = df[["Categoria", "Tipo"]].drop_duplicates()
    cur.executemany(
        """
        INSERT INTO tb_categorias (nome, tipo)
        VALUES (%s, %s)
        ON CONFLICT (nome) DO NOTHING
        """,
        categorias.values.tolist()
    )

    # Buscar IDs
    cur.execute("SELECT id, nome FROM tb_contas")
    contas_map = {nome: id for id, nome in cur.fetchall()}

    cur.execute("SELECT id, nome FROM tb_categorias")
    categorias_map = {nome: id for id, nome in cur.fetchall()}

    # Inserir transações
    transacoes = [
        (
            row["Data"],
            row["Descrição"],
            abs(row["Valor"]),
            row["Tipo"],
            row["Transação"],
            contas_map[row["Conta"]],
            categorias_map[row["Categoria"]]
        )
        for _, row in df.iterrows()
    ]

    # print(transacoes[:5])  # Debug: print first 5 transactions")

    sql = """
        INSERT INTO tb_transacoes
        (data, descricao, valor, tipo, transação, conta_id, categoria_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    execute_batch(cur, sql, transacoes, page_size=1000)

    conn.commit()
    cur.close()
    conn.close()

    print(f"✅ {len(transacoes)} transações carregadas com sucesso!")
