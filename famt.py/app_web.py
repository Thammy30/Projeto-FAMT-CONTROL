import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Importa as funções originais sem alterá-las
from famtcontrol import inicializar_banco, _hash_senha, DB_NAME

st.set_page_config(page_title="FAMT Control", page_icon="💰", layout="centered")
inicializar_banco()

# Gerenciamento de sessão
if 'usuario_id' not in st.session_state:
    st.session_state.usuario_id = None
if 'email_logado' not in st.session_state:
    st.session_state.email_logado = None
if 'primeiro_acesso' not in st.session_state:
    st.session_state.primeiro_acesso = 0

st.title("💰 FAMT Control")
st.caption("Apresentação do Projeto - Squad FAMT")

# --- TELA DE LOGIN / CADASTRO ---
if st.session_state.usuario_id is None:
    aba1, aba2 = st.tabs(["🔑 Login", "📝 Cadastrar Usuário"])
    
    with aba1:
        st.subheader("Login no Sistema")
        email = st.text_input("E-mail", key="login_email").strip().lower()
        senha = st.text_input("Senha", type="password", key="login_senha").strip()
        
        if st.button("Entrar", use_container_width=True, type="primary"):
            conexao = sqlite3.connect(DB_NAME)
            cursor = conexao.cursor()
            cursor.execute("SELECT id, senha_hash, primeiro_acesso FROM Usuarios WHERE email = ?", (email,))
            usuario = cursor.fetchone()
            conexao.close()
            
            if usuario:
                u_id, hash_banco, prim_acesso = usuario
                
                # Valida o hash da senha digitada (atende LGPD / REQ-EXT-01)
                if _hash_senha(senha) == hash_banco:
                    st.session_state.usuario_id = u_id
                    st.session_state.email_logado = email
                    st.session_state.primeiro_acesso = prim_acesso
                    st.toast("🔒 Login efetuado!", icon="🔓")
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta.")
            else:
                st.error("❌ E-mail não encontrado.")
                
    with aba2:
        st.subheader("Criar Nova Conta")
        novo_email = st.text_input("E-mail para cadastro").strip().lower()
        if st.button("Cadastrar", use_container_width=True):
            if not novo_email or "@" not in novo_email:
                st.error("❌ Digite um e-mail válido.")
            else:
                conexao = sqlite3.connect(DB_NAME)
                cursor = conexao.cursor()
                try:
                    # Todo usuário novo nasce com primeiro_acesso = 1 (Obrigatório trocar senha)
                    cursor.execute("INSERT INTO Usuarios (email, senha_hash, primeiro_acesso) VALUES (?, ?, 1)", 
                                   (novo_email, _hash_senha("famt123")))
                    conexao.commit()
                    st.toast(f"📝 Usuário cadastrado!", icon="✅")
                    st.success(f"✅ Usuário cadastrado! A senha provisória é: famt123")
                except sqlite3.IntegrityError:
                    st.error("❌ Este e-mail já está cadastrado.")
                finally:
                    conexao.close()

# --- BLOQUEIO DE PRIMEIRO ACESSO: REDEFINIÇÃO DE SENHA OBRIGATÓRIA ---
elif st.session_state.primeiro_acesso == 1:
    st.subheader("⚠️ Redefinição de Senha Obrigatória")
    st.warning("Seu primeiro acesso foi detectado. Por motivos de segurança, você deve alterar sua senha provisória antes de continuar.")
    
    nova_senha = st.text_input("Digite sua NOVA senha", type="password")
    confirma_senha = st.text_input("Confirme sua NOVA senha", type="password")
    
    if st.button("Salvar Nova Senha", type="primary", use_container_width=True):
        if nova_senha == "famt123":
            st.error("❌ Erro: A nova senha não pode ser a senha provisória.")
        elif nova_senha != confirma_senha:
            st.error("❌ Erro: As senhas não coincidem.")
        elif len(nova_senha) < 4:
            st.error("❌ Erro: A senha deve ter pelo menos 4 caracteres.")
        else:
            # Salva o novo hash com segurança e derruba a flag de primeiro acesso
            novo_hash = _hash_senha(nova_senha)
            conexao = sqlite3.connect(DB_NAME)
            cursor = conexao.cursor()
            cursor.execute("""
                UPDATE Usuarios 
                SET senha_hash = ?, primeiro_acesso = 0 
                WHERE id = ?
            """, (novo_hash, st.session_state.usuario_id))
            conexao.commit()
            conexao.close()
            
            st.session_state.primeiro_acesso = 0
            st.toast("🔑 Senha definitiva salva!", icon="✅")
            st.success("✅ Senha definitiva salva com sucesso! Entrando no sistema...")
            st.rerun()

