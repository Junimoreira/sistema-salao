import streamlit as st
import pandas as pd
import psycopg2
import os
import bcrypt
from datetime import datetime

st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)


st.set_page_config(
    page_title="Sistema Salão",
    page_icon="💈",
    layout="wide"
)



# =========================
# 🔌 CONEXÃO COM BANCO
# =========================
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# =========================
# 🧱 CRIAR TABELAS
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    usuario TEXT,
    senha TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS caixa (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER,
    tipo TEXT,
    categoria TEXT,
    descricao TEXT,
    valor REAL,
    data DATE
)
""")

conn.commit()

# =========================
# 🔐 LOGIN / CADASTRO
# =========================
st.markdown("## 💈 Sistema de Gestão para Salão")
st.markdown("---")

menu = st.sidebar.selectbox("Menu", ["Login", "Cadastro"])

# =========================
# 📝 CADASTRO
# =========================
if menu == "Cadastro":
    st.subheader("Criar conta")

    novo_usuario = st.text_input("Usuário")
    nova_senha = st.text_input("Senha", type="password")

    if st.button("Cadastrar"):
        senha_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt())

        cursor.execute(
            "INSERT INTO usuarios (usuario, senha) VALUES (%s, %s)",
            (novo_usuario, senha_hash.decode())
        )
        conn.commit()

        st.success("Usuário criado!")

# =========================
# 🔐 LOGIN
# =========================
elif menu == "Login":
    st.subheader("Entrar")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        try:
            cursor.execute(
                "SELECT * FROM usuarios WHERE usuario=%s",
                (usuario,)
            )
            user = cursor.fetchone()

            if user:
                senha_db = user[2]

                if senha_db.startswith("$2b$"):
                    if bcrypt.checkpw(senha.encode(), senha_db.encode()):
                        st.session_state["usuario_id"] = user[0]
                        st.success("Login realizado!")
                        st.rerun()
                    else:
                        st.error("Senha incorreta")
                else:
                    st.error("Usuário antigo precisa recadastrar senha")
            else:
                st.error("Usuário não encontrado")

        except Exception as e:
            st.error(f"Erro: {e}")

	st.sidebar.write(f"👤 Usuário ID: {usuario_id}")

# =========================
# 🏠 SISTEMA LOGADO
# =========================
if "usuario_id" in st.session_state:

    st.title("💰 Controle de Caixa")

    usuario_id = st.session_state["usuario_id"]

    # =========================
    # ➕ NOVO REGISTRO
    # =========================
    st.subheader("➕ Novo Registro")

    col1, col2 = st.columns(2)

	with col1:
    		tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
    		categoria = st.selectbox("Categoria", ["Corte", "Escova", "Barba", "Produto", "Despesa"])

	with col2:
    		descricao = st.text_input("Descrição")
    		valor = st.number_input("Valor", min_value=0.0, format="%.2f")

    if st.button("Salvar"):
        data = datetime.now().date()

        cursor.execute("""
        INSERT INTO caixa (usuario_id, tipo, categoria, descricao, valor, data)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (usuario_id, tipo, categoria, descricao, valor, data))

        conn.commit()
        st.success("Salvo!")
        st.rerun()

    # =========================
    # 📊 BUSCAR DADOS
    # =========================
    cursor.execute(
        "SELECT * FROM caixa WHERE usuario_id=%s",
        (usuario_id,)
    )
    dados = cursor.fetchall()

    colunas = ["id", "usuario_id", "tipo", "categoria", "descricao", "valor", "data"]
    df = pd.DataFrame(dados, columns=colunas)

    if not df.empty:

        entradas = df[df["tipo"] == "Entrada"]["valor"].sum()
        saidas = df[df["tipo"] == "Saída"]["valor"].sum()

        st.subheader("📊 Resumo")
        st.metric("Lucro", f"R$ {entradas - saidas:.2f}")

        # =========================
        # 📋 REGISTROS
        # =========================
        st.subheader("📋 Registros")

        for index, row in df.iterrows():
            col1, col2, col3 = st.columns(3)

		col1.metric("💰 Entradas", f"R$ {entradas:.2f}")
		col2.metric("💸 Saídas", f"R$ {saidas:.2f}")
		col3.metric("📈 Lucro", f"R$ {entradas - saidas:.2f}")

 		st.markdown("### 📋 Histórico de Movimentações")
    		st.markdown("---")

            if col4.button("Excluir", key=row["id"]):
                cursor.execute(
                    "DELETE FROM caixa WHERE id=%s",
                    (row["id"],)
                )
                conn.commit()
                st.rerun()

    else:
        st.info("Nenhum registro ainda.")

	st.subheader("📊 Receita por Categoria")

	grafico = df.groupby("categoria")["valor"].sum()
	st.bar_chart(grafico)

    # =========================
    # 🚪 LOGOUT
    # =========================
    if st.button("Sair"):
        del st.session_state["usuario_id"]
        st.rerun()