import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import base64
from pathlib import Path

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="LECTRA Dashboard | Adient Morocco",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== COULEURS DYNAMIQUES POUR PLOTLY ====================
def get_plotly_colors():
    """Retourne les couleurs Plotly adaptées au thème (Dark/Light)"""
    is_light = st.session_state.get('theme', 'light') != 'dark'
    if is_light:
        return {
            'text': '#111827',
            'text_secondary': '#334155',
            'grid': 'rgba(15,23,42,0.06)',
            'axis': '#334155',
            'bg': 'rgba(255,255,255,0)',
            'paper': 'rgba(255,255,255,0)',
            'tick': '#334155',
            'title': '#111827'
        }
    else:
        return {
            'text': '#e2e8f0',
            'text_secondary': '#cbd5e1',
            'grid': 'rgba(255,255,255,0.08)',
            'axis': '#cbd5e1',
            'bg': 'rgba(0,0,0,0)',
            'paper': 'rgba(0,0,0,0)',
            'tick': '#cbd5e1',
            'title': '#e2e8f0'
        }

# ==================== CSS ====================
st.markdown("""
<style>
* { font-family: 'Segoe UI', system-ui, -apple-system, 'Helvetica Neue', Arial, sans-serif !important; }
[data-testid="stIconMaterial"],
[data-testid="stSidebarCollapseButton"] span,
[data-testid="stSidebarCollapsedControl"] span,
[data-testid="stExpandSidebarButton"] span,
[data-testid="collapsedControl"] span,
[data-testid="baseButton-headerNoPadding"] span,
.material-symbols-rounded, .material-symbols-outlined, .material-icons,
span[class*="material-symbols"], span[class*="material-icons"], i[class*="material"] {
  font-family: 'Material Symbols Rounded','Material Symbols Outlined','Material Icons Round','Material Icons' !important;
  font-feature-settings: 'liga' !important;
}
html, body, [data-testid="stAppViewContainer"], .main {
    background: #ffffff !important;
    color: #1e293b !important;
}
[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding-top: 1.2rem !important; max-width: 100% !important; }
.kpi-card {
    background:#ffffff; border-radius:14px; padding:20px 18px 16px;
    border:1.5px solid #333333; box-shadow:0 1px 3px rgba(15,23,42,.06),0 1px 2px rgba(15,23,42,.04);
    position:relative; overflow:hidden;
    transition:transform .25s, box-shadow .25s, border-color .25s; margin-bottom:8px;
}
.kpi-card::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; background:var(--accent,#1F4E79); border-radius:14px 14px 0 0; }
.kpi-card:hover { transform:translateY(-3px); box-shadow:0 12px 28px rgba(15,23,42,.10); border-color:#333333; }
.kpi-value { font-size:34px; font-weight:800; color:var(--accent,#1F4E79); line-height:1.1; letter-spacing:-1px; }
.kpi-label { font-size:13px; color:#111827; margin-top:6px; font-weight:600; letter-spacing:.5px; text-transform:uppercase; }
.kpi-unit  { font-size:13px; color:#94a3b8; margin-top:3px; }
.kpi-badge { position:absolute; top:14px; right:14px; font-size:10px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; padding:2px 8px; border-radius:20px; background:rgba(31,78,121,.10); color:#1F4E79; }
.page-header { background:linear-gradient(135deg,#0f3a52,#14506e); border:1px solid #0f3a52; border-left:4px solid #9cc31a; border-radius:14px; padding:22px 26px; margin-bottom:16px; position:relative; overflow:hidden; box-shadow:0 4px 14px rgba(15,58,82,.18); }
.page-header::after { content:''; position:absolute; top:-40px; right:-40px; width:150px; height:150px; border-radius:50%; background:rgba(255,255,255,.06); }
.page-header h1 { font-size:22px !important; font-weight:800 !important; letter-spacing:-.5px; margin:0 !important; color:#ffffff !important; }
.page-header p { margin:4px 0 0 !important; opacity:.9; font-size:14px !important; color:#cfe0ea !important; }
.header-badge { display:inline-block; font-size:12px; font-weight:700; letter-spacing:1px; text-transform:uppercase; background:rgba(255,255,255,.12); color:#ffffff; border:1px solid rgba(255,255,255,.25); padding:3px 10px; border-radius:20px; margin-top:8px; }
.status-bar { display:flex; align-items:center; gap:18px; flex-wrap:wrap; background:#ffffff; border:1px solid #333333; border-radius:12px; padding:10px 18px; margin-bottom:16px; font-size:14px; color:#111827; box-shadow:0 1px 2px rgba(15,23,42,.04); }
.status-dot { width:7px; height:7px; border-radius:50%; display:inline-block; margin-right:5px; }
.status-online { background:#4A6FA5; box-shadow:0 0 0 3px rgba(22,163,74,.18); animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:.45;} }
.alert-card-red    { background:#f6ecef; border:1px solid #333333; border-left:3px solid #8C2D4A; border-radius:10px; padding:11px 13px; margin-bottom:7px; transition:background .2s; }
.alert-card-orange { background:#faf4e4; border:1px solid #333333; border-left:3px solid #D4A03C; border-radius:10px; padding:11px 13px; margin-bottom:7px; transition:background .2s; }
.alert-card-green  { background:#eef3f8; border:1px solid #333333; border-left:3px solid #4A6FA5; border-radius:10px; padding:11px 13px; margin-bottom:7px; transition:background .2s; }
.alert-card-red:hover    { background:#f0dbe1; }
.alert-card-orange:hover { background:#f5ecd0; }
.alert-card-green:hover  { background:#e3ecf6; }
.alert-machine { font-weight:700; font-size:15px; color:#1e293b; }
.alert-tps     { font-size:13px; color:#111827; margin-top:2px; }
.alert-badge   { display:inline-block; font-size:10px; font-weight:700; letter-spacing:.8px; padding:2px 7px; border-radius:5px; text-transform:uppercase; float:right; }
.badge-red     { background:#f0dbe1; color:#8C2D4A; }
.badge-orange  { background:#f5ecd0; color:#8A6A1F; }
.badge-green   { background:#e3ecf6; color:#2F5C8A; }
.section-title { font-size:15px; font-weight:700; color:#1e293b; display:flex; align-items:center; gap:8px; padding-bottom:9px; border-bottom:1px solid #333333; margin-bottom:14px; }
.section-title .dot { width:7px; height:7px; border-radius:50%; background:#1F4E79; display:inline-block; flex-shrink:0; }
.tab-bar { display:flex; gap:6px; margin-bottom:16px; flex-wrap:wrap; }
.tab-btn { font-size:14px; font-weight:600; padding:6px 16px; border-radius:20px; cursor:pointer; background:#ffffff; border:1px solid #333333; color:#111827; transition:all .15s; }
.tab-btn.active { background:rgba(31,78,121,.10); border-color:#1F4E79; color:#1F4E79; }
.shift-tabs { display:flex; gap:6px; margin-bottom:14px; flex-wrap:wrap; }
.shift-tab { font-size:13px; font-weight:600; padding:5px 14px; border-radius:20px; cursor:pointer; background:#ffffff; border:1px solid #333333; color:#111827; transition:all .15s; user-select:none; }
.shift-tab:hover  { border-color:#1F4E79; color:#1F4E79; }
.shift-tab.active { background:rgba(31,78,121,.10); border-color:#1F4E79; color:#1F4E79; }
.perf-table { width:100%; border-collapse:collapse; }
.perf-table th { font-size:12px; font-weight:700; color:#111827; text-transform:uppercase; letter-spacing:.8px; padding:11px 12px; background:#f8fafc; border-bottom:1px solid #333333; text-align:left; }
.perf-table td { padding:11px 12px; font-size:14px; color:#1e293b; border-bottom:1px solid #f1f5f9; }
.perf-table tr:hover td { background:#f8fafc; }
.perf-wrap { background:#ffffff; border:1px solid #333333; border-radius:12px; overflow:hidden; box-shadow:0 1px 3px rgba(15,23,42,.06); }
.tps-pill { display:inline-block; font-weight:700; font-size:13px; padding:2px 9px; border-radius:20px; }
.toast-bar { background:#ecfeff; border:1px solid #333333; border-radius:10px; padding:10px 16px; margin-bottom:16px; font-size:14px; color:#0e7490; display:flex; align-items:center; gap:8px; }
[data-testid="stSidebar"] { background:#002f44 !important; border-right:1px solid #0c3a52 !important; }
[data-testid="stSidebar"] * { color:#dbe7ee !important; }
[data-testid="stSidebar"] .stButton button { background:rgba(255,255,255,.04) !important; border:1px solid rgba(255,255,255,.10) !important; border-radius:9px !important; color:#dbe7ee !important; font-size:15px !important; transition:all .2s !important; text-align:left !important; }
[data-testid="stSidebar"] .stButton button:hover { background:rgba(156,195,26,.16) !important; border-color:#9cc31a !important; color:#ffffff !important; }
.block-container [data-baseweb="select"] > div { background:#ffffff !important; border-color:#333333 !important; }
.block-container [data-baseweb="select"] div { color:#1e293b !important; }
.js-plotly-plot .plotly { border-radius:12px; overflow:hidden; }
div[data-testid="stDataFrame"] { border-radius:10px; overflow:hidden; border:1px solid #333333; }
::-webkit-scrollbar { width:8px; height:8px; }
::-webkit-scrollbar-track { background:#f1f5f9; }
::-webkit-scrollbar-thumb { background:#cbd5e1; border-radius:4px; }
::-webkit-scrollbar-thumb:hover { background:#1F4E79; }
.mini-stat { display:inline-flex; align-items:center; gap:5px; font-size:13px; color:#111827; background:#f8fafc; border:1px solid #333333; border-radius:7px; padding:4px 10px; }
.progress-wrap { background:#eef2f6; border-radius:4px; height:6px; margin-top:8px; overflow:hidden; }
.progress-fill { height:6px; border-radius:4px; transition:width .6s ease; }
@keyframes countUp { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }
.kpi-value { animation: countUp .5s ease forwards; }
hr { border-color:#333333 !important; }
</style>
""", unsafe_allow_html=True)

