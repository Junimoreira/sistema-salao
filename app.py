import streamlit as st
import pandas as pd
import psycopg2
import os
import bcrypt
from datetime import datetime

# =========================
# 🎨 CONFIGURAÇÃO
# =========================
st.set_page_config(
    page_title="Sistema Salão",
    page_icon="💈",
    layout="wide"
)

st.markdown("""
<style>
.stMetric {
    background-color: #f0f2f6;
    padding: 10px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

cursor.execute("SELECT usuario, senha FROM usuarios")
usuarios = cursor.fetchall()

for u in usuarios:
    print(u)

# =========================
# 🔌 CONEXÃO COM BANCO
# =========================
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()


# Estado inicial
if "logado" not in st.session_state:
    st.session_state.logado = False

if "tela" not in st.session_state:
    st.session_state.tela = "login"


# ---------------- LOGIN ----------------
if not st.session_state.logado:
    st.title("🔐 Login")

    usuario = st.text_input("Usuário", key="login_user")
    senha = st.text_input("Senha", type="password", key="login_pass")

    if st.button("Entrar"):
        if usuario == "admin" and senha == "123":  # depois você liga no banco
            st.session_state.logado = True
            st.session_state.tela = "menu"
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")


# ---------------- MENU (após login) ----------------
else:
    st.sidebar.title("Menu")

    opcao = st.sidebar.radio(
        "Navegação",
        ["Dashboard", "Categorias", "Produtos", "Movimentações", "Sair"]
    )

    # -------- DASHBOARD --------
    if opcao == "Dashboard":
        st.title("📊 Dashboard")

    # -------- CATEGORIAS --------
    elif opcao == "Categorias":
        st.title("📂 Cadastro de Categorias")

        nome_categoria = st.text_input("Nome da categoria", key="cat_nome")

        if st.button("Salvar Categoria"):
            st.success("Categoria salva!")

    # -------- PRODUTOS --------
    elif opcao == "Produtos":
        st.title("📦 Cadastro de Produtos")

        nome = st.text_input("Nome do produto", key="prod_nome")
        custo = st.number_input("Custo", key="prod_custo")

        if st.button("Salvar Produto"):
            st.success("Produto salvo!")

    # -------- MOVIMENTAÇÕES --------
    elif opcao == "Movimentações":
        st.title("📋 Histórico de Movimentações")

    # -------- SAIR --------
    elif opcao == "Sair":
        st.session_state.logado = False
        st.session_state.tela = "login"
        st.rerun()