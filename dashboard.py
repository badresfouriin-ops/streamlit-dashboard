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
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS ====================
# Palette image de reference :
# Fond       : #000000  Sidebar  : #0a0a0a
# Cyan       : #00d4d4  Vert     : #00e676
# Rouge      : #ff1744  Jaune    : #ffc107
# Blanc      : #ffffff  Gris     : #8b949e
# Bordure    : #1f1f1f  Card bg  : #0a0a0a
st.markdown("""
<style>
* { font-family: 'Times New Roman', Times, serif !important; }

/* ── Base fond noir bleu comme l'image ── */
html, body, [data-testid="stAppViewContainer"], .main {
    background: #000000 !important;
    color: #ffffff !important;
}
[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding-top: 1.2rem !important; max-width: 100% !important; }

/* ── KPI Cards ── */
.kpi-card {
    background: #0a0a0a;
    border-radius: 12px;
    padding: 20px 16px 16px;
    border: 1px solid #1f1f1f;
    position: relative; overflow: hidden;
    transition: transform .3s, box-shadow .3s, border-color .3s;
    margin-bottom: 8px;
}
.kpi-card::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: var(--accent, #00d4d4);
    border-radius: 12px 12px 0 0;
}
.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 32px rgba(0,212,212,.15);
    border-color: var(--accent, #00d4d4);
}
.kpi-value { font-size:36px; font-weight:800; color:var(--accent,#00d4d4); line-height:1.1; letter-spacing:-1px; }
.kpi-label { font-size:11px; color:#8b949e; margin-top:6px; font-weight:600; letter-spacing:.5px; text-transform:uppercase; }
.kpi-unit  { font-size:11px; color:#4a5568; margin-top:3px; }
.kpi-badge {
    position:absolute; top:14px; right:14px;
    font-size:9px; font-weight:700; letter-spacing:.8px; text-transform:uppercase;
    padding:2px 7px; border-radius:20px;
    background:rgba(0,212,212,.1); color:#00d4d4;
}

/* ── Page Header ── */
.page-header {
    background: linear-gradient(135deg, #0a0a0a, #0a0a0a);
    border: 1px solid #1f1f1f;
    border-left: 4px solid #00d4d4;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
    position: relative; overflow: hidden;
}
.page-header::after {
    content:''; position:absolute;
    top:-40px; right:-40px;
    width:140px; height:140px; border-radius:50%;
    background:rgba(0,212,212,.05);
}
.page-header h1 {
    font-size:22px !important; font-weight:800 !important;
    letter-spacing:-.5px; margin:0 !important; color:#ffffff !important;
}
.page-header p { margin:4px 0 0 !important; opacity:.5; font-size:12px !important; color:#8b949e !important; }
.header-badge {
    display:inline-block; font-size:10px; font-weight:700;
    letter-spacing:1px; text-transform:uppercase;
    background:rgba(0,212,212,.1); color:#00d4d4;
    border:1px solid rgba(0,212,212,.3);
    padding:3px 10px; border-radius:20px; margin-top:8px;
}

/* ── Status Bar ── */
.status-bar {
    display:flex; align-items:center; gap:18px; flex-wrap:wrap;
    background:#0a0a0a;
    border:1px solid #1f1f1f;
    border-radius:10px;
    padding:9px 18px; margin-bottom:16px;
    font-size:12px; color:#8b949e;
}
.status-dot { width:7px; height:7px; border-radius:50%; display:inline-block; margin-right:5px; }
.status-online { background:#00e676; box-shadow:0 0 8px #00e676; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:.5;} }

/* ── Alert Cards ── */
.alert-card-red    { background:rgba(255,23,68,.08);  border:1px solid rgba(255,23,68,.25);  border-left:3px solid #ff1744; border-radius:10px; padding:11px 13px; margin-bottom:7px; transition:background .2s; }
.alert-card-orange { background:rgba(255,193,7,.08);  border:1px solid rgba(255,193,7,.25);  border-left:3px solid #ffc107; border-radius:10px; padding:11px 13px; margin-bottom:7px; transition:background .2s; }
.alert-card-green  { background:rgba(0,230,118,.08);  border:1px solid rgba(0,230,118,.25);  border-left:3px solid #00e676; border-radius:10px; padding:11px 13px; margin-bottom:7px; transition:background .2s; }
.alert-card-red:hover    { background:rgba(255,23,68,.14); }
.alert-card-orange:hover { background:rgba(255,193,7,.14); }
.alert-card-green:hover  { background:rgba(0,230,118,.14); }
.alert-machine { font-weight:700; font-size:13px; color:#ffffff; }
.alert-tps     { font-size:11px; color:#8b949e; margin-top:2px; }
.alert-badge   { display:inline-block; font-size:9px; font-weight:700; letter-spacing:.8px; padding:2px 6px; border-radius:4px; text-transform:uppercase; float:right; }
.badge-red     { background:rgba(255,23,68,.2);  color:#ff6b8a; }
.badge-orange  { background:rgba(255,193,7,.2);  color:#ffc107; }
.badge-green   { background:rgba(0,230,118,.2);  color:#00e676; }

/* ── Section Titles ── */
.section-title {
    font-size:13px; font-weight:700; color:#ffffff;
    display:flex; align-items:center; gap:8px;
    padding-bottom:9px; border-bottom:1px solid #1f1f1f; margin-bottom:14px;
}
.section-title .dot { width:7px; height:7px; border-radius:50%; background:#00d4d4; display:inline-block; flex-shrink:0; }

/* ── Tabs ── */
.tab-bar { display:flex; gap:6px; margin-bottom:16px; flex-wrap:wrap; }
.tab-btn {
    font-size:12px; font-weight:600; padding:6px 16px;
    border-radius:20px; cursor:pointer;
    background:#0a0a0a; border:1px solid #1f1f1f;
    color:#8b949e; transition:all .15s;
}
.tab-btn.active { background:rgba(0,212,212,.12); border-color:#00d4d4; color:#00d4d4; }
.shift-tabs { display:flex; gap:6px; margin-bottom:14px; flex-wrap:wrap; }
.shift-tab {
    font-size:11px; font-weight:600; padding:5px 14px;
    border-radius:20px; cursor:pointer;
    background:#0a0a0a; border:1px solid #1f1f1f;
    color:#8b949e; transition:all .15s; user-select:none;
}
.shift-tab:hover  { border-color:#00d4d4; color:#00d4d4; }
.shift-tab.active { background:rgba(0,212,212,.12); border-color:#00d4d4; color:#00d4d4; }

/* ── Perf Table ── */
.perf-table { width:100%; border-collapse:collapse; }
.perf-table th {
    font-size:10px; font-weight:700; color:#8b949e;
    text-transform:uppercase; letter-spacing:.8px;
    padding:10px 12px; background:#0a0a0a;
    border-bottom:1px solid #1f1f1f; text-align:left;
}
.perf-table td { padding:10px 12px; font-size:12px; color:#ffffff; border-bottom:1px solid #1f1f1f; }
.perf-table tr:hover td { background:rgba(0,212,212,.04); }
.tps-pill { display:inline-block; font-weight:700; font-size:11px; padding:2px 9px; border-radius:20px; }

/* ── Toast ── */
.toast-bar {
    background: rgba(0,212,212,.08);
    border:1px solid rgba(0,212,212,.2);
    border-radius:10px; padding:10px 16px; margin-bottom:16px;
    font-size:12px; color:#00d4d4; display:flex; align-items:center; gap:8px;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0a0a0a !important;
    border-right:1px solid #1f1f1f !important;
}
[data-testid="stSidebar"] * { color:#e2e8f0 !important; }
[data-testid="stSidebar"] .stButton button {
    background:#0a0a0a !important;
    border:1px solid #1f1f1f !important;
    border-radius:8px !important;
    color:#e2e8f0 !important;
    font-size:13px !important;
    transition:all .2s !important;
    text-align:left !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background:rgba(0,212,212,.1) !important;
    border-color:#00d4d4 !important;
    color:#00d4d4 !important;
}

/* ── Charts ── */
.js-plotly-plot .plotly { border-radius:12px; overflow:hidden; }
div[data-testid="stDataFrame"] { border-radius:10px; overflow:hidden; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#000000; }
::-webkit-scrollbar-thumb { background:#1f1f1f; border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background:#00d4d4; }

/* ── Mini stat ── */
.mini-stat {
    display:inline-flex; align-items:center; gap:5px;
    font-size:11px; color:#8b949e;
    background:rgba(0,212,212,.05);
    border:1px solid #1f1f1f;
    border-radius:6px; padding:3px 8px;
}

/* ── Progress bar ── */
.progress-wrap { background:#1f1f1f; border-radius:4px; height:6px; margin-top:6px; overflow:hidden; }
.progress-fill { height:6px; border-radius:4px; transition:width .6s ease; }

/* ── Animated KPI counter ── */
@keyframes countUp { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }
.kpi-value { animation: countUp .5s ease forwards; }

/* ── Dividers ── */
hr { border-color:#1f1f1f !important; }
</style>
""", unsafe_allow_html=True)

