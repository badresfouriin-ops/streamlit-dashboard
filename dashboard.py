import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import requests
import base64  # Import indispensable pour l'encodage de l'image d'arrière-plan

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
    .main { background-color: #f8f9fa; }

    .kpi-card {
        background: linear-gradient(135deg, #ffffff, #f0f4ff);
        border-radius: 12px;
        padding: 18px 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-left: 4px solid #1f77b4;
        transition: transform 0.2s, box-shadow 0.2s;
        margin-bottom: 10px;
    }
    .kpi-card:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.12); }
    .kpi-value { font-size: 34px; font-weight: 800; color: #1f77b4; line-height: 1.1; }
    .kpi-label { font-size: 13px; color: #555; margin-top: 4px; font-weight: 500; }
    .kpi-unit { font-size: 11px; color: #aaa; margin-top: 2px; }

    .alert-card-red {
        background: linear-gradient(135deg, #fff5f5, #ffe0e0);
        border-left: 4px solid #e53e3e;
        border-radius: 10px; padding: 14px; margin-bottom: 8px;
    }
    .alert-card-orange {
        background: linear-gradient(135deg, #fffaf0, #ffecd2);
        border-left: 4px solid #ed8936;
        border-radius: 10px; padding: 14px; margin-bottom: 8px;
    }
    .alert-card-green {
        background: linear-gradient(135deg, #f0fff4, #d4edda);
        border-left: 4px solid #38a169;
        border-radius: 10px; padding: 14px; margin-bottom: 8px;
    }

    .section-title {
        font-size: 20px; font-weight: 700; color: #2d3748;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 6px; margin-bottom: 16px;
    }

    .page-header {
        background: linear-gradient(135deg, #1f77b4, #2196F3);
        color: white; padding: 20px 25px; border-radius: 12px;
        margin-bottom: 20px;
    }

    [data-testid="stSidebar"] { background-color: #1a1f2e; }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }

    .nav-item {
        padding: 10px 15px; border-radius: 8px; margin: 4px 0;
        cursor: pointer; transition: background 0.2s;
    }
    .nav-item:hover { background: rgba(255,255,255,0.1); }
    .nav-item-active { background: rgba(31,119,180,0.4); border-left: 3px solid #1f77b4; }
</style>
""", unsafe_allow_html=True)

# ==================== AUTHENTIFICATION ====================
USERS = {
    "admin123":  {"role": "admin",  "nom": "Administrateur"},
    "invite123": {"role": "invite", "nom": "Invité"},
    "chef123":   {"role": "chef",   "nom": "Chef d'atelier"},
}

def verifier_mot_de_passe():
    if "authentifie" not in st.session_state:
        st.session_state.authentifie = False
        st.session_state.role = None
        st.session_state.nom_user = ""

    if st.session_state.authentifie:
        return True

    # Encodage image de fond
    bg_image_path = "background.png"
    if os.path.exists(bg_image_path):
        with open(bg_image_path, "rb") as image_file:
            img_base64 = base64.b64encode(image_file.read()).decode()
        bg_css = f'background-image: url("data:image/png;base64,{img_base64}");'
    else:
        bg_css = "background: linear-gradient(135deg, #061826, #0b2d3b);"

    st.markdown(f"""
    <style>
    /* Cache éléments Streamlit inutiles */
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stSidebar"] {{
        display: none !important;
    }}
    .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
    }}

    /* Fond photo plein écran */
    .stApp {{
        {bg_css}
        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        min-height: 100vh !important;
        overflow: hidden !important;
    }}

    /* Overlay sombre avec dégradé directionnel */
    .stApp::before {{
        content: "";
        position: fixed;
        inset: 0;
        background: linear-gradient(
            105deg,
            rgba(3,18,32,0.08) 0%,
            rgba(3,18,32,0.55) 35%,
            rgba(3,18,32,0.82) 65%,
            rgba(3,18,32,0.92) 100%
        );
        z-index: 0;
    }}

    /* Carte login flottante */
    .login-card {{
        position: fixed;
        top: 50%;
        left: 42px;
        transform: translateY(-50%);
        width: 395px;
        background: rgba(255,255,255,0.98);
        border-radius: 16px;
        box-shadow: 0 25px 60px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.1);
        z-index: 10;
        padding: 38px 40px 30px;
        box-sizing: border-box;
    }}

    /* Ligne verte déco en haut de la carte */
    .login-card::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #9cc31a, #c8e840);
        border-radius: 16px 16px 0 0;
    }}

    /* Texte droite */
    .right-text {{
        position: fixed;
        left: 500px;
        bottom: 65px;
        z-index: 5;
        color: white;
        max-width: 700px;
    }}

    /* Inputs style amélioré */
    .stTextInput label p {{
        color: #073447 !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        margin-bottom: 4px !important;
    }}
    .stTextInput input {{
        background: #f8fafc !important;
        border: 1.5px solid #d7dee8 !important;
        border-radius: 8px !important;
        height: 44px !important;
        font-size: 14px !important;
        color: #1a2332 !important;
        padding: 0 14px !important;
        transition: all 0.2s !important;
    }}
    .stTextInput input:focus {{
        border-color: #9cc31a !important;
        background: #ffffff !important;
        box-shadow: 0 0 0 3px rgba(156,195,26,0.15) !important;
    }}
    .stTextInput input::placeholder {{
        color: #b0bec5 !important;
        font-size: 13px !important;
    }}

    /* Checkbox */
    .stCheckbox label p {{
        color: #4a5568 !important;
        font-size: 12px !important;
    }}

    /* Bouton connexion */
    .stButton button {{
        background: linear-gradient(135deg, #003f52, #005a74) !important;
        color: white !important;
        height: 48px !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        border: none !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s !important;
        margin-top: 8px !important;
    }}
    .stButton button:hover {{
        background: linear-gradient(135deg, #002f3e, #004a60) !important;
        box-shadow: 0 6px 18px rgba(0,63,82,0.35) !important;
        transform: translateY(-1px) !important;
    }}

    /* Alerte erreur */
    [data-testid="stAlert"] {{
        border-radius: 8px !important;
        font-size: 13px !important;
    }}

    /* Formulaire positionné dans la carte */
    section[data-testid="stMain"] > div {{
        position: fixed !important;
        top: 50% !important;
        left: 82px !important;
        transform: translateY(calc(-50% + 175px)) !important;
        width: 315px !important;
        z-index: 20 !important;
        padding: 0 !important;
        background: transparent !important;
    }}
    </style>

    <!-- CARTE BLANCHE LOGIN -->
    <div class="login-card">
        <!-- Logo texte Adient -->
        <div style="text-align:center; margin-bottom:22px;">
            <div style="font-size:28px; font-weight:900; letter-spacing:3px; color:#073447;">
                <span style="color:#9cc31a; font-size:32px; line-height:1;">&#9135;</span>ADIENT
            </div>
        </div>

        <!-- Icône + Titres -->
        <div style="text-align:center; margin-bottom:18px;">
            <div style="
                width:64px; height:64px; border-radius:50%;
                background:linear-gradient(135deg,#e8f5d0,#f0f9e0);
                border:2px solid #9cc31a;
                display:flex; align-items:center; justify-content:center;
                margin:0 auto 14px; font-size:28px;
            ">✂️</div>
            <div style="font-size:22px; font-weight:900; color:#073447; letter-spacing:2px;">PERFORMANCE</div>
            <div style="font-size:17px; font-weight:800; color:#9cc31a; letter-spacing:1px; margin-bottom:10px;">ATELIER DE COUPE</div>
            <div style="font-size:12px; color:#6b7a8a; line-height:1.6;">
                Suivez et améliorez la performance<br>de votre atelier de coupe
            </div>
        </div>

        <!-- Séparateur vert -->
        <div style="height:2px; background:linear-gradient(90deg,transparent,#9cc31a,transparent); margin:20px 0 24px;"></div>

        <!-- Labels champs (au-dessus des inputs Streamlit) -->
        <div style="font-size:13px; font-weight:700; color:#073447; margin-bottom:42px;">
            <div style="margin-bottom:6px;">👤 Nom d'utilisateur</div>
            <div style="margin-top:54px;">🔐 Mot de passe</div>
        </div>
    </div>

    <!-- TEXTE DROITE -->
    <div class="right-text">
        <div style="color:#9cc31a; font-size:11px; font-weight:800; letter-spacing:4px; margin-bottom:10px;">
            ADIENT MOROCCO — TIFLET
        </div>
        <div style="font-size:36px; font-weight:900; line-height:1.2; margin-bottom:20px;">
            UNE PERFORMANCE<br>
            <span style="color:#9cc31a;">QUI FAIT LA DIFFÉRENCE</span>
        </div>
        <div style="display:flex; gap:30px; margin-bottom:32px;">
            <div style="opacity:0.85; font-size:12px; font-weight:600;">
                <span style="color:#9cc31a;">⏱️</span> TEMPS RÉEL
            </div>
            <div style="opacity:0.85; font-size:12px; font-weight:600;">
                <span style="color:#9cc31a;">📊</span> KPIs
            </div>
            <div style="opacity:0.85; font-size:12px; font-weight:600;">
                <span style="color:#9cc31a;">🎯</span> OBJECTIFS
            </div>
            <div style="opacity:0.85; font-size:12px; font-weight:600;">
                <span style="color:#9cc31a;">📈</span> AMÉLIORATION
            </div>
        </div>
        <!-- Carte indicateurs -->
        <div style="
            background:rgba(255,255,255,0.07);
            border:1px solid rgba(255,255,255,0.15);
            border-radius:14px; padding:22px 28px;
            backdrop-filter:blur(12px);
            max-width:680px;
        ">
            <div style="color:#9cc31a; font-size:10px; font-weight:800; letter-spacing:3px; margin-bottom:16px;">
                📊 INDICATEURS — DERNIER SHIFT
            </div>
            <div style="display:grid; grid-template-columns:repeat(4,1fr); text-align:center; gap:10px;">
                <div style="border-right:1px solid rgba(255,255,255,0.12); padding:0 8px;">
                    <div style="font-size:26px; font-weight:900; color:white;">41%</div>
                    <div style="font-size:9px; color:rgba(255,255,255,0.55); margin-top:4px; letter-spacing:1px;">TPS MOYEN</div>
                </div>
                <div style="border-right:1px solid rgba(255,255,255,0.12); padding:0 8px;">
                    <div style="font-size:26px; font-weight:900; color:white;">40%</div>
                    <div style="font-size:9px; color:rgba(255,255,255,0.55); margin-top:4px; letter-spacing:1px;">ADV ATELIER</div>
                </div>
                <div style="border-right:1px solid rgba(255,255,255,0.12); padding:0 8px;">
                    <div style="font-size:26px; font-weight:900; color:white;">6</div>
                    <div style="font-size:9px; color:rgba(255,255,255,0.55); margin-top:4px; letter-spacing:1px;">MACHINES</div>
                </div>
                <div style="padding:0 8px;">
                    <div style="font-size:26px; font-weight:900; color:white;">900</div>
                    <div style="font-size:9px; color:rgba(255,255,255,0.55); margin-top:4px; letter-spacing:1px;">MIN / SHIFT</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Inputs Streamlit
    st.text_input("", placeholder="Entrez votre nom d'utilisateur",
                  key="login_user", label_visibility="collapsed")
    mot_de_passe = st.text_input("", type="password",
                                  placeholder="Entrez votre mot de passe",
                                  key="login_pwd", label_visibility="collapsed")

    c1, c2 = st.columns([1, 1])
    with c1:
        st.checkbox("Se souvenir de moi", key="remember_me")
    with c2:
        st.markdown(
            "<div style='text-align:right; padding-top:6px;'>"
            "<a href='#' style='color:#9cc31a; font-size:12px; font-weight:600; text-decoration:none;'>"
            "Mot de passe oublié ?"
            "</a></div>",
            unsafe_allow_html=True
        )

    if st.button("Se connecter", use_container_width=True, key="btn_login"):
        if mot_de_passe in USERS:
            st.session_state.authentifie = True
            st.session_state.role = USERS[mot_de_passe]["role"]
            st.session_state.nom_user = USERS[mot_de_passe]["nom"]
            st.rerun()
        elif mot_de_passe:
            st.error("❌ Mot de passe incorrect.")

    st.markdown("""
    <div style="text-align:center; margin-top:20px; padding-top:16px;
                border-top:1px solid #eef2f5;">
        <span style="color:#9cc31a;">🛡️</span>
        <span style="color:#6b7a8a; font-size:12px; font-weight:500;"> Accès sécurisé</span>
    </div>
    """, unsafe_allow_html=True)

    return False



# ==================== SIDEBAR NAVIGATION ====================
def sidebar_navigation():
    with st.sidebar:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='text-align:center; padding:15px; background:rgba(255,255,255,0.05);
                    border-radius:10px; margin-bottom:15px;'>
            <div style='font-size:32px;'>👤</div>
            <div style='font-size:14px; font-weight:700;'>{st.session_state.nom_user}</div>
            <div style='font-size:11px; opacity:0.6;'>{st.session_state.role.upper()}</div>
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
        st.markdown(f"### 🕐 `{datetime.now().strftime('%d/%m/%Y %H:%M')}`")
        st.markdown("---")
        st.caption("LECTRA Dashboard v3.0")
        st.caption("Adient Morocco | Projet PFE 2025")
        st.markdown("---")
        if st.button("🔓 Déconnexion", use_container_width=True):
            st.session_state.authentifie = False
            st.rerun()


# ==================== UTILITAIRES ====================
def time_to_minutes(val):
    if isinstance(val, str) and ':' in val:
        parts = val.strip().split(':')
        try:
            if len(parts) == 3:
                return int(parts[0]) * 60 + int(parts[1]) + int(parts[2]) / 60
            elif len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
        except:
            return 0
    elif isinstance(val, (int, float)) and not pd.isna(val):
        return float(val)
    return 0


def charger_donnees():
    excel_path = "modele_lectra.xlsx"
    if not os.path.exists(excel_path):
        st.error(f"❌ Fichier introuvable : {excel_path}")
        return None
    try:
        all_sheets = pd.read_excel(excel_path, sheet_name=None)
        dataframes = []
        for sheet_name, df in all_sheets.items():
            if df is not None and not df.empty:
                df['Machine'] = sheet_name
                dataframes.append(df)
        if dataframes:
            df = pd.concat(dataframes, ignore_index=True)
            if 'CUTTING TIME' in df.columns:
                df['CUTTING TIME'] = pd.to_numeric(df['CUTTING TIME'], errors='coerce').fillna(0)
            if 'INTERRUPTIONS TIME' in df.columns:
                df['INTERRUPTIONS TIME'] = pd.to_numeric(df['INTERRUPTIONS TIME'], errors='coerce').fillna(0)
            return df
        return None
    except Exception as e:
        st.error(f"Erreur de chargement: {e}")
        return None

def calculer_tps_adv(df):
    """Lit directement les valeurs TPS et ADV depuis les colonnes Excel"""
    resultats = []
    
    for machine in sorted(df['Machine'].unique()):
        df_m = df[df['Machine'] == machine]
        
        # Récupérer la dernière valeur non vide de TPS Shift
        tps_vals = df_m['TPS Shift'].dropna()
        if len(tps_vals) > 0:
            tps = float(tps_vals.iloc[-1])
        else:
            tps = 0
        
        # Récupérer la dernière valeur non vide de ADV
        adv_vals = df_m['ADV'].dropna() if 'ADV' in df_m.columns else []
        if len(adv_vals) > 0:
            adv = float(adv_vals.iloc[-1])
        else:
            adv = 0
        
        # Calculs pour les graphiques
        cutting = df_m['CUTTING TIME'].sum() if 'CUTTING TIME' in df_m.columns else 0
        interruptions = df_m['INTERRUPTIONS TIME'].sum() if 'INTERRUPTIONS TIME' in df_m.columns else 0
        
        # Pour DT_POSIT et ΔT_Matelas (nécessaires pour page Pertes)
        dt_posit = 0
        dt_matelas = 0
        
        resultats.append({
            'Machine': machine,
            'TPS (%)': tps,
            'Objectif (%)': 75,
            'Écart (%)': round(tps - 75, 1) if tps > 0 else 0,
            'ADV (%)': adv,
            'Cutting (min)': round(cutting, 1),
            'Interruptions (min)': round(interruptions, 1),
            'DT_POSIT (min)': dt_posit,
            'ΔT_Matelas (min)': dt_matelas,
            'Statut': "✅ OK" if tps >= 75 else "❌ NOK",
        })
    
    return pd.DataFrame(resultats)

def page_header(icon, titre, sous_titre):
    st.markdown(f"""
    <div class="page-header">
        <h1 style='margin:0; font-size:28px;'>{icon} {titre}</h1>
        <p style='margin:4px 0 0; opacity:0.85; font-size:14px;'>{sous_titre}</p>
    </div>
    """, unsafe_allow_html=True)


# ==================== PAGE 1 : ACCUEIL ====================
def page_accueil(df, df_tps):
    page_header("🏠", "Tableau de Bord — Vue d'ensemble", "Adient Morocco | Atelier de Coupe | Projet MMA / Mercedes")

    tps_moyen = df_tps['TPS (%)'].mean()
    adv_moyen = df_tps['ADV (%)'].mean() if df_tps['ADV (%)'].sum() > 0 else 0
    machines_nok = len(df_tps[df_tps['TPS (%)'] < 75])
    total_interruptions = df['INTERRUPTIONS TIME'].sum() if 'INTERRUPTIONS TIME' in df.columns else 0
    total_markers = len(df)
    jours = df['DATE'].nunique() if 'DATE' in df.columns else 1

    cols = st.columns(5)
    kpis = [
        (f"{tps_moyen:.1f}%",          "⚙️ TPS Moyen Atelier",       "",          "#1f77b4"),
        (f"{adv_moyen:.1f}%",          "📦 ADV Moyenne",             "",          "#2ca02c"),
        (f"{machines_nok}/{len(df_tps)}","🚨 Machines sous objectif","",          "#d62728"),
        (f"{total_interruptions:.0f}", "⚠️ Total Interruptions",     "minutes",   "#ff7f0e"),
        (f"{total_markers}",           "🗂️ Total Markers",           f"{jours}j", "#9467bd"),
    ]
    for col, (val, label, unit, color) in zip(cols, kpis):
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="border-left-color:{color};">
                <div class="kpi-value" style="color:{color};">{val}</div>
                <div class="kpi-label">{label}</div>
                <div class="kpi-unit">{unit}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<div class="section-title">🎯 Jauge TPS Atelier</div>', unsafe_allow_html=True)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=tps_moyen,
            delta={'reference': 75, 'increasing': {'color': "#2ca02c"}, 'decreasing': {'color': "#d62728"}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': "#1f77b4"},
                'steps': [
                    {'range': [0, 40],  'color': '#ffe0e0'},
                    {'range': [40, 75], 'color': '#fff3cd'},
                    {'range': [75, 100],'color': '#d4edda'},
                ],
                'threshold': {'line': {'color': "red", 'width': 3}, 'thickness': 0.75, 'value': 75}
            },
            title={'text': "TPS Moyen Atelier (%)"}
        ))
        fig_gauge.update_layout(height=280, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">🚨 Alertes Machines</div>', unsafe_allow_html=True)
        critiques = df_tps[df_tps['TPS (%)'] < 40]
        attention = df_tps[(df_tps['TPS (%)'] >= 40) & (df_tps['TPS (%)'] < 75)]
        ok_machines = df_tps[df_tps['TPS (%)'] >= 75]

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**🔴 Critique**")
            if len(critiques) == 0: st.success("Aucune")
            for _, r in critiques.iterrows():
                st.markdown(f'<div class="alert-card-red"><b>{r["Machine"]}</b><br><small>TPS: {r["TPS (%)"]:.1f}%</small></div>', unsafe_allow_html=True)
        with c2:
            st.markdown("**🟠 À surveiller**")
            if len(attention) == 0: st.success("Aucune")
            for _, r in attention.iterrows():
                st.markdown(f'<div class="alert-card-orange"><b>{r["Machine"]}</b><br><small>TPS: {r["TPS (%)"]:.1f}%</small></div>', unsafe_allow_html=True)
        with c3:
            st.markdown("**🟢 Objectif atteint**")
            if len(ok_machines) == 0: st.warning("Aucune")
            for _, r in ok_machines.iterrows():
                st.markdown(f'<div class="alert-card-green"><b>{r["Machine"]}</b><br><small>TPS: {r["TPS (%)"]:.1f}%</small></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-title">📊 Résumé Performance par Machine</div>', unsafe_allow_html=True)
    df_resume = df_tps[['Machine', 'TPS (%)', 'Objectif (%)', 'Écart (%)', 'ADV (%)', 'Statut']].copy()
    st.dataframe(df_resume, use_container_width=True, hide_index=True)


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
        yaxis=dict(title="TPS (%)", range=[0, 100]), plot_bgcolor='white', paper_bgcolor='white',
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
            fig_evol.update_layout(yaxis=dict(range=[0, 100], title="TPS (%)"), plot_bgcolor='white', paper_bgcolor='white', height=350)
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
    page_header("📉", "Analyse des Pertes", "Interruptions, DT_POSIT et ΔT_Matelas par machine")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">📊 Pertes empilées par machine</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Interruptions', x=df_tps['Machine'], y=df_tps['Interruptions (min)'], marker_color='#d62728'))
        fig.add_trace(go.Bar(name='DT_POSIT',      x=df_tps['Machine'], y=df_tps['DT_POSIT (min)'], marker_color='#ff7f0e'))
        fig.add_trace(go.Bar(name='ΔT_Matelas',    x=df_tps['Machine'], y=df_tps['ΔT_Matelas (min)'], marker_color='#7f7f7f'))
        fig.update_layout(barmode='stack', plot_bgcolor='white', paper_bgcolor='white', height=380, yaxis_title="Minutes")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">🥧 Répartition globale des pertes</div>', unsafe_allow_html=True)
        t_int = df_tps['Interruptions (min)'].sum()
        t_pos = df_tps['DT_POSIT (min)'].sum()
        t_del = df_tps['ΔT_Matelas (min)'].sum()
        fig_pie = px.pie(
            values=[t_int, t_pos, t_del], names=['Interruptions', 'DT_POSIT', 'ΔT_Matelas'],
            color_discrete_sequence=['#d62728', '#ff7f0e', '#7f7f7f'], hole=0.4, title="Répartition globale"
        )
        fig_pie.update_traces(textinfo='percent+label')
        fig_pie.update_layout(height=380)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-title">📊 Diagramme de Pareto des Pertes</div>', unsafe_allow_html=True)
    pareto_data = pd.DataFrame({'Source': ['Interruptions', 'ΔT_Matelas', 'DT_POSIT'], 'Total (min)': [t_int, t_del, t_pos]}).sort_values('Total (min)', ascending=False)
    pareto_data['Cumul (%)'] = pareto_data['Total (min)'].cumsum() / pareto_data['Total (min)'].sum() * 100

    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Bar(
        x=pareto_data['Source'], y=pareto_data['Total (min)'], marker_color=['#d62728', '#ff7f0e', '#7f7f7f'], name='Durée (min)',
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
        plot_bgcolor='white', paper_bgcolor='white', legend=dict(orientation="h", yanchor="bottom", y=1.02), height=400
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
                values=[row['Interruptions (min)'], row['DT_POSIT (min)'], row['ΔT_Matelas (min)']],
                names=['Interruptions', 'DT_POSIT', 'ΔT_Matelas'], title=row['Machine'],
                color_discrete_sequence=['#d62728', '#ff7f0e', '#7f7f7f'], hole=0.35
            )
            fig_m.update_traces(textinfo='percent')
            fig_m.update_layout(height=280, margin=dict(t=40, b=10, l=10, r=10), showlegend=False)
            st.plotly_chart(fig_m, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-title">📋 Tableau détaillé des pertes</div>', unsafe_allow_html=True)
    cols_pertes = ['Machine', 'Interruptions (min)', 'DT_POSIT (min)', 'ΔT_Matelas (min)', 'Cutting (min)', 'TPS (%)']
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
    fig_adv.update_layout(yaxis=dict(title="ADV (%)", range=[0, 120]), plot_bgcolor='white', paper_bgcolor='white', height=380)
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
        fig_adv_m.update_layout(yaxis=dict(range=[0, 120], title="ADV (%)"), plot_bgcolor='white', paper_bgcolor='white', height=350)
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
    col1, col2, col3, col4 = st.columns(4)
    tps_val = df_tps_m['TPS (%)']
    color_tps = "#2ca02c" if tps_val >= 75 else "#ff7f0e" if tps_val >= 40 else "#d62728"
    for col, val, label, color in [
        (col1, f"{tps_val:.1f}%",              "⚙️ TPS",             color_tps),
        (col2, f"{df_tps_m['Interruptions (min)']:.0f} min", "⚠️ Interruptions", "#d62728"),
        (col3, f"{df_tps_m['DT_POSIT (min)']:.0f} min",     "📍 DT_POSIT",      "#ff7f0e"),
        (col4, f"{df_tps_m['ΔT_Matelas (min)']:.0f} min",   "🔄 ΔT_Matelas",    "#7f7f7f"),
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
            values=[df_tps_m['Interruptions (min)'], df_tps_m['DT_POSIT (min)'], df_tps_m['ΔT_Matelas (min)']],
            names=['Interruptions', 'DT_POSIT', 'ΔT_Matelas'], color_discrete_sequence=['#d62728', '#ff7f0e', '#7f7f7f'], hole=0.4
        )
        fig_pie.update_traces(textinfo='percent+label')
        fig_pie.update_layout(height=280, margin=dict(t=20, b=10))
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    if 'DATE' in df_m.columns:
        st.markdown(f'<div class="section-title">📈 Évolution journalière — {machine_selectionnee}</div>', unsafe_allow_html=True)
        evol = df_m.groupby('DATE')['CUTTING TIME'].sum().reset_index()
        fig_evol = px.line(evol, x='DATE', y='CUTTING TIME', markers=True, title=f"Temps de coupe journalier — {machine_selectionnee}")
        fig_evol.update_layout(plot_bgcolor='white', paper_bgcolor='white', height=300)
        st.plotly_chart(fig_evol, use_container_width=True)

    st.markdown("---")
    st.markdown(f'<div class="section-title">📋 Données — {machine_selectionnee}</div>', unsafe_allow_html=True)
    cols_show = [c for c in ['DATE', 'Marker', 'CUTTING TIME', 'INTERRUPTIONS TIME', 'POSIT/Marker', 'ΔT_Matelas', 'STATE'] if c in df_m.columns]
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

    cols_show = [c for c in ['DATE', 'Machine', 'Marker', 'CUTTING TIME', 'INTERRUPTIONS TIME', 'POSIT/Marker', 'ΔT_Matelas', 'STATE'] if c in df_f.columns]
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

    df_tps = calculer_tps_adv(df)
    page = st.session_state.get('page_active', 'Accueil')

    if page == "Accueil": page_accueil(df, df_tps)
    elif page == "TPS & Performance": page_tps(df, df_tps)
    elif page == "Analyse des Pertes": page_pertes(df, df_tps)
    elif page == "ADV Production": page_adv(df, df_tps)
    elif page == "Analyse par Machine": page_machine(df, df_tps)
    elif page == "Données Brutes": page_donnees(df, df_tps)

    st.markdown("---")
    st.markdown("""
    <p style='text-align:center; color:#aaa; font-size:12px;'>
        🏭 Adient Morocco — LECTRA Dashboard v3.0 | Projet PFE 2025 | Tiflet
    </p>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
