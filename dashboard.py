import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import requests
import base64

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="LECTRA Dashboard | Adient Morocco",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS GENERAL ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

    /* ── Global Dark Theme ── */
    html, body, .main {
        color: #e2e8f0 !important;
    }
    [data-testid="stHeader"] { background-color: #0d1117 !important; }
    .block-container { padding-top: 1.5rem !important; }

    /* ── KPI Cards ── */
    .kpi-card {
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 14px;
        padding: 22px 16px 18px;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        margin-bottom: 10px;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: var(--accent, #3b82f6);
        border-radius: 14px 14px 0 0;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 28px rgba(0,0,0,0.4);
        border-color: var(--accent, #3b82f6);
    }
    .kpi-value {
        font-family: 'Syne', sans-serif;
        font-size: 32px;
        font-weight: 800;
        color: var(--accent, #3b82f6);
        line-height: 1.1;
        letter-spacing: -0.5px;
    }
    .kpi-label { font-size: 12px; color: #8b949e; margin-top: 6px; font-weight: 500; letter-spacing: 0.4px; text-transform: uppercase; }
    .kpi-unit { font-size: 11px; color: #484f58; margin-top: 3px; }
    .kpi-trend { font-size: 11px; margin-top: 6px; font-weight: 600; }

    /* ── Alert Cards ── */
    .alert-card-red {
        background: rgba(220, 38, 38, 0.1);
        border: 1px solid rgba(220, 38, 38, 0.3);
        border-left: 3px solid #dc2626;
        border-radius: 10px; padding: 12px 14px; margin-bottom: 8px;
        transition: background 0.2s;
    }
    .alert-card-red:hover { background: rgba(220,38,38,0.16); }
    .alert-card-orange {
        background: rgba(234, 88, 12, 0.1);
        border: 1px solid rgba(234, 88, 12, 0.3);
        border-left: 3px solid #ea580c;
        border-radius: 10px; padding: 12px 14px; margin-bottom: 8px;
        transition: background 0.2s;
    }
    .alert-card-orange:hover { background: rgba(234,88,12,0.16); }
    .alert-card-green {
        background: rgba(22, 163, 74, 0.1);
        border: 1px solid rgba(22, 163, 74, 0.3);
        border-left: 3px solid #16a34a;
        border-radius: 10px; padding: 12px 14px; margin-bottom: 8px;
        transition: background 0.2s;
    }
    .alert-card-green:hover { background: rgba(22,163,74,0.16); }
    .alert-machine { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 14px; color: #e2e8f0; }
    .alert-tps { font-size: 12px; color: #8b949e; margin-top: 2px; }
    .alert-badge {
        display: inline-block;
        font-size: 10px; font-weight: 700; letter-spacing: 0.8px;
        padding: 2px 7px; border-radius: 4px; text-transform: uppercase;
        float: right;
    }
    .badge-red   { background: rgba(220,38,38,0.25);  color: #fca5a5; }
    .badge-orange{ background: rgba(234,88,12,0.25);  color: #fed7aa; }
    .badge-green { background: rgba(22,163,74,0.25);  color: #86efac; }

    /* ── Section Titles ── */
    .section-title {
        font-family: 'Syne', sans-serif;
        font-size: 16px; font-weight: 700;
        color: #e2e8f0;
        display: flex; align-items: center; gap: 8px;
        padding-bottom: 10px;
        border-bottom: 1px solid #21262d;
        margin-bottom: 16px;
        letter-spacing: 0.2px;
    }
    .section-title .dot {
        width: 8px; height: 8px; border-radius: 50%;
        background: #3b82f6; display: inline-block; flex-shrink: 0;
    }

    /* ── Page Header ── */
    .page-header {
        background: linear-gradient(135deg, #161b22 0%, #1c2333 100%);
        border: 1px solid #21262d;
        border-left: 4px solid #3b82f6;
        color: #e2e8f0;
        padding: 22px 28px;
        border-radius: 14px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .page-header::after {
        content: '';
        position: absolute;
        top: -30px; right: -30px;
        width: 120px; height: 120px;
        border-radius: 50%;
        background: rgba(59, 130, 246, 0.06);
    }
    .page-header h1 {
        font-family: 'Syne', sans-serif !important;
        font-size: 26px !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
        margin: 0 !important;
        color: #f0f6ff !important;
    }
    .page-header p { margin: 5px 0 0 !important; opacity: 0.6; font-size: 13px !important; }
    .header-badge {
        display: inline-block;
        font-size: 10px; font-weight: 700;
        letter-spacing: 1px; text-transform: uppercase;
        background: rgba(59,130,246,0.15);
        color: #93c5fd;
        border: 1px solid rgba(59,130,246,0.3);
        padding: 3px 10px; border-radius: 20px;
        margin-top: 10px;
    }

    /* ── Status Bar ── */
    .status-bar {
        display: flex; align-items: center; gap: 20px;
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 10px;
        padding: 10px 20px;
        margin-bottom: 18px;
        font-size: 12px; color: #8b949e;
    }
    .status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 5px; }
    .status-online { background: #22c55e; box-shadow: 0 0 6px #22c55e; }

    /* ── Summary Table ── */
    .perf-table { width: 100%; border-collapse: collapse; margin-top: 4px; }
    .perf-table th {
        font-family: 'Syne', sans-serif;
        font-size: 11px; font-weight: 700;
        color: #8b949e; text-transform: uppercase;
        letter-spacing: 0.8px;
        padding: 10px 14px;
        background: #161b22;
        border-bottom: 1px solid #21262d;
        text-align: left;
    }
    .perf-table td {
        padding: 11px 14px;
        font-size: 13px; color: #c9d1d9;
        border-bottom: 1px solid #161b22;
    }
    .perf-table tr:hover td { background: rgba(255,255,255,0.02); }
    .tps-pill {
        display: inline-block;
        font-weight: 700; font-size: 12px;
        padding: 2px 10px; border-radius: 20px;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #0d1117 !important;
        border-right: 1px solid #21262d;
    }
    [data-testid="stSidebar"] * { color: #c9d1d9 !important; }
    [data-testid="stSidebar"] .stButton button {
        background: #161b22 !important;
        border: 1px solid #21262d !important;
        border-radius: 8px !important;
        color: #c9d1d9 !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 13px !important;
        transition: all 0.2s !important;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background: #1c2333 !important;
        border-color: #3b82f6 !important;
        color: #93c5fd !important;
    }

    /* ── Plotly overrides for dark theme ── */
    .js-plotly-plot .plotly { border-radius: 12px; overflow: hidden; }
    div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ==================== AUTHENTIFICATION ====================
USERS = {
    "admin123":  {"role": "admin",  "nom": "Administrateur"},
    "invite123": {"role": "invite", "nom": "Invité"},
    "chef123":   {"role": "chef",   "nom": "Chef d'atelier"},
}

def verifier_mot_de_passe():
    """Fonction d'authentification - Tout dans le même panneau blanc"""
    if "authentifie" not in st.session_state:
        st.session_state.authentifie = False
        st.session_state.role = None
        st.session_state.nom_user = ""

    if st.session_state.authentifie:
        return True

    bg_image_path = "background.png"

    if os.path.exists(bg_image_path):
        with open(bg_image_path, "rb") as image_file:
            img_base64 = base64.b64encode(image_file.read()).decode()

        background_style = f"""
            background-image: url("data:image/png;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        """
    else:
        background_style = """
            background: linear-gradient(135deg, #0a2b3e 0%, #1a4a6f 100%);
        """

    st.markdown(
        f"""
        <style>
        /* Masquer les éléments Streamlit */
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stSidebar"] {{
            display: none !important;
        }}

        /* Fond principal */
        [data-testid="stAppViewContainer"] {{
            {background_style}
        }}

        /* Overlay sombre */
        [data-testid="stAppViewContainer"]::before {{
            content: "";
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.55);
            z-index: 0;
            pointer-events: none;
        }}

        /* Contenu au-dessus de l'overlay */
        .main,
        .block-container {{
            position: relative;
            z-index: 1;
        }}

        .block-container {{
            padding: 0 !important;
            max-width: 100% !important;
        }}

        /* Inputs */
        .stTextInput input {{
            background: #f8fafc !important;
            border: 1px solid #d7dee8 !important;
            border-radius: 6px !important;
            height: 36px !important;
            font-size: 13px !important;
            padding: 0 10px !important;
            color: #000 !important;
        }}

        /* Bouton */
        .stButton button {{
            background: #003f52 !important;
            color: white !important;
            height: 38px !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            margin-top: 5px !important;
            border: none !important;
        }}

        .stCheckbox label p {{
            font-size: 11px !important;
        }}

        div[data-testid="column"] {{
            gap: 0px !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

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

        st.markdown("<p style='text-align: left; font-size: 12px; font-weight: 600; color: #333; margin-bottom: 4px;'>👤 Nom d'utilisateur</p>", unsafe_allow_html=True)
        username = st.text_input("", placeholder="Entrez votre nom d'utilisateur", key="login_user", label_visibility="collapsed")

        st.markdown("<p style='text-align: left; font-size: 12px; font-weight: 600; color: #333; margin-top: 10px; margin-bottom: 4px;'>🔐 Mot de passe</p>", unsafe_allow_html=True)
        password = st.text_input("", type="password", placeholder="Entrez votre mot de passe", key="login_pwd", label_visibility="collapsed")

        col_check, col_forgot = st.columns([1, 1])
        with col_check:
            st.checkbox("Se souvenir de moi")
        with col_forgot:
            st.markdown("<div style='text-align: right; padding-top: 3px;'><a href='#' style='color: #9cc31a; font-size: 11px; text-decoration: none;'>Mot de passe oublié ?</a></div>", unsafe_allow_html=True)

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
                <p style="color: #00334e; font-size: 11px; font-weight: 700; letter-spacing: 2px; margin-bottom: 12px;">
                    ADIENT MOROCCO — TIFLET
                </p>
                <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin-bottom: 10px;">
                    <div style="font-size: 11px; font-weight: 500; color: #555;">
                        <span style="color: #9cc31a;">⏱️</span> TEMPS RÉEL
                    </div>
                    <div style="font-size: 11px; font-weight: 500; color: #555;">
                        <span style="color: #9cc31a;">📊</span> KPIs
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
                <span style="color: #9cc31a;">🛡️</span>
                <span style="color: #888; font-size: 10px;"> Accès sécurisé</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    return False

# ==================== SIDEBAR NAVIGATION ====================
def sidebar_navigation():
    with st.sidebar:
        st.markdown("<br>", unsafe_allow_html=True)
        role_color = {"admin": "#3b82f6", "chef": "#f59e0b", "invite": "#8b949e"}.get(st.session_state.role, "#8b949e")
        role_icon  = {"admin": "🔑", "chef": "⚙️", "invite": "👁️"}.get(st.session_state.role, "👤")
        st.markdown(f"""
        <div style='text-align:center; padding:16px 12px; background:#161b22;
                    border:1px solid #21262d; border-radius:12px; margin-bottom:16px;'>
            <div style='font-size:36px; margin-bottom:6px;'>{role_icon}</div>
            <div style='font-family:Syne,sans-serif; font-size:15px; font-weight:700; color:#e2e8f0;'>
                {st.session_state.nom_user}
            </div>
            <div style='font-size:10px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase;
                        color:{role_color}; margin-top:4px;'>
                {st.session_state.role}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.role == "admin":
            st.success("✅ Accès complet")
        elif st.session_state.role == "chef":
            st.warning("⚙️ Chef d'atelier")
        else:
            st.info("👁️ Lecture seule")

        st.markdown("---")
        st.markdown("### 🧭 Navigation")

        pages = [
            ("🏠", "Accueil",             "Vue d'ensemble & alertes"),
            ("⚙️", "TPS & Performance",   "Taux de productivité"),
            ("📉", "Analyse des Pertes",  "Interruptions & pertes"),
            ("📦", "ADV Production",      "Adhérence au volume"),
            ("🔍", "Analyse par Machine", "Détail machine"),
            ("📋", "Données Brutes",      "Tableau & export"),
        ]

        if 'page_active' not in st.session_state:
            st.session_state.page_active = "Accueil"

        for icon, nom, desc in pages:
            if st.button(f"{icon}  {nom}", key=f"nav_{nom}", use_container_width=True, help=desc):
                st.session_state.page_active = nom
                st.rerun()

        st.markdown("---")
        st.markdown(f"""
        <div style='font-family:monospace; font-size:12px; color:#484f58; text-align:center;
                    padding:8px; background:#161b22; border-radius:8px; margin-bottom:8px;'>
            🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}
        </div>""", unsafe_allow_html=True)
        st.caption("LECTRA Dashboard v4.0")
        st.caption("Adient Morocco | PFE 2025")
        st.markdown("---")
        if st.button("🔓 Déconnexion", use_container_width=True):
            st.session_state.authentifie = False
            st.rerun()

# ==================== GENERATION DONNEES DEMO ====================
def generer_donnees_demo():
    machines = [f"L{i:02d}" for i in range(1, 21)]
    dates = pd.date_range(start='2025-06-01', end='2025-06-07', freq='D')
    
    data_rows = []
    for machine in machines:
        for date in dates:
            for shift in range(1, 4):
                tps = np.random.uniform(45, 95)
                adv = np.random.uniform(50, 110)
                cutting_time = np.random.uniform(120, 300)
                interruptions = np.random.uniform(10, 60)
                coda = np.random.uniform(0, 100)
                dt_matelas = np.random.uniform(5, 30)
                dt_posit = np.random.uniform(0, 50)
                posit_marker = np.random.uniform(0, 15)
                
                data_rows.append({
                    'DATE': date,
                    'Machine': machine,
                    'Shift': shift,
                    'TPS Shift': tps,
                    'ADV': adv,
                    'CUTTING TIME': cutting_time,
                    'INTERRUPTIONS TIME': interruptions,
                    'CODA INTERRUPTIONS TIME': coda,
                    'ΔT_Matelas': dt_matelas,
                    'DT_POSIT (min)': dt_posit,
                    'POSIT/Marker': posit_marker,
                    'Marker': f"MKR_{machine}_{date.day}_{shift}",
                    'STATE': np.random.choice(['En production', 'Maintenance', 'Panne', 'Arrêt'], p=[0.7, 0.1, 0.1, 0.1])
                })
    
    df = pd.DataFrame(data_rows)
    return df

# ==================== UTILITAIRES ====================
def time_to_minutes(val):
    """Convertit un format HH:MM:SS ou HH:MM en minutes"""
    if pd.isna(val):
        return 0
    if isinstance(val, str) and ':' in val:
        parts = val.strip().split(':')
        try:
            if len(parts) == 3:
                return int(parts[0]) * 60 + int(parts[1]) + int(parts[2]) / 60
            elif len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
        except:
            return 0
    elif isinstance(val, (int, float)):
        return float(val)
    return 0

def charger_donnees():
    excel_path = "modele_lectra.xlsx"
    
    if not os.path.exists(excel_path):
        return generer_donnees_demo()
    
    try:
        all_sheets = pd.read_excel(excel_path, sheet_name=None)
        dataframes = []
        
        for sheet_name, df in all_sheets.items():
            if df is not None and not df.empty:
                df['Machine'] = sheet_name
                
                # Colonnes numériques standard
                cols_to_convert = ['TPS Shift', 'ADV', 'CUTTING TIME', 'INTERRUPTIONS TIME', 'DWN TIME']
                
                for col in cols_to_convert:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Traitement pour DT_POSIT
                if 'DT_POSIT (min)' in df.columns:
                    df['DT_POSIT (min)'] = pd.to_numeric(df['DT_POSIT (min)'], errors='coerce')
                elif 'DT_POSIT' in df.columns:
                    df['DT_POSIT (min)'] = pd.to_numeric(df['DT_POSIT'], errors='coerce')
                elif 'DT_POSIT(min)' in df.columns:
                    df['DT_POSIT (min)'] = pd.to_numeric(df['DT_POSIT(min)'], errors='coerce')
                else:
                    df['DT_POSIT (min)'] = 0
                
                # Traitement pour CODA
                if 'CODA INTERRUPTIONS TIME' in df.columns:
                    df['CODA INTERRUPTIONS TIME'] = pd.to_numeric(df['CODA INTERRUPTIONS TIME'], errors='coerce')
                elif 'CODA INTERRUPTION' in df.columns:
                    df['CODA INTERRUPTIONS TIME'] = pd.to_numeric(df['CODA INTERRUPTION'], errors='coerce')
                else:
                    df['CODA INTERRUPTIONS TIME'] = 0
                
                # Traitement pour POSIT/Marker (format HH:MM:SS)
                if 'POSIT/Marker' in df.columns:
                    df['POSIT/Marker'] = df['POSIT/Marker'].apply(lambda x: time_to_minutes(x))
                elif 'POSIT/Mar' in df.columns:
                    df['POSIT/Marker'] = df['POSIT/Mar'].apply(lambda x: time_to_minutes(x))
                else:
                    df['POSIT/Marker'] = 0
                
                # Traitement pour ΔT_Matelas (format HH:MM:SS)
                if 'ΔT_Matelas' in df.columns:
                    df['ΔT_Matelas'] = df['ΔT_Matelas'].apply(lambda x: time_to_minutes(x))
                elif 'AT_Matel' in df.columns:
                    df['ΔT_Matelas'] = df['AT_Matel'].apply(lambda x: time_to_minutes(x))
                else:
                    df['ΔT_Matelas'] = 0
                
                if 'DATE' in df.columns:
                    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
                
                dataframes.append(df)
        
        if dataframes:
            df_combined = pd.concat(dataframes, ignore_index=True)
            return df_combined
        else:
            return generer_donnees_demo()
            
    except Exception as e:
        st.warning(f"Erreur lors du chargement: {e}")
        return generer_donnees_demo()

def calculer_tps_adv(df):
    """Calcule les indicateurs TPS et ADV par machine"""
    if df is None or df.empty:
        return pd.DataFrame()
    
    resultats = []
    
    for machine in sorted(df['Machine'].unique()):
        df_m = df[df['Machine'] == machine]
        
        tps_vals = df_m['TPS Shift'].dropna()
        tps_moyen = tps_vals.mean() if len(tps_vals) > 0 else 0
        
        adv_vals = df_m['ADV'].dropna() if 'ADV' in df_m.columns else pd.Series()
        adv_moyen = adv_vals.mean() if len(adv_vals) > 0 else 0
        
        cutting = df_m['CUTTING TIME'].fillna(0).sum() if 'CUTTING TIME' in df_m.columns else 0
        interruptions = df_m['INTERRUPTIONS TIME'].fillna(0).sum() if 'INTERRUPTIONS TIME' in df_m.columns else 0
        dwn_time = df_m['DWN TIME'].fillna(0).sum() if 'DWN TIME' in df_m.columns else 0
        dt_matelas = df_m['ΔT_Matelas'].fillna(0).sum() if 'ΔT_Matelas' in df_m.columns else 0
        
        coda = df_m['CODA INTERRUPTIONS TIME'].fillna(0).sum() if 'CODA INTERRUPTIONS TIME' in df_m.columns else 0
        posit_marker = df_m['POSIT/Marker'].fillna(0).sum() if 'POSIT/Marker' in df_m.columns else 0
        dt_posit = df_m['DT_POSIT (min)'].fillna(0).sum() if 'DT_POSIT (min)' in df_m.columns else 0
        
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
            'Statut': "✅ OK" if tps_moyen >= 75 else "⚠️ NOK"
        })
    
    return pd.DataFrame(resultats)

def page_header(icon, titre, sous_titre, badge=None):
    badge_html = f'<span class="header-badge">{badge}</span>' if badge else ''
    st.markdown(f"""
    <div class="page-header">
        <h1>{icon} {titre}</h1>
        <p>{sous_titre}</p>
        {badge_html}
    </div>
    """, unsafe_allow_html=True)

# ==================== PAGE 1 : ACCUEIL ====================
def page_accueil(df, df_tps):
    now = datetime.now()
    page_header(
        "🏭", "Tableau de Bord — Vue d'ensemble",
        "Adient Morocco | Atelier de Coupe | Projet MMA / Mercedes",
        badge=f"Mis à jour : {now.strftime('%d/%m/%Y %H:%M')}"
    )

    total_machines = len(df_tps)
    ok_count   = len(df_tps[df_tps['TPS (%)'] >= 75])
    nok_count  = total_machines - ok_count
    health_pct = int(ok_count / total_machines * 100) if total_machines else 0
    health_color = "#22c55e" if health_pct >= 70 else "#f59e0b" if health_pct >= 40 else "#ef4444"

    st.markdown(f"""
    <div class="status-bar">
        <span><span class="status-dot status-online"></span> Système en ligne</span>
        <span style="color:#21262d;">|</span>
        <span>🏭 {total_machines} machines</span>
        <span style="color:#21262d;">|</span>
        <span style="color:{health_color}; font-weight:700;">● Santé atelier : {health_pct}%</span>
        <span style="color:#21262d;">|</span>
        <span>✅ {ok_count} OK &nbsp;·&nbsp; ⚠️ {nok_count} NOK</span>
        <span style="margin-left:auto; font-family: monospace;">📅 {now.strftime('%A %d %B %Y').capitalize()}</span>
    </div>
    """, unsafe_allow_html=True)

    tps_moyen  = df_tps['TPS (%)'].mean()
    adv_moyen  = df_tps['ADV (%)'].mean() if df_tps['ADV (%)'].sum() > 0 else 0
    machines_nok = len(df_tps[df_tps['TPS (%)'] < 75])
    total_interruptions = df['INTERRUPTIONS TIME'].sum() if 'INTERRUPTIONS TIME' in df.columns else 0
    total_coda = df['CODA INTERRUPTIONS TIME'].sum() if 'CODA INTERRUPTIONS TIME' in df.columns else 0
    total_dt_posit = df['DT_POSIT (min)'].sum() if 'DT_POSIT (min)' in df.columns else 0
    total_dt_matelas = df['ΔT_Matelas'].sum() if 'ΔT_Matelas' in df.columns else 0
    total_markers = len(df)
    jours = df['DATE'].nunique() if 'DATE' in df.columns else 1

    tps_color   = "#22c55e" if tps_moyen >= 75 else "#f59e0b" if tps_moyen >= 40 else "#ef4444"
    adv_color   = "#22c55e" if adv_moyen >= 100 else "#f59e0b" if adv_moyen >= 80 else "#ef4444"
    nok_color   = "#ef4444" if machines_nok > 0 else "#22c55e"
    inter_color = "#f59e0b"
    mark_color  = "#a855f7"

    kpis = [
        (f"{tps_moyen:.1f}%",            "TPS Moyen Atelier",      "Taux de productivité",  tps_color),
        (f"{adv_moyen:.1f}%",            "ADV Moyenne",            "Adhérence au volume",   adv_color),
        (f"{machines_nok}/{len(df_tps)}","Machines sous objectif", "< 75% TPS",             nok_color),
        (f"{total_interruptions:.0f}",   "Total Interruptions",    "minutes cumulées",      inter_color),
        (f"{total_markers}",             "Total Markers",          f"{jours} jours analysés", mark_color),
    ]

    cols = st.columns(5)
    for col, (val, label, sublabel, color) in zip(cols, kpis):
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="--accent:{color};">
                <div class="kpi-value">{val}</div>
                <div class="kpi-label">{label}</div>
                <div class="kpi-unit">{sublabel}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<div class="section-title"><span class="dot"></span> Jauge TPS Atelier</div>', unsafe_allow_html=True)
        gauge_color = tps_color
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=tps_moyen,
            number={'font': {'size': 42, 'color': gauge_color, 'family': 'Syne'}},
            delta={
                'reference': 75,
                'increasing': {'color': "#22c55e"},
                'decreasing': {'color': "#ef4444"},
                'font': {'size': 14}
            },
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': '#484f58', 'tickfont': {'color': '#8b949e', 'size': 10}},
                'bar': {'color': gauge_color, 'thickness': 0.28},
                'bgcolor': '#161b22',
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 40],  'color': 'rgba(239,68,68,0.15)'},
                    {'range': [40, 75], 'color': 'rgba(245,158,11,0.12)'},
                    {'range': [75, 100],'color': 'rgba(34,197,94,0.12)'},
                ],
                'threshold': {
                    'line': {'color': "#f59e0b", 'width': 2},
                    'thickness': 0.78,
                    'value': 75
                }
            },
            title={'text': "TPS Moyen Atelier (%)", 'font': {'size': 13, 'color': '#8b949e', 'family': 'DM Sans'}}
        ))
        fig_gauge.update_layout(
            height=280,
            margin=dict(t=40, b=20, l=20, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#c9d1d9'
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title"><span class="dot" style="background:#ef4444"></span> Alertes Machines</div>', unsafe_allow_html=True)

        critiques   = df_tps[df_tps['TPS (%)'] < 40]
        attention   = df_tps[(df_tps['TPS (%)'] >= 40) & (df_tps['TPS (%)'] < 75)]
        ok_machines = df_tps[df_tps['TPS (%)'] >= 75]

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown("""<div style="font-size:12px;font-weight:700;color:#fca5a5;text-transform:uppercase;
                letter-spacing:0.8px;margin-bottom:10px;">🔴 Critique</div>""", unsafe_allow_html=True)
            if len(critiques) == 0:
                st.markdown('<div class="alert-card-red"><div class="alert-machine" style="color:#8b949e;font-weight:400;font-size:13px;">Aucune machine</div></div>', unsafe_allow_html=True)
            for _, r in critiques.iterrows():
                st.markdown(f"""
                <div class="alert-card-red">
                    <span class="alert-badge badge-red">CRITIQUE</span>
                    <div class="alert-machine">{r["Machine"]}</div>
                    <div class="alert-tps">TPS : {r['TPS (%)']:.1f}% &nbsp;·&nbsp; Écart : {r['Écart (%)']:.1f}%</div>
                </div>""", unsafe_allow_html=True)

        with c2:
            st.markdown("""<div style="font-size:12px;font-weight:700;color:#fed7aa;text-transform:uppercase;
                letter-spacing:0.8px;margin-bottom:10px;">🟠 À surveiller</div>""", unsafe_allow_html=True)
            if len(attention) == 0:
                st.markdown('<div class="alert-card-orange"><div class="alert-machine" style="color:#8b949e;font-weight:400;font-size:13px;">Aucune machine</div></div>', unsafe_allow_html=True)
            for _, r in attention.iterrows():
                st.markdown(f"""
                <div class="alert-card-orange">
                    <span class="alert-badge badge-orange">ATTENTION</span>
                    <div class="alert-machine">{r["Machine"]}</div>
                    <div class="alert-tps">TPS : {r['TPS (%)']:.1f}% &nbsp;·&nbsp; Écart : {r['Écart (%)']:.1f}%</div>
                </div>""", unsafe_allow_html=True)

        with c3:
            st.markdown("""<div style="font-size:12px;font-weight:700;color:#86efac;text-transform:uppercase;
                letter-spacing:0.8px;margin-bottom:10px;">🟢 Objectif atteint</div>""", unsafe_allow_html=True)
            if len(ok_machines) == 0:
                st.markdown('<div class="alert-card-green"><div class="alert-machine" style="color:#8b949e;font-weight:400;font-size:13px;">Aucune machine</div></div>', unsafe_allow_html=True)
            for _, r in ok_machines.iterrows():
                st.markdown(f"""
                <div class="alert-card-green">
                    <span class="alert-badge badge-green">OK</span>
                    <div class="alert-machine">{r["Machine"]}</div>
                    <div class="alert-tps">TPS : {r['TPS (%)']:.1f}% &nbsp;·&nbsp; ADV : {r['ADV (%)']:.1f}%</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    st.markdown('<div class="section-title"><span class="dot" style="background:#a855f7"></span> Résumé Performance par Machine</div>', unsafe_allow_html=True)

    rows_html = ""
    for _, r in df_tps.iterrows():
        tps = r['TPS (%)']
        adv = r['ADV (%)']
        if tps >= 75:
            pill_style = "background:rgba(34,197,94,0.18);color:#86efac;"
            statut = "✅ OK"
        elif tps >= 40:
            pill_style = "background:rgba(245,158,11,0.18);color:#fde68a;"
            statut = "⚠️ NOK"
        else:
            pill_style = "background:rgba(239,68,68,0.18);color:#fca5a5;"
            statut = "🔴 CRITIQUE"

        ecart = r['Écart (%)']
        ecart_html = f'<span style="color:#22c55e;">+{ecart:.1f}%</span>' if ecart >= 0 else f'<span style="color:#ef4444;">{ecart:.1f}%</span>'

        rows_html += f"""
        <tr>
            <td style="font-weight:600;color:#e2e8f0;font-family:Syne,sans-serif;">{r['Machine']}</td>
            <td><span class="tps-pill" style="{pill_style}">{tps:.1f}%</span></td>
            <td style="color:#8b949e;">75%</td>
            <td>{ecart_html}</td>
            <td style="color:#93c5fd;">{adv:.1f}%</td>
            <td><span class="tps-pill" style="{pill_style}">{statut}</span></td>
        </tr>"""

    st.markdown(f"""
    <div style="background:#161b22;border:1px solid #21262d;border-radius:12px;overflow:hidden;">
        <table class="perf-table">
            <thead>
                <tr>
                    <th>Machine</th>
                    <th>TPS (%)</th>
                    <th>Objectif</th>
                    <th>Écart</th>
                    <th>ADV (%)</th>
                    <th>Statut</th>
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

# ==================== PAGE 2 : TPS & PERFORMANCE ====================
def page_tps(df, df_tps):
    page_header("⚙️", "TPS & Performance", "Taux de Productivité Synthétique par machine")

    st.markdown('<div class="section-title">📊 TPS par Machine vs Objectif (75%)</div>', unsafe_allow_html=True)
    colors = ['#d62728' if t < 40 else '#ff7f0e' if t < 75 else '#2ca02c' for t in df_tps['TPS (%)']]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_tps['Machine'], y=df_tps['TPS (%)'],
        marker_color=colors, name='TPS Réel',
        text=[f"{v:.1f}%" for v in df_tps['TPS (%)']], textposition='outside'
    ))
    fig.add_trace(go.Scatter(
        x=df_tps['Machine'], y=[75] * len(df_tps),
        mode='lines', name='Objectif 75%', line=dict(color='#1f77b4', width=2, dash='dash')
    ))
    fig.update_layout(
        yaxis=dict(title="TPS (%)", range=[0, 100]), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02), height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">🗺️ Heatmap Cutting Time</div>', unsafe_allow_html=True)
        if 'DATE' in df.columns:
            pivot = df.pivot_table(values='CUTTING TIME', index='Machine', columns='DATE', aggfunc='sum', fill_value=0)
            fig_heat = px.imshow(pivot, text_auto='.0f', aspect='auto', color_continuous_scale='Blues', title="Temps de coupe (Machine × Date)")
            fig_heat.update_layout(height=350)
            st.plotly_chart(fig_heat, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">📈 Évolution TPS journalier</div>', unsafe_allow_html=True)
        if 'DATE' in df.columns:
            tps_jour = []
            for date in sorted(df['DATE'].unique()):
                df_d = df[df['DATE'] == date]
                df_tps_d = calculer_tps_adv(df_d)
                tps_jour.append({'Date': date, 'TPS Moyen (%)': df_tps_d['TPS (%)'].mean()})
            df_tps_jour = pd.DataFrame(tps_jour)
            fig_evol = go.Figure()
            fig_evol.add_trace(go.Scatter(
                x=df_tps_jour['Date'], y=df_tps_jour['TPS Moyen (%)'], mode='lines+markers+text',
                text=[f"{v:.1f}%" for v in df_tps_jour['TPS Moyen (%)']], textposition='top center',
                line=dict(color='#1f77b4', width=2), marker=dict(size=8)
            ))
            fig_evol.add_trace(go.Scatter(
                x=df_tps_jour['Date'], y=[75] * len(df_tps_jour), mode='lines', name='Objectif 75%', line=dict(color='red', dash='dash', width=1.5)
            ))
            fig_evol.update_layout(yaxis=dict(range=[0, 100], title="TPS (%)"), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=350)
            st.plotly_chart(fig_evol, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-title">🎯 Jauges TPS par Machine</div>', unsafe_allow_html=True)
    machines = df_tps['Machine'].tolist()
    n_cols = min(3, len(machines))
    cols = st.columns(n_cols)
    for i, (_, row) in enumerate(df_tps.iterrows()):
        with cols[i % n_cols]:
            color = "#2ca02c" if row['TPS (%)'] >= 75 else "#ff7f0e" if row['TPS (%)'] >= 40 else "#d62728"
            fig_g = go.Figure(go.Indicator(
                mode="gauge+number", value=row['TPS (%)'],
                gauge={
                    'axis': {'range': [0, 100]}, 'bar': {'color': color},
                    'steps': [{'range': [0, 40], 'color': '#ffe0e0'}, {'range': [40, 75], 'color': '#fff3cd'}, {'range': [75, 100], 'color': '#d4edda'}],
                    'threshold': {'line': {'color': "red", 'width': 2}, 'thickness': 0.75, 'value': 75}
                },
                title={'text': row['Machine']}
            ))
            fig_g.update_layout(height=220, margin=dict(t=50, b=10, l=20, r=20))
            st.plotly_chart(fig_g, use_container_width=True)

# ==================== PAGE 3 : ANALYSE DES PERTES ====================
def page_pertes(df, df_tps):
    page_header("📉", "Analyse des Pertes", "Interruptions, CODA, DT_POSIT, POSIT/Marker et ΔT_Matelas par machine")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">📊 Pertes empilées par machine</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Interruptions', x=df_tps['Machine'], y=df_tps['Interruptions (min)'], marker_color='#d62728'))
        fig.add_trace(go.Bar(name='CODA', x=df_tps['Machine'], y=df_tps['CODA (min)'], marker_color='#9467bd'))
        fig.add_trace(go.Bar(name='DT_POSIT', x=df_tps['Machine'], y=df_tps['DT_POSIT (min)'], marker_color='#ff7f0e'))
        fig.add_trace(go.Bar(name='POSIT/Marker', x=df_tps['Machine'], y=df_tps['POSIT/Marker'], marker_color='#17becf'))
        fig.add_trace(go.Bar(name='ΔT_Matelas', x=df_tps['Machine'], y=df_tps['ΔT_Matelas (min)'], marker_color='#7f7f7f'))
        fig.update_layout(barmode='stack', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=450, yaxis_title="Minutes")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">🥧 Répartition globale des pertes</div>', unsafe_allow_html=True)
        t_int = df_tps['Interruptions (min)'].sum()
        t_coda = df_tps['CODA (min)'].sum()
        t_pos = df_tps['DT_POSIT (min)'].sum()
        t_posit_marker = df_tps['POSIT/Marker'].sum()
        t_del = df_tps['ΔT_Matelas (min)'].sum()
        
        fig_pie = px.pie(
            values=[t_int, t_coda, t_pos, t_posit_marker, t_del], 
            names=['Interruptions', 'CODA', 'DT_POSIT', 'POSIT/Marker', 'ΔT_Matelas'],
            color_discrete_sequence=['#d62728', '#9467bd', '#ff7f0e', '#17becf', '#7f7f7f'], 
            hole=0.4, title="Répartition globale"
        )
        fig_pie.update_traces(textinfo='percent+label')
        fig_pie.update_layout(height=450)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-title">📊 Diagramme de Pareto des Pertes</div>', unsafe_allow_html=True)
    
    pareto_data = pd.DataFrame({
        'Source': ['Interruptions', 'CODA', 'DT_POSIT', 'POSIT/Marker', 'ΔT_Matelas'], 
        'Total (min)': [t_int, t_coda, t_pos, t_posit_marker, t_del]
    }).sort_values('Total (min)', ascending=False)
    pareto_data['Cumul (%)'] = pareto_data['Total (min)'].cumsum() / pareto_data['Total (min)'].sum() * 100

    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Bar(
        x=pareto_data['Source'], y=pareto_data['Total (min)'], 
        marker_color=['#d62728', '#9467bd', '#ff7f0e', '#17becf', '#7f7f7f'], 
        name='Durée (min)',
        text=[f"{v:.0f} min" for v in pareto_data['Total (min)']], textposition='outside'
    ))
    fig_pareto.add_trace(go.Scatter(
        x=pareto_data['Source'], y=pareto_data['Cumul (%)'], mode='lines+markers+text',
        text=[f"{v:.1f}%" for v in pareto_data['Cumul (%)']], textposition='top center', name='Cumul (%)', yaxis='y2',
        line=dict(color='#1f77b4', width=2), marker=dict(size=8)
    ))
    fig_pareto.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="80%", yref='y2')
    fig_pareto.update_layout(
        yaxis=dict(title="Durée (minutes)"), yaxis2=dict(title="Cumul (%)", overlaying='y', side='right', range=[0, 110]),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', legend=dict(orientation="h", yanchor="bottom", y=1.02), height=450
    )
    st.plotly_chart(fig_pareto, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-title">🥧 Répartition des pertes par machine</div>', unsafe_allow_html=True)
    machines = df_tps['Machine'].tolist()
    n_cols = min(3, len(machines))
    cols_pie = st.columns(n_cols)
    for i, (_, row) in enumerate(df_tps.iterrows()):
        with cols_pie[i % n_cols]:
            fig_m = px.pie(
                values=[row['Interruptions (min)'], row['CODA (min)'], row['DT_POSIT (min)'], row['POSIT/Marker'], row['ΔT_Matelas (min)']],
                names=['Interruptions', 'CODA', 'DT_POSIT', 'POSIT/Marker', 'ΔT_Matelas'], 
                title=row['Machine'],
                color_discrete_sequence=['#d62728', '#9467bd', '#ff7f0e', '#17becf', '#7f7f7f'], 
                hole=0.35
            )
            fig_m.update_traces(textinfo='percent')
            fig_m.update_layout(height=300, margin=dict(t=40, b=10, l=10, r=10), showlegend=False)
            st.plotly_chart(fig_m, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-title">📋 Tableau détaillé des pertes</div>', unsafe_allow_html=True)
    cols_pertes = ['Machine', 'Interruptions (min)', 'CODA (min)', 'DT_POSIT (min)', 'POSIT/Marker', 'ΔT_Matelas (min)', 'Cutting (min)', 'TPS (%)']
    st.dataframe(df_tps[cols_pertes], use_container_width=True, hide_index=True)

# ==================== PAGE 4 : ADV PRODUCTION ====================
def page_adv(df, df_tps):
    page_header("📦", "ADV — Adhérence au Volume de Production", "Suivi journalier de la production réalisée vs planifiée")

    if 'DATE' not in df.columns or 'ADV' not in df.columns:
        st.warning("⚠️ Colonnes DATE ou ADV non disponibles dans les données.")
        return

    df_adv = df.groupby('DATE').apply(lambda x: pd.to_numeric(x['ADV'], errors='coerce').mean() * 100).reset_index()
    df_adv.columns = ['DATE', 'ADV (%)']
    df_adv = df_adv.dropna()

    adv_moy = df_adv['ADV (%)'].mean()
    adv_min = df_adv['ADV (%)'].min()
    adv_max = df_adv['ADV (%)'].max()
    jours_nok = len(df_adv[df_adv['ADV (%)'] < 100])

    col1, col2, col3, col4 = st.columns(4)
    for col, val, label, color in [
        (col1, f"{adv_moy:.1f}%",  "📊 ADV Moyenne",       "#1f77b4"),
        (col2, f"{adv_min:.1f}%",  "📉 ADV Minimale",      "#d62728"),
        (col3, f"{adv_max:.1f}%",  "📈 ADV Maximale",      "#2ca02c"),
        (col4, f"{jours_nok}j",    "❌ Jours sous objectif","#ff7f0e"),
    ]:
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="border-left-color:{color};">
                <div class="kpi-value" style="color:{color};">{val}</div>
                <div class="kpi-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-title">📊 ADV journalière vs Objectif (100%)</div>', unsafe_allow_html=True)
    colors_adv = ['#2ca02c' if v >= 100 else '#d62728' for v in df_adv['ADV (%)']]
    fig_adv = go.Figure()
    fig_adv.add_trace(go.Bar(
        x=df_adv['DATE'], y=df_adv['ADV (%)'], marker_color=colors_adv, name='ADV Réelle',
        text=[f"{v:.1f}%" for v in df_adv['ADV (%)']], textposition='outside'
    ))
    fig_adv.add_trace(go.Scatter(x=df_adv['DATE'], y=[100] * len(df_adv), mode='lines', name='Objectif 100%', line=dict(color='#ff7f0e', width=2, dash='dash')))
    fig_adv.update_layout(yaxis=dict(title="ADV (%)", range=[0, 120]), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=380)
    st.plotly_chart(fig_adv, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-title">🏭 ADV par Machine</div>', unsafe_allow_html=True)
    df_adv_m = df_tps[df_tps['ADV (%)'] > 0][['Machine', 'ADV (%)']]
    if not df_adv_m.empty:
        colors_m = ['#2ca02c' if v >= 100 else '#d62728' for v in df_adv_m['ADV (%)']]
        fig_adv_m = go.Figure(go.Bar(
            x=df_adv_m['Machine'], y=df_adv_m['ADV (%)'], marker_color=colors_m,
            text=[f"{v:.1f}%" for v in df_adv_m['ADV (%)']], textposition='outside'
        ))
        fig_adv_m.add_hline(y=100, line_dash="dash", line_color="orange", annotation_text="Objectif 100%")
        fig_adv_m.update_layout(yaxis=dict(range=[0, 120], title="ADV (%)"), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=350)
        st.plotly_chart(fig_adv_m, use_container_width=True)
    else:
        st.info("Pas de données ADV par machine disponibles.")

# ==================== PAGE 5 : ANALYSE PAR MACHINE ====================
def page_machine(df, df_tps):
    page_header("🔍", "Analyse Détaillée par Machine", "Sélectionnez une machine pour voir son analyse complète")

    machine_selectionnee = st.selectbox("🏭 Choisir une machine :", sorted(df['Machine'].unique()))
    df_m = df[df['Machine'] == machine_selectionnee]
    df_tps_m = df_tps[df_tps['Machine'] == machine_selectionnee].iloc[0]

    st.markdown("---")
    col1, col2, col3, col4, col5 = st.columns(5)
    tps_val = df_tps_m['TPS (%)']
    color_tps = "#2ca02c" if tps_val >= 75 else "#ff7f0e" if tps_val >= 40 else "#d62728"
    
    for col, val, label, color in [
        (col1, f"{tps_val:.1f}%", "⚙️ TPS", color_tps),
        (col2, f"{df_tps_m['Interruptions (min)']:.0f} min", "⚠️ Interruptions", "#d62728"),
        (col3, f"{df_tps_m['CODA (min)']:.0f} min", "📊 CODA", "#9467bd"),
        (col4, f"{df_tps_m['DT_POSIT (min)']:.0f} min", "📍 DT_POSIT", "#ff7f0e"),
        (col5, f"{df_tps_m['ΔT_Matelas (min)']:.0f} min", "🔄 ΔT_Matelas", "#7f7f7f"),
    ]:
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="border-left-color:{color};">
                <div class="kpi-value" style="color:{color};">{val}</div>
                <div class="kpi-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f'<div class="section-title">🎯 Jauge TPS — {machine_selectionnee}</div>', unsafe_allow_html=True)
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number+delta", value=tps_val, delta={'reference': 75},
            gauge={
                'axis': {'range': [0, 100]}, 'bar': {'color': color_tps},
                'steps': [{'range': [0, 40], 'color': '#ffe0e0'}, {'range': [40, 75], 'color': '#fff3cd'}, {'range': [75, 100], 'color': '#d4edda'}],
                'threshold': {'line': {'color': "red", 'width': 3}, 'thickness': 0.75, 'value': 75}
            },
            title={'text': f"TPS {machine_selectionnee} (%)"}
        ))
        fig_g.update_layout(height=280, margin=dict(t=40, b=10, l=20, r=20))
        st.plotly_chart(fig_g, use_container_width=True)

    with col2:
        st.markdown(f'<div class="section-title">🥧 Répartition des pertes — {machine_selectionnee}</div>', unsafe_allow_html=True)
        fig_pie = px.pie(
            values=[df_tps_m['Interruptions (min)'], df_tps_m['CODA (min)'], df_tps_m['DT_POSIT (min)'], df_tps_m['POSIT/Marker'], df_tps_m['ΔT_Matelas (min)']],
            names=['Interruptions', 'CODA', 'DT_POSIT', 'POSIT/Marker', 'ΔT_Matelas'], 
            color_discrete_sequence=['#d62728', '#9467bd', '#ff7f0e', '#17becf', '#7f7f7f'], 
            hole=0.4
        )
        fig_pie.update_traces(textinfo='percent+label')
        fig_pie.update_layout(height=280, margin=dict(t=20, b=10))
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    if 'DATE' in df_m.columns:
        st.markdown(f'<div class="section-title">📈 Évolution journalière — {machine_selectionnee}</div>', unsafe_allow_html=True)
        evol = df_m.groupby('DATE')['CUTTING TIME'].sum().reset_index()
        fig_evol = px.line(evol, x='DATE', y='CUTTING TIME', markers=True, title=f"Temps de coupe journalier — {machine_selectionnee}")
        fig_evol.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=300)
        st.plotly_chart(fig_evol, use_container_width=True)

    st.markdown("---")
    st.markdown(f'<div class="section-title">📋 Données — {machine_selectionnee}</div>', unsafe_allow_html=True)
    cols_show = [c for c in ['DATE', 'Marker', 'CUTTING TIME', 'INTERRUPTIONS TIME', 'CODA INTERRUPTIONS TIME', 'DT_POSIT (min)', 'POSIT/Marker', 'ΔT_Matelas', 'STATE'] if c in df_m.columns]
    st.dataframe(df_m[cols_show], use_container_width=True, hide_index=True)

# ==================== PAGE 6 : DONNÉES BRUTES ====================
def page_donnees(df, df_tps):
    page_header("📋", "Données Brutes", "Tableau complet avec filtres et export")

    col1, col2, col3 = st.columns(3)
    with col1:
        machines = ['Toutes'] + sorted(df['Machine'].unique().tolist())
        filtre_machine = st.selectbox("🏭 Machine", machines)
    with col2:
        if 'DATE' in df.columns:
            dates = ['Toutes'] + sorted(df['DATE'].unique().tolist(), reverse=True)
            filtre_date = st.selectbox("📅 Date", dates)
        else:
            filtre_date = 'Toutes'
    with col3:
        if 'STATE' in df.columns:
            states = ['Tous'] + sorted(df['STATE'].dropna().unique().tolist())
            filtre_state = st.selectbox("⚙️ Statut", states)
        else:
            filtre_state = 'Tous'

    df_f = df.copy()
    if filtre_machine != 'Toutes': df_f = df_f[df_f['Machine'] == filtre_machine]
    if filtre_date   != 'Toutes' and 'DATE' in df_f.columns: df_f = df_f[df_f['DATE'] == filtre_date]
    if filtre_state  != 'Tous'   and 'STATE' in df_f.columns: df_f = df_f[df_f['STATE'] == filtre_state]

    st.info(f"📊 **{len(df_f)} lignes** affichées sur {len(df)} total")
    st.markdown("---")

    cols_show = [c for c in ['DATE', 'Machine', 'Marker', 'CUTTING TIME', 'INTERRUPTIONS TIME', 'CODA INTERRUPTIONS TIME', 'DT_POSIT (min)', 'POSIT/Marker', 'ΔT_Matelas', 'STATE'] if c in df_f.columns]
    if st.session_state.role == "admin":
        st.caption("✏️ Mode édition — double-cliquez pour modifier")
        st.data_editor(df_f[cols_show], use_container_width=True, hide_index=True)
    else:
        st.dataframe(df_f[cols_show], use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown('<div class="section-title">📥 Export</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📎 Exporter données filtrées (CSV)", data=df_f.to_csv(index=False).encode('utf-8'), file_name=f"lectra_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv", use_container_width=True)
    with col2:
        st.download_button("📊 Exporter tableau TPS/ADV (CSV)", data=df_tps.to_csv(index=False).encode('utf-8'), file_name=f"tps_adv_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv", use_container_width=True)

# ==================== MAIN ====================
def main():
    if not verifier_mot_de_passe():
        return

    sidebar_navigation()

    df = charger_donnees()
    if df is None or df.empty:
        st.warning("⚠️ Aucune donnée trouvée. Vérifiez le fichier modele_lectra.xlsx")
        st.stop()

    # ==================== FILTRE DATE GLOBAL ====================
    if 'DATE' in df.columns and not df.empty:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📅 Filtre par Date")
        
        # Récupérer toutes les dates disponibles
        dates_disponibles = sorted(df['DATE'].unique())
        
        # Créer un sélecteur de dates
        date_min = dates_disponibles[0] if dates_disponibles else datetime.now()
        date_max = dates_disponibles[-1] if dates_disponibles else datetime.now()
        
        # Sélecteur de plage de dates
        date_debut = st.sidebar.date_input(
            "📅 Date de début",
            value=date_min,
            min_value=date_min,
            max_value=date_max
        )
        
        date_fin = st.sidebar.date_input(
            "📅 Date de fin",
            value=date_max,
            min_value=date_min,
            max_value=date_max
        )
        
        # Convertir en datetime pour la comparaison
        date_debut = pd.to_datetime(date_debut)
        date_fin = pd.to_datetime(date_fin)
        
        # Filtrer les données
        df_filtre = df[(df['DATE'] >= date_debut) & (df['DATE'] <= date_fin)]
        
        if df_filtre.empty:
            st.warning(f"⚠️ Aucune donnée disponible entre le {date_debut.strftime('%d/%m/%Y')} et le {date_fin.strftime('%d/%m/%Y')}")
            st.stop()
        
        # Afficher la plage sélectionnée dans la sidebar
        st.sidebar.info(f"📊 Données du **{date_debut.strftime('%d/%m/%Y')}** au **{date_fin.strftime('%d/%m/%Y')}**")
        
        # Calculer TPS avec les données filtrées
        df_tps = calculer_tps_adv(df_filtre)
        
        # Stocker les données filtrées dans session_state
        st.session_state.df_filtre = df_filtre
        st.session_state.df_tps = df_tps
        st.session_state.date_debut = date_debut
        st.session_state.date_fin = date_fin
    else:
        df_tps = calculer_tps_adv(df)
        st.session_state.df_filtre = df
        st.session_state.df_tps = df_tps
    
    page = st.session_state.get('page_active', 'Accueil')

    if page == "Accueil": 
        page_accueil(st.session_state.df_filtre, st.session_state.df_tps)
    elif page == "TPS & Performance": 
        page_tps(st.session_state.df_filtre, st.session_state.df_tps)
    elif page == "Analyse des Pertes": 
        page_pertes(st.session_state.df_filtre, st.session_state.df_tps)
    elif page == "ADV Production": 
        page_adv(st.session_state.df_filtre, st.session_state.df_tps)
    elif page == "Analyse par Machine": 
        page_machine(st.session_state.df_filtre, st.session_state.df_tps)
    elif page == "Données Brutes": 
        page_donnees(st.session_state.df_filtre, st.session_state.df_tps)

    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; color:#484f58; font-size:11px; padding:20px 0 10px; letter-spacing:0.5px;'>
        🏭 Adient Morocco — LECTRA Dashboard v4.0 &nbsp;|&nbsp; Projet PFE 2025 &nbsp;|&nbsp; Tiflet
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
