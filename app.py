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

    novo_usuario = st.text_input("Usuário", key="cad_usuario")
    nova_senha = st.text_input("Senha", type="password", key="cad_senha")

    if st.button("Cadastrar", key="btn_cadastrar"):
        if novo_usuario and nova_senha:
            senha_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt())

            cursor.execute(
                "INSERT INTO usuarios (usuario, senha) VALUES (%s, %s)",
                (novo_usuario, senha_hash.decode())
            )
            conn.commit()

            st.success("Usuário criado!")
        else:
            st.warning("Preencha todos os campos")

# =========================
# 🔐 LOGIN
# =========================
elif menu == "Login":
    st.subheader("Entrar")

    usuario = st.text_input("Usuário", key="login_usuario")
    senha = st.text_input("Senha", type="password", key="login_senha")

    if st.button("Entrar", key="btn_login"):
        try:
            cursor.execute(
                "SELECT * FROM usuarios WHERE usuario=%s",
                (usuario,)
            )
            user = cursor.fetchone()

            if user:
                senha_db = user[2]

                if bcrypt.checkpw(senha.encode(), senha_db.encode()):
                    st.session_state["usuario_id"] = user[0]
                    st.success("Login realizado!")
                    st.rerun()
                else:
                    st.error("Senha incorreta")
            else:
                st.error("Usuário não encontrado")

        except Exception as e:
            st.error(f"Erro: {e}")

# =========================
# 🏠 SISTEMA LOGADO
# =========================
if "usuario_id" in st.session_state:

    usuario_id = st.session_state["usuario_id"]

    st.sidebar.write(f"👤 Usuário ID: {usuario_id}")

    st.title("💰 Controle de Caixa")

    # =========================
    # ➕ NOVO REGISTRO
    # =========================
    st.subheader("➕ Novo Registro")

    col1, col2 = st.columns(2)

    with col1:
        tipo = st.selectbox("Tipo", ["Entrada", "Saída"], key="tipo")
        categoria = st.selectbox(
            "Categoria",
            ["Corte", "Escova", "Barba", "Produto", "Despesa"],
            key="categoria"
        )

    with col2:
        descricao = st.text_input("Descrição", key="desc")
        valor = st.number_input("Valor", min_value=0.0, format="%.2f", key="valor")

    if st.button("Salvar", key="btn_salvar"):
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
        col1, col2, col3 = st.columns(3)

        col1.metric("💰 Entradas", f"R$ {entradas:.2f}")
        col2.metric("💸 Saídas", f"R$ {saidas:.2f}")
        col3.metric("📈 Lucro", f"R$ {entradas - saidas:.2f}")

        # =========================
        # 📋 HISTÓRICO
        # =========================
        st.subheader("📋 Histórico de Movimentações")
        st.markdown("---")

        for index, row in df.iterrows():
            c1, c2, c3, c4 = st.columns(4)

            c1.write(row["descricao"])
            c2.write(row["categoria"])
            c3.write(f"R$ {row['valor']:.2f}")

            if c4.button("Excluir", key=f"del_{row['id']}"):
                cursor.execute(
                    "DELETE FROM caixa WHERE id=%s",
                    (row["id"],)
                )
                conn.commit()
                st.rerun()

        # =========================
        # 📊 GRÁFICO
        # =========================
        st.subheader("📊 Receita por Categoria")

        grafico = df.groupby("categoria")["valor"].sum()
        st.bar_chart(grafico)

    else:
        st.info("Nenhum registro ainda.")

    # =========================
    # 🚪 LOGOUT
    # =========================
    if st.button("Sair", key="btn_sair"):
        del st.session_state["usuario_id"]
        st.rerun()
