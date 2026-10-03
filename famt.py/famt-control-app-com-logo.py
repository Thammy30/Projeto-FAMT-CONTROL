import streamlit as st
import sqlite3
from pathlib import Path
import pandas as pd
import hashlib
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# =============================================================================
# LOGO E CONFIGURAÇÃO DO BANCO DE DADOS
# =============================================================================
LOGO_PATH = Path(__file__).resolve().parent / "Logo Fintech FAMT Control.png"

def logo_html(css_class="system-logo"):
    """Retorna a logo em base64 para funcionar dentro do HTML do Streamlit."""
    import base64
    if not LOGO_PATH.exists():
        return ""
    data = base64.b64encode(LOGO_PATH.read_bytes()).decode("utf-8")
    return f'<img class="{css_class}" src="data:image/png;base64,{data}" alt="FAMT Control">'

DB_NAME = "famt_control.db"

def _hash_senha(senha: str) -> str:
    """Gera hash SHA-256 seguro para a senha."""
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()

def inicializar_banco():
    """Cria o esquema do banco de dados SQLite v2 se não existir."""
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Tabela de Usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            primeiro_acesso INTEGER DEFAULT 1 CHECK (primeiro_acesso IN (0, 1))
        );
    """)
    
    # Tabela de Transações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            valor REAL NOT NULL CHECK (valor > 0),
            tipo TEXT NOT NULL CHECK (tipo IN ('Receita', 'Despesa')),
            data TEXT NOT NULL,
            descricao TEXT NOT NULL,
            categoria TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES Usuarios(id) ON DELETE CASCADE
        );
    """)
    
    # Usuário padrão para testes rápidos da banca
    cursor.execute("SELECT id FROM Usuarios WHERE email = 'thamirys@umc.edu.br';")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO Usuarios (email, senha_hash, primeiro_acesso)
            VALUES ('thamirys@umc.edu.br', ?, 0);
        """, (_hash_senha("famt123"),))
        
        # Inserir alguns dados de demonstração
        u_id = cursor.lastrowid
        demo_data = [
            (u_id, 1500.00, 'Receita', '2026-09-01 10:00:00', 'Bolsa de Estágio UMC', 'Salário'),
            (u_id, 320.00, 'Despesa', '2026-09-03 12:30:00', 'Mensalidade Faculdade', 'Educação'),
            (u_id, 150.00, 'Despesa', '2026-09-05 14:00:00', 'Supermercado', 'Alimentação'),
            (u_id, 80.00, 'Despesa', '2026-09-07 18:20:00', 'Recarga Bilhete Único', 'Transporte'),
            (u_id, 52.00, 'Despesa', '2026-09-10 09:15:00', 'Conta de Luz', 'Contas')
        ]
        cursor.executemany("""
            INSERT INTO Transacoes (usuario_id, valor, tipo, data, descricao, categoria)
            VALUES (?, ?, ?, ?, ?, ?);
        """, demo_data)
        
    conexao.commit()
    conexao.close()

# Inicializa o banco ao rodar o app
inicializar_banco()

# =============================================================================
# CONFIGURAÇÃO DE PÁGINA E CSS CUSTOMIZADO (DASHBOARD PURPLE DARK MODE)
# =============================================================================
st.set_page_config(
    page_title="FAMT CONTROL - Dashboard",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    background: #0D0E1D;
    color: #F4F2FF;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

[data-testid="stHeader"] {
    background: #0D0E1D !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111126 0%, #14132D 100%) !important;
    border-right: 1px solid #2C2B4A !important;
    min-width: 248px !important;
    width: 248px !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 12px;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 11px;
    padding: 6px 10px 13px 10px;
}

.brand-bag, .dashboard-logo, .promo-bag {
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 18px;
    background: linear-gradient(145deg, #8A42FF, #5C25D9);
    box-shadow: 0 8px 24px rgba(124, 77, 255, .30);
}

.brand-bag {
    width: 42px;
    height: 42px;
    font-size: 25px;
}

.brand-bag-img {
    width: 42px;
    height: 42px;
    object-fit: cover;
    border-radius: 18px;
    display: block;
    box-shadow: 0 8px 24px rgba(124, 77, 255, .30);
}

.dashboard-logo-img {
    width: 64px;
    height: 64px;
    object-fit: cover;
    border-radius: 22px;
    display: block;
    box-shadow: 0 8px 24px rgba(124, 77, 255, .30);
}

.promo-bag-img {
    width: 40px;
    height: 40px;
    object-fit: cover;
    border-radius: 18px;
    display: block;
}

.brand-title {
    font-size: 20px;
    font-weight: 800;
    color: #FFFFFF;
}

.brand-title span, .dashboard-name span, .promo-title span {
    color: #A36BFF;
}

.sidebar-divider {
    height: 1px;
    background: #292945;
    margin: 3px 0 15px 0;
}

[data-testid="stSidebar"] .stRadio > label {
    display: none;
}

[data-testid="stSidebar"] .stRadio [role="radiogroup"] {
    gap: 7px;
}

[data-testid="stSidebar"] .stRadio [role="radio"] {
    background: transparent;
    border-radius: 10px;
    padding: 10px 12px;
    color: #D2CEE8;
    border: 1px solid transparent;
    font-size: 14px;
}

[data-testid="stSidebar"] .stRadio [role="radio"]:hover {
    background: #211D43;
    color: #FFFFFF;
}

[data-testid="stSidebar"] .stRadio [role="radio"][aria-checked="true"] {
    background: linear-gradient(90deg, #7141D5, #6740C9);
    color: #FFFFFF;
    box-shadow: 0 5px 18px rgba(112, 65, 213, .25);
}

.sidebar-spacer {
    min-height: 250px;
}

.sidebar-tip {
    padding: 8px 10px 5px 10px;
    color: #BFB9D8;
}

.tip-icon {
    color: #A56BFF;
    font-size: 30px;
    margin-bottom: 5px;
}

.tip-title {
    font-size: 13px;
    line-height: 1.5;
}

.tip-line {
    width: 30px;
    height: 2px;
    background: #A56BFF;
    margin-top: 12px;
}

.sidebar-user {
    color: #8F89AA;
    font-size: 10px;
    padding: 18px 10px 5px 10px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.top-header {
    min-height: 58px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #292945;
    margin: -5px 0 20px 0;
    padding: 0 0 14px 0;
}

.welcome {
    display: flex;
    align-items: center;
    gap: 10px;
}

.welcome-icon {
    font-size: 25px;
}

.greeting-title {
    color: #FFFFFF;
    font-size: 17px;
    font-weight: 700;
    margin: 0;
}

.greeting-subtitle {
    color: #8E8AA9;
    font-size: 11px;
    margin-top: 3px;
}

.top-actions {
    display: flex;
    align-items: center;
    gap: 20px;
}

.dashboard-title-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 8px 0 20px 0;
}

.dashboard-brand {
    display: flex;
    align-items: center;
    gap: 13px;
}

.dashboard-logo {
    width: 64px;
    height: 64px;
    font-size: 34px;
    border-radius: 22px;
}

.dashboard-name {
    font-size: 27px;
    font-weight: 800;
    letter-spacing: -1px;
}

.dashboard-subtitle {
    color: #A49DBE;
    font-size: 14px;
    margin-top: 1px;
}

.date-box {
    min-width: 260px;
    display: flex;
    align-items: center;
    gap: 11px;
    background: #15162B;
    border: 1px solid #343555;
    border-radius: 13px;
    padding: 11px 15px;
}

.date-icon {
    color: #F2F0FF;
    font-size: 24px;
}

.date-label {
    color: #F0EDF9;
    font-size: 13px;
    font-weight: 600;
}

.date-value {
    color: #8883A3;
    font-size: 10px;
    margin-top: 3px;
}


/* Styling for st.popover buttons to match v10 date-box */
div[data-testid="stPopover"] button {
    background: #15162B !important;
    border: 1px solid #343555 !important;
    border-radius: 13px !important;
    color: #F0EDF9 !important;
    font-weight: 600 !important;
    padding: 10px 16px !important;
    font-size: 13px !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stPopover"] button:hover {
    border-color: #7C3AED !important;
    color: #FFFFFF !important;
    background: #1C1A3C !important;
}

.date-chevron {
    margin-left: auto;
    color: #BEB9D5;
}

.metric-card {
    min-height: 112px;
    background: linear-gradient(145deg, #17192F, #15162A);
    border: 1px solid #333555;
    border-radius: 13px;
    padding: 14px 15px;
    box-shadow: 0 8px 25px rgba(0,0,0,.18);
}

.metric-icon {
    width: 37px;
    height: 37px;
    border-radius: 11px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 8px;
}

.metric-icon.receita { background: rgba(67,198,166,.20); color: #43C6A6; }
.metric-icon.despesa { background: rgba(239,71,111,.20); color: #EF476F; }
.metric-icon.saldo { background: rgba(124,77,255,.22); color: #AA7CFF; }
.metric-icon.meta { background: rgba(150,91,255,.22); color: #B27EFF; }

.metric-label {
    color: #D6D2E7;
    font-size: 12px;
    font-weight: 500;
    margin-top: -45px;
    margin-left: 49px;
    padding-top: 2px;
}

.metric-value {
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 800;
    margin: 4px 0 4px 49px;
}

.metric-change {
    font-size: 10px;
    font-weight: 600;
    margin-left: 49px;
}

.metric-change.positive { color: #43C6A6; }
.metric-change.negative { color: #EF476F; }
.metric-change.purple { color: #B08AFF; }

.metric-period {
    color: #716C88;
    font-size: 9px;
    margin-left: 49px;
    margin-top: 2px;
}

.progress-wrap {
    display: flex;
    align-items: center;
    gap: 9px;
    margin: 8px 0 0 49px;
}

.progress-track {
    flex: 1;
    height: 8px;
    background: #313352;
    border-radius: 20px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #773BFF, #A467FF);
    border-radius: 20px;
}

.progress-wrap span {
    color: #D8D3EA;
    font-size: 10px;
}

.section-gap { height: 14px; }
.section-gap-small { height: 8px; }

.panel-title {
    height: 42px;
    display: flex;
    align-items: center;
    gap: 9px;
    color: #EDEAF8;
    font-size: 14px;
    font-weight: 700;
    padding: 0 13px;
    border: 1px solid #303252;
    border-bottom: none;
    border-radius: 13px 13px 0 0;
    background: #15162B;
}

.title-icon {
    color: #BE86FF;
    font-size: 19px;
}

.legend {
    margin-left: auto;
    color: #B1ABC8;
    font-size: 9px;
    font-weight: 500;
}

.legend-dot {
    width: 9px;
    height: 9px;
    display: inline-block;
    border-radius: 50%;
    margin: 0 4px 0 7px;
}

.receita-dot { background: #43C6A6; }
.despesa-dot { background: #7C4DFF; }

.stPlotlyChart {
    border: 1px solid #303252;
    border-top: none;
    border-radius: 0 0 13px 13px;
    background: #15162B;
    padding: 0 5px 4px 5px;
}

.recent-item {
    min-height: 49px;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 7px 8px;
    background: #15162B;
    border: 1px solid #303252;
    border-bottom: none;
}

.recent-item:last-child {
    border-bottom: 1px solid #303252;
    border-radius: 0 0 13px 13px;
}

.recent-icon {
    width: 29px;
    height: 29px;
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    flex: 0 0 29px;
}

.recent-income {
    color: #43C6A6;
    background: rgba(67,198,166,.15);
}

.recent-expense {
    color: #EF476F;
    background: rgba(239,71,111,.13);
}

.recent-info {
    min-width: 0;
    flex: 1;
}

.recent-name {
    color: #ECEAF5;
    font-size: 10px;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.recent-meta {
    color: #716C88;
    font-size: 8px;
    margin-top: 2px;
}

.recent-value {
    font-size: 9px;
    font-weight: 700;
    white-space: nowrap;
}

.stButton > button {
    background: #17182D;
    color: #C8C3DF;
    border: 1px solid #39385B;
    border-radius: 11px;
    min-height: 43px;
    font-size: 12px;
    font-weight: 600;
    box-shadow: none;
}

.stButton > button:hover {
    border-color: #8B55FF;
    color: #FFFFFF;
    background: #211D42;
}

div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(90deg, #7A3FFF, #914EFF);
    border-color: #8C51FF;
    color: white;
    box-shadow: 0 7px 20px rgba(124, 63, 255, .25);
}

/* Estilo customizado para os botões secundários "Ver todas ->" funcionais */
div[data-testid="stButton"] button[kind="secondary"] {
    background: transparent !important;
    border: none !important;
    color: #A970FF !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    padding: 0 !important;
    min-height: auto !important;
    height: auto !important;
    box-shadow: none !important;
    float: right !important;
}

div[data-testid="stButton"] button[kind="secondary"]:hover {
    color: #FFFFFF !important;
    text-decoration: underline !important;
    background: transparent !important;
}

.bottom-panel {
    min-height: 190px;
    background: #15162B;
    border: 1px solid #303252;
    border-radius: 13px;
    padding: 14px;
}

.bottom-title {
    color: #EAE7F7;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 13px;
}

.bottom-title > span {
    color: #B17BFF;
    font-size: 19px;
    margin-right: 8px;
}

.goal-card {
    display: flex;
    align-items: center;
    gap: 11px;
    background: #1B1D38;
    border: 1px solid #303252;
    border-radius: 10px;
    padding: 11px;
}

.goal-icon {
    width: 45px;
    height: 45px;
    border-radius: 10px;
    background: #292B50;
    color: #B49CFF;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 23px;
}

.goal-info {
    flex: 1;
}

.goal-name {
    color: #EEEAF8;
    font-size: 11px;
    font-weight: 600;
}

.goal-amount {
    color: #B9B2D0;
    font-size: 9px;
    margin-top: 4px;
}

.goal-progress {
    height: 8px;
    background: #333556;
    border-radius: 20px;
    overflow: hidden;
    margin-top: 7px;
}

.goal-progress div {
    height: 100%;
    background: linear-gradient(90deg, #763BFF, #9E63FF);
    border-radius: 20px;
}

.goal-percent {
    color: #E8E4F5;
    font-size: 10px;
    font-weight: 600;
}

.goal-foot {
    color: #817A9B;
    font-size: 9px;
    margin-top: 11px;
}

.alert-box {
    min-height: 50px;
    border-radius: 10px;
    padding: 9px;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    font-size: 9px;
}

.alert-box.warning {
    background: rgba(188, 88, 69, .20);
    border: 1px solid rgba(231, 111, 88, .32);
    color: #F18A73;
}

.alert-box.success {
    background: rgba(39, 156, 139, .16);
    border: 1px solid rgba(55, 198, 177, .40);
    color: #4CCCB6;
}

.alert-symbol {
    width: 24px;
    height: 24px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255,255,255,.07);
    font-weight: 800;
    font-size: 13px;
}

.alert-box span {
    color: #B7B1C9;
    font-size: 8px;
}

.alert-arrow {
    margin-left: auto;
    font-size: 18px;
}

.brand-promo {
    position: relative;
    overflow: hidden;
    background: linear-gradient(145deg, #1C1A3C, #17152E);
    border: 1px solid #3B315F;
    border-radius: 14px;
    padding: 20px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 18px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}

.brand-promo:after {
    content: "";
    position: absolute;
    width: 180px;
    height: 120px;
    right: -30px;
    top: -40px;
    border-radius: 50%;
    border: 30px solid rgba(123, 64, 255, .15);
    pointer-events: none;
}

.promo-content-left {
    display: flex;
    align-items: center;
    gap: 16px;
}

.promo-bag {
    width: 46px;
    height: 46px;
    font-size: 28px;
    margin-bottom: 0;
    display: flex;
    align-items: center;
    justify-content: center;
}

.promo-bag-img {
    width: 46px;
    height: 46px;
    object-fit: contain;
}

.promo-text-group {
    display: flex;
    flex-direction: column;
}

.promo-title {
    color: white;
    font-size: 18px;
    font-weight: 800;
}

.promo-title span {
    color: #7C3AED;
}

.promo-text {
    color: #B4AECA;
    font-size: 13px;
    line-height: 1.4;
    margin-top: 2px;
}

.promo-chart {
    color: #A86CFF;
    font-size: 38px;
    font-weight: bold;
    margin-top: 0;
    padding-right: 15px;
}

.page-heading {
    color: #FFFFFF;
    font-size: 25px;
    font-weight: 800;
    margin: 12px 0 4px 0;
}

.page-caption {
    color: #8E88A8;
    font-size: 12px;
    margin-bottom: 22px;
}

.large-panel {
    min-height: 240px;
}

.stTextInput input,
.stNumberInput input,
[data-baseweb="select"] > div {
    background: #17182D !important;
    color: #F5F2FF !important;
    border-color: #353656 !important;
}

label {
    color: #CFC9E3 !important;
}

[data-testid="stDataEditor"] {
    border: 1px solid #343555;
    border-radius: 12px;
    overflow: hidden;
}

.stAlert {
    border-radius: 10px;
}

.login-header-famt {
    text-align: center;
    padding: 10px 0 24px 0;
}

.login-logo-famt {
    width: 82px;
    height: 82px;
    margin: 0 auto 16px auto;
    border-radius: 24px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 15px 35px rgba(139, 92, 246, 0.30);
    border: 1px solid rgba(255,255,255,0.10);
    background: transparent;
}

.login-logo-famt img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}

.title-famt {
    text-align: center;
    color: #FFFFFF;
    font-size: 34px;
    font-weight: 800;
    letter-spacing: -1.5px;
    line-height: 1.1;
}

.title-famt span { color: #9B63FF; }

.subtitle-famt {
    text-align: center;
    color: #94A3B8;
    font-size: 14px;
    margin-top: 8px;
    margin-bottom: 10px;
}

.login-footer {
    text-align: center;
    color: #64748B;
    font-size: 11px;
    margin-top: 22px;
    padding-bottom: 10px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =============================================================================
# GERENCIAMENTO DE SESSÃO
# =============================================================================
if 'usuario_id' not in st.session_state:
    st.session_state.usuario_id = None
if 'email_logado' not in st.session_state:
    st.session_state.email_logado = None
if 'primeiro_acesso' not in st.session_state:
    st.session_state.primeiro_acesso = 0

# =============================================================================
# TELA DE LOGIN / CADASTRO
# =============================================================================
if st.session_state.usuario_id is None:
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_center:
        logo_path = Path(__file__).resolve().parent / "Logo Fintech FAMT Control.png"
        st.markdown('<div class="login-header-famt">', unsafe_allow_html=True)
        
        if logo_path.exists():
            import base64
            logo_data = base64.b64encode(logo_path.read_bytes()).decode("utf-8")
            st.markdown(
                f'<div class="login-logo-famt"><img src="data:image/png;base64,{logo_data}" alt="FAMT Control"></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown('<div class="login-logo-famt">💰</div>', unsafe_allow_html=True)
            
        st.markdown("""
            <div class="title-famt">
                FAMT <span>CONTROL</span>
            </div>
            <div class="subtitle-famt">
                Seu dinheiro sob controle • Squad FAMT
            </div>
            </div>
        """, unsafe_allow_html=True)
        
        aba1, aba2 = st.tabs(["🔑 Login no Sistema", "📝 Criar Nova Conta"])
        
        with aba1:
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("E-mail pessoal", key="login_email").strip().lower()
            senha = st.text_input("Senha de acesso", type="password", key="login_senha").strip()
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Entrar no FAMT CONTROL", use_container_width=True, type="primary"):
                if not email or not senha:
                    st.error("❌ Por favor, preencha todos os campos.")
                else:
                    conexao = sqlite3.connect(DB_NAME)
                    cursor = conexao.cursor()
                    cursor.execute("SELECT id, senha_hash, primeiro_acesso FROM Usuarios WHERE email = ?", (email,))
                    usuario = cursor.fetchone()
                    conexao.close()
                    
                    if usuario:
                        u_id, hash_banco, prim_acesso = usuario
                        if _hash_senha(senha) == hash_banco:
                            st.session_state.usuario_id = u_id
                            st.session_state.email_logado = email
                            st.session_state.primeiro_acesso = prim_acesso
                            st.toast("🔓 Login efetuado com sucesso!", icon="✅")
                            st.rerun()
                        else:
                            st.error("❌ Senha incorreta. Tente novamente.")
                    else:
                        st.error("❌ E-mail não encontrado no sistema.")
                        
        with aba2:
            st.markdown("<br>", unsafe_allow_html=True)
            novo_email = st.text_input("E-mail para cadastro", key="cad_email").strip().lower()
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Cadastrar Conta", use_container_width=True):
                if not novo_email or "@" not in novo_email:
                    st.error("❌ Digite um e-mail válido.")
                else:
                    conexao = sqlite3.connect(DB_NAME)
                    cursor = conexao.cursor()
                    try:
                        cursor.execute("INSERT INTO Usuarios (email, senha_hash, primeiro_acesso) VALUES (?, ?, 1)",
                                       (novo_email, _hash_senha("famt123")))
                        conexao.commit()
                        st.toast("📝 Usuário cadastrado com sucesso!", icon="✅")
                        st.success("✅ Conta criada! A sua senha provisória é: **famt123**")
                    except sqlite3.IntegrityError:
                        st.error("❌ Este e-mail já está cadastrado no banco de dados.")
                    finally:
                        conexao.close()
                        
        st.markdown('<div class="login-footer">FAMT CONTROL • Gestão Financeira Pessoal</div>', unsafe_allow_html=True)

# =============================================================================
# BLOQUEIO DE PRIMEIRO ACESSO
# =============================================================================
elif st.session_state.primeiro_acesso == 1:
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.warning("⚠️ **Primeiro Acesso Detectado (Conformidade LGPD)**")
        st.info("Por motivos de segurança, é obrigatório alterar sua senha provisória antes de acessar o painel financeiro.")
        
        nova_senha = st.text_input("Digite sua NOVA senha", type="password")
        confirma_senha = st.text_input("Confirme sua NOVA senha", type="password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Salvar Nova Senha Definitiva", use_container_width=True, type="primary"):
            if nova_senha == "famt123":
                st.error("❌ A nova senha não pode ser igual à senha provisória.")
            elif nova_senha != confirma_senha:
                st.error("❌ As senhas digitadas não coincidem.")
            elif len(nova_senha) < 4:
                st.error("❌ A senha deve conter pelo menos 4 caracteres.")
            else:
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
                st.toast("🔑 Senha salva com sucesso!", icon="✅")
                st.success("✅ Senha atualizada! Acessando o painel...")
                st.rerun()

# =============================================================================
# TELA PRINCIPAL DO SISTEMA (DASHBOARD COMPLETO)
# =============================================================================
else:
    # --- SIDEBAR / NAVEGAÇÃO PRINCIPAL ---
    if "menu" not in st.session_state:
        st.session_state.menu = "Painel"

    def navegar_para(destino):
        st.session_state.menu = destino
        st.session_state.nav_radio_key = destino

    with st.sidebar:
        st.markdown(f"""
            <div class="sidebar-brand">
                {logo_html("brand-bag-img") if LOGO_PATH.exists() else '<div class="brand-bag">💰</div>'}
                <div>
                    <div class="brand-title">FAMT <span>CONTROL</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
        
        opcoes_menu = ["Painel", "Lançar", "Extrato e Edição", "Metas", "Gráficos", "Notificações", "Alertas e Dicas", "Configurações"]
        if st.session_state.menu not in opcoes_menu:
            st.session_state.menu = "Painel"
            
        idx_menu = opcoes_menu.index(st.session_state.menu)

        def ao_mudar_radio():
            st.session_state.menu = st.session_state.nav_radio_key

        menu = st.radio(
            "Navegação",
            opcoes_menu,
            index=idx_menu,
            key="nav_radio_key",
            on_change=ao_mudar_radio,
            label_visibility="collapsed"
        )
        
        st.markdown("<div class='sidebar-spacer'></div>", unsafe_allow_html=True)
        
        st.markdown("""
            <div class="sidebar-tip">
                <div class="tip-icon">♧</div>
                <div class="tip-title">Pequenos hábitos geram<br>grandes conquistas!</div>
                <div class="tip-line"></div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='sidebar-user'>👤 " + st.session_state.email_logado + "</div>", unsafe_allow_html=True)
        
        if st.button("Sair", use_container_width=True):
            st.session_state.usuario_id = None
            st.session_state.email_logado = None
            st.session_state.primeiro_acesso = 0
            st.rerun()

    # --- GERENCIAMENTO DE DATAS E CALENDÁRIO ---
    agora = datetime.now()
    import calendar
    primeiro_dia_mes_atual = agora.replace(day=1)
    ultimo_dia_num_atual = calendar.monthrange(agora.year, agora.month)[1]
    ultimo_dia_mes_atual = agora.replace(day=ultimo_dia_num_atual)

    # Inicializa período selecionado na session_state (padrão: mês atual)
    if "data_inicio_sel" not in st.session_state:
        st.session_state.data_inicio_sel = primeiro_dia_mes_atual.date()
    if "data_fim_sel" not in st.session_state:
        st.session_state.data_fim_sel = ultimo_dia_mes_atual.date()

    d_inicio = st.session_state.data_inicio_sel
    d_fim = st.session_state.data_fim_sel

    def moeda(valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # --- CONSULTA DE DADOS NO SQLITE ---
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

    if historico:
        df_bruto = pd.DataFrame(historico, columns=["ID", "Tipo", "Valor", "Categoria", "Descrição", "Data"])
        df_bruto["Data_dt"] = pd.to_datetime(df_bruto["Data"], errors='coerce')
        
        # Filtra pelo período selecionado no calendário
        dt_ini_pd = pd.to_datetime(d_inicio)
        dt_fim_pd = pd.to_datetime(d_fim) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        
        mask_periodo = (df_bruto["Data_dt"] >= dt_ini_pd) & (df_bruto["Data_dt"] <= dt_fim_pd)
        df_calculo = df_bruto[mask_periodo].copy()
        
        historico_filtrado = df_calculo[["ID", "Tipo", "Valor", "Categoria", "Descrição", "Data"]].values.tolist() if not df_calculo.empty else []
        
        total_receitas = float(df_calculo.loc[df_calculo["Tipo"] == "Receita", "Valor"].sum()) if not df_calculo.empty else 0.0
        total_despesas = float(df_calculo.loc[df_calculo["Tipo"] == "Despesa", "Valor"].sum()) if not df_calculo.empty else 0.0
    else:
        df_calculo = pd.DataFrame(columns=["ID", "Tipo", "Valor", "Categoria", "Descrição", "Data"])
        historico_filtrado = []
        total_receitas = 0.0
        total_despesas = 0.0

    saldo_liquido = total_receitas - total_despesas
    
    # Meta do mês armazenada em session_state para permitir edição
    if "meta_mes" not in st.session_state:
        st.session_state.meta_mes = 1000.00
        
    meta_mes = st.session_state.meta_mes
    progresso_meta = min(100, int((saldo_liquido / meta_mes) * 100)) if saldo_liquido > 0 and meta_mes > 0 else 0

    # --- CABEÇALHO SUPERIOR ---
    col_welcome, col_notification = st.columns([8, 1])
    with col_welcome:
        st.markdown("""
            <div class="top-header">
                <div class="welcome">
                    <div class="welcome-icon">👋</div>
                    <div>
                        <div class="greeting-title">Olá, Seja Bem-Vindo(a)!</div>
                        <div class="greeting-subtitle">Aqui está um resumo da sua vida financeira.</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    # --- NOTIFICAÇÕES DINÂMICAS ---
    if "notificacoes_lidas" not in st.session_state:
        st.session_state.notificacoes_lidas = False

    lista_notificacoes = []
    if saldo_liquido < 0:
        lista_notificacoes.append({
            "titulo": "🚨 Saldo Devedor",
            "texto": f"Seu saldo está em {moeda(saldo_liquido)}. Recomenda-se conter despesas."
        })
    if not df_calculo.empty:
        ultima_trans = df_calculo.iloc[0]
        tipo_lbl = "Receita" if ultima_trans["Tipo"] == "Receita" else "Despesa"
        lista_notificacoes.append({
            "titulo": f"📌 Último Lançamento ({tipo_lbl})",
            "texto": f"{ultima_trans['Descrição']} - {moeda(float(ultima_trans['Valor']))}"
        })
    else:
        lista_notificacoes.append({
            "titulo": "ℹ️ Bem-vindo ao FAMT Control",
            "texto": "Cadastre suas primeiras movimentações na aba 'Lançar'."
        })

    qtd_notif = 0 if st.session_state.notificacoes_lidas else len(lista_notificacoes)
    badge_sininho = f"🔔 {qtd_notif}" if qtd_notif > 0 else "🔔"

    with col_notification:
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        with st.popover(badge_sininho):
            st.markdown("### 🔔 Notificações")
            
            # Sempre exibe as notificações mesmo se marcadas como lidas
            for notif in lista_notificacoes:
                status_tag = " <span style='color:#10B981; font-size:11px; font-weight:600;'>(Nova)</span>" if not st.session_state.notificacoes_lidas else " <span style='color:#94A3B8; font-size:11px;'>(Lida)</span>"
                st.markdown(f"**{notif['titulo']}**{status_tag}<br>{notif['texto']}", unsafe_allow_html=True)
                st.markdown("<div style='margin: 8px 0; border-bottom: 1px solid #282B45;'></div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if not st.session_state.notificacoes_lidas:
                if st.button("✓ Marcar como lidas", key="btn_limpar_notif", use_container_width=True):
                    st.session_state.notificacoes_lidas = True
                    st.toast("✅ Notificações marcadas como lidas!")
                    st.rerun()
            else:
                st.caption("✓ Todas as notificações estão marcadas como lidas.")
            
            st.button("🔍 Ver todas as notificações →", key="btn_ver_todas_notif", type="secondary", use_container_width=True, on_click=navegar_para, args=("Notificações",))

    # --- CABEÇALHO DA MARCA + PERÍODO COM CALENDÁRIO ---
    col_brand, col_date = st.columns([3.5, 1.2])
    with col_brand:
        st.markdown(f"""
            <div class="dashboard-brand">
                {logo_html("dashboard-logo-img") if LOGO_PATH.exists() else '<div class="dashboard-logo">💰</div>'}
                <div>
                    <div class="dashboard-name">FAMT <span>Control</span></div>
                    <div class="dashboard-subtitle">Seu dinheiro sob controle.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_date:
        st.markdown("<div style='height: 2px;'></div>", unsafe_allow_html=True)
        rotulo_popover = f"📅  {d_inicio.strftime('%d/%m/%Y')} - {d_fim.strftime('%d/%m/%Y')}"
        with st.popover(rotulo_popover, use_container_width=True):
            st.markdown("### 📅 Selecionar Período no Calendário")
            st.caption("Escolha as datas inicial e final no calendário abaixo:")
            
            datas_selecionadas = st.date_input(
                "Intervalo de Análise:",
                value=(st.session_state.data_inicio_sel, st.session_state.data_fim_sel),
                format="DD/MM/YYYY",
                key="input_calendario_header_v15"
            )
            
            if isinstance(datas_selecionadas, (list, tuple)) and len(datas_selecionadas) == 2:
                d1, d2 = datas_selecionadas
                if d1 != st.session_state.data_inicio_sel or d2 != st.session_state.data_fim_sel:
                    st.session_state.data_inicio_sel = d1
                    st.session_state.data_fim_sel = d2
                    st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📅 Voltar ao Mês Atual", key="btn_reset_calendario_v15", type="secondary", use_container_width=True):
                st.session_state.data_inicio_sel = primeiro_dia_mes_atual.date()
                st.session_state.data_fim_sel = ultimo_dia_mes_atual.date()
                st.rerun()

    # =========================================================================
    # PAINEL PRINCIPAL
    # =========================================================================
    if menu == "Painel":
        c1, c2, c3, c4 = st.columns(4, gap="small")
        
        with c1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon receita">↗</div>
                    <div class="metric-label">Receitas</div>
                    <div class="metric-value">{moeda(total_receitas)}</div>
                    <div class="metric-change positive">↑ Entrada acumulada</div>
                    <div class="metric-period">vs. mês anterior</div>
                </div>
            """, unsafe_allow_html=True)
            
        with c2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon despesa">↘</div>
                    <div class="metric-label">Despesas</div>
                    <div class="metric-value">{moeda(total_despesas)}</div>
                    <div class="metric-change negative">↑ Saídas registradas</div>
                    <div class="metric-period">vs. mês anterior</div>
                </div>
            """, unsafe_allow_html=True)
            
        with c3:
            saldo_cor = "#EF476F" if saldo_liquido < 0 else "#FFFFFF"
            saldo_change = "⚠️ Saldo devedor" if saldo_liquido < 0 else "→ Saldo positivo"
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon saldo">👛</div>
                    <div class="metric-label">Saldo Atual</div>
                    <div class="metric-value" style="color:{saldo_cor};">{moeda(saldo_liquido)}</div>
                    <div class="metric-change purple">{saldo_change}</div>
                    <div class="metric-period">vs. mês anterior</div>
                </div>
            """, unsafe_allow_html=True)
            
        with c4:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon meta">🎯</div>
                    <div class="metric-label">Meta do Mês</div>
                    <div class="metric-value">{moeda(meta_mes)}</div>
                    <div class="progress-wrap">
                        <div class="progress-track"><div class="progress-fill" style="width:{progresso_meta}%;"></div></div>
                        <span>{progresso_meta}%</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)

        # --- GRÁFICOS + LANÇAMENTOS RECENTES ---
        chart1, chart2, recent = st.columns([1.45, 1.15, 1.0], gap="small")
        
        with chart1:
            st.markdown("""
                <div class="panel-title">
                    <span class="title-icon">📊</span>
                    <span>Receitas x Despesas</span>
                    <div class="legend"><span class="legend-dot receita-dot"></span>Receitas <span class="legend-dot despesa-dot"></span>Despesas</div>
                </div>
            """, unsafe_allow_html=True)
            
            if not df_calculo.empty:
                df_graf = df_calculo.copy()
                df_graf["Data_dt"] = pd.to_datetime(df_graf["Data"])
                df_graf["Mês"] = df_graf["Data_dt"].dt.month
                meses = list(range(1, agora.month + 1))
                nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
                linhas = []
                for m in meses:
                    linhas.append({
                        "Mês": nomes[m-1],
                        "Receita": df_graf.loc[(df_graf["Mês"] == m) & (df_graf["Tipo"] == "Receita"), "Valor"].sum(),
                        "Despesa": df_graf.loc[(df_graf["Mês"] == m) & (df_graf["Tipo"] == "Despesa"), "Valor"].sum()
                    })
                df_mes = pd.DataFrame(linhas)
                fig_bar = px.bar(
                    df_mes,
                    x="Mês",
                    y=["Receita", "Despesa"],
                    barmode="group",
                    color_discrete_map={"Receita": "#43C6A6", "Despesa": "#7C4DFF"}
                )
                fig_bar.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#D9D7F2",
                    height=255,
                    margin=dict(l=10, r=10, t=5, b=5),
                    showlegend=False,
                    xaxis=dict(showgrid=False, zeroline=False, title=None),
                    yaxis=dict(showgrid=True, gridcolor="#272A47", zeroline=False, title=None),
                )
                fig_bar.update_traces(marker_line_width=0, hovertemplate="R$ %{y:.2f}<extra></extra>")
                st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Nenhum dado cadastrado para exibir o gráfico.")

        with chart2:
            st.markdown("""
                <div class="panel-title">
                    <span class="title-icon">🍩</span>
                    <span>Gastos por categoria</span>
                </div>
            """, unsafe_allow_html=True)
            
            df_despesas = df_calculo[df_calculo["Tipo"] == "Despesa"]
            if not df_despesas.empty:
                df_cat = df_despesas.groupby("Categoria")["Valor"].sum().reset_index()
                fig_donut = px.pie(
                    df_cat,
                    values="Valor",
                    names="Categoria",
                    hole=0.62,
                    color_discrete_sequence=["#7C4DFF", "#3B9EF8", "#E84DA8", "#F4A340", "#43C6A6"]
                )
                fig_donut.update_traces(
                    textposition="inside",
                    textinfo="percent",
                    hovertemplate="%{label}<br>R$ %{value:.2f}<extra></extra>",
                    marker_line_width=0
                )
                fig_donut.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#FFFFFF",
                    height=255,
                    margin=dict(l=0, r=0, t=5, b=5),
                    showlegend=True,
                    legend=dict(
                        font=dict(size=10, color="#D9D7F2"),
                        orientation="v",
                        x=1.0,
                        y=0.5
                    )
                )
                st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Cadastre despesas para ver a distribuição por categoria.")

        with recent:
            st.markdown("""
                <div class="panel-title">
                    <span class="title-icon">🧾</span>
                    <span>Últimos lançamentos</span>
                </div>
            """, unsafe_allow_html=True)
            
            if historico_filtrado:
                for item in historico_filtrado[:5]:
                    _, tipo, valor, cat, desc, dt = item
                    classe = "recent-income" if tipo == "Receita" else "recent-expense"
                    sinal = "+" if tipo == "Receita" else "-"
                    icone = "↗" if tipo == "Receita" else "↘"
                    st.markdown(f"""
                        <div class="recent-item">
                            <div class="recent-icon {classe}">{icone}</div>
                            <div class="recent-info">
                                <div class="recent-name">{desc}</div>
                                <div class="recent-meta">{dt[:10]} · {cat}</div>
                            </div>
                            <div class="recent-value {classe}">{sinal} {moeda(valor)}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhuma transação recente.")

        st.markdown("<div class='section-gap-small'></div>", unsafe_allow_html=True)

        # --- BOTÕES DE AÇÃO (TODOS COM FAIXA ROXA PRIMARY) ---
        b1, b2, b3 = st.columns([1.05, 0.95, 0.95], gap="small")
        with b1:
            st.button("＋  Novo lançamento", use_container_width=True, key="btn_novo", type="primary", on_click=navegar_para, args=("Lançar",))
        with b2:
            st.button("🧾  Ver extrato", use_container_width=True, key="btn_extrato", type="primary", on_click=navegar_para, args=("Extrato e Edição",))
        with b3:
            st.button("📊  Ver gráficos", use_container_width=True, key="btn_graficos", type="primary", on_click=navegar_para, args=("Gráficos",))

        st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)

        # --- METAS + ALERTAS EM 2 COLUNAS LADO A LADO ---
        lower1, lower2 = st.columns(2, gap="small")
        
        with lower1:
            col_t1, col_b1 = st.columns([2.5, 1])
            with col_t1:
                st.markdown('<div class="bottom-title" style="margin-bottom:0;"><span>◎</span> Metas</div>', unsafe_allow_html=True)
            with col_b1:
                st.button("Ver todas →", key="btn_ver_todas_metas", type="secondary", on_click=navegar_para, args=("Metas",))

            st.markdown(f"""
                <div class="bottom-panel" style="margin-top:5px;">
                    <div class="goal-card">
                        <div class="goal-icon">🎯</div>
                        <div class="goal-info">
                            <div class="goal-name">Organizar minhas finanças</div>
                            <div class="goal-amount">{moeda(saldo_liquido)} / {moeda(meta_mes)}</div>
                            <div class="goal-progress"><div style="width:{progresso_meta}%;"></div></div>
                        </div>
                        <div class="goal-percent">{progresso_meta}%</div>
                    </div>
                    <div class="goal-foot">▣ &nbsp; Continue acompanhando seu progresso</div>
                </div>
            """, unsafe_allow_html=True)

        with lower2:
            col_t2, col_b2 = st.columns([2.5, 1])
            with col_t2:
                st.markdown('<div class="bottom-title" style="margin-bottom:0;"><span>♧</span> Alertas e dicas</div>', unsafe_allow_html=True)
            with col_b2:
                st.button("Ver todos →", key="btn_ver_todos_alertas", type="secondary", on_click=navegar_para, args=("Alertas e Dicas",))

            st.markdown(f"""
                <div class="bottom-panel" style="margin-top:5px;">
                    <div class="alert-box warning">
                        <div class="alert-symbol">!</div>
                        <div><b>Atenção!</b><br><span>Seu saldo atual é {moeda(saldo_liquido)}.</span></div>
                        <div class="alert-arrow">›</div>
                    </div>
                    <div class="alert-box success">
                        <div class="alert-symbol">✦</div>
                        <div><b>Parabéns!</b><br><span>Continue registrando suas movimentações.</span></div>
                        <div class="alert-arrow">›</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # --- CARD RETANGULAR BANNER GRANDE ABAIXO DOS DOIS CARDS ---
        st.markdown(f"""
            <div class="brand-promo">
                <div class="promo-content-left">
                    {logo_html("promo-bag-img") if LOGO_PATH.exists() else '<div class="promo-bag">💰</div>'}
                    <div class="promo-text-group">
                        <div class="promo-title">FAMT <span>Control</span></div>
                        <div class="promo-text">Organize suas finanças, conquiste seus objetivos e mantenha o controle total do seu orçamento.</div>
                    </div>
                </div>
                <div class="promo-chart">⌁↗</div>
            </div>
        """, unsafe_allow_html=True)

        if saldo_liquido < 0:
            st.markdown("<div class='section-gap-small'></div>", unsafe_allow_html=True)
            st.error("🚨 Seu saldo está negativo. Revise suas despesas não essenciais.")

    # =========================================================================
    # ABA LANÇAR
    # =========================================================================
    elif menu == "Lançar":
        col_head, col_back = st.columns([3.5, 1])
        with col_head:
            st.markdown('<div class="page-heading">Novo lançamento</div>', unsafe_allow_html=True)
            st.markdown('<div class="page-caption">Cadastre receitas ou despesas com validação contábil imediata.</div>', unsafe_allow_html=True)
        with col_back:
            st.button("← Voltar ao Painel", key="btn_back_lancar", type="secondary", on_click=navegar_para, args=("Painel",))
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            tipo = st.selectbox("Tipo de Lançamento", ["Receita", "Despesa"])
            valor = st.number_input("Valor da Transação (R$)", min_value=0.01, step=10.0, value=50.00)
        with col_f2:
            descricao = st.text_input("Descrição detalhada", placeholder="Ex: Bolsa de Estágio UMC, Almoço, Livros")
            categoria = st.text_input("Categoria do gasto/ganho", placeholder="Ex: Alimentação, Educação, Salário, Transporte")
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Salvar Transação no Banco de Dados", type="primary", use_container_width=True):
            if not descricao or not categoria:
                st.error("❌ Por favor, preencha a Descrição e a Categoria.")
            else:
                data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conexao = sqlite3.connect(DB_NAME, timeout=10)
                cursor = conexao.cursor()
                cursor.execute("""
                    INSERT INTO Transacoes (usuario_id, valor, tipo, data, descricao, categoria)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (st.session_state.usuario_id, valor, tipo, data_atual, descricao, categoria))
                conexao.commit()
                conexao.close()
                st.toast(f"🎉 {'Receita' if tipo == 'Receita' else 'Despesa'} de R$ {valor:.2f} cadastrada com sucesso!", icon="💰")
                st.session_state.notificacoes_lidas = False
                st.session_state.menu = "Painel"
                st.session_state.nav_radio_key = "Painel"
                st.rerun()

    # =========================================================================
    # ABA EXTRATO COM BOTÕES DE EDITAR E EXCLUIR
    # =========================================================================
    elif menu == "Extrato e Edição":
        col_head, col_back = st.columns([3.5, 1])
        with col_head:
            st.markdown('<div class="page-heading">Extrato e edição</div>', unsafe_allow_html=True)
            st.markdown('<div class="page-caption">Consulte, edite ou exclua seus lançamentos com botões dedicados.</div>', unsafe_allow_html=True)
        with col_back:
            st.button("← Voltar ao Painel", key="btn_back_extrato", type="secondary", on_click=navegar_para, args=("Painel",))
        
        # 1. FORMULÁRIO DE EDIÇÃO (EXIBIDO QUANDO UM ITEM É SELECIONADO PARA EDITAR)
        if "transacao_em_edicao" in st.session_state and st.session_state.transacao_em_edicao:
            edit_id = st.session_state.transacao_em_edicao
            conexao = sqlite3.connect(DB_NAME, timeout=10)
            cursor = conexao.cursor()
            cursor.execute("SELECT id, tipo, valor, categoria, descricao FROM Transacoes WHERE id = ? AND usuario_id = ?", (edit_id, st.session_state.usuario_id))
            item_edit = cursor.fetchone()
            conexao.close()
            
            if item_edit:
                _, e_tipo, e_valor, e_cat, e_desc = item_edit
                st.markdown(f"### ✏️ Editar Lançamento #{edit_id}")
                with st.form(key=f"form_editar_{edit_id}"):
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        novo_tipo = st.selectbox("Tipo de Lançamento", ["Receita", "Despesa"], index=0 if e_tipo == "Receita" else 1)
                        novo_valor = st.number_input("Valor (R$)", min_value=0.01, step=10.0, value=float(e_valor))
                    with col_e2:
                        nova_desc = st.text_input("Descrição", value=e_desc)
                        nova_cat = st.text_input("Categoria", value=e_cat)
                    
                    btn_save_col, btn_canc_col = st.columns(2)
                    with btn_save_col:
                        sub_save = st.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True)
                    with btn_canc_col:
                        sub_cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
                    
                    if sub_save:
                        if not nova_desc or not nova_cat:
                            st.error("❌ Por favor, preencha a Descrição e a Categoria.")
                        else:
                            conexao = sqlite3.connect(DB_NAME, timeout=10)
                            cursor = conexao.cursor()
                            cursor.execute("""
                                UPDATE Transacoes
                                SET tipo = ?, valor = ?, categoria = ?, descricao = ?
                                WHERE id = ? AND usuario_id = ?
                            """, (novo_tipo, float(novo_valor), nova_cat, nova_desc, edit_id, st.session_state.usuario_id))
                            conexao.commit()
                            conexao.close()
                            st.session_state.transacao_em_edicao = None
                            st.session_state.notificacoes_lidas = False
                            st.toast("✅ Transação atualizada com sucesso!", icon="💾")
                            st.rerun()
                    if sub_cancel:
                        st.session_state.transacao_em_edicao = None
                        st.rerun()
                st.markdown("<hr style='border-color: #282B45; margin: 20px 0;'>", unsafe_allow_html=True)

        # 2. CAIXA DE CONFIRMAÇÃO DE EXCLUSÃO
        if "transacao_para_excluir" in st.session_state and st.session_state.transacao_para_excluir:
            del_id = st.session_state.transacao_para_excluir
            st.warning(f"⚠️ **Atenção:** Deseja realmente excluir o lançamento **#{del_id}**?")
            col_del1, col_del2 = st.columns(2)
            with col_del1:
                if st.button("🔴 Confirmar Exclusão", key="btn_confirm_del_yes", type="primary", use_container_width=True):
                    conexao = sqlite3.connect(DB_NAME, timeout=10)
                    cursor = conexao.cursor()
                    cursor.execute("DELETE FROM Transacoes WHERE id = ? AND usuario_id = ?", (del_id, st.session_state.usuario_id))
                    conexao.commit()
                    conexao.close()
                    st.session_state.transacao_para_excluir = None
                    st.session_state.notificacoes_lidas = False
                    st.toast("🗑️ Lançamento excluído com sucesso!", icon="✅")
                    st.rerun()
            with col_del2:
                if st.button("❌ Cancelar", key="btn_confirm_del_no", use_container_width=True):
                    st.session_state.transacao_para_excluir = None
                    st.rerun()
            st.markdown("<hr style='border-color: #282B45; margin: 20px 0;'>", unsafe_allow_html=True)

        # 3. LISTA DE LANÇAMENTOS COM BOTÕES DEDICADOS
        if historico_filtrado:
            st.markdown("<br>", unsafe_allow_html=True)
            # Cabeçalho da Tabela
            col_h1, col_h2, col_h3, col_h4, col_h5, col_h6, col_h7 = st.columns([1.2, 2.2, 1.5, 1.1, 1.5, 0.9, 0.9])
            with col_h1: st.markdown("**Data**")
            with col_h2: st.markdown("**Descrição**")
            with col_h3: st.markdown("**Categoria**")
            with col_h4: st.markdown("**Tipo**")
            with col_h5: st.markdown("**Valor**")
            with col_h6: st.markdown("**Editar**")
            with col_h7: st.markdown("**Excluir**")
            st.markdown("<div style='border-bottom: 2px solid #282B45; margin-bottom: 12px;'></div>", unsafe_allow_html=True)

            for item in historico_filtrado:
                t_id, t_tipo, t_valor, t_cat, t_desc, t_data = item
                c_dt, c_desc, c_cat, c_tipo, c_val, c_edit, c_del = st.columns([1.2, 2.2, 1.5, 1.1, 1.5, 0.9, 0.9])
                
                c_dt.write(t_data[:10] if len(t_data) >= 10 else t_data)
                c_desc.write(f"**{t_desc}**")
                c_cat.write(t_cat)
                if t_tipo == "Receita":
                    c_tipo.markdown("<span style='color:#10B981; font-weight:600;'>↗ Receita</span>", unsafe_allow_html=True)
                    c_val.markdown(f"<span style='color:#10B981; font-weight:700;'>+ {moeda(t_valor)}</span>", unsafe_allow_html=True)
                else:
                    c_tipo.markdown("<span style='color:#EF4444; font-weight:600;'>↘ Despesa</span>", unsafe_allow_html=True)
                    c_val.markdown(f"<span style='color:#EF4444; font-weight:700;'>- {moeda(t_valor)}</span>", unsafe_allow_html=True)
                    
                with c_edit:
                    if st.button("✏️ Editar", key=f"btn_edit_{t_id}", type="secondary", use_container_width=True):
                        st.session_state.transacao_em_edicao = t_id
                        st.session_state.transacao_para_excluir = None
                        st.rerun()
                with c_del:
                    if st.button("🗑️ Excluir", key=f"btn_del_{t_id}", type="secondary", use_container_width=True):
                        st.session_state.transacao_para_excluir = t_id
                        st.session_state.transacao_em_edicao = None
                        st.rerun()
                
                st.markdown("<div style='border-bottom: 1px solid #1E2138; margin: 6px 0;'></div>", unsafe_allow_html=True)
        else:
            st.info("Nenhum lançamento encontrado para este usuário.")

    # =========================================================================
    # ABA METAS (EDITÁVEL)
    # =========================================================================
    elif menu == "Metas":
        col_head, col_back = st.columns([3.5, 1])
        with col_head:
            st.markdown('<div class="page-heading">🎯 Metas financeiras</div>', unsafe_allow_html=True)
            st.markdown('<div class="page-caption">Defina seus objetivos mensais de economia e acompanhe o progresso em tempo real.</div>', unsafe_allow_html=True)
        with col_back:
            st.button("← Voltar ao Painel", key="btn_back_metas", type="secondary", on_click=navegar_para, args=("Painel",))
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 1. Card com o progresso atual da Meta
        st.markdown(f"""
            <div class="bottom-panel large-panel" style="margin-bottom: 20px;">
                <div class="bottom-title"><span>◎</span> Meta Principal do Mês</div>
                <div class="goal-card">
                    <div class="goal-icon">🎯</div>
                    <div class="goal-info">
                        <div class="goal-name">Objetivo de Economia</div>
                        <div class="goal-amount">{moeda(saldo_liquido)} / {moeda(meta_mes)}</div>
                        <div class="goal-progress"><div style="width:{progresso_meta}%;"></div></div>
                    </div>
                    <div class="goal-percent">{progresso_meta}%</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 2. Formulário de Edição da Meta
        col_m1, col_m2 = st.columns([2, 1], gap="medium")
        
        with col_m1:
            st.markdown("### ✏️ Alterar o Valor da Meta Mensal")
            st.caption("Escolha o valor que você deseja economizar ou acumular neste mês:")
            
            nova_meta_input = st.number_input(
                "Defina o novo valor da meta (R$):",
                min_value=1.0,
                max_value=None,
                value=float(st.session_state.meta_mes),
                step=10.0,
                key="input_nova_meta"
            )
            
            if st.button("💾 Salvar Nova Meta", type="primary", use_container_width=True, key="btn_salvar_meta"):
                st.session_state.meta_mes = float(nova_meta_input)
                st.toast(f"🎉 Nova meta definida para {moeda(float(nova_meta_input))}!", icon="🎯")
                st.rerun()

        with col_m2:
            st.markdown("### 💡 Diagnóstico da Meta")
            if saldo_liquido >= meta_mes and meta_mes > 0:
                st.success(f"🟢 **PARABÉNS!** You atingiu 100% da sua meta mensal acumulando **{moeda(saldo_liquido)}**!")
            elif saldo_liquido > 0:
                falta = meta_mes - saldo_liquido
                st.warning(f"🟡 **EM PROGRESSO:** Falta pouco! Guarde mais **{moeda(falta)}** para alcançar seu objetivo de **{moeda(meta_mes)}**.")
            else:
                st.error(f"🔴 **SALDO ZERADO OU NEGATIVO:** Cadastre receitas para iniciar o progresso rumo à meta de **{moeda(meta_mes)}**.")


    # =========================================================================
    # ABA GRÁFICOS (ANALYSIS & VISUALIZATIONS)
    # =========================================================================
    elif menu == "Gráficos":
        col_head, col_back = st.columns([3.5, 1])
        with col_head:
            st.markdown('<div class="page-heading">📊 Análise de Gráficos e Indicadores</div>', unsafe_allow_html=True)
            st.markdown('<div class="page-caption">Visualização detalhada do desempenho financeiro, distribuição de despesas e evolução.</div>', unsafe_allow_html=True)
        with col_back:
            st.button("← Voltar ao Painel", key="btn_back_graficos", type="secondary", on_click=navegar_para, args=("Painel",))
        
        # Métrica de Indicadores
        g1, g2, g3, g4 = st.columns(4, gap="small")
        
        taxa_poupanca = ((saldo_liquido / total_receitas) * 100) if total_receitas > 0 else 0
        df_despesas_only = df_calculo[df_calculo["Tipo"] == "Despesa"] if not df_calculo.empty else pd.DataFrame()
        maior_despesa_val = float(df_despesas_only["Valor"].max()) if not df_despesas_only.empty else 0.0
        maior_despesa_nome = df_despesas_only.loc[df_despesas_only["Valor"].idxmax(), "Descrição"] if not df_despesas_only.empty else "Nenhuma"
        
        with g1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon receita">↗</div>
                    <div class="metric-label">Total Entradas</div>
                    <div class="metric-value">{moeda(total_receitas)}</div>
                    <div class="metric-change positive">100% Saldo Bruto</div>
                </div>
            """, unsafe_allow_html=True)
        with g2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon despesa">↘</div>
                    <div class="metric-label">Total Saídas</div>
                    <div class="metric-value">{moeda(total_despesas)}</div>
                    <div class="metric-change negative">{"- " + f"{(total_despesas/total_receitas*100):.1f}% da Renda" if total_receitas > 0 else "0%"}</div>
                </div>
            """, unsafe_allow_html=True)
        with g3:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon saldo">👛</div>
                    <div class="metric-label">Taxa de Poupança</div>
                    <div class="metric-value">{taxa_poupanca:.1f}%</div>
                    <div class="metric-change positive">{"✓ Positiva" if taxa_poupanca >= 0 else "⚠️ Negativa"}</div>
                </div>
            """, unsafe_allow_html=True)
        with g4:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon meta">🎯</div>
                    <div class="metric-label">Maior Gasto do Mês</div>
                    <div class="metric-value">{moeda(maior_despesa_val)}</div>
                    <div class="metric-change negative">{maior_despesa_nome[:20]}</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div class='section-gap-small'></div>", unsafe_allow_html=True)

        # Fileira 1: Gráfico de Receitas x Despesas + Rosca por Categoria
        col_g1, col_g2 = st.columns([1.2, 1.1], gap="small")
        with col_g1:
            st.markdown("### 📈 Comparativo de Entradas x Saídas")
            if not df_calculo.empty:
                df_grouped = df_calculo.groupby("Tipo")["Valor"].sum().reset_index()
                fig_bar = px.bar(
                    df_grouped, x="Tipo", y="Valor", color="Tipo",
                    color_discrete_map={"Receita": "#10B981", "Despesa": "#7C3AED"},
                    text_auto='.2f'
                )
                fig_bar.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#94A3B8',
                    showlegend=False,
                    height=300,
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                fig_bar.update_traces(marker_line_width=0)
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Nenhum lançamento cadastrado.")

        with col_g2:
            st.markdown("### 🍩 Gastos por Categoria")
            if not df_despesas_only.empty:
                df_cat = df_despesas_only.groupby("Categoria")["Valor"].sum().reset_index()
                fig_donut = px.pie(
                    df_cat, values="Valor", names="Categoria", hole=0.55,
                    color_discrete_sequence=["#8B5CF6", "#3B82F6", "#EC4899", "#F59E0B", "#10B981"]
                )
                fig_donut.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#FFFFFF',
                    height=300,
                    margin=dict(l=10, r=10, t=10, b=10),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_donut, use_container_width=True)
            else:
                st.info("Nenhuma despesa cadastrada.")

        st.markdown("<div class='section-gap-small'></div>", unsafe_allow_html=True)

        # Fileira 2: Ranking das Categoria de Despesas
        st.markdown("### 📊 Ranking das Maiores Categorias de Despesa")
        if not df_despesas_only.empty:
            df_rank = df_despesas_only.groupby("Categoria")["Valor"].sum().reset_index().sort_values(by="Valor", ascending=True)
            fig_rank = px.bar(
                df_rank, x="Valor", y="Categoria", orientation='h',
                color="Valor", color_continuous_scale=["#3B82F6", "#7C3AED"],
                text_auto='.2f'
            )
            fig_rank.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#94A3B8',
                coloraxis_showscale=False,
                height=280,
                margin=dict(l=10, r=10, t=10, b=10)
            )
            fig_rank.update_traces(marker_line_width=0)
            st.plotly_chart(fig_rank, use_container_width=True)
        else:
            st.info("Cadastre despesas para visualizar o ranking por categoria.")


    # =========================================================================
    # ABA NOTIFICAÇÕES (DEDICADA)
    # =========================================================================
    elif menu == "Notificações":
        col_head, col_back = st.columns([3.5, 1])
        with col_head:
            st.markdown('<div class="page-heading">🔔 Central de Notificações</div>', unsafe_allow_html=True)
            st.markdown('<div class="page-caption">Histórico de avisos do sistema, lançamentos recentes e alertas de saldo.</div>', unsafe_allow_html=True)
        with col_back:
            st.button("← Voltar ao Painel", key="btn_back_notif", type="secondary", on_click=navegar_para, args=("Painel",))

        # Indicadores do topo das notificações
        n1, n2, n3 = st.columns(3, gap="small")
        qtd_total = len(lista_notificacoes)
        qtd_novas = 0 if st.session_state.notificacoes_lidas else len(lista_notificacoes)
        
        with n1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon saldo">🔔</div>
                    <div class="metric-label">Total de Notificações</div>
                    <div class="metric-value">{qtd_total}</div>
                    <div class="metric-change positive">No histórico</div>
                </div>
            """, unsafe_allow_html=True)
        with n2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon receita">✨</div>
                    <div class="metric-label">Não Lidas (Novas)</div>
                    <div class="metric-value">{qtd_novas}</div>
                    <div class="metric-change positive">{"Pendentes de leitura" if qtd_novas > 0 else "Tudo em dia"}</div>
                </div>
            """, unsafe_allow_html=True)
        with n3:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon despesa">⚠️</div>
                    <div class="metric-label">Alertas de Saldo</div>
                    <div class="metric-value">{"1" if saldo_liquido < 0 else "0"}</div>
                    <div class="metric-change negative">{"Atenção necessária" if saldo_liquido < 0 else "Sem alertas"}</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div class='section-gap-small'></div>", unsafe_allow_html=True)

        # Ações de controle
        col_act1, col_act2 = st.columns([1, 1])
        with col_act1:
            if not st.session_state.notificacoes_lidas:
                if st.button("✓ Marcar todas como lidas", key="btn_marcar_todas_lidas_page", type="primary", use_container_width=True):
                    st.session_state.notificacoes_lidas = True
                    st.toast("✅ Todas as notificações foram marcadas como lidas!")
                    st.rerun()
            else:
                st.info("✓ Todas as notificações já foram marcadas como lidas.")

        st.markdown("<div class='section-gap-small'></div>", unsafe_allow_html=True)
        st.markdown("### 📋 Histórico Detalhado de Notificações")

        if lista_notificacoes:
            for i, notif in enumerate(lista_notificacoes):
                status_badge = '<span style="background-color:rgba(16,185,129,0.2); color:#10B981; padding:3px 8px; border-radius:6px; font-size:11px; font-weight:700;">NOVA</span>' if not st.session_state.notificacoes_lidas else '<span style="background-color:rgba(148,163,184,0.15); color:#94A3B8; padding:3px 8px; border-radius:6px; font-size:11px;">LIDA</span>'
                st.markdown(f"""
                    <div class="bottom-panel" style="margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div style="font-size: 16px; font-weight: 700; color: #FFFFFF;">{notif['titulo']}</div>
                            <div>{status_badge}</div>
                        </div>
                        <div style="font-size: 13px; color: #94A3B8; line-height: 1.5;">{notif['texto']}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhuma notificação no momento.")

    # =========================================================================
    # ABA ALERTAS E DICAS
    # =========================================================================
    elif menu == "Alertas e Dicas":
        col_head, col_back = st.columns([3.5, 1])
        with col_head:
            st.markdown('<div class="page-heading">🔔 Central de Alertas & Dicas Financeiras</div>', unsafe_allow_html=True)
            st.markdown('<div class="page-caption">Diagnósticos automáticos sobre o seu saldo, recomendações contábeis e simuladores de economia.</div>', unsafe_allow_html=True)
        with col_back:
            st.button("← Voltar ao Painel", key="btn_back_alertas", type="secondary", on_click=navegar_para, args=("Painel",))

        # Card de Status Geral
        if saldo_liquido < 0:
            st.error(f"🚨 **ALERTA CONTÁBIL CRÍTICO (REQ-BUS-01):** Seu saldo está negativo em **{moeda(abs(saldo_liquido))}**. Recomendamos conter imediatamente despesas não essenciais.")
        else:
            st.success(f"✅ **SAÚDE FINANCEIRA ESTÁVEL:** Parabéns! Seu saldo líquido acumulado é de **{moeda(saldo_liquido)}**.")

        st.markdown("<div class='section-gap-small'></div>", unsafe_allow_html=True)

        # Colunas de Alertas e Dicas
        col_a1, col_a2 = st.columns([1.1, 1.1], gap="small")

        with col_a1:
            st.markdown("### ⚠️ Diagnósticos & Alertas Automáticos")
            
            # Alerta 1: Saldo
            if saldo_liquido < 0:
                st.markdown(f"""
                    <div class="alert-box warning" style="margin-bottom:12px;">
                        <div class="alert-symbol">!</div>
                        <div><b>Saldo Devedor Ativo</b><br><span>Você gastou mais do que recebeu este mês ({moeda(total_despesas)} em despesas vs. {moeda(total_receitas)} em receitas).</span></div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="alert-box success" style="margin-bottom:12px;">
                        <div class="alert-symbol">✦</div>
                        <div><b>Saldo Positivo Garantido</b><br><span>Você está com folga orçamentária de {moeda(saldo_liquido)}. Excelente trabalho!</span></div>
                    </div>
                """, unsafe_allow_html=True)

            # Alerta 2: Concentração de Gastos
            if not df_calculo.empty and total_despesas > 0:
                df_desp = df_calculo[df_calculo["Tipo"] == "Despesa"]
                if not df_desp.empty:
                    top_cat = df_desp.groupby("Categoria")["Valor"].sum().reset_index().sort_values(by="Valor", ascending=False).iloc[0]
                    pct_top = (top_cat["Valor"] / total_despesas) * 100
                    if pct_top > 40:
                        st.markdown(f"""
                            <div class="alert-box warning" style="margin-bottom:12px;">
                                <div class="alert-symbol">⚡</div>
                                <div><b>Alta Concentração de Gastos</b><br><span>A categoria <b>{top_cat['Categoria']}</b> representa {pct_top:.1f}% de todos os seus gastos ({moeda(top_cat['Valor'])}).</span></div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div class="alert-box success" style="margin-bottom:12px;">
                                <div class="alert-symbol">⚖️</div>
                                <div><b>Gastos Diversificados</b><br><span>Sua maior categoria de gasto ({top_cat['Categoria']}) representa {pct_top:.1f}% do total. Boa distribuição!</span></div>
                            </div>
                        """, unsafe_allow_html=True)

            # Alerta 3: Meta de Economia
            st.markdown(f"""
                <div class="alert-box warning">
                    <div class="alert-symbol">🎯</div>
                    <div><b>Meta de Economia Mensal</b><br><span>Sua meta cadastrada é {moeda(meta_mes)}. Progresso atual: <b>{progresso_meta}%</b>.</span></div>
                </div>
            """, unsafe_allow_html=True)

        with col_a2:
            st.markdown("### 💡 Dicas de Educação Financeira (Squad FAMT)")
            
            st.markdown("""
                <div class="bottom-panel" style="margin-bottom:12px;">
                    <div style="font-size:15px; font-weight:700; color:#FFFFFF; margin-bottom:6px;">📊 1. Regra 50/30/20 para Estudantes</div>
                    <div style="font-size:13px; color:#94A3B8; line-height:1.5;">
                        Separe sua renda em: <b>50%</b> para necessidades fundamentais (mensalidade, transporte), <b>30%</b> para estilo de vida e <b>20%</b> para guardar ou reserva de emergência.
                    </div>
                </div>
                
                <div class="bottom-panel" style="margin-bottom:12px;">
                    <div style="font-size:15px; font-weight:700; color:#FFFFFF; margin-bottom:6px;">☕ 2. Atenção aos "Gastos Fantasmas"</div>
                    <div style="font-size:13px; color:#94A3B8; line-height:1.5;">
                        Cafés diários, lanches na faculdade e assinaturas pouco usadas parecem inofensivos, mas somam centenas de reais ao final do mês. Registre tudo no FAMT Control!
                    </div>
                </div>

                <div class="bottom-panel">
                    <div style="font-size:15px; font-weight:700; color:#FFFFFF; margin-bottom:6px;">🛡️ 3. Monte sua Reserva de Emergência</div>
                    <div style="font-size:13px; color:#94A3B8; line-height:1.5;">
                        Guarde o equivalente a 3 meses de gastos fixos em uma aplicação segura de liquidez diária para imprevistos com transporte ou estudos.
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div class='section-gap-small'></div>", unsafe_allow_html=True)

        # SIMULADOR RÁPIDO DE ECONOMIA
        st.markdown("### 🧮 Simulador de Economia Automático")
        val_simul = st.number_input("Quanto você consegue guardar por mês? (R$)", min_value=1.0, max_value=None, value=100.0, step=10.0)
        
        sim_3m = val_simul * 3
        sim_6m = val_simul * 6
        sim_12m = val_simul * 12
        
        s1, s2, s3 = st.columns(3, gap="small")
        with s1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Acumulado em 3 Meses</div>
                    <div class="metric-value">{moeda(sim_3m)}</div>
                    <div class="metric-change positive">1º Trimestre</div>
                </div>
            """, unsafe_allow_html=True)
        with s2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Acumulado em 6 Meses</div>
                    <div class="metric-value">{moeda(sim_6m)}</div>
                    <div class="metric-change positive">1 Semestre Letivo</div>
                </div>
            """, unsafe_allow_html=True)
        with s3:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Acumulado em 12 Meses</div>
                    <div class="metric-value">{moeda(sim_12m)}</div>
                    <div class="metric-change positive">1 Ano Inteiro</div>
                </div>
            """, unsafe_allow_html=True)

    # =========================================================================
    # ABA CONFIGURAÇÕES
    # =========================================================================
    elif menu == "Configurações":
        col_head, col_back = st.columns([3.5, 1])
        with col_head:
            st.markdown('<div class="page-heading">Configurações</div>', unsafe_allow_html=True)
            st.markdown('<div class="page-caption">Opções de manutenção da conta e do histórico financeiro.</div>', unsafe_allow_html=True)
        with col_back:
            st.button("← Voltar ao Painel", key="btn_back_config", type="secondary", on_click=navegar_para, args=("Painel",))
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Limpar Todo o Meu Histórico de Transações", type="secondary", use_container_width=True):
            conexao = sqlite3.connect(DB_NAME, timeout=10)
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM Transacoes WHERE usuario_id = ?;", (st.session_state.usuario_id,))
            conexao.commit()
            conexao.close()
            st.toast("💥 Histórico do usuário resetado!", icon="🗑️")
            st.rerun()