# ==================== AUTH ====================
USERS = {
    "admin123":  {"role": "admin",  "nom": "Administrateur"},
    "invite123": {"role": "invite", "nom": "Invité"},
    "chef123":   {"role": "chef",   "nom": "Chef d'atelier"},
}

def get_base64_of_bin_file(bin_file):
    """Convertit un fichier en base64 pour l'affichage en arrière-plan"""
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

    # ---- ENCODAGE DE L'IMAGE D'ARRIÈRE-PLAN EN BASE64 ----
    bg_image_path = "background.png" # Assurez-vous que l'image est à côté du script sous ce nom
    img_base64 = ""
    
    if os.path.exists(bg_image_path):
        with open(bg_image_path, "rb") as image_file:
            img_base64 = base64.b64encode(image_file.read()).decode()
        bg_css = f"background: url(data:image/png;base64,{img_base64}) no-repeat center center fixed !important; background-size: cover !important;"
    else:
        # Dégradé par défaut si l'image est manquante
        bg_css = "background: linear-gradient(135deg, #0a0f1e 0%, #1a2332 50%, #0d1b2a 100%) !important;"

    st.markdown(f"""
    <style>
    /* Masquer les éléments Streamlit par défaut */
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stSidebar"] {{ display: none !important; }}
    
    /* Container principal avec l'image de fond */
    [data-testid="stAppViewContainer"] {{ 
        {bg_css}
    }}
    
    /* Overlay semi-transparent pour améliorer la lisibilité */
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.55);
        z-index: 0;
        pointer-events: none;
    }}
    
    /* Contenu au-dessus de l'overlay */
    .main, .block-container {{ 
        position: relative; 
        z-index: 1; 
    }}
    
    .block-container {{ 
        padding: 0 !important; 
        max-width: 100% !important; 
    }}
    
    /* Style des champs de formulaire */
    .stTextInput input {{
        background: #f8fafc !important;
        border: 1px solid #d7dee8 !important;
        border-radius: 6px !important;
        height: 36px !important;
        font-size: 13px !important;
        padding: 0 10px !important;
        color: #000 !important;
    }}
    
    .stTextInput input:focus {{
        border-color: #9cc31a !important;
        box-shadow: 0 0 0 2px rgba(156,195,26,0.2) !important;
        outline: none !important;
    }}
    
    /* Style du bouton de connexion */
    .stButton button {{
        background: #003f52 !important;
        color: white !important;
        height: 38px !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
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
        font-size: 11px !important; 
    }}
    
    div[data-testid="column"] {{ 
        gap: 0px !important; 
    }}
    
    /* Style personnalisé pour les labels */
    .login-label {{
        text-align: left;
        font-size: 12px;
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
            <div style="font-size: 12px; font-weight: 700; color: #9cc31a; margin-bottom: 15px;">
                ATELIER DE COUPE
            </div>
            <div style="height: 1px; background: linear-gradient(90deg, transparent, #9cc31a, transparent); margin-bottom: 20px;"></div>
        """, unsafe_allow_html=True)

        st.markdown("<p class='login-label'> Nom d'utilisateur</p>", unsafe_allow_html=True)
        username = st.text_input("", placeholder="Entrez votre nom d'utilisateur", key="login_user", label_visibility="collapsed")

        st.markdown("<p class='login-label' style='margin-top: 10px;'>🔐 Mot de passe</p>", unsafe_allow_html=True)
        password = st.text_input("", type="password", placeholder="Entrez votre mot de passe", key="login_pwd", label_visibility="collapsed")

        col_check, col_forgot = st.columns([1, 1])
        with col_check:
            st.checkbox("Se souvenir de moi")
        with col_forgot:
            st.markdown("<div style='text-align: right; padding-top: 3px;'><a href='#' style='color: #9cc31a; font-size: 11px; text-decoration: none;'>Mot de passe oublié ?</a></div>", unsafe_allow_html=True)

        if st.button(" SE CONNECTER", use_container_width=True):
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
                <p style="color: #00334e; font-size: 11px; font-weight: 700; letter-spacing: 2px; margin-bottom: 12px;">
                    ADIENT MOROCCO — TIFLET
                </p>
                <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin-bottom: 10px;">
                    <div style="font-size: 11px; font-weight: 500; color: #555;">
                        <span style="color: #9cc31a;">⏱️</span> TEMPS RÉEL
                    </div>
                    <div style="font-size: 11px; font-weight: 500; color: #555;">
                        <span style="color: #9cc31a;"></span> KPIs
                    </div>
                    <div style="font-size: 11px; font-weight: 500; color: #555;">
                        <span style="color: #9cc31a;">🎯</span> OBJECTIFS
                    </div>
                    <div style="font-size: 11px; font-weight: 500; color: #555;">
                        <span style="color: #9cc31a;">📈</span> AMÉLIORATION
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div style="text-align: center; margin-top: 18px; padding-top: 12px; border-top: 1px solid #eee;">
                <span style="color: #9cc31a;"></span>
                <span style="color: #888; font-size: 10px;"> Accès sécurisé</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    return False