# ==================== AUTH ====================
USERS = {
    "admin123":  {"role": "admin",  "nom": "Administrateur"},
    "invite123": {"role": "invite", "nom": "Invité"},
    "chef123":   {"role": "chef",   "nom": "Chef d'atelier"},
}

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def verifier_mot_de_passe():
    if 'authentifie' not in st.session_state:
        st.session_state.authentifie = False
        st.session_state.role = None
        st.session_state.nom_user = ""

    if st.session_state.authentifie:
        return True

    bg_image_path = "background.png"
    img_base64 = ""

    if os.path.exists(bg_image_path):
        with open(bg_image_path, "rb") as image_file:
            img_base64 = base64.b64encode(image_file.read()).decode()
        bg_css = f"background: url(data:image/png;base64,{img_base64}) no-repeat center center fixed !important; background-size: cover !important;"
    else:
        bg_css = "background: linear-gradient(135deg, #eef3f8 0%, #e2eaf2 50%, #dde8f0 100%) !important;"

    st.markdown(f"""
    <style>
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stSidebar"] {{ display: none !important; }}
    div[data-testid="stAppViewContainer"], .stApp {{ 
        {bg_css}
    }}
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(255,255,255,0.35);
        z-index: 0;
        pointer-events: none;
    }}
    .main, .block-container {{ 
        position: relative; 
        z-index: 1; 
    }}
    .block-container {{ 
        padding: 0 !important; 
        max-width: 100% !important; 
    }}
    .stTextInput input {{
        background: #f8fafc !important;
        border: 1px solid #d7dee8 !important;
        border-radius: 6px !important;
        height: 36px !important;
        font-size: 15px !important;
        padding: 0 10px !important;
        color: #000 !important;
    }}
    .stTextInput input:focus {{
        border-color: #9cc31a !important;
        box-shadow: 0 0 0 2px rgba(156,195,26,0.2) !important;
        outline: none !important;
    }}
    .stButton button {{
        background: #003f52 !important;
        color: white !important;
        height: 38px !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        margin-top: 5px !important;
        border: none !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
    }}
    .stButton button:hover {{
        background: #005c78 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }}
    .stCheckbox label p {{ 
        font-size: 13px !important; 
    }}
    div[data-testid="column"] {{ 
        gap: 0px !important; 
    }}
    .login-label {{
        text-align: left;
        font-size: 14px;
        font-weight: 600;
        color: #333;
        margin-bottom: 4px;
    }}
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 30px 35px 25px 35px;
            margin: 60px auto;
            max-width: 420px;
            box-shadow: 0 15px 40px rgba(0,0,0,0.25);
            position: relative;
            z-index: 10;
            text-align: center;
        ">
            <div style="font-size: 24px; font-weight: 800; color: #00334e; margin-bottom: 10px;">
                <span style="color: #9cc31a;">/</span>ADIENT
            </div>
            <div style="font-size: 18px; font-weight: 800; color: #00334e; margin-bottom: 5px;">
                PERFORMANCE
            </div>
            <div style="font-size: 14px; font-weight: 700; color: #9cc31a; margin-bottom: 15px;">
                ATELIER DE COUPE
            </div>
            <div style="height: 1px; background: linear-gradient(90deg, transparent, #9cc31a, transparent); margin-bottom: 20px;"></div>
        """, unsafe_allow_html=True)

        st.markdown("<p class='login-label'>👤 Nom d'utilisateur</p>", unsafe_allow_html=True)
        username = st.text_input("", placeholder="Entrez votre nom d'utilisateur", key="login_user", label_visibility="collapsed")

        st.markdown("<p class='login-label' style='margin-top: 10px;'>🔐 Mot de passe</p>", unsafe_allow_html=True)
        password = st.text_input("", type="password", placeholder="Entrez votre mot de passe", key="login_pwd", label_visibility="collapsed")

        col_check, col_forgot = st.columns([1, 1])
        with col_check:
            st.checkbox("Se souvenir de moi")
        with col_forgot:
            st.markdown("<div style='text-align: right; padding-top: 3px;'><a href='#' style='color: #9cc31a; font-size: 13px; text-decoration: none;'>Mot de passe oublié ?</a></div>", unsafe_allow_html=True)

        if st.button("🔓 SE CONNECTER", use_container_width=True):
            if password in USERS:
                st.session_state.authentifie = True
                st.session_state.role = USERS[password]["role"]
                st.session_state.nom_user = USERS[password]["nom"]
                st.rerun()
            elif password:
                st.error("❌ Identifiants incorrects")

        st.markdown("""
            <div style="height: 1px; background: linear-gradient(90deg, transparent, #9cc31a, transparent); margin: 20px 0 15px 0;"></div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div style="text-align: center;">
                <p style="color: #00334e; font-size: 13px; font-weight: 700; letter-spacing: 2px; margin-bottom: 12px;">
                    ADIENT MOROCCO — TIFLET
                </p>
                <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin-bottom: 10px;">
                    <div style="font-size: 13px; font-weight: 500; color: #555;">
                        <span style="color: #9cc31a;">⏱️</span> TEMPS RÉEL
                    </div>
                    <div style="font-size: 13px; font-weight: 500; color: #555;">
                        <span style="color: #9cc31a;">📊</span> KPIs
                    </div>
                    <div style="font-size: 13px; font-weight: 500; color: #555;">
                        <span style="color: #9cc31a;">🎯</span> OBJECTIFS
                    </div>
                    <div style="font-size: 13px; font-weight: 500; color: #555;">
                        <span style="color: #9cc31a;">📈</span> AMÉLIORATION
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div style="text-align: center; margin-top: 18px; padding-top: 12px; border-top: 1px solid #eee;">
                <span style="color: #9cc31a;">🛡️</span>
                <span style="color: #888; font-size: 12px;"> Accès sécurisé</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    return False

# ==================== SIDEBAR ====================
def sidebar_navigation():
    with st.sidebar:
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center;padding:0 8px 16px;border-bottom:1px solid rgba(255,255,255,.1);margin-bottom:14px;">
            <div style="font-size:22px;font-weight:800;color:#f0f6ff;letter-spacing:-1px;">
                <span style="color:#9cc31a;">/</span>ADIENT
            </div>
            <div style="font-size:10px;color:#9cc31a;letter-spacing:2.5px;text-transform:uppercase;margin-top:1px;">Atelier de Coupe</div>
        </div>
        """, unsafe_allow_html=True)

        role_color = {"admin":"#1F4E79","chef":"#D4A03C","invite":"#9fb6c4"}.get(st.session_state.role,"#9fb6c4")
        role_icon  = {"admin":"","chef":"","invite":""}.get(st.session_state.role,"")
        st.markdown(f"""
        <div style="text-align:center;padding:14px 10px;
            background:linear-gradient(145deg,rgba(15,23,42,.9),rgba(17,24,39,.9));
            border:1px solid rgba(255,255,255,.05);border-radius:12px;margin-bottom:12px;">
            <div style="font-size:16px;font-weight:700;color:#ffffff;">{st.session_state.nom_user}</div>
            <div style="font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:{role_color};margin-top:3px;">{st.session_state.role}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.role == "admin":
            st.success("Accès complet")
        elif st.session_state.role == "chef":
            st.warning("Chef d'atelier")
        else:
            st.info("Lecture seule")

        st.markdown("---")
        st.markdown("<div style='font-size:12px;color:#9fb6c4;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;padding:0 4px 6px;'>Navigation</div>", unsafe_allow_html=True)

        pages = [
            ("", "Accueil",             "Vue d'ensemble & alertes"),
            ("", "TPS & Performance",   "Taux de productivité"),
            ("", "Analyse des Pertes",  "Interruptions & pertes"),
            ("", "ADV Production",      "Adhérence au volume"),
            ("", "Analyse par Machine", "Détail machine"),
            ("", "Données Brutes",      "Tableau & export"),
        ]

        if 'page_active' not in st.session_state:
            st.session_state.page_active = "Accueil"

        for icon, nom, desc in pages:
            if st.button(f"{nom}", key=f"nav_{nom}", use_container_width=True, help=desc):
                st.session_state.page_active = nom
                st.rerun()

        st.markdown("---")

        st.markdown("<div style='font-size:12px;color:#9fb6c4;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;padding:0 4px 6px;'>Apparence</div>", unsafe_allow_html=True)
        theme = st.radio("", ["Dark", "Light"], horizontal=True,
                         index=0 if st.session_state.get('theme','light')=='dark' else 1,
                         key="theme_radio", label_visibility="collapsed")
        new_theme = "dark" if theme == "Dark" else "light"
        if new_theme != st.session_state.get('theme','light'):
            st.session_state.theme = new_theme
            st.rerun()

        # CSS Thème sombre (optionnel)
        if st.session_state.get('theme','light') == 'dark':
            st.markdown("""
            <style>
            html, body, [data-testid="stAppViewContainer"],
            [data-testid="stAppViewContainer"] > .main, .main, .block-container {
                background:#0f172a !important; color:#e2e8f0 !important;
            }
            .kpi-card { background:#1e293b !important; border:1.5px solid #334155 !important; box-shadow:0 2px 10px rgba(0,0,0,.35) !important; }
            .kpi-label { color:#cbd5e1 !important; }
            .kpi-unit  { color:#94a3b8 !important; }
            .perf-wrap { background:#1e293b !important; border-color:#334155 !important; }
            .status-bar { background:#1e293b !important; border-color:#334155 !important; color:#cbd5e1 !important; }
            .section-title { color:#e2e8f0 !important; border-bottom-color:#334155 !important; }
            .alert-card-red, .alert-card-orange, .alert-card-green { background:#1e293b !important; border-color:#334155 !important; }
            .alert-machine { color:#e2e8f0 !important; }
            .alert-tps { color:#94a3b8 !important; }
            .perf-table th { background:#111c2e !important; color:#cbd5e1 !important; border-color:#334155 !important; }
            .perf-table td { color:#e2e8f0 !important; border-color:#26344a !important; }
            .perf-table tr:hover td { background:rgba(255,255,255,.04) !important; }
            .tab-btn, .shift-tab { background:#1e293b !important; border-color:#334155 !important; color:#cbd5e1 !important; }
            .mini-stat { background:#1e293b !important; border-color:#334155 !important; color:#cbd5e1 !important; }
            .toast-bar { background:#14213a !important; border-color:#334155 !important; color:#93c5fd !important; }
            .progress-wrap { background:#334155 !important; }
            [data-testid="stDataFrame"] { background:#1e293b !important; }
            hr { border-color:#334155 !important; }
            </style>
            """, unsafe_allow_html=True)

        st.markdown("---")

        st.markdown("<div style='font-size:12px;color:#9fb6c4;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;padding:0 4px 6px;'>Mode données</div>", unsafe_allow_html=True)
        mode_sim = st.toggle("Mode Simulation", value=st.session_state.get('mode_simulation', False), key="sim_toggle")
        if mode_sim != st.session_state.get('mode_simulation', False):
            st.session_state.mode_simulation = mode_sim
            st.rerun()

        st.markdown("---")
        st.markdown(f"""
        <div style="font-family:monospace;font-size:13px;color:#aebfcb;text-align:center;
            padding:7px;background:rgba(255,255,255,.05);border-radius:8px;margin-bottom:8px;
            border:1px solid rgba(255,255,255,.08);">
            {datetime.now().strftime('%d/%m/%Y %H:%M')}
        </div>""", unsafe_allow_html=True)
        st.caption("LECTRA Dashboard v5.0")
        st.caption("Adient Morocco | PFE 2025")
        st.markdown("---")
        if st.button("Déconnexion", use_container_width=True):
            st.session_state.authentifie = False
            st.rerun()

# ==================== DONNEES SIMULATION ====================
def generer_donnees_demo():
    """Données réelles simulation — LO1→LO6, 06–04 Avril/juin 2025 (valeurs réelles)"""

    def hms_to_min(hms):
        h, m, s = map(int, hms.split(':'))
        return h * 60 + m + s / 60

    # date -> ADV journalière (%)
    adv_jour = {
        '2025-04-06': 68.56,
        '2025-04-07': 56.42,
        '2025-04-08': 65.23,
        '2025-04-09': 61.67,
        '2025-06-01': 75.20,
        '2025-06-02': 70.15,
        '2025-06-03': 73.80,
        '2025-06-04': 72.40,
    }

    # date -> machine -> (INTERRUPTIONS, CODA, DT_POSIT, ΔT_Matelas, TPS %)
    data = {
        '2025-04-06': {
            'L01': ('03:13:29', '00:51:04', '01:25:00', '01:49:00', 54.45),
            'L02': ('04:01:12', '00:24:28', '01:21:18', '01:12:43', 59.08),
            'L03': ('04:26:41', '00:32:52', '01:26:51', '01:52:15', 45.00),
            'L04': ('04:01:00', '01:15:10', '01:27:23', '01:54:57', 42.12),
            'L05': ('03:22:51', '00:30:10', '01:05:30', '02:10:21', 32.15),
            'L06': ('04:31:21', '01:21:32', '00:57:23', '01:22:31', 31.51),
        },
        '2025-04-07': {
            'L01': ('02:38:09', '00:30:26', '01:10:00', '02:43:00', 37.76),
            'L02': ('02:54:01', '00:20:07', '01:12:43', '02:17:01', 48.00),
            'L03': ('03:07:10', '00:45:32', '00:58:46', '01:56:48', 36.41),
            'L04': ('03:33:42', '01:32:52', '01:14:50', '02:04:45', 30.12),
            'L05': ('02:58:26', '00:29:49', '01:15:10', '01:54:50', 39.40),
            'L06': ('03:12:08', '01:32:52', '01:26:51', '01:54:50', 42.52),
        },
        '2025-04-08': {
            'L01': ('03:05:03', '00:29:40', '00:48:00', '02:55:00', 30.71),
            'L02': ('04:17:23', '01:01:25', '01:11:14', '02:27:22', 44.85),
            'L03': ('03:33:42', '00:45:32', '01:21:18', '02:17:01', 35.10),
            'L04': ('02:54:01', '00:45:32', '01:14:50', '01:54:57', 39.40),
            'L05': ('04:10:00', '01:10:23', '01:15:10', '01:52:15', 37.15),
            'L06': ('02:41:00', '00:45:32', '00:48:00', '01:22:31', 69.51),
        },
        '2025-04-09': {
            'L01': ('04:35:50', '00:06:06', '01:04:00', '03:44:00', 40.53),
            'L02': ('03:08:54', '00:43:12', '01:58:47', '02:46:22', 49.54),
            'L03': ('04:10:00', '01:15:10', '01:10:23', '01:54:57', 38.12),
            'L04': ('04:17:23', '01:01:25', '01:11:14', '02:27:22', 41.10),
            'L05': ('04:26:41', '00:32:52', '01:26:51', '01:52:15', 45.00),
            'L06': ('02:02:05', '00:05:17', '01:01:00', '02:58:00', 32.71),
        },
        '2025-06-01': {
            'L01': ('02:41:00', '00:43:00', '01:13:00', '01:12:00', 61.20),
            'L02': ('03:22:00', '00:17:00', '01:09:00', '00:55:00', 65.50),
            'L03': ('03:48:00', '00:25:00', '01:14:00', '01:13:00', 50.32),
            'L04': ('03:18:00', '01:07:00', '01:15:00', '01:13:00', 49.80),
            'L05': ('02:45:00', '00:22:00', '01:28:00', '01:13:00', 41.10),
            'L06': ('03:52:00', '00:13:00', '00:47:00', '00:40:00', 40.20),
        },
        '2025-06-02': {
            'L01': ('02:05:00', '00:22:00', '01:00:00', '01:12:00', 45.50),
            'L02': ('02:16:00', '00:12:00', '01:35:00', '01:13:00', 55.80),
            'L03': ('02:29:00', '00:37:00', '00:48:00', '01:35:00', 44.20),
            'L04': ('02:55:00', '01:24:00', '01:04:00', '01:23:00', 38.40),
            'L05': ('02:20:00', '00:21:00', '01:05:00', '01:13:00', 47.20),
            'L06': ('02:34:00', '01:24:00', '01:16:00', '01:13:00', 50.30),
        },
        '2025-06-03': {
            'L01': ('02:27:00', '00:21:00', '00:38:00', '00:50:00', 38.50),
            'L02': ('03:39:00', '00:53:00', '01:01:00', '01:45:00', 52.60),
            'L03': ('02:55:00', '00:37:00', '01:11:00', '01:35:00', 43.00),
            'L04': ('02:16:00', '00:37:00', '01:04:00', '01:13:00', 47.20),
            'L05': ('02:18:00', '00:02:00', '01:10:00', '01:00:00', 45.00),
            'L06': ('02:03:00', '00:00:00', '00:38:00', '00:40:00', 76.30),
        },
        '2025-06-04': {
            'L01': ('03:57:00', '00:54:00', '00:00:00', '00:00:00', 48.30),
            'L02': ('02:31:00', '00:00:00', '01:48:00', '02:04:00', 57.30),
            'L03': ('03:32:00', '00:00:00', '00:37:00', '01:13:00', 46.00),
            'L04': ('03:39:00', '00:25:00', '01:00:00', '01:49:00', 49.00),
            'L05': ('03:48:00', '00:00:00', '01:16:00', '02:16:00', 52.80),
            'L06': ('01:24:00', '00:00:00', '00:51:00', '02:16:00', 41.50),
        },
    }

    rng = np.random.default_rng(42)
    n_markers = 10
    rows, marker_id = [], 1

    for date_str, machines in data.items():
        date = pd.Timestamp(date_str)
        adv_target = adv_jour[date_str] / 100

        for machine, (inter, coda, dtpos, matel, tps_target) in machines.items():
            inter_min = hms_to_min(inter)
            coda_min  = hms_to_min(coda)
            dtpos_min = hms_to_min(dtpos)
            matel_min = hms_to_min(matel)

            tps_jit = rng.uniform(-0.4, 0.4, n_markers); tps_jit -= tps_jit.mean()
            adv_jit = rng.uniform(-0.005, 0.005, n_markers); adv_jit -= adv_jit.mean()

            for j in range(n_markers):
                tps_shift = round(tps_target + tps_jit[j], 2)
                rows.append({
                    'DATE': date,
                    'Machine': machine,
                    'Marker': f"MRK-{marker_id:04d}",
                    'TPS Shift': tps_shift,
                    'ADV': round(adv_target + adv_jit[j], 4),
                    'CUTTING TIME': round(tps_shift * 4.8, 1),
                    'INTERRUPTIONS TIME': round(inter_min / n_markers, 2),
                    'CODA INTERRUPTIONS TIME': round(coda_min / n_markers, 2),
                    'DWN TIME': round(dtpos_min / n_markers, 2),
                    'DT_POSIT (min)': round(dtpos_min / n_markers, 2),
                    'ΔT_Matelas': round(matel_min / n_markers, 2),
                    'POSIT/Marker': round(dtpos_min / n_markers / 10, 3),
                    'STATE': 'NOK' if tps_shift < 75 else 'OK',
                })
                marker_id += 1

    return pd.DataFrame(rows)

# ==================== UTILITAIRES ====================
def time_to_minutes(val):
    if pd.isna(val): return 0
    if isinstance(val, str) and ':' in val:
        parts = val.strip().split(':')
        try:
            if len(parts) == 3: return int(parts[0])*60 + int(parts[1]) + int(parts[2])/60
            if len(parts) == 2: return int(parts[0])*60 + int(parts[1])
        except: return 0
    elif isinstance(val, (int, float)): return float(val)
    return 0

def charger_donnees():
    if st.session_state.get('mode_simulation', False):
        return generer_donnees_demo()

    excel_path = "modele_lectra.xlsx"
    if not os.path.exists(excel_path):
        return generer_donnees_demo()

    try:
        all_sheets = pd.read_excel(excel_path, sheet_name=None)
        dataframes = []
        for sheet_name, df in all_sheets.items():
            if df is not None and not df.empty:
                df['Machine'] = sheet_name
                for col in ['TPS Shift','ADV','CUTTING TIME','INTERRUPTIONS TIME','DWN TIME']:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                for src, dst in [('DT_POSIT (min)','DT_POSIT (min)'),('DT_POSIT','DT_POSIT (min)'),('DT_POSIT(min)','DT_POSIT (min)')]:
                    if src in df.columns:
                        df['DT_POSIT (min)'] = pd.to_numeric(df[src], errors='coerce')
                        break
                else:
                    df['DT_POSIT (min)'] = 0
                for src in ['CODA INTERRUPTIONS TIME','CODA INTERRUPTION']:
                    if src in df.columns:
                        df['CODA INTERRUPTIONS TIME'] = pd.to_numeric(df[src], errors='coerce')
                        break
                else:
                    df['CODA INTERRUPTIONS TIME'] = 0
                for src in ['POSIT/Marker','POSIT/Mar']:
                    if src in df.columns:
                        df['POSIT/Marker'] = df[src].apply(time_to_minutes)
                        break
                else:
                    df['POSIT/Marker'] = 0
                for src in ['ΔT_Matelas','AT_Matel']:
                    if src in df.columns:
                        df['ΔT_Matelas'] = df[src].apply(time_to_minutes)
                        break
                else:
                    df['ΔT_Matelas'] = 0
                if 'DATE' in df.columns:
                    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
                dataframes.append(df)
        if dataframes:
            df_c = pd.concat(dataframes, ignore_index=True)
            if 'TPS Shift' in df_c.columns and df_c['TPS Shift'].dropna().empty:
                return generer_donnees_demo()
            return df_c
        return generer_donnees_demo()
    except Exception as e:
        st.warning(f"Erreur chargement: {e}")
        return generer_donnees_demo()

def calculer_tps_adv(df):
    if df is None or df.empty: return pd.DataFrame()
    resultats = []
    for machine in sorted(df['Machine'].unique()):
        df_m = df[df['Machine'] == machine]
        tps_vals = df_m['TPS Shift'].dropna()
        tps_moyen = tps_vals.mean() if len(tps_vals) > 0 else 0
        adv_vals = df_m['ADV'].dropna() if 'ADV' in df_m.columns else pd.Series()
        adv_moyen = adv_vals.mean() * 100 if len(adv_vals) > 0 else 0
        cutting       = df_m['CUTTING TIME'].fillna(0).sum()           if 'CUTTING TIME' in df_m.columns else 0
        interruptions = df_m['INTERRUPTIONS TIME'].fillna(0).sum()     if 'INTERRUPTIONS TIME' in df_m.columns else 0
        dwn_time      = df_m['DWN TIME'].fillna(0).sum()               if 'DWN TIME' in df_m.columns else 0
        dt_matelas    = df_m['ΔT_Matelas'].fillna(0).sum()             if 'ΔT_Matelas' in df_m.columns else 0
        coda          = df_m['CODA INTERRUPTIONS TIME'].fillna(0).sum()if 'CODA INTERRUPTIONS TIME'in df_m.columns else 0
        posit_marker  = df_m['POSIT/Marker'].fillna(0).sum()           if 'POSIT/Marker' in df_m.columns else 0
        dt_posit      = df_m['DT_POSIT (min)'].fillna(0).sum()         if 'DT_POSIT (min)' in df_m.columns else 0
        resultats.append({
            'Machine': machine,
            'TPS (%)': round(tps_moyen, 1),
            'Objectif (%)': 75,
            'Écart (%)': round(tps_moyen - 75, 1),
            'ADV (%)': round(adv_moyen, 1),
            'Cutting (min)': round(cutting, 1),
            'Interruptions (min)': round(interruptions, 1),
            'DWN TIME (min)': round(dwn_time, 1),
            'ΔT_Matelas (min)': round(dt_matelas, 1),
            'DT_POSIT (min)': round(dt_posit, 1),
            'CODA (min)': round(coda, 1),
            'POSIT/Marker': round(posit_marker, 1),
            'Statut': "OK" if tps_moyen >= 75 else "NOK"
        })
    return pd.DataFrame(resultats)

# ── Layout Plotly dynamique (Dark / Light) ──
def pl(yaxis_title=None, yaxis_range=None, height=None, **extra):
    colors = get_plotly_colors()
    axis_common = dict(gridcolor=colors['grid'], zeroline=False, showline=False,
                       tickfont=dict(size=12, color=colors['tick']), automargin=True)
    layout = dict(
        paper_bgcolor=colors['paper'],
        plot_bgcolor=colors['bg'],
        font_color=colors['text'],
        font_family='Segoe UI, system-ui, sans-serif',
        margin=dict(t=48, b=40, l=52, r=24),
        hovermode='x unified',
        hoverlabel=dict(bgcolor='#ffffff', bordercolor='#e5e7eb',
                        font=dict(color='#111827', family='Segoe UI, system-ui, sans-serif', size=12)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0,
                    font=dict(size=12, color=colors['text'])),
        xaxis=dict(**axis_common),
    )
    yax = dict(**axis_common)
    if yaxis_title:
        yax['title'] = dict(text=yaxis_title, font=dict(color=colors['title'], size=12))
    if yaxis_range:
        yax['range'] = yaxis_range
    layout['yaxis'] = yax
    if height:
        layout['height'] = height
    layout.update(extra)
    return layout

def page_header(icon, titre, sous_titre, badge=None):
    badge_html = f'<span class="header-badge">{badge}</span>' if badge else ''
    st.markdown(f"""
    <div class="page-header">
        <h1>{titre}</h1>
        <p>{sous_titre}</p>
        {badge_html}
    </div>""", unsafe_allow_html=True)

# ==================== PAGE 1 : ACCUEIL ====================
def page_accueil(df, df_tps):
    colors = get_plotly_colors()
    now = datetime.now()
    page_header("", "Tableau de Bord — Vue d'ensemble",
                "Adient Morocco | Atelier de Coupe | Projet MMA / Mercedes",
                badge=f"Mis à jour : {now.strftime('%d/%m/%Y %H:%M')}")

    if st.session_state.get('mode_simulation', False):
        st.markdown(f"""
        <div class="toast-bar">
            <strong>Mode Simulation actif</strong> — Données LO1→LO6 · 06–09 Avril 2025 · {len(df)} markers chargés
        </div>""", unsafe_allow_html=True)

    total_machines = len(df_tps)
    ok_count   = len(df_tps[df_tps['TPS (%)'] >= 75])
    nok_count  = total_machines - ok_count
    health_pct = int(ok_count / total_machines * 100) if total_machines else 0
    health_color = "#4A6FA5" if health_pct >= 70 else "#D4A03C" if health_pct >= 40 else "#8C2D4A"
    jours = df['DATE'].nunique() if 'DATE' in df.columns else 1

    st.markdown(f"""
    <div class="status-bar">
        <span><span class="status-dot status-online"></span> Système en ligne</span>
        <span style="color:#cbd5e1;">|</span>
        <span>{total_machines} machines</span>
        <span style="color:#cbd5e1;">|</span>
        <span style="color:{health_color};font-weight:700;">● Santé atelier : {health_pct}%</span>
        <span style="color:#cbd5e1;">|</span>
        <span>{ok_count} OK &nbsp;·&nbsp; {nok_count} NOK</span>
        <span style="margin-left:auto;font-family:monospace;font-size:13px;">{now.strftime('%A %d %B %Y').capitalize()} · {jours}j analysés</span>
    </div>""", unsafe_allow_html=True)

    tps_moyen  = df_tps['TPS (%)'].mean()
    adv_moyen  = df_tps['ADV (%)'].mean() if df_tps['ADV (%)'].sum() > 0 else 0
    machines_nok = len(df_tps[df_tps['TPS (%)'] < 75])
    total_inter  = df['INTERRUPTIONS TIME'].sum() if 'INTERRUPTIONS TIME' in df.columns else 0
    total_markers = len(df)

    tps_color  = "#4A6FA5" if tps_moyen >= 75 else "#D4A03C" if tps_moyen >= 40 else "#8C2D4A"
    adv_color  = "#4A6FA5" if adv_moyen >= 100 else "#D4A03C" if adv_moyen >= 80 else "#8C2D4A"
    nok_color  = "#8C2D4A" if machines_nok > 0 else "#4A6FA5"

    kpis = [
        (f"{tps_moyen:.1f}%",             "TPS Moyen Atelier",      "Taux de productivité",    tps_color,  "TPS"),
        (f"{adv_moyen:.1f}%",             "ADV Moyenne",            "Adhérence au volume",     adv_color,  "ADV"),
        (f"{machines_nok}/{total_machines}","Machines sous objectif","< 75% TPS",               nok_color,  "NOK"),
        (f"{total_inter:.0f}",            "Total Interruptions",    "minutes cumulées",        "#D4A03C",  "MIN"),
        (f"{total_markers}",              "Total Markers",          f"{jours} jours analysés", "#1F4E79",  "PCS"),
    ]
    cols_kpi = st.columns(5)
    for col, (val, label, sublabel, color, badge) in zip(cols_kpi, kpis):
        with col:
            pct_val = None
            if label == "TPS Moyen Atelier":
                pct_val = min(tps_moyen, 100)
            elif label == "ADV Moyenne":
                pct_val = min(adv_moyen, 100)
            progress_html = ""
            if pct_val is not None:
                progress_html = f'<div class="progress-wrap"><div class="progress-fill" style="width:{pct_val:.1f}%;background:{color};"></div></div>'
            st.markdown(f"""
            <div class="kpi-card" style="--accent:{color};">
                <span class="kpi-badge">{badge}</span>
                <div class="kpi-value">{val}</div>
                <div class="kpi-label">{label}</div>
                <div class="kpi-unit">{sublabel}</div>
                {progress_html}
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    shift_options = [" Tous les shifts"]
    if 'Shift' in df.columns:
        for s in sorted(df['Shift'].unique()):
            shift_options.append(f"Shift {s}")
    if 'shift_actif' not in st.session_state:
        st.session_state.shift_actif = shift_options[0]

    tabs_html = "".join([
        f'<span class="shift-tab {"active" if t == st.session_state.shift_actif else ""}">{t}</span>'
        for t in shift_options
    ])
    st.markdown(f'<div class="shift-tabs">{tabs_html}</div>', unsafe_allow_html=True)
    shift_sel = st.selectbox("", shift_options, key="shift_select", label_visibility="collapsed")
    if shift_sel != st.session_state.shift_actif:
        st.session_state.shift_actif = shift_sel
    if 'Shift' in df.columns and shift_sel != " Tous les shifts":
        try:
            shift_num = int(shift_sel.split()[-1])
            df     = df[df['Shift'] == shift_num]
            df_tps = calculer_tps_adv(df)
        except: pass

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<div class="section-title"><span class="dot"></span> Jauge TPS Atelier</div>', unsafe_allow_html=True)
        gauge_color = tps_color
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=tps_moyen,
            number={'font':{'size':44,'color':gauge_color,'family':'Segoe UI, system-ui, sans-serif'}},
            delta={'reference':75,'increasing':{'color':"#4A6FA5"},'decreasing':{'color':"#8C2D4A"},'font':{'size':14,'family':'Segoe UI, system-ui, sans-serif'}},
            gauge={
                'axis':{'range':[0,100],'tickwidth':1,'tickcolor':colors['tick'],'tickfont':{'color':colors['tick'],'size':10,'family':'Segoe UI, system-ui, sans-serif'}},
                'bar':{'color':gauge_color,'thickness':.28},
                'bgcolor':'rgba(0,0,0,0)', 'borderwidth':0,
                'steps':[
                    {'range':[0,40],  'color':'rgba(140,45,74,.12)'},
                    {'range':[40,75], 'color':'rgba(212,160,60,.10)'},
                    {'range':[75,100],'color':'rgba(74,111,165,.10)'},
                ],
                'threshold':{'line':{'color':"#D4A03C",'width':2},'thickness':.75,'value':75}
            },
            title={'text':"TPS Moyen Atelier (%)","font":{'size':12,'color':colors['text_secondary'],'family':'Segoe UI, system-ui, sans-serif'}}
        ))
        fig_gauge.update_layout(height=280, margin=dict(t=40,b=10,l=20,r=20),
            paper_bgcolor=colors['paper'], plot_bgcolor=colors['bg'], 
            font_color=colors['text'], font_family='Segoe UI, system-ui, sans-serif')
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title"><span class="dot" style="background:#8C2D4A"></span> Alertes Machines</div>', unsafe_allow_html=True)
        critiques   = df_tps[df_tps['TPS (%)'] <  40]
        attention   = df_tps[(df_tps['TPS (%)'] >= 40) & (df_tps['TPS (%)'] < 75)]
        ok_machines = df_tps[df_tps['TPS (%)'] >= 75]
        c1, c2, c3 = st.columns(3)

        def alert_col(col, items, card_cls, badge_cls, badge_txt, head_color, head_txt, empty_txt):
            with col:
                st.markdown(f"<div style='font-size:13px;font-weight:700;color:{head_color};text-transform:uppercase;letter-spacing:.8px;margin-bottom:9px;'>{head_txt}</div>", unsafe_allow_html=True)
                if len(items) == 0:
                    st.markdown(f'<div class="{card_cls}"><div class="alert-machine" style="font-weight:400;font-size:14px;">{empty_txt}</div></div>', unsafe_allow_html=True)
                for _, r in items.iterrows():
                    extra = f"ADV : {r['ADV (%)']:.1f}%" if badge_txt == "OK" else f"Écart : {r['Écart (%)']:.1f}%"
                    st.markdown(f"""
                    <div class="{card_cls}">
                        <span class="alert-badge {badge_cls}">{badge_txt}</span>
                        <div class="alert-machine">{r['Machine']}</div>
                        <div class="alert-tps">TPS : {r['TPS (%)']:.1f}% · {extra}</div>
                    </div>""", unsafe_allow_html=True)

        alert_col(c1, critiques,   "alert-card-red",    "badge-red",    "CRITIQUE",  "#8C2D4A", "Critique",       "Aucune machine")
        alert_col(c2, attention,   "alert-card-orange", "badge-orange", "ATTENTION", "#8A6A1F", "À surveiller",   "Aucune machine")
        alert_col(c3, ok_machines, "alert-card-green",  "badge-green",  "OK",        "#2F5C8A", "Objectif atteint","Aucune machine")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    total_inter  = df['INTERRUPTIONS TIME'].sum() if 'INTERRUPTIONS TIME' in df.columns else 0
    total_coda   = df['CODA INTERRUPTIONS TIME'].sum() if 'CODA INTERRUPTIONS TIME' in df.columns else 0
    total_dt_mat = df['ΔT_Matelas'].sum() if 'ΔT_Matelas' in df.columns else 0
    st.markdown(f"""
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px;">
        <span class="mini-stat">Interruptions : <strong style="color:#8C2D4A;">{total_inter:.0f} min</strong></span>
        <span class="mini-stat">CODA : <strong style="color:#1F4E79;">{total_coda:.0f} min</strong></span>
        <span class="mini-stat">ΔT Matelas : <strong>{total_dt_mat:.0f} min</strong></span>
        <span class="mini-stat">Markers : <strong style="color:#1F4E79;">{total_markers}</strong></span>
        <span class="mini-stat">Jours : <strong style="color:#2F5C8A;">{jours}</strong></span>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title"><span class="dot" style="background:#1F4E79"></span> Résumé Performance par Machine</div>', unsafe_allow_html=True)
    rows_html = ""
    for _, r in df_tps.iterrows():
        tps = r['TPS (%)']
        if tps >= 75:   pill = "background:rgba(74,111,165,.18);color:#2F5C8A;";  statut = "OK"
        elif tps >= 40: pill = "background:rgba(212,160,60,.18);color:#8A6A1F;"; statut = "NOK"
        else:           pill = "background:rgba(140,45,74,.18);color:#8C2D4A;";  statut = "CRITIQUE"
        ecart = r['Écart (%)']
        ecart_html = f'<span style="color:#4A6FA5;">+{ecart:.1f}%</span>' if ecart >= 0 else f'<span style="color:#8C2D4A;">{ecart:.1f}%</span>'
        rows_html += f"""
        <tr>
            <td style="font-weight:700;color:{colors['text']};">{r['Machine']}</td>
            <td><span class="tps-pill" style="{pill}">{tps:.1f}%</span></td>
            <td style="color:{colors['text_secondary']};">75%</td>
            <td>{ecart_html}</td>
            <td style="color:#1F4E79;">{r['ADV (%)']:.1f}%</td>
            <td style="color:{colors['text_secondary']};">{r['Interruptions (min)']:.0f} min</td>
            <td><span class="tps-pill" style="{pill}">{statut}</span></td>
        </tr>"""
    st.markdown(f"""
    <div class="perf-wrap">
        <table class="perf-table">
            <thead><tr>
                <th>Machine</th><th>TPS (%)</th><th>Objectif</th>
                <th>Écart</th><th>ADV (%)</th><th>Interruptions</th><th>Statut</th>
            </tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>""", unsafe_allow_html=True)

# ==================== PAGE 2 : TPS ====================
def page_tps(df, df_tps):
    colors = get_plotly_colors()
    CYAN  = "#1F4E79"          # bleu marine (palette)
    VERT  = "#4A6FA5"
    ROUGE = "#8C2D4A"
    BLANC = colors['text']
    GRIS  = colors['text_secondary']
    JAUNE = "#D4A03C"          # or (objectif)
    BG    = colors['bg']
    PAL   = ['#1F4E79', '#4A6FA5', '#D4A03C', '#8C2D4A', '#9DB4C8', '#2C6E8F']

    page_header("", "TPS & Performance", "Taux de Productivité Synthétique par machine")

    # --- Cartes machines (horizontales) juste apres le bandeau ---
    if not df_tps.empty:
        cols_h = st.columns(len(df_tps))
        for i, (col, (_, row)) in enumerate(zip(cols_h, df_tps.iterrows())):
            with col:
                tps_v = row['TPS (%)']
                c = PAL[i % len(PAL)]
                st.markdown(f"""
                <div class="kpi-card" style="--accent:{c};text-align:center;">
                    <div class="kpi-value" style="color:{c};font-size:26px;">{tps_v:.1f}%</div>
                    <div class="kpi-label">{row['Machine']}</div>
                    <div class="kpi-unit">TPS</div>
                    <div class="progress-wrap"><div class="progress-fill" style="width:{min(tps_v,100):.1f}%;background:{c};"></div></div>
                </div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    tps_moyen = df_tps['TPS (%)'].mean()
    adv_moyen = df_tps['ADV (%)'].mean() if 'ADV (%)' in df_tps.columns else 0
    t_int     = df_tps['Interruptions (min)'].sum() if 'Interruptions (min)' in df_tps.columns else 0
    t_coda    = df_tps['CODA (min)'].sum()           if 'CODA (min)'          in df_tps.columns else 0

    D = max(0, min(100, 100 - (t_int / max(t_int + t_coda, 1)) * 100))
    Q = min(100, adv_moyen)
    P = min(100, tps_moyen)

    if 'DATE' in df.columns:
        tps_jour = [{'Date': d, 'TPS (%)': calculer_tps_adv(df[df['DATE']==d])['TPS (%)'].mean()}
                    for d in sorted(df['DATE'].unique())]
        df_tj = pd.DataFrame(tps_jour)
    else:
        df_tj = pd.DataFrame()

    col_left, col_right = st.columns([1, 2])

    with col_left:
        fig_trs = go.Figure(go.Indicator(
            mode="gauge+number",
            value=tps_moyen,
            number={
                'suffix': '%', 'valueformat': '.0f',
                'font': {'size': 58, 'color': CYAN, 'family': 'Segoe UI, system-ui, sans-serif'}
            },
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': '#333',
                         'tickfont': {'color': GRIS, 'size': 11, 'family': 'Segoe UI, system-ui, sans-serif'}},
                'bar': {'color': CYAN, 'thickness': 0.32},
                'bgcolor': BG, 'borderwidth': 0,
                'steps': [
                    {'range': [0,  40], 'color': 'rgba(140,45,74,.12)'},
                    {'range': [40, 75], 'color': 'rgba(212,160,60,.10)'},
                    {'range': [75,100], 'color': 'rgba(74,111,165,.10)'},
                ],
                'threshold': {'line': {'color': JAUNE, 'width': 2}, 'thickness': 0.75, 'value': 75}
            },
            title={'text': 'TPS', 'font': {'size': 20, 'color': BLANC, 'family': 'Segoe UI, system-ui, sans-serif'}}
        ))
        fig_trs.update_layout(
            height=300, margin=dict(t=60, b=5, l=20, r=20),
            paper_bgcolor=colors['paper'], plot_bgcolor=colors['bg'],
            font_color=colors['text'], font_family='Segoe UI, system-ui, sans-serif'
        )
        st.plotly_chart(fig_trs, use_container_width=True)

        # Résumé sous la jauge
        if not df_tps.empty:
            best  = df_tps.loc[df_tps['TPS (%)'].idxmax()]
            worst = df_tps.loc[df_tps['TPS (%)'].idxmin()]
            ecart = tps_moyen - 75
            st.markdown(f"""
            <div style="display:flex;flex-direction:column;gap:8px;margin-top:8px;">
              <div class="mini-stat" style="display:flex;justify-content:space-between;width:100%;"><span>Moyenne atelier</span><strong style="color:#1F4E79;">{tps_moyen:.1f}%</strong></div>
              <div class="mini-stat" style="display:flex;justify-content:space-between;width:100%;"><span>Meilleure machine</span><strong style="color:#4A6FA5;">{best['Machine']} · {best['TPS (%)']:.1f}%</strong></div>
              <div class="mini-stat" style="display:flex;justify-content:space-between;width:100%;"><span>Plus basse</span><strong style="color:#8C2D4A;">{worst['Machine']} · {worst['TPS (%)']:.1f}%</strong></div>
              <div class="mini-stat" style="display:flex;justify-content:space-between;width:100%;"><span>Écart à l'objectif</span><strong style="color:#D4A03C;">{ecart:+.1f} pts</strong></div>
            </div>""", unsafe_allow_html=True)

        def mini_cercle(val, label):
            cols_local = get_plotly_colors()
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=val,
                number={'suffix': '%', 'valueformat': '.0f',
                        'font': {'size': 26, 'color': CYAN, 'family': 'Segoe UI, system-ui, sans-serif'}},
                gauge={
                    'axis': {'range': [0, 100], 'visible': False},
                    'bar': {'color': CYAN, 'thickness': 0.28},
                    'bgcolor': 'rgba(0,212,212,.08)',
                    'bordercolor': CYAN, 'borderwidth': 1,
                },
                title={'text': label, 'font': {'size': 16, 'color': cols_local['text'], 'family': 'Segoe UI, system-ui, sans-serif'}},
                domain={'x': [0, 1], 'y': [0, 1]}
            ))
            fig.update_layout(height=200, margin=dict(t=45, b=15, l=25, r=25),
                paper_bgcolor=cols_local['paper'], plot_bgcolor=cols_local['bg'],
                font_color=cols_local['text'], font_family='Segoe UI, system-ui, sans-serif')
            return fig

    with col_right:
        st.markdown('<div class="section-title"><span class="dot" style="background:#1F4E79"></span> Evolution du TPS</div>', unsafe_allow_html=True)
        if not df_tj.empty:
            dmin = df_tj['TPS (%)'].min(); dmax = df_tj['TPS (%)'].max()
            y_lo = max(0, min(dmin, 75) - 12)
            y_hi = max(dmax, 75) + 10
            fig_evol = go.Figure()
            fig_evol.add_trace(go.Scatter(
                x=df_tj['Date'], y=df_tj['TPS (%)'],
                mode='lines+markers',
                line=dict(color=CYAN, width=3, shape='spline'),
                marker=dict(size=7, color=CYAN, line=dict(color='#ffffff', width=1)),
                fill='tozeroy', fillcolor='rgba(31,78,121,.08)',
                name='TPS', hovertemplate='%{x|%d %b}<br>TPS %{y:.1f}%<extra></extra>'
            ))
            fig_evol.add_trace(go.Scatter(
                x=df_tj['Date'], y=[75]*len(df_tj),
                mode='lines', name='Objectif 75%',
                line=dict(color=JAUNE, dash='dot', width=1.5)
            ))
            fig_evol.update_layout(**pl(yaxis_title="TPS (%)", yaxis_range=[y_lo, y_hi], height=300,
                legend=dict(font=dict(color=BLANC, size=12))))
            st.plotly_chart(fig_evol, use_container_width=True)
        else:
            st.info("Pas de données temporelles disponibles.")

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        st.markdown('<div class="section-title"><span class="dot" style="background:#1F4E79"></span> TPS par Machine</div>', unsafe_allow_html=True)
        colors_m = [PAL[i % len(PAL)] for i in range(len(df_tps))]
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=df_tps['Machine'], y=df_tps['TPS (%)'],
            marker_color=colors_m, marker_line_color='rgba(0,0,0,0)',
            name='TPS Réel',
            text=[f"{v:.1f}%" for v in df_tps['TPS (%)']],
            textposition='outside',
            textfont=dict(size=12, color=BLANC, family='Segoe UI, system-ui, sans-serif')
        ))
        fig_bar.add_trace(go.Scatter(
            x=df_tps['Machine'], y=[75]*len(df_tps),
            mode='lines', name='Objectif 75%',
            line=dict(color='#D4A03C', width=1.5, dash='dot')
        ))
        if 'ADV (%)' in df_tps.columns:
            fig_bar.add_trace(go.Scatter(
                x=df_tps['Machine'], y=df_tps['ADV (%)'],
                mode='lines+markers', name='ADV (%)',
                line=dict(color='#8C2D4A', width=2),
                marker=dict(size=6, color='#8C2D4A')
            ))
        fig_bar.update_layout(**pl(yaxis_title="(%)", yaxis_range=[0, 110], height=300,
            bargap=0.32, legend=dict(font=dict(color=BLANC, size=12))))
        st.plotly_chart(fig_bar, use_container_width=True)

# ==================== PAGE 3 : PERTES ====================
def page_pertes(df, df_tps):
    colors = get_plotly_colors()
    page_header("", "Analyse des Pertes", "Interruptions, CODA, DT_POSIT, POSIT/Marker et ΔT_Matelas par machine")

    t_int  = df_tps['Interruptions (min)'].sum()
    t_coda = df_tps['CODA (min)'].sum()
    t_pos  = df_tps['DT_POSIT (min)'].sum()
    t_pm   = df_tps['POSIT/Marker'].sum()
    t_mat  = df_tps['ΔT_Matelas (min)'].sum()
    total  = t_int + t_coda + t_pos + t_pm + t_mat

    kpi_cols = st.columns(5)
    for col, val, lbl, color in [
        (kpi_cols[0], f"{t_int:.0f}", "Interruptions (min)", "#1F4E79"),
        (kpi_cols[1], f"{t_coda:.0f}", "CODA (min)",          "#8C2D4A"),
        (kpi_cols[2], f"{t_pos:.0f}",  "DT_POSIT (min)",      "#D4A03C"),
        (kpi_cols[3], f"{t_pm:.0f}",   "POSIT/Marker",        "#4A6FA5"),
        (kpi_cols[4], f"{t_mat:.0f}",  "ΔT_Matelas (min)",    "#9DB4C8"),
    ]:
        with col:
            st.markdown(f"""<div class="kpi-card" style="--accent:{color};">
                <div class="kpi-value" style="font-size:26px;">{val}</div>
                <div class="kpi-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title"><span class="dot"></span> Pertes empilées par machine</div>', unsafe_allow_html=True)
        fig = go.Figure()
        for name, col_name, color in [
            ('Interruptions','Interruptions (min)','#1F4E79'),
            ('CODA','CODA (min)','#8C2D4A'),
            ('DT_POSIT','DT_POSIT (min)','#D4A03C'),
            ('POSIT/Marker','POSIT/Marker','#4A6FA5'),
            ('ΔT_Matelas','ΔT_Matelas (min)','#9DB4C8'),
        ]:
            fig.add_trace(go.Bar(name=name, x=df_tps['Machine'], y=df_tps[col_name], marker_color=color))
        fig.update_layout(**pl(yaxis_title="Minutes", height=380), barmode='stack')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title"><span class="dot"></span> Répartition globale</div>', unsafe_allow_html=True)
        fig_pie = px.pie(values=[t_int,t_coda,t_pos,t_pm,t_mat],
            names=['Interruptions','CODA','DT_POSIT','POSIT/Marker','ΔT_Matelas'],
            color_discrete_sequence=['#1F4E79','#8C2D4A','#D4A03C','#4A6FA5','#9DB4C8'], hole=0.45)
        fig_pie.update_traces(textinfo='percent+label', textfont_size=11, textfont_family='Segoe UI, system-ui, sans-serif')
        fig_pie.update_layout(**pl(height=380))
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-title"><span class="dot"></span> Pareto des Pertes</div>', unsafe_allow_html=True)
    pareto = pd.DataFrame({'Source':['Interruptions','CODA','DT_POSIT','POSIT/Marker','ΔT_Matelas'],
        'Total (min)':[t_int,t_coda,t_pos,t_pm,t_mat]}).sort_values('Total (min)',ascending=False)
    pareto['Cumul (%)'] = pareto['Total (min)'].cumsum() / pareto['Total (min)'].sum() * 100
    fig_p = go.Figure()
    fig_p.add_trace(go.Bar(x=pareto['Source'],y=pareto['Total (min)'],
        marker_color=['#1F4E79','#8C2D4A','#D4A03C','#4A6FA5','#9DB4C8'],
        text=[f"{v:.0f}" for v in pareto['Total (min)']],textposition='outside',name='min'))
    fig_p.add_trace(go.Scatter(x=pareto['Source'],y=pareto['Cumul (%)'],
        mode='lines+markers+text',text=[f"{v:.0f}%" for v in pareto['Cumul (%)']],
        textposition='top center',name='Cumul %',yaxis='y2',
        line=dict(color='#1F4E79',width=2),marker=dict(size=7)))
    fig_p.add_hline(y=80,line_dash="dash",line_color="#D4A03C",annotation_text="80%",yref='y2')
    fig_p.update_layout(**pl(yaxis_title="Durée (min)", height=400),
        yaxis2=dict(title="Cumul (%)",overlaying='y',side='right',range=[0,110],
                    tickfont=dict(size=11, family='Segoe UI, system-ui, sans-serif'),gridcolor='rgba(0,0,0,0)'))
    st.plotly_chart(fig_p, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-title"><span class="dot"></span> Tableau détaillé</div>', unsafe_allow_html=True)
    cols_p = ['Machine','Interruptions (min)','CODA (min)','DT_POSIT (min)','POSIT/Marker','ΔT_Matelas (min)','Cutting (min)','TPS (%)']
    st.dataframe(df_tps[cols_p], use_container_width=True, hide_index=True)

# ==================== PAGE 4 : ADV ====================
def page_adv(df, df_tps):
    colors = get_plotly_colors()
    page_header("", "ADV — Adhérence au Volume", "Suivi journalier de la production réalisée vs planifiée")
    if 'DATE' not in df.columns or 'ADV' not in df.columns:
        st.warning("Colonnes DATE ou ADV non disponibles.")
        return

    df_adv = df.groupby('DATE').apply(lambda x: pd.to_numeric(x['ADV'],errors='coerce').mean()*100).reset_index()
    df_adv.columns = ['DATE','ADV (%)']
    df_adv = df_adv.dropna()

    adv_moy = df_adv['ADV (%)'].mean()
    adv_min = df_adv['ADV (%)'].min()
    adv_max = df_adv['ADV (%)'].max()
    j_nok   = len(df_adv[df_adv['ADV (%)'] < 100])

    kpi_cols = st.columns(4)
    for col, val, lbl, color in [
        (kpi_cols[0], f"{adv_moy:.1f}%", "ADV Moyenne",       "#1F4E79"),
        (kpi_cols[1], f"{adv_min:.1f}%", "ADV Minimale",      "#8C2D4A"),
        (kpi_cols[2], f"{adv_max:.1f}%", "ADV Maximale",      "#4A6FA5"),
        (kpi_cols[3], f"{j_nok}j",       "Jours sous objectif","#D4A03C"),
    ]:
        with col:
            st.markdown(f"""<div class="kpi-card" style="--accent:{color};">
                <div class="kpi-value" style="font-size:28px;">{val}</div>
                <div class="kpi-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span class="dot"></span> ADV journalière vs Objectif</div>', unsafe_allow_html=True)
    colors_adv = ['#4A6FA5' if v >= 100 else '#8C2D4A' for v in df_adv['ADV (%)']]
    fig_adv = go.Figure()
    fig_adv.add_trace(go.Bar(x=df_adv['DATE'],y=df_adv['ADV (%)'],marker_color=colors_adv,name='ADV Réelle',
        text=[f"{v:.1f}%" for v in df_adv['ADV (%)']],textposition='outside',textfont=dict(size=13, family='Segoe UI, system-ui, sans-serif')))
    fig_adv.add_trace(go.Scatter(x=df_adv['DATE'],y=[100]*len(df_adv),mode='lines',name='Objectif 100%',
        line=dict(color='#D4A03C',width=2,dash='dash')))
    fig_adv.update_layout(**pl(yaxis_title="ADV (%)", yaxis_range=[0,110], height=360))
    st.plotly_chart(fig_adv, use_container_width=True)

    st.markdown('<div class="section-title"><span class="dot"></span> ADV par Machine</div>', unsafe_allow_html=True)
    df_adv_m = df_tps[df_tps['ADV (%)'] > 0][['Machine','ADV (%)']]
    if not df_adv_m.empty:
        fig_adv_m = go.Figure(go.Bar(x=df_adv_m['Machine'],y=df_adv_m['ADV (%)'],
            marker_color=['#4A6FA5' if v >= 100 else '#8C2D4A' for v in df_adv_m['ADV (%)']],
            text=[f"{v:.1f}%" for v in df_adv_m['ADV (%)']],textposition='outside'))
        fig_adv_m.add_hline(y=100,line_dash="dash",line_color="#D4A03C",annotation_text="Objectif 100%")
        fig_adv_m.update_layout(**pl(yaxis_title="ADV (%)", yaxis_range=[0,110], height=320))
        st.plotly_chart(fig_adv_m, use_container_width=True)

# ==================== PAGE 5 : MACHINE ====================
def page_machine(df, df_tps):
    colors = get_plotly_colors()
    page_header("", "Analyse Détaillée par Machine", "Sélectionnez une machine pour son analyse complète")
    machine_sel = st.selectbox("Choisir une machine :", sorted(df['Machine'].unique()))
    df_m   = df[df['Machine'] == machine_sel]
    row    = df_tps[df_tps['Machine'] == machine_sel].iloc[0]
    tps_v  = row['TPS (%)']
    color  = "#4A6FA5" if tps_v >= 75 else "#D4A03C" if tps_v >= 40 else "#8C2D4A"

    kpi_cols = st.columns(5)
    for col, val, lbl, c in [
        (kpi_cols[0], f"{tps_v:.1f}%",                "TPS",           color),
        (kpi_cols[1], f"{row['Interruptions (min)']:.0f} min","Interruptions","#1F4E79"),
        (kpi_cols[2], f"{row['CODA (min)']:.0f} min",  "CODA",          "#8C2D4A"),
        (kpi_cols[3], f"{row['DT_POSIT (min)']:.0f} min","DT_POSIT",   "#D4A03C"),
        (kpi_cols[4], f"{row['ΔT_Matelas (min)']:.0f} min","ΔT_Matelas","#9DB4C8"),
    ]:
        with col:
            st.markdown(f"""<div class="kpi-card" style="--accent:{c};">
                <div class="kpi-value" style="font-size:22px;">{val}</div>
                <div class="kpi-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number+delta", value=tps_v,
            number={'suffix':'%','font':{'size':40,'color':color,'family':'Segoe UI, system-ui, sans-serif'}},
            delta={'reference':75},
            gauge={'axis':{'range':[0,100],'tickfont':{'size':11,'color':colors['tick']}},'bar':{'color':color,'thickness':0.3},
                'steps':[{'range':[0,40],'color':'rgba(140,45,74,.12)'},{'range':[40,75],'color':'rgba(212,160,60,.10)'},{'range':[75,100],'color':'rgba(74,111,165,.10)'}],
                'threshold':{'line':{'color':"#D4A03C",'width':2},'thickness':.75,'value':75}},
            title={'text':f"TPS {machine_sel} (%)","font":{'color':colors['text'],'family':'Segoe UI, system-ui, sans-serif'}}
        ))
        fig_g.update_layout(height=260, margin=dict(t=50,b=10,l=20,r=20),
            paper_bgcolor=colors['paper'], plot_bgcolor=colors['bg'],
            font_color=colors['text'], font_family='Segoe UI, system-ui, sans-serif')
        st.plotly_chart(fig_g, use_container_width=True)

    with col2:
        fig_pie = px.pie(
            values=[row['Interruptions (min)'],row['CODA (min)'],row['DT_POSIT (min)'],row['POSIT/Marker'],row['ΔT_Matelas (min)']],
            names=['Interruptions','CODA','DT_POSIT','POSIT/Marker','ΔT_Matelas'],
            color_discrete_sequence=['#1F4E79','#8C2D4A','#D4A03C','#4A6FA5','#9DB4C8'], hole=0.42)
        fig_pie.update_traces(textinfo='percent+label', textfont_family='Segoe UI, system-ui, sans-serif')
        fig_pie.update_layout(**pl(height=260, margin=dict(t=20,b=10)))
        st.plotly_chart(fig_pie, use_container_width=True)

    if 'DATE' in df_m.columns:
        st.markdown("---")
        evol = df_m.groupby('DATE')['CUTTING TIME'].sum().reset_index()
        fig_e = px.line(evol,x='DATE',y='CUTTING TIME',markers=True,
            title=f"Temps de coupe — {machine_sel}")
        fig_e.update_traces(line=dict(color='#1F4E79', width=3, shape='spline'),
                            marker=dict(size=7, color='#1F4E79'))
        fig_e.update_layout(**pl(height=280))
        st.plotly_chart(fig_e, use_container_width=True)

    st.markdown("---")
    cols_show = [c for c in ['DATE','Marker','CUTTING TIME','INTERRUPTIONS TIME','CODA INTERRUPTIONS TIME','DT_POSIT (min)','POSIT/Marker','ΔT_Matelas','STATE'] if c in df_m.columns]
    st.dataframe(df_m[cols_show], use_container_width=True, hide_index=True)

# ==================== PAGE 6 : DONNEES ====================
def page_donnees(df, df_tps):
    colors = get_plotly_colors()
    page_header("", "Données Brutes", "Tableau complet avec filtres et export")
    col1, col2, col3 = st.columns(3)
    with col1:
        filtre_m = st.selectbox("Machine", ['Toutes'] + sorted(df['Machine'].unique().tolist()))
    with col2:
        filtre_d = st.selectbox("Date", ['Toutes'] + sorted(df['DATE'].unique().tolist(), reverse=True)) if 'DATE' in df.columns else 'Toutes'
    with col3:
        filtre_s = st.selectbox("Statut", ['Tous'] + sorted(df['STATE'].dropna().unique().tolist())) if 'STATE' in df.columns else 'Tous'

    df_f = df.copy()
    if filtre_m != 'Toutes': df_f = df_f[df_f['Machine'] == filtre_m]
    if filtre_d != 'Toutes' and 'DATE' in df_f.columns: df_f = df_f[df_f['DATE'] == filtre_d]
    if filtre_s != 'Tous' and 'STATE' in df_f.columns: df_f = df_f[df_f['STATE'] == filtre_s]

    st.markdown(f"""<div class="toast-bar"><strong>{len(df_f)}</strong> lignes affichées sur <strong>{len(df)}</strong> total</div>""", unsafe_allow_html=True)

    cols_show = [c for c in ['DATE','Machine','Marker','CUTTING TIME','INTERRUPTIONS TIME','CODA INTERRUPTIONS TIME','DT_POSIT (min)','POSIT/Marker','ΔT_Matelas','STATE'] if c in df_f.columns]
    if st.session_state.role == "admin":
        st.caption("Mode édition admin — double-cliquez pour modifier")
        st.data_editor(df_f[cols_show], use_container_width=True, hide_index=True)
    else:
        st.dataframe(df_f[cols_show], use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown('<div class="section-title"><span class="dot"></span> Export</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("Données filtrées (CSV)", data=df_f.to_csv(index=False).encode('utf-8'),
            file_name=f"lectra_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv", use_container_width=True)
    with c2:
        st.download_button("Tableau TPS/ADV (CSV)", data=df_tps.to_csv(index=False).encode('utf-8'),
            file_name=f"tps_adv_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv", use_container_width=True)

# ==================== MAIN ====================
def main():
    if not verifier_mot_de_passe():
        return

    sidebar_navigation()

    df = charger_donnees()
    if df is None or df.empty:
        st.warning("Aucune donnée trouvée.")
        st.stop()

    if 'DATE' in df.columns and not df.empty:
        st.sidebar.markdown("---")
        st.sidebar.markdown("<div style='font-size:12px;color:#9fb6c4;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;padding:0 4px 6px;'>Filtre par date</div>", unsafe_allow_html=True)
        dates_dispo = sorted(df['DATE'].unique())
        date_min = dates_dispo[0]; date_max = dates_dispo[-1]
        date_debut = pd.to_datetime(st.sidebar.date_input("Début", value=date_min, min_value=date_min, max_value=date_max))
        date_fin   = pd.to_datetime(st.sidebar.date_input("Fin",   value=date_max, min_value=date_min, max_value=date_max))
        df_filtre = df[(df['DATE'] >= date_debut) & (df['DATE'] <= date_fin)]
        if df_filtre.empty:
            st.warning(f"Aucune donnée entre {date_debut.strftime('%d/%m/%Y')} et {date_fin.strftime('%d/%m/%Y')}")
            st.stop()
        st.sidebar.info(f"**{date_debut.strftime('%d/%m/%Y')}** → **{date_fin.strftime('%d/%m/%Y')}**")
    else:
        df_filtre = df

    df_tps = calculer_tps_adv(df_filtre)

    page = st.session_state.get('page_active', 'Accueil')
    if   page == "Accueil":             page_accueil(df_filtre, df_tps)
    elif page == "TPS & Performance":   page_tps(df_filtre, df_tps)
    elif page == "Analyse des Pertes":  page_pertes(df_filtre, df_tps)
    elif page == "ADV Production":      page_adv(df_filtre, df_tps)
    elif page == "Analyse par Machine": page_machine(df_filtre, df_tps)
    elif page == "Données Brutes":      page_donnees(df_filtre, df_tps)

    st.markdown("""
    <div style='text-align:center;color:#94a3b8;font-size:13px;padding:20px 0 10px;letter-spacing:.5px;'>
        Adient Morocco — LECTRA Dashboard v5.0 &nbsp;|&nbsp; Projet PFE 2025 &nbsp;|&nbsp; Tiflet
    </div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