# --- TELA PRINCIPAL DO SISTEMA ---
else:
    st.sidebar.write(f"Logado como: **{st.session_state.email_logado}**")
    if st.sidebar.button("🚪 Sair do Sistema"):
        st.session_state.usuario_id = None
        st.session_state.email_logado = None
        st.session_state.primeiro_acesso = 0
        st.rerun()

    # Busca lançamentos
    conexao = sqlite3.connect(DB_NAME, timeout=10)
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT id, tipo, valor, categoria, descricao, data 
        FROM Transacoes 
        WHERE usuario_id = ? 
        ORDER BY data DESC;
    """, (st.session_state.usuario_id,))
    historico = cursor.fetchall()
    conexao.close()
    
    # Processamento matemático
    if historico:
        df_calculo = pd.DataFrame(historico, columns=["ID", "Tipo", "Valor", "Categoria", "Descrição", "Data"])
        total_receitas = float(df_calculo[df_calculo["Tipo"] == "Receita"]["Valor"].sum())
        total_despesas = float(df_calculo[df_calculo["Tipo"] == "Despesa"]["Valor"].sum())
    else:
        total_receitas = 0.0
        total_despesas = 0.0
        
    saldo_liquido = total_receitas - total_despesas
    
    # Abas
    aba_dash, aba_lancar, aba_extrato, aba_config = st.tabs(["📊 Painel", "➕ Lançar", "🧾 Extrato & Edição", "⚙️ Configurações"])
    
    with aba_dash:
        st.subheader("📊 Painel Financeiro")
        col1, col2, col3 = st.columns(3)
        col1.metric("Receitas", f"R$ {total_receitas:.2f}")
        col2.metric("Despesas", f"R$ {total_despesas:.2f}")
        
        if saldo_liquido < 0:
            col3.metric("Saldo Líquido", f"R$ {saldo_liquido:.2f}", delta="⚠️ SALDO DEVEDOR", delta_color="inverse")
            st.error("🚨 Alerta Contábil (REQ-BUS-01): Seu saldo está negativo! Cuidado com os gastos devedores.")
        else:
            col3.metric("Saldo Líquido", f"R$ {saldo_liquido:.2f}")
            st.success("💪 Tudo certo! Seu saldo está positivo.")

    with aba_lancar:
        st.subheader("➕ Adicionar Lançamento")
        tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
        valor = st.number_input("Valor (R$)", min_value=0.01, step=10.0)
        descricao = st.text_input("Descrição (Ex: Mensalidade UMC)")
        categoria = st.text_input("Categoria (Ex: Moradia, Alimentação)")

        if st.button("Salvar no Banco", type="primary"):
            data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conexao = sqlite3.connect(DB_NAME, timeout=10)
            cursor = conexao.cursor()
            cursor.execute("""
                INSERT INTO Transacoes (usuario_id, valor, tipo, data, descricao, categoria)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (st.session_state.usuario_id, valor, tipo, data_atual, descricao, categoria))
            conexao.commit()
            conexao.close()
            
            if tipo == "Receita":
                st.toast(f"🎉 Receita de R$ {valor:.2f} cadastrada com sucesso!", icon="💰")
            else:
                st.toast(f"💸 Despesa de R$ {valor:.2f} cadastrada com sucesso!", icon="📉")
                
            st.rerun()

    with aba_extrato:
        st.subheader("🧾 Histórico Contábil & Edição Direta")
        st.info("💡 **Dica para a Banca:** Dê dois cliques em qualquer célula abaixo para editar o texto/valor e aperte Enter para atualizar o banco de dados automaticamente!")
        
        if historico:
            df_visual = pd.DataFrame(historico, columns=["ID", "Tipo", "Valor (R$)", "Categoria", "Descrição", "Data/Hora"])
            df_editado = st.data_editor(df_visual, hide_index=True, disabled=["ID", "Data/Hora"], use_container_width=True)
            
            if not df_editado.equals(df_visual):
                conexao = sqlite3.connect(DB_NAME, timeout=10)
                cursor = conexao.cursor()
                for index, row in df_editado.iterrows():
                    cursor.execute("""
                        UPDATE Transacoes 
                        SET tipo = ?, valor = ?, categoria = ?, descricao = ?
                        WHERE id = ?
                    """, (row["Tipo"], float(row["Valor (R$)"]), row["Categoria"], row["Descrição"], int(row["ID"])))
                conexao.commit()
                conexao.close()
                st.toast("🔄 Alterações salvas no banco de dados!", icon="💾")
                st.rerun()
        else:
            st.info("Nenhum lançamento encontrado para este usuário.")

    with aba_config:
        st.subheader("⚙️ Gerenciamento do Banco de Dados")
        if st.button("🗑️ Limpar Todo o Histórico", type="secondary", use_container_width=True):
            conexao = sqlite3.connect(DB_NAME, timeout=10)
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM Transacoes WHERE usuario_id = ?;", (st.session_state.usuario_id,))
            conexao.commit()
            conexao.close()
            st.toast("💥 Banco de dados resetado com sucesso!", icon="🗑️")
            st.rerun()
