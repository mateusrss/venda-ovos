import streamlit as st
import pandas as pd
import copy

# ==== CONFIG ====
st.set_page_config(page_title="App Silvério", layout="centered")
st.title("App Silvério 🍫")

# ==== CREDENCIAIS ====
USER = "Paraiso"
PASSWORD = "12345"

def check_credentials(username, password):
    return username == USER and password == PASSWORD

# ==== DADOS FIXOS ====
itens_atuais = {
    "OVO FERRERO GRAN ROCHER 365G": {"normal": 70.66, "avariado": 59.10},
    "OVO FERRERO COLLECTION 241G": {"normal": 55.16, "avariado": 46.13},
    "OVO FERRERO ROCHER CAIXA 137,5G": {"normal": 35.09, "avariado": 29.35},
    "OVO KINDER MAXI SURPRESAS DOS DINOS 150G": {"normal": 51.24, "avariado": 41.38},
    "OVO KINDER MAXI SURPRESAS DAS FADAS 150G": {"normal": 51.24, "avariado": 41.38},
    "OVO FERRERO ROCHER DARK CAIXA 137,5G": {"normal": 35.09, "avariado": 29.35},
    "OVO FERRERO ROCHER 225G": {"normal": 55.16, "avariado": 46.13}
}

# ==== INICIALIZAR SESSION_STATE ====
st.session_state['itens'] = copy.deepcopy(itens_atuais)

# ==== LOGIN ====
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    username = st.text_input("Usuário:")
    password = st.text_input("Senha:", type='password')

    if st.button("Entrar"):
        if check_credentials(username, password):
            st.session_state['authenticated'] = True
            st.success("Login bem-sucedido!")
            st.balloons()
        else:
            st.error("Nome de usuário ou senha incorretos.")
else:
    # ==== MENU LATERAL ====
    menu = st.sidebar.radio("Menu", ["📋 Registrar Venda", "⚙️ Administrar Preços", "🔄 Resetar Preços", "🚪 Logout"])

    itens = st.session_state['itens']

    # ==== REGISTRAR VENDA ====
    if menu == "📋 Registrar Venda":
        st.title("📋 Registrar Venda")
        with st.form("form_venda"):
            funcionario = st.text_input("Cliente / Funcionario:")
            data = st.date_input("Data da venda:")
            venda = st.selectbox("Selecione a mercadoria:", list(itens.keys()))
            tipo = st.radio("Tipo do produto:", options=["normal", "avariado"], horizontal=True)
            quantidade = st.number_input("Quantidade:", min_value=1, step=1)
            submit = st.form_submit_button("Registrar Venda")

        if submit:
            preco_unitario = itens[venda][tipo]
            total = preco_unitario * quantidade

            st.markdown(f"💰 Preço unitário ({tipo}): R$ {preco_unitario:.2f}")
            st.markdown(f"### 🧾 Total da venda: R$ {total:.2f}")

            nome_arquivo = 'vendas_ovos.xlsx'
            try:
                df = pd.read_excel(nome_arquivo)
            except FileNotFoundError:
                df = pd.DataFrame(columns=[
                    'Data', 'Funcionário', 'Mercadoria', 'Tipo',
                    'Quantidade', 'Preço Unitário', 'Total'
                ])

            nova_venda = pd.DataFrame({
                'Data': [data.strftime("%d/%m/%Y")],
                'Funcionário': [funcionario],
                'Mercadoria': [venda],
                'Tipo': [tipo],
                'Quantidade': [quantidade],
                'Preço Unitário': [preco_unitario],
                'Total': [total]
            })

            df = pd.concat([df, nova_venda], ignore_index=True)
            df.to_excel(nome_arquivo, index=False)

            st.success("✅ Venda registrada com sucesso!")
            st.balloons()

        # Mostrar vendas registradas
        st.markdown("## 📊 Vendas Registradas")
        try:
            df = pd.read_excel("vendas_ovos.xlsx")
            st.dataframe(df)
        except:
            st.warning("Nenhuma venda registrada ainda.")

    # ==== ADMINISTRAR PREÇOS ====
    elif menu == "⚙️ Administrar Preços":
        st.title("⚙️ Administração de Preços")
        produto = st.selectbox("Selecione o produto:", list(itens.keys()))
        
        preco_normal = st.number_input("Preço Normal", value=itens[produto]["normal"], format="%.2f")
        preco_avariado = st.number_input("Preço Avariado", value=itens[produto]["avariado"], format="%.2f")

        if st.button("Salvar Preços"):
            itens[produto]["normal"] = preco_normal
            itens[produto]["avariado"] = preco_avariado
            st.success(f"Preços atualizados para: {produto}")
            st.session_state['itens'] = itens

        st.markdown("### 🧾 Tabela Atual de Preços")
        st.dataframe(pd.DataFrame(itens).T.rename(columns={"normal": "Normal (R$)", "avariado": "Avariado (R$)"}))

    # ==== RESETAR PREÇOS ====
    elif menu == "🔄 Resetar Preços":
        st.session_state['itens'] = itens_atuais.copy()
        st.success("Preços restaurados com sucesso!")
        st.experimental_rerun()

    # ==== LOGOUT ====
    elif menu == "🚪 Logout":
        st.session_state['authenticated'] = False
        st.success("Você foi desconectado.")
        st.balloons()
