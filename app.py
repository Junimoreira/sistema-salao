import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Conexão
conn = sqlite3.connect("dados.db", check_same_thread=False)
cursor = conn.cursor()

# =========================
# 🧱 CRIAR TABELAS
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT,
    senha TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS caixa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    tipo TEXT,
    categoria TEXT,
    descricao TEXT,
    valor REAL,
    data TEXT
)
""")

conn.commit()

# =========================
# 🔐 LOGIN
# =========================
st.title("💈 Sistema para Salão")

menu = st.sidebar.selectbox("Menu", ["Login", "Cadastro"])

if menu == "Cadastro":
    st.subheader("Criar conta")

    novo_usuario = st.text_input("Usuário")
    nova_senha = st.text_input("Senha", type="password")

    if st.button("Cadastrar"):
        cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (novo_usuario, nova_senha))
        conn.commit()
        st.success("Usuário criado!")

elif menu == "Login":
    st.subheader("Entrar")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND senha=?", (usuario, senha))
        user = cursor.fetchone()

        if user:
            st.session_state["usuario_id"] = user[0]
            st.success("Login realizado!")
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

# =========================
# 🏠 SISTEMA LOGADO
# =========================
if "usuario_id" in st.session_state:

    st.title("💰 Controle de Caixa")

    usuario_id = st.session_state["usuario_id"]

    # NOVO REGISTRO
    st.subheader("➕ Novo Registro")

    tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
    categoria = st.selectbox("Categoria", ["Corte", "Escova", "Barba", "Produto", "Despesa"])
    descricao = st.text_input("Descrição")
    valor = st.number_input("Valor", min_value=0.0, format="%.2f")

    if st.button("Salvar"):
        data = datetime.now().strftime("%Y-%m-%d")

        cursor.execute("""
        INSERT INTO caixa (usuario_id, tipo, categoria, descricao, valor, data)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (usuario_id, tipo, categoria, descricao, valor, data))

        conn.commit()
        st.success("Salvo!")
        st.rerun()

    # BUSCAR DADOS DO USUÁRIO
    df = pd.read_sql(f"SELECT * FROM caixa WHERE usuario_id = {usuario_id}", conn)

    if not df.empty:
        df["data"] = pd.to_datetime(df["data"])

        entradas = df[df["tipo"] == "Entrada"]["valor"].sum()
        saidas = df[df["tipo"] == "Saída"]["valor"].sum()

        st.subheader("📊 Resumo")
        st.metric("Lucro", f"R$ {entradas - saidas:.2f}")

        # REGISTROS
        st.subheader("📋 Registros")

        for index, row in df.iterrows():
            col1, col2, col3, col4 = st.columns([2,2,2,1])

            col1.write(row["categoria"])
            col2.write(row["descricao"])
            col3.write(f"R$ {row['valor']:.2f}")

            if col4.button("Excluir", key=row["id"]):
                cursor.execute("DELETE FROM caixa WHERE id=?", (row["id"],))
                conn.commit()
                st.rerun()

    if st.button("Sair"):
        del st.session_state["usuario_id"]
        st.rerun()