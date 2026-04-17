import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Conexão com banco
conn = sqlite3.connect("dados.db", check_same_thread=False)
cursor = conn.cursor()

# Criar tabela com categoria
cursor.execute("""
CREATE TABLE IF NOT EXISTS caixa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT,
    categoria TEXT,
    descricao TEXT,
    valor REAL,
    data TEXT
)
""")
conn.commit()

st.set_page_config(page_title="Controle de Caixa", layout="centered")

st.title("💈 Controle de Caixa - Salão")

# =========================
# ➕ NOVO REGISTRO
# =========================
st.subheader("➕ Novo Registro")

col1, col2 = st.columns(2)

with col1:
    tipo = st.selectbox("Tipo", ["Entrada", "Saída"])

with col2:
    categoria = st.selectbox("Categoria", [
        "Corte",
        "Escova",
        "Coloração",
        "Barba",
        "Produto",
        "Despesa"
    ])

descricao = st.text_input("Descrição")
valor = st.number_input("Valor", min_value=0.0, format="%.2f")

if st.button("Salvar"):
    data = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        INSERT INTO caixa (tipo, categoria, descricao, valor, data)
        VALUES (?, ?, ?, ?, ?)
    """, (tipo, categoria, descricao, valor, data))
    conn.commit()
    st.success("Registro salvo!")

# =========================
# 📅 FILTRO POR MÊS
# =========================
st.subheader("📅 Filtrar por mês")

mes_atual = datetime.now().month
ano_atual = datetime.now().year

mes = st.selectbox("Mês", list(range(1, 13)), index=mes_atual - 1)
ano = st.number_input("Ano", value=ano_atual)

# Buscar dados
df = pd.read_sql("SELECT * FROM caixa", conn)

if not df.empty:
    df["data"] = pd.to_datetime(df["data"])

    df_filtrado = df[
        (df["data"].dt.month == mes) &
        (df["data"].dt.year == ano)
    ]

    # =========================
    # 📊 RESUMO
    # =========================
    st.subheader("📊 Resumo")

    entradas = df_filtrado[df_filtrado["tipo"] == "Entrada"]["valor"].sum()
    saidas = df_filtrado[df_filtrado["tipo"] == "Saída"]["valor"].sum()
    total = entradas - saidas

    col1, col2, col3 = st.columns(3)

    col1.metric("Entradas", f"R$ {entradas:.2f}")
    col2.metric("Saídas", f"R$ {saidas:.2f}")
    col3.metric("Lucro", f"R$ {total:.2f}")

    # =========================
    # 🗑️ EXCLUIR REGISTRO
    # =========================
    st.subheader("🗑️ Registros")

    for index, row in df_filtrado.iterrows():
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

        col1.write(row["categoria"])
        col2.write(row["descricao"])
        col3.write(f"R$ {row['valor']:.2f}")

        if col4.button("Excluir", key=row["id"]):
            cursor.execute("DELETE FROM caixa WHERE id = ?", (row["id"],))
            conn.commit()
            st.experimental_rerun()

else:
    st.info("Nenhum registro encontrado.")