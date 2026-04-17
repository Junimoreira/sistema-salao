import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Conectar banco
conn = sqlite3.connect("dados.db", check_same_thread=False)
cursor = conn.cursor()

# Criar tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS caixa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT,
    descricao TEXT,
    valor REAL,
    data TEXT
)
""")
conn.commit()

st.title("💈 Controle de Caixa - Salão")

# Entrada de dados
st.subheader("➕ Novo Registro")

tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
descricao = st.text_input("Descrição")
valor = st.number_input("Valor", min_value=0.0, format="%.2f")

if st.button("Salvar"):
    data = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO caixa (tipo, descricao, valor, data) VALUES (?, ?, ?, ?)",
                   (tipo, descricao, valor, data))
    conn.commit()
    st.success("Registro salvo!")

# Mostrar dados
st.subheader("📊 Resumo do Dia")

df = pd.read_sql("SELECT * FROM caixa", conn)

if not df.empty:
    hoje = datetime.now().strftime("%Y-%m-%d")
    df_hoje = df[df["data"] == hoje]

    entradas = df_hoje[df_hoje["tipo"] == "Entrada"]["valor"].sum()
    saidas = df_hoje[df_hoje["tipo"] == "Saída"]["valor"].sum()

    st.write(f"💰 Entradas: R$ {entradas:.2f}")
    st.write(f"💸 Saídas: R$ {saidas:.2f}")
    st.write(f"📈 Total: R$ {entradas - saidas:.2f}")

    st.dataframe(df_hoje)
else:
    st.info("Nenhum registro ainda.")