# ==================== SIDEBAR ====================
def sidebar_navigation():
    with st.sidebar:
        st.markdown("<br>", unsafe_allow_html=True)

        # Logo
        st.markdown("""
        <div style="text-align:center;padding:0 8px 16px;border-bottom:1px solid #21262d;margin-bottom:14px;">
            <div style="font-size:22px;font-weight:800;color:#f0f6ff;letter-spacing:-1px;">
                <span style="color:#9cc31a;">/</span>ADIENT
            </div>
            <div style="font-size:9px;color:#9cc31a;letter-spacing:2.5px;text-transform:uppercase;margin-top:1px;">Atelier de Coupe</div>
        </div>
        """, unsafe_allow_html=True)

        # User card
        role_color = {"admin":"#00d4d4","chef":"#ffc107","invite":"#8b949e"}.get(st.session_state.role,"#8b949e")
        role_icon  = {"admin":"","chef":"","invite":""}.get(st.session_state.role,"")
        st.markdown(f"""
        <div style="text-align:center;padding:14px 10px;
            background:linear-gradient(145deg,rgba(15,23,42,.9),rgba(17,24,39,.9));
            border:1px solid rgba(255,255,255,.05);border-radius:12px;margin-bottom:12px;">
            <div style="font-size:30px;margin-bottom:5px;">{role_icon}</div>
            <div style="font-size:14px;font-weight:700;color:#ffffff;">{st.session_state.nom_user}</div>
            <div style="font-size:9px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:{role_color};margin-top:3px;">{st.session_state.role}</div>
        </div>
        """, unsafe_allow_html=True)

        # Access badge
        if st.session_state.role == "admin":
            st.success(" Accès complet")
        elif st.session_state.role == "chef":
            st.warning(" Chef d'atelier")
        else:
            st.info(" Lecture seule")

        st.markdown("---")
        st.markdown("<div style='font-size:10px;color:#8b949e;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;padding:0 4px 6px;'>Navigation</div>", unsafe_allow_html=True)

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
            if st.button(f"{icon}  {nom}", key=f"nav_{nom}", use_container_width=True, help=desc):
                st.session_state.page_active = nom
                st.rerun()

        st.markdown("---")

        # Theme switcher
        st.markdown("<div style='font-size:10px;color:#8b949e;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;padding:0 4px 6px;'>Apparence</div>", unsafe_allow_html=True)
        theme = st.radio("", ["Dark", "Light"], horizontal=True,
                         index=0 if st.session_state.get('theme','dark')=='dark' else 1,
                         key="theme_radio", label_visibility="collapsed")
        new_theme = "dark" if theme == "Dark" else "light"
        if new_theme != st.session_state.get('theme','dark'):
            st.session_state.theme = new_theme
            st.rerun()
        if st.session_state.get('theme','dark') == 'light':
            st.markdown("""
            <style>
            html, body, [data-testid="stAppViewContainer"],
            [data-testid="stAppViewContainer"] > .main, .main, .block-container {
                background: #f1f5f9 !important; color: #0f172a !important;
            }
            [data-testid="stAppViewContainer"] *, .main * { color: #0f172a !important; }
            [data-testid="stSidebar"] { background: linear-gradient(180deg,#1e293b 0%,#0f172a 100%) !important; border-right:1px solid #334155 !important; }
            [data-testid="stSidebar"] * { color:#e2e8f0 !important; }
            [data-testid="stSidebar"] .stButton button { background:rgba(255,255,255,.06) !important; border:1px solid #334155 !important; color:#e2e8f0 !important; }
            [data-testid="stSidebar"] .stButton button:hover { background:rgba(59,130,246,.18) !important; border-color:#3b82f6 !important; color:#93c5fd !important; }
            .kpi-card { background:#ffffff !important; border:1px solid #e2e8f0 !important; box-shadow:0 2px 12px rgba(0,0,0,.06) !important; }
            .kpi-label { color:#64748b !important; } .kpi-unit { color:#94a3b8 !important; } .kpi-badge { background:#f1f5f9 !important; color:#64748b !important; }
            .page-header { background:linear-gradient(135deg,#1e3a8a,#2563eb) !important; border-color:rgba(59,130,246,.4) !important; }
            .page-header h1 { color:#ffffff !important; } .page-header p { color:rgba(255,255,255,.7) !important; }
            .status-bar { background:#ffffff !important; border-color:#e2e8f0 !important; color:#475569 !important; }
            .section-title { color:#1e293b !important; border-bottom-color:#e2e8f0 !important; }
            .alert-machine { color:#1e293b !important; } .alert-tps { color:#64748b !important; }
            .perf-table th { background:#f8fafc !important; color:#64748b !important; border-color:#e2e8f0 !important; }
            .perf-table td { color:#1e293b !important; border-color:#f1f5f9 !important; }
            .perf-table tr:hover td { background:rgba(59,130,246,.04) !important; }
            .toast-bar { background:linear-gradient(135deg,rgba(34,197,94,.08),rgba(59,130,246,.08)) !important; border-color:rgba(34,197,94,.2) !important; color:#15803d !important; }
            .tab-btn, .shift-tab { background:#ffffff !important; border-color:#e2e8f0 !important; color:#475569 !important; }
            .tab-btn.active, .shift-tab.active { background:rgba(59,130,246,.1) !important; border-color:#3b82f6 !important; color:#1d4ed8 !important; }
            .mini-stat { background:#f8fafc !important; border-color:#e2e8f0 !important; color:#475569 !important; }
            .progress-wrap { background:#e2e8f0 !important; }
            ::-webkit-scrollbar-track { background:#f1f5f9 !important; }
            ::-webkit-scrollbar-thumb { background:#cbd5e1 !important; }
            [data-testid="stDataFrame"] { background:#ffffff !important; }
            hr { border-color:#e2e8f0 !important; }
            </style>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Simulation toggle
        st.markdown("<div style='font-size:10px;color:#8b949e;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;padding:0 4px 6px;'>Mode données</div>", unsafe_allow_html=True)
        mode_sim = st.toggle(" Mode Simulation", value=st.session_state.get('mode_simulation', False), key="sim_toggle")
        if mode_sim != st.session_state.get('mode_simulation', False):
            st.session_state.mode_simulation = mode_sim
            st.rerun()

        st.markdown("---")
        st.markdown(f"""
        <div style="font-family:monospace;font-size:11px;color:#8b949e;text-align:center;
            padding:7px;background:rgba(22,27,34,.8);border-radius:8px;margin-bottom:8px;
            border:1px solid #21262d;">
             {datetime.now().strftime('%d/%m/%Y %H:%M')}
        </div>""", unsafe_allow_html=True)
        st.caption("LECTRA Dashboard v5.0")
        st.caption("Adient Morocco | PFE 2025")
        st.markdown("---")
        if st.button(" Déconnexion", use_container_width=True):
            st.session_state.authentifie = False
            st.rerun()

# ==================== DONNEES SIMULATION ====================
def generer_donnees_demo():
    """Données réelles simulation — LO1→LO6, 06–09 Avril 2025 (valeurs réelles)"""

    def hms_to_min(hms):
        h, m, s = map(int, hms.split(':'))
        return h * 60 + m + s / 60

    # date -> ADV journalière (%)
    adv_jour = {
        '2025-04-06': 68.56,
        '2025-04-07': 56.42,
        '2025-04-08': 65.23,
        '2025-04-09': 61.67,
    }

    # date -> machine -> (INTERRUPTIONS, CODA, DT_POSIT, ΔT_Matelas, TPS %)
    data = {
        '2025-04-06': {
            'LO1': ('03:13:29', '00:51:04', '01:25:00', '01:49:00', 54.45),
            'LO2': ('04:01:12', '00:24:28', '01:21:18', '01:12:43', 59.08),
            'LO3': ('04:26:41', '00:32:52', '01:26:51', '01:52:15', 45.00),
            'LO4': ('04:01:00', '01:15:10', '01:27:23', '01:54:57', 42.12),
            'LO5': ('03:22:51', '00:30:10', '01:05:30', '02:10:21', 32.15),
            'LO6': ('04:31:21', '01:21:32', '00:57:23', '01:22:31', 31.51),
        },
        '2025-04-07': {
            'LO1': ('02:38:09', '00:30:26', '01:10:00', '02:43:00', 37.76),
            'LO2': ('02:54:01', '00:20:07', '01:12:43', '02:17:01', 48.00),
            'LO3': ('03:07:10', '00:45:32', '00:58:46', '01:56:48', 36.41),
            'LO4': ('03:33:42', '01:32:52', '01:14:50', '02:04:45', 30.12),
            'LO5': ('02:58:26', '00:29:49', '01:15:10', '01:54:50', 39.40),
            'LO6': ('03:12:08', '01:32:52', '01:26:51', '01:54:50', 42.52),
        },
        '2025-04-08': {
            'LO1': ('03:05:03', '00:29:40', '00:48:00', '02:55:00', 30.71),
            'LO2': ('04:17:23', '01:01:25', '01:11:14', '02:27:22', 44.85),
            'LO3': ('03:33:42', '00:45:32', '01:21:18', '02:17:01', 35.10),
            'LO4': ('02:54:01', '00:45:32', '01:14:50', '01:54:57', 39.40),
            'LO5': ('04:10:00', '01:10:23', '01:15:10', '01:52:15', 37.15),
            'LO6': ('02:41:00', '00:45:32', '00:48:00', '01:22:31', 69.51),
        },
        '2025-04-09': {
            'LO1': ('04:35:50', '00:06:06', '01:04:00', '03:44:00', 40.53),
            'LO2': ('03:08:54', '00:43:12', '01:58:47', '02:46:22', 49.54),
            'LO3': ('04:10:00', '01:15:10', '01:10:23', '01:54:57', 38.12),
            'LO4': ('04:17:23', '01:01:25', '01:11:14', '02:27:22', 41.10),
            'LO5': ('04:26:41', '00:32:52', '01:26:51', '01:52:15', 45.00),
            'LO6': ('02:02:05', '00:05:17', '01:01:00', '02:58:00', 32.71),
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

            # jitter centré sur 0 -> la moyenne des 10 markers = valeur cible exacte
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
            'Statut': " OK" if tps_moyen >= 75 else " NOK"
        })
    return pd.DataFrame(resultats)

# ── Layout Plotly dark — base sans yaxis pour éviter les conflits ──
PLOT_LAYOUT_BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color='#ffffff',
    font_family='Times New Roman, Times, serif',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11, color='#ffffff', family='Times New Roman, Times, serif')),
    xaxis=dict(gridcolor='rgba(255,255,255,0.06)', tickfont=dict(size=11, color='#ffffff', family='Times New Roman, Times, serif')),
)

PLOT_LAYOUT = PLOT_LAYOUT_BASE

def pl(yaxis_title=None, yaxis_range=None, height=None, **extra):
    """Helper : retourne un dict layout sans conflits yaxis."""
    layout = dict(**PLOT_LAYOUT_BASE)
    yax = dict(gridcolor='rgba(255,255,255,0.06)', tickfont=dict(size=11, color='#ffffff', family='Times New Roman, Times, serif'))
    if yaxis_title: yax['title'] = dict(text=yaxis_title, font=dict(color='#ffffff'))
    if yaxis_range: yax['range'] = yaxis_range
    layout['yaxis'] = yax
    if height: layout['height'] = height
    layout.update(extra)
    return layout

def page_header(icon, titre, sous_titre, badge=None):
    badge_html = f'<span class="header-badge">{badge}</span>' if badge else ''
    st.markdown(f"""
    <div class="page-header">
        <h1>{icon} {titre}</h1>
        <p>{sous_titre}</p>
        {badge_html}
    </div>""", unsafe_allow_html=True)

# ==================== PAGE 1 : ACCUEIL ====================
def page_accueil(df, df_tps):
    now = datetime.now()
    page_header("","Tableau de Bord — Vue d'ensemble",
                "Adient Morocco | Atelier de Coupe | Projet MMA / Mercedes",
                badge=f"Mis à jour : {now.strftime('%d/%m/%Y %H:%M')}")

    # Toast simulation
    if st.session_state.get('mode_simulation', False):
        st.markdown(f"""
        <div class="toast-bar">
             <strong>Mode Simulation actif</strong> — Données LO1→LO6 · 06–09 Avril 2025 · {len(df)} markers chargés
        </div>""", unsafe_allow_html=True)

    total_machines = len(df_tps)
    ok_count   = len(df_tps[df_tps['TPS (%)'] >= 75])
    nok_count  = total_machines - ok_count
    health_pct = int(ok_count / total_machines * 100) if total_machines else 0
    health_color = "#00e676" if health_pct >= 70 else "#ffc107" if health_pct >= 40 else "#ff1744"
    jours = df['DATE'].nunique() if 'DATE' in df.columns else 1

    st.markdown(f"""
    <div class="status-bar">
        <span><span class="status-dot status-online"></span> Système en ligne</span>
        <span style="color:#21262d;">|</span>
        <span> {total_machines} machines</span>
        <span style="color:#21262d;">|</span>
        <span style="color:{health_color};font-weight:700;">● Santé atelier : {health_pct}%</span>
        <span style="color:#21262d;">|</span>
        <span> {ok_count} OK &nbsp;·&nbsp;  {nok_count} NOK</span>
        <span style="margin-left:auto;font-family:monospace;font-size:11px;"> {now.strftime('%A %d %B %Y').capitalize()} · {jours}j analysés</span>
    </div>""", unsafe_allow_html=True)

    # KPIs
    tps_moyen  = df_tps['TPS (%)'].mean()
    adv_moyen  = df_tps['ADV (%)'].mean() if df_tps['ADV (%)'].sum() > 0 else 0
    machines_nok = len(df_tps[df_tps['TPS (%)'] < 75])
    total_inter  = df['INTERRUPTIONS TIME'].sum() if 'INTERRUPTIONS TIME' in df.columns else 0
    total_markers = len(df)

    tps_color  = "#00e676" if tps_moyen >= 75 else "#ffc107" if tps_moyen >= 40 else "#ff1744"
    adv_color  = "#00e676" if adv_moyen >= 100 else "#ffc107" if adv_moyen >= 80 else "#ff1744"
    nok_color  = "#ff1744" if machines_nok > 0 else "#00e676"

    kpis = [
        (f"{tps_moyen:.1f}%",             "TPS Moyen Atelier",      "Taux de productivité",    tps_color,  "TPS"),
        (f"{adv_moyen:.1f}%",             "ADV Moyenne",            "Adhérence au volume",     adv_color,  "ADV"),
        (f"{machines_nok}/{total_machines}","Machines sous objectif","< 75% TPS",               nok_color,  "NOK"),
        (f"{total_inter:.0f}",            "Total Interruptions",    "minutes cumulées",        "#ffc107",  "MIN"),
        (f"{total_markers}",              "Total Markers",          f"{jours} jours analysés", "#00d4d4",  "PCS"),
    ]
    cols = st.columns(5)
    for col, (val, label, sublabel, color, badge) in zip(cols, kpis):
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

    # ── Shift tabs ──
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

    # Gauge + Alerts
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<div class="section-title"><span class="dot"></span> Jauge TPS Atelier</div>', unsafe_allow_html=True)
        gauge_color = tps_color
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=tps_moyen,
            number={'font':{'size':44,'color':gauge_color,'family':'Times New Roman, Times, serif'}},
            delta={'reference':75,'increasing':{'color':"#00e676"},'decreasing':{'color':"#ff1744"},'font':{'size':14,'family':'Times New Roman, Times, serif'}},
            gauge={
                'axis':{'range':[0,100],'tickwidth':1,'tickcolor':'#8b949e','tickfont':{'color':'#8b949e','size':10,'family':'Times New Roman, Times, serif'}},
                'bar':{'color':gauge_color,'thickness':.28},
                'bgcolor':'rgba(0,0,0,0)', 'borderwidth':0,
                'steps':[
                    {'range':[0,40],  'color':'rgba(239,68,68,.12)'},
                    {'range':[40,75], 'color':'rgba(245,158,11,.10)'},
                    {'range':[75,100],'color':'rgba(34,197,94,.10)'},
                ],
                'threshold':{'line':{'color':"#ffc107",'width':2},'thickness':.75,'value':75}
            },
            title={'text':"TPS Moyen Atelier (%)","font":{'size':12,'color':'#8b949e','family':'Times New Roman, Times, serif'}}
        ))
        fig_gauge.update_layout(height=280, margin=dict(t=40,b=10,l=20,r=20),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#ffffff', font_family='Times New Roman, Times, serif')
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title"><span class="dot" style="background:#ff1744"></span> Alertes Machines</div>', unsafe_allow_html=True)
        critiques   = df_tps[df_tps['TPS (%)'] <  40]
        attention   = df_tps[(df_tps['TPS (%)'] >= 40) & (df_tps['TPS (%)'] < 75)]
        ok_machines = df_tps[df_tps['TPS (%)'] >= 75]
        c1, c2, c3 = st.columns(3)

        def alert_col(col, items, card_cls, badge_cls, badge_txt, head_color, head_txt, empty_txt):
            with col:
                st.markdown(f"<div style='font-size:11px;font-weight:700;color:{head_color};text-transform:uppercase;letter-spacing:.8px;margin-bottom:9px;'>{head_txt}</div>", unsafe_allow_html=True)
                if len(items) == 0:
                    st.markdown(f'<div class="{card_cls}"><div class="alert-machine" style="color:#8b949e;font-weight:400;font-size:12px;">{empty_txt}</div></div>', unsafe_allow_html=True)
                for _, r in items.iterrows():
                    extra = f"ADV : {r['ADV (%)']:.1f}%" if badge_txt == "OK" else f"Écart : {r['Écart (%)']:.1f}%"
                    st.markdown(f"""
                    <div class="{card_cls}">
                        <span class="alert-badge {badge_cls}">{badge_txt}</span>
                        <div class="alert-machine">{r['Machine']}</div>
                        <div class="alert-tps">TPS : {r['TPS (%)']:.1f}% · {extra}</div>
                    </div>""", unsafe_allow_html=True)

        alert_col(c1, critiques,   "alert-card-red",    "badge-red",    "CRITIQUE",  "#ff8a9e", " Critique",       "Aucune machine")
        alert_col(c2, attention,   "alert-card-orange", "badge-orange", "ATTENTION", "#ffe082", " À surveiller",   "Aucune machine")
        alert_col(c3, ok_machines, "alert-card-green",  "badge-green",  "OK",        "#80ffc8", " Objectif atteint","Aucune machine")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Mini stats row
    total_inter  = df['INTERRUPTIONS TIME'].sum() if 'INTERRUPTIONS TIME' in df.columns else 0
    total_coda   = df['CODA INTERRUPTIONS TIME'].sum() if 'CODA INTERRUPTIONS TIME' in df.columns else 0
    total_dt_mat = df['ΔT_Matelas'].sum() if 'ΔT_Matelas' in df.columns else 0
    st.markdown(f"""
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px;">
        <span class="mini-stat"> Interruptions : <strong style="color:#ff1744;">{total_inter:.0f} min</strong></span>
        <span class="mini-stat"> CODA : <strong style="color:#00d4d4;">{total_coda:.0f} min</strong></span>
        <span class="mini-stat"> ΔT Matelas : <strong style="color:#8b949e;">{total_dt_mat:.0f} min</strong></span>
        <span class="mini-stat"> Markers : <strong style="color:#00d4d4;">{total_markers}</strong></span>
        <span class="mini-stat"> Jours : <strong style="color:#80ffc8;">{jours}</strong></span>
    </div>""", unsafe_allow_html=True)

    # Summary table
    st.markdown('<div class="section-title"><span class="dot" style="background:#00d4d4"></span> Résumé Performance par Machine</div>', unsafe_allow_html=True)
    rows_html = ""
    for _, r in df_tps.iterrows():
        tps = r['TPS (%)']
        if tps >= 75:   pill = "background:rgba(34,197,94,.18);color:#80ffc8;";  statut = " OK"
        elif tps >= 40: pill = "background:rgba(245,158,11,.18);color:#ffe082;"; statut = " NOK"
        else:           pill = "background:rgba(239,68,68,.18);color:#ff8a9e;";  statut = " CRITIQUE"
        ecart = r['Écart (%)']
        ecart_html = f'<span style="color:#00e676;">+{ecart:.1f}%</span>' if ecart >= 0 else f'<span style="color:#ff1744;">{ecart:.1f}%</span>'
        rows_html += f"""
        <tr>
            <td style="font-weight:700;color:#ffffff;">{r['Machine']}</td>
            <td><span class="tps-pill" style="{pill}">{tps:.1f}%</span></td>
            <td style="color:#8b949e;">75%</td>
            <td>{ecart_html}</td>
            <td style="color:#00d4d4;">{r['ADV (%)']:.1f}%</td>
            <td style="color:#8b949e;">{r['Interruptions (min)']:.0f} min</td>
            <td><span class="tps-pill" style="{pill}">{statut}</span></td>
        </tr>"""
    st.markdown(f"""
    <div style="background:rgba(22,27,34,.8);border:1px solid #21262d;border-radius:12px;overflow:hidden;">
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
    # Palette exacte de l'image de reference
    CYAN  = "#00d4d4"
    VERT  = "#00e676"
    ROUGE = "#ff1744"
    BLANC = "#ffffff"
    GRIS  = "#8b949e"
    JAUNE = "#ffc107"
    BG    = "rgba(0,0,0,0)"

    page_header("", "TPS & Performance", "Taux de Productivite Synthetique par machine")

    # Calculs globaux
    tps_moyen = df_tps['TPS (%)'].mean()
    adv_moyen = df_tps['ADV (%)'].mean() if 'ADV (%)' in df_tps.columns else 0
    t_int     = df_tps['Interruptions (min)'].sum() if 'Interruptions (min)' in df_tps.columns else 0
    t_coda    = df_tps['CODA (min)'].sum()           if 'CODA (min)'          in df_tps.columns else 0

    D = max(0, min(100, 100 - (t_int / max(t_int + t_coda, 1)) * 100))
    Q = min(100, adv_moyen)
    P = min(100, tps_moyen)

    # Evolution journaliere
    if 'DATE' in df.columns:
        tps_jour = [{'Date': d, 'TPS (%)': calculer_tps_adv(df[df['DATE']==d])['TPS (%)'].mean()}
                    for d in sorted(df['DATE'].unique())]
        df_tj = pd.DataFrame(tps_jour)
    else:
        df_tj = pd.DataFrame()

    # Layout : gauche TRS + D/Q/P  |  droite evolution + barres
    col_left, col_right = st.columns([1, 2])

    with col_left:
        # Grand cercle TRS central — cyan comme dans l'image
        fig_trs = go.Figure(go.Indicator(
            mode="gauge+number",
            value=tps_moyen,
            number={
                'suffix': '%', 'valueformat': '.0f',
                'font': {'size': 58, 'color': CYAN, 'family': 'Times New Roman, Times, serif'}
            },
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': '#333',
                         'tickfont': {'color': GRIS, 'size': 9, 'family': 'Times New Roman, Times, serif'}},
                'bar': {'color': CYAN, 'thickness': 0.25},
                'bgcolor': BG, 'borderwidth': 0,
                'steps': [
                    {'range': [0,  40], 'color': 'rgba(255,23,68,.12)'},
                    {'range': [40, 75], 'color': 'rgba(255,193,7,.10)'},
                    {'range': [75,100], 'color': 'rgba(0,230,118,.10)'},
                ],
                'threshold': {'line': {'color': JAUNE, 'width': 2}, 'thickness': 0.75, 'value': 75}
            },
            title={'text': 'TPS', 'font': {'size': 20, 'color': BLANC, 'family': 'Times New Roman, Times, serif'}}
        ))
        fig_trs.update_layout(
            height=300, margin=dict(t=60, b=5, l=20, r=20),
            paper_bgcolor=BG, plot_bgcolor=BG,
            font_color=BLANC, font_family='Times New Roman, Times, serif'
        )
        st.plotly_chart(fig_trs, use_container_width=True)

        # TPS par machine — petits cercles cyan comme dans l'image
        def mini_cercle(val, label):
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=val,
                number={'suffix': '%', 'valueformat': '.0f',
                        'font': {'size': 26, 'color': CYAN, 'family': 'Times New Roman, Times, serif'}},
                gauge={
                    'axis': {'range': [0, 100], 'visible': False},
                    'bar': {'color': CYAN, 'thickness': 0.28},
                    'bgcolor': 'rgba(0,212,212,.08)',
                    'bordercolor': CYAN, 'borderwidth': 1,
                },
                title={'text': label, 'font': {'size': 16, 'color': BLANC, 'family': 'Times New Roman, Times, serif'}},
                domain={'x': [0, 1], 'y': [0, 1]}
            ))
            fig.update_layout(height=200, margin=dict(t=45, b=15, l=25, r=25),
                paper_bgcolor=BG, plot_bgcolor=BG,
                font_color=BLANC, font_family='Times New Roman, Times, serif')
            return fig

        machines_list = df_tps['Machine'].tolist() if not df_tps.empty else []
        n = len(machines_list)
        if n:
            nb_par_ligne = 3
            for i in range(0, n, nb_par_ligne):
                row_machines = list(df_tps.iloc[i:i+nb_par_ligne].iterrows())
                cols_m = st.columns(len(row_machines))
                for col, (_, row) in zip(cols_m, row_machines):
                    with col:
                        st.plotly_chart(mini_cercle(row['TPS (%)'], row['Machine']), use_container_width=True)

    with col_right:
        # Evolution du TPS — ligne cyan sur fond sombre comme dans l'image
        st.markdown('<div class="section-title"><span class="dot" style="background:#00d4d4"></span> Evolution du TPS</div>', unsafe_allow_html=True)
        if not df_tj.empty:
            fig_evol = go.Figure()
            fig_evol.add_trace(go.Scatter(
                x=df_tj['Date'], y=df_tj['TPS (%)'],
                mode='lines+markers+text',
                text=[f"{v:.0f}%" for v in df_tj['TPS (%)']],
                textposition='top center',
                textfont=dict(size=10, color=BLANC, family='Times New Roman, Times, serif'),
                line=dict(color=CYAN, width=2),
                marker=dict(size=5, color=CYAN),
                fill='tozeroy', fillcolor='rgba(0,212,212,.07)',
                name='TPS'
            ))
            fig_evol.add_trace(go.Scatter(
                x=df_tj['Date'], y=[75]*len(df_tj),
                mode='lines', name='Objectif 75%',
                line=dict(color=JAUNE, dash='dot', width=1.5)
            ))
            fig_evol.update_layout(**pl(yaxis_title="TPS (%)", yaxis_range=[0, 105], height=220,
                legend=dict(font=dict(color=BLANC, size=10))))
            st.plotly_chart(fig_evol, use_container_width=True)
        else:
            st.info("Pas de donnees temporelles disponibles.")

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        # TPS par machine — barres vert/rouge/jaune comme OEE by Day Team dans l'image
        st.markdown('<div class="section-title"><span class="dot" style="background:#00d4d4"></span> TPS par Machine</div>', unsafe_allow_html=True)
        colors_m = [VERT if t >= 75 else JAUNE if t >= 40 else ROUGE for t in df_tps['TPS (%)']]
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=df_tps['Machine'], y=df_tps['TPS (%)'],
            marker_color=colors_m, marker_line_color='rgba(0,0,0,0)',
            name='TPS Reel',
            text=[f"{v:.1f}%" for v in df_tps['TPS (%)']],
            textposition='outside',
            textfont=dict(size=11, color=BLANC, family='Times New Roman, Times, serif')
        ))
        # Ligne objectif blanche pointillee comme dans l'image
        fig_bar.add_trace(go.Scatter(
            x=df_tps['Machine'], y=[75]*len(df_tps),
            mode='lines', name='Objectif 75%',
            line=dict(color=BLANC, width=1.5, dash='dot')
        ))
        # ADV en ligne cyan
        if 'ADV (%)' in df_tps.columns:
            fig_bar.add_trace(go.Scatter(
                x=df_tps['Machine'], y=df_tps['ADV (%)'],
                mode='lines+markers', name='ADV (%)',
                line=dict(color=CYAN, width=2),
                marker=dict(size=6, color=CYAN)
            ))
        fig_bar.update_layout(**pl(yaxis_title="(%)", yaxis_range=[0, 120], height=270,
            bargap=0.25, legend=dict(font=dict(color=BLANC, size=10))))
        st.plotly_chart(fig_bar, use_container_width=True)

# ==================== PAGE 3 : PERTES ====================
def page_pertes(df, df_tps):
    page_header("","Analyse des Pertes","Interruptions, CODA, DT_POSIT, POSIT/Marker et ΔT_Matelas par machine")

    # Résumé pertes
    t_int  = df_tps['Interruptions (min)'].sum()
    t_coda = df_tps['CODA (min)'].sum()
    t_pos  = df_tps['DT_POSIT (min)'].sum()
    t_pm   = df_tps['POSIT/Marker'].sum()
    t_mat  = df_tps['ΔT_Matelas (min)'].sum()
    total  = t_int + t_coda + t_pos + t_pm + t_mat

    kpi_cols = st.columns(5)
    for col, val, lbl, color in [
        (kpi_cols[0], f"{t_int:.0f}", "Interruptions (min)", "#ff1744"),
        (kpi_cols[1], f"{t_coda:.0f}", "CODA (min)",          "#00d4d4"),
        (kpi_cols[2], f"{t_pos:.0f}",  "DT_POSIT (min)",      "#ffc107"),
        (kpi_cols[3], f"{t_pm:.0f}",   "POSIT/Marker",        "#00d4d4"),
        (kpi_cols[4], f"{t_mat:.0f}",  "ΔT_Matelas (min)",    "#8b949e"),
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
            ('Interruptions','Interruptions (min)','#ff1744'),
            ('CODA','CODA (min)','#00d4d4'),
            ('DT_POSIT','DT_POSIT (min)','#ffc107'),
            ('POSIT/Marker','POSIT/Marker','#00d4d4'),
            ('ΔT_Matelas','ΔT_Matelas (min)','#8b949e'),
        ]:
            fig.add_trace(go.Bar(name=name, x=df_tps['Machine'], y=df_tps[col_name], marker_color=color))
        fig.update_layout(**pl(yaxis_title="Minutes", height=380), barmode='stack')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title"><span class="dot"></span> Répartition globale</div>', unsafe_allow_html=True)
        fig_pie = px.pie(values=[t_int,t_coda,t_pos,t_pm,t_mat],
            names=['Interruptions','CODA','DT_POSIT','POSIT/Marker','ΔT_Matelas'],
            color_discrete_sequence=['#ff1744','#00d4d4','#ffc107','#00d4d4','#8b949e'], hole=0.45)
        fig_pie.update_traces(textinfo='percent+label', textfont_size=11, textfont_family='Times New Roman, Times, serif')
        fig_pie.update_layout(**PLOT_LAYOUT, height=380)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-title"><span class="dot"></span> Pareto des Pertes</div>', unsafe_allow_html=True)
    pareto = pd.DataFrame({'Source':['Interruptions','CODA','DT_POSIT','POSIT/Marker','ΔT_Matelas'],
        'Total (min)':[t_int,t_coda,t_pos,t_pm,t_mat]}).sort_values('Total (min)',ascending=False)
    pareto['Cumul (%)'] = pareto['Total (min)'].cumsum() / pareto['Total (min)'].sum() * 100
    fig_p = go.Figure()
    fig_p.add_trace(go.Bar(x=pareto['Source'],y=pareto['Total (min)'],
        marker_color=['#ff1744','#00d4d4','#ffc107','#00d4d4','#8b949e'],
        text=[f"{v:.0f}" for v in pareto['Total (min)']],textposition='outside',name='min'))
    fig_p.add_trace(go.Scatter(x=pareto['Source'],y=pareto['Cumul (%)'],
        mode='lines+markers+text',text=[f"{v:.0f}%" for v in pareto['Cumul (%)']],
        textposition='top center',name='Cumul %',yaxis='y2',
        line=dict(color='#00d4d4',width=2),marker=dict(size=7)))
    fig_p.add_hline(y=80,line_dash="dash",line_color="#ffc107",annotation_text="80%",yref='y2')
    fig_p.update_layout(**pl(yaxis_title="Durée (min)", height=400),
        yaxis2=dict(title="Cumul (%)",overlaying='y',side='right',range=[0,110],
                    tickfont=dict(size=11, family='Times New Roman, Times, serif'),gridcolor='rgba(0,0,0,0)'))
    st.plotly_chart(fig_p, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-title"><span class="dot"></span> Camemberts par machine</div>', unsafe_allow_html=True)
    n_cols = min(3, len(df_tps))
    cols_pie = st.columns(n_cols)
    for i, (_, row) in enumerate(df_tps.iterrows()):
        with cols_pie[i % n_cols]:
            fig_m = px.pie(values=[row['Interruptions (min)'],row['CODA (min)'],row['DT_POSIT (min)'],row['POSIT/Marker'],row['ΔT_Matelas (min)']],
                names=['Interruptions','CODA','DT_POSIT','POSIT/Marker','ΔT_Matelas'],
                color_discrete_sequence=['#ff1744','#00d4d4','#ffc107','#00d4d4','#8b949e'],
                title=row['Machine'], hole=0.38)
            fig_m.update_traces(textinfo='percent', textfont_family='Times New Roman, Times, serif')
            fig_m.update_layout(height=280,margin=dict(t=40,b=10,l=10,r=10),showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',font_color='#ffffff', font_family='Times New Roman, Times, serif')
            st.plotly_chart(fig_m, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-title"><span class="dot"></span> Tableau détaillé</div>', unsafe_allow_html=True)
    cols_p = ['Machine','Interruptions (min)','CODA (min)','DT_POSIT (min)','POSIT/Marker','ΔT_Matelas (min)','Cutting (min)','TPS (%)']
    st.dataframe(df_tps[cols_p], use_container_width=True, hide_index=True)

# ==================== PAGE 4 : ADV ====================
def page_adv(df, df_tps):
    page_header("","ADV — Adhérence au Volume","Suivi journalier de la production réalisée vs planifiée")
    if 'DATE' not in df.columns or 'ADV' not in df.columns:
        st.warning(" Colonnes DATE ou ADV non disponibles.")
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
        (kpi_cols[0], f"{adv_moy:.1f}%", "ADV Moyenne",       "#00d4d4"),
        (kpi_cols[1], f"{adv_min:.1f}%", "ADV Minimale",      "#ff1744"),
        (kpi_cols[2], f"{adv_max:.1f}%", "ADV Maximale",      "#00e676"),
        (kpi_cols[3], f"{j_nok}j",       "Jours sous objectif","#ffc107"),
    ]:
        with col:
            st.markdown(f"""<div class="kpi-card" style="--accent:{color};">
                <div class="kpi-value" style="font-size:28px;">{val}</div>
                <div class="kpi-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span class="dot"></span> ADV journalière vs Objectif</div>', unsafe_allow_html=True)
    colors_adv = ['#00e676' if v >= 100 else '#ff1744' for v in df_adv['ADV (%)']]
    fig_adv = go.Figure()
    fig_adv.add_trace(go.Bar(x=df_adv['DATE'],y=df_adv['ADV (%)'],marker_color=colors_adv,name='ADV Réelle',
        text=[f"{v:.1f}%" for v in df_adv['ADV (%)']],textposition='outside',textfont=dict(size=11, family='Times New Roman, Times, serif')))
    fig_adv.add_trace(go.Scatter(x=df_adv['DATE'],y=[100]*len(df_adv),mode='lines',name='Objectif 100%',
        line=dict(color='#ffc107',width=2,dash='dash')))
    fig_adv.update_layout(**pl(yaxis_title="ADV (%)", yaxis_range=[0,130], height=360))
    st.plotly_chart(fig_adv, use_container_width=True)

    st.markdown('<div class="section-title"><span class="dot"></span> ADV par Machine</div>', unsafe_allow_html=True)
    df_adv_m = df_tps[df_tps['ADV (%)'] > 0][['Machine','ADV (%)']]
    if not df_adv_m.empty:
        fig_adv_m = go.Figure(go.Bar(x=df_adv_m['Machine'],y=df_adv_m['ADV (%)'],
            marker_color=['#00e676' if v >= 100 else '#ff1744' for v in df_adv_m['ADV (%)']],
            text=[f"{v:.1f}%" for v in df_adv_m['ADV (%)']],textposition='outside'))
        fig_adv_m.add_hline(y=100,line_dash="dash",line_color="#ffc107",annotation_text="Objectif 100%")
        fig_adv_m.update_layout(**pl(yaxis_title="ADV (%)", yaxis_range=[0,130], height=320))
        st.plotly_chart(fig_adv_m, use_container_width=True)

# ==================== PAGE 5 : MACHINE ====================
def page_machine(df, df_tps):
    page_header("","Analyse Détaillée par Machine","Sélectionnez une machine pour son analyse complète")
    machine_sel = st.selectbox(" Machine :", sorted(df['Machine'].unique()))
    df_m   = df[df['Machine'] == machine_sel]
    row    = df_tps[df_tps['Machine'] == machine_sel].iloc[0]
    tps_v  = row['TPS (%)']
    color  = "#00e676" if tps_v >= 75 else "#ffc107" if tps_v >= 40 else "#ff1744"

    kpi_cols = st.columns(5)
    for col, val, lbl, c in [
        (kpi_cols[0], f"{tps_v:.1f}%",                "TPS",           color),
        (kpi_cols[1], f"{row['Interruptions (min)']:.0f} min","Interruptions","#ff1744"),
        (kpi_cols[2], f"{row['CODA (min)']:.0f} min",  "CODA",          "#00d4d4"),
        (kpi_cols[3], f"{row['DT_POSIT (min)']:.0f} min","DT_POSIT",   "#ffc107"),
        (kpi_cols[4], f"{row['ΔT_Matelas (min)']:.0f} min","ΔT_Matelas","#8b949e"),
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
            mode="gauge+number+delta", value=tps_v, delta={'reference':75},
            gauge={'axis':{'range':[0,100]},'bar':{'color':color},
                'steps':[{'range':[0,40],'color':'rgba(239,68,68,.12)'},{'range':[40,75],'color':'rgba(245,158,11,.10)'},{'range':[75,100],'color':'rgba(34,197,94,.10)'}],
                'threshold':{'line':{'color':"#ffc107",'width':2},'thickness':.75,'value':75}},
            title={'text':f"TPS {machine_sel} (%)","font":{'color':'#ffffff','family':'Times New Roman, Times, serif'}}
        ))
        fig_g.update_layout(height=260, margin=dict(t=50,b=10,l=20,r=20),
            paper_bgcolor='rgba(0,0,0,0)',font_color='#ffffff', font_family='Times New Roman, Times, serif')
        st.plotly_chart(fig_g, use_container_width=True)

    with col2:
        fig_pie = px.pie(
            values=[row['Interruptions (min)'],row['CODA (min)'],row['DT_POSIT (min)'],row['POSIT/Marker'],row['ΔT_Matelas (min)']],
            names=['Interruptions','CODA','DT_POSIT','POSIT/Marker','ΔT_Matelas'],
            color_discrete_sequence=['#ff1744','#00d4d4','#ffc107','#00d4d4','#8b949e'], hole=0.42)
        fig_pie.update_traces(textinfo='percent+label', textfont_family='Times New Roman, Times, serif')
        fig_pie.update_layout(**PLOT_LAYOUT, height=260, margin=dict(t=20,b=10))
        st.plotly_chart(fig_pie, use_container_width=True)

    if 'DATE' in df_m.columns:
        st.markdown("---")
        evol = df_m.groupby('DATE')['CUTTING TIME'].sum().reset_index()
        fig_e = px.line(evol,x='DATE',y='CUTTING TIME',markers=True,
            title=f"Temps de coupe — {machine_sel}")
        fig_e.update_layout(**PLOT_LAYOUT, height=280)
        st.plotly_chart(fig_e, use_container_width=True)

    st.markdown("---")
    cols_show = [c for c in ['DATE','Marker','CUTTING TIME','INTERRUPTIONS TIME','CODA INTERRUPTIONS TIME','DT_POSIT (min)','POSIT/Marker','ΔT_Matelas','STATE'] if c in df_m.columns]
    st.dataframe(df_m[cols_show], use_container_width=True, hide_index=True)

# ==================== PAGE 6 : DONNEES ====================
def page_donnees(df, df_tps):
    page_header("","Données Brutes","Tableau complet avec filtres et export")
    col1, col2, col3 = st.columns(3)
    with col1:
        filtre_m = st.selectbox(" Machine", ['Toutes'] + sorted(df['Machine'].unique().tolist()))
    with col2:
        filtre_d = st.selectbox(" Date", ['Toutes'] + sorted(df['DATE'].unique().tolist(), reverse=True)) if 'DATE' in df.columns else 'Toutes'
    with col3:
        filtre_s = st.selectbox(" Statut", ['Tous'] + sorted(df['STATE'].dropna().unique().tolist())) if 'STATE' in df.columns else 'Tous'

    df_f = df.copy()
    if filtre_m != 'Toutes': df_f = df_f[df_f['Machine'] == filtre_m]
    if filtre_d != 'Toutes' and 'DATE' in df_f.columns: df_f = df_f[df_f['DATE'] == filtre_d]
    if filtre_s != 'Tous' and 'STATE' in df_f.columns: df_f = df_f[df_f['STATE'] == filtre_s]

    st.markdown(f"""<div class="toast-bar"> <strong>{len(df_f)}</strong> lignes affichées sur <strong>{len(df)}</strong> total</div>""", unsafe_allow_html=True)

    cols_show = [c for c in ['DATE','Machine','Marker','CUTTING TIME','INTERRUPTIONS TIME','CODA INTERRUPTIONS TIME','DT_POSIT (min)','POSIT/Marker','ΔT_Matelas','STATE'] if c in df_f.columns]
    if st.session_state.role == "admin":
        st.caption("✏️ Mode édition admin — double-cliquez pour modifier")
        st.data_editor(df_f[cols_show], use_container_width=True, hide_index=True)
    else:
        st.dataframe(df_f[cols_show], use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown('<div class="section-title"><span class="dot"></span> Export</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(" Données filtrées (CSV)", data=df_f.to_csv(index=False).encode('utf-8'),
            file_name=f"lectra_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv", use_container_width=True)
    with c2:
        st.download_button(" Tableau TPS/ADV (CSV)", data=df_tps.to_csv(index=False).encode('utf-8'),
            file_name=f"tps_adv_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv", use_container_width=True)

# ==================== MAIN ====================
def main():
    if not verifier_mot_de_passe():
        return

    sidebar_navigation()

    df = charger_donnees()
    if df is None or df.empty:
        st.warning(" Aucune donnée trouvée.")
        st.stop()

    # Filtre date global
    if 'DATE' in df.columns and not df.empty:
        st.sidebar.markdown("---")
        st.sidebar.markdown("<div style='font-size:10px;color:#8b949e;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;padding:0 4px 6px;'>Filtre par date</div>", unsafe_allow_html=True)
        dates_dispo = sorted(df['DATE'].unique())
        date_min = dates_dispo[0]; date_max = dates_dispo[-1]
        date_debut = pd.to_datetime(st.sidebar.date_input(" Début", value=date_min, min_value=date_min, max_value=date_max))
        date_fin   = pd.to_datetime(st.sidebar.date_input(" Fin",   value=date_max, min_value=date_min, max_value=date_max))
        df_filtre = df[(df['DATE'] >= date_debut) & (df['DATE'] <= date_fin)]
        if df_filtre.empty:
            st.warning(f" Aucune donnée entre {date_debut.strftime('%d/%m/%Y')} et {date_fin.strftime('%d/%m/%Y')}")
            st.stop()
        st.sidebar.info(f" **{date_debut.strftime('%d/%m/%Y')}** → **{date_fin.strftime('%d/%m/%Y')}**")
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
    <div style='text-align:center;color:#8b949e;font-size:11px;padding:20px 0 10px;letter-spacing:.5px;'>
         Adient Morocco — LECTRA Dashboard v5.0 &nbsp;|&nbsp; Projet PFE 2025 &nbsp;|&nbsp; Tiflet
    </div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
