import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import base64

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="LECTRA Dashboard | Adient Morocco",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS GENERAL ====================
st.markdown("""
<style>
    /* Reset et styles de base */
    .main { background-color: #f0f2f6; }
    
    /* Cartes KPI */
    .kpi-card {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        border-radius: 16px;
        padding: 20px 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-left: 4px solid #1f77b4;
        transition: all 0.3s ease;
        margin-bottom: 10px;
    }
    .kpi-card:hover { 
        transform: translateY(-5px); 
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    .kpi-value { 
        font-size: 38px; 
        font-weight: 800; 
        color: #1f77b4; 
        line-height: 1.1; 
    }
    .kpi-label { 
        font-size: 13px; 
        color: #555; 
        margin-top: 8px; 
        font-weight: 500; 
    }
    .kpi-unit { 
        font-size: 11px; 
        color: #aaa; 
        margin-top: 4px; 
    }

    /* Cartes d'alertes */
    .alert-card-red {
        background: linear-gradient(135deg, #fff5f5, #ffe0e0);
        border-left: 4px solid #e53e3e;
        border-radius: 10px; 
        padding: 14px; 
        margin-bottom: 8px;
    }
    .alert-card-orange {
        background: linear-gradient(135deg, #fffaf0, #ffecd2);
        border-left: 4px solid #ed8936;
        border-radius: 10px; 
        padding: 14px; 
        margin-bottom: 8px;
    }
    .alert-card-green {
        background: linear-gradient(135deg, #f0fff4, #d4edda);
        border-left: 4px solid #38a169;
        border-radius: 10px; 
        padding: 14px; 
        margin-bottom: 8px;
    }

    /* Titres de section */
    .section-title {
        font-size: 20px; 
        font-weight: 700; 
        color: #2d3748;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 8px; 
        margin-bottom: 20px;
    }

    /* En-tête de page */
    .page-header {
        background: linear-gradient(135deg, #1f77b4, #2196F3);
        color: white; 
        padding: 20px 25px; 
        border-radius: 12px;
        margin-bottom: 25px;
    }

    /* Sidebar personnalisée */
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #1a1f2e 0%, #0f1420 100%);
    }
    [data-testid="stSidebar"] * { 
        color: #e2e8f0 !important; 
    }
    
    /* Boutons sidebar */
    [data-testid="stSidebar"] .stButton button {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        text-align: left;
        transition: all 0.3s;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background: rgba(31,119,180,0.4);
        transform: translateX(5px);
    }

    /* Métriques personnalisées */
    .metric-container {
        background: white;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ==================== AUTHENTIFICATION AMÉLIORÉE ====================
USERS = {
    "admin123": {"role": "admin", "nom": "Administrateur", "password": "admin123"},
    "chef123": {"role": "chef", "nom": "Chef d'atelier", "password": "chef123"},
    "invite123": {"role": "invite", "nom": "Invité", "password": "invite123"},
}

def verifier_mot_de_passe():
    """Fonction d'authentification - Tout dans le même panneau blanc"""
    if "authentifie" not in st.session_state:
        st.session_state.authentifie = False
        st.session_state.role = None
        st.session_state.nom_user = ""

    if st.session_state.authentifie:
        return True

    # Image de fond
    bg_image_path = "background.png"
    if os.path.exists(bg_image_path):
        with open(bg_image_path, "rb") as image_file:
            img_base64 = base64.b64encode(image_file.read()).decode()
        bg_css = f'background-image: url("data:image/png;base64,{img_base64}"); background-size: cover; background-position: center;'
    else:
        bg_css = "background: linear-gradient(135deg, #0a2b3e, #1a4a6f);"

    st.markdown(f"""
    <style>
        [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stSidebar"] {{
            display: none !important;
        }}
        
        .block-container {{
            padding: 0 !important;
            max-width: 100% !important;
        }}
        
        .stApp {{
            {bg_css}
            background-attachment: fixed;
        }}
        
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.55);
            z-index: 0;
        }}
        
        .stTextInput input {{
            background: #f8fafc !important;
            border: 1px solid #d7dee8 !important;
            border-radius: 6px !important;
            height: 36px !important;
            font-size: 13px !important;
            padding: 0 10px !important;
        }}
        
        .stButton button {{
            background: #003f52 !important;
            color: white !important;
            height: 38px !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            margin-top: 5px !important;
        }}
        
        .stCheckbox label p {{
            font-size: 11px !important;
        }}
        
        div[data-testid="column"] {{
            gap: 0px !important;
        }}
    </style>
    """, unsafe_allow_html=True)

    # Centrer le panneau blanc
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Panneau blanc unique avec tout le contenu
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
            <!-- Logo ADIENT -->
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

        # Formulaire de connexion compact
        st.markdown("<p style='text-align: left; font-size: 12px; font-weight: 600; color: #333; margin-bottom: 4px;'>👤 Nom d'utilisateur</p>", unsafe_allow_html=True)
        username = st.text_input("", placeholder="Entrez votre nom d'utilisateur", key="login_user", label_visibility="collapsed")

        st.markdown("<p style='text-align: left; font-size: 12px; font-weight: 600; color: #333; margin-top: 10px; margin-bottom: 4px;'>🔐 Mot de passe</p>", unsafe_allow_html=True)
        password = st.text_input("", type="password", placeholder="Entrez votre mot de passe", key="login_pwd", label_visibility="collapsed")

        # Deux colonnes pour checkbox et lien
        col_check, col_forgot = st.columns([1, 1])
        with col_check:
            st.checkbox("Se souvenir de moi")
        with col_forgot:
            st.markdown("<div style='text-align: right; padding-top: 3px;'><a href='#' style='color: #9cc31a; font-size: 11px; text-decoration: none;'>Mot de passe oublié ?</a></div>", unsafe_allow_html=True)

        # Bouton de connexion
        if st.button("🔓 SE CONNECTER", use_container_width=True):
            if password in USERS:
                st.session_state.authentifie = True
                st.session_state.role = USERS[password]["role"]
                st.session_state.nom_user = USERS[password]["nom"]
                st.rerun()
            elif password:
                st.error("❌ Identifiants incorrects")

        # Séparateur
        st.markdown("""
            <div style="height: 1px; background: linear-gradient(90deg, transparent, #9cc31a, transparent); margin: 20px 0 15px 0;"></div>
        """, unsafe_allow_html=True)

        # Texte ADIENT MOROCCO et indicateurs dans le même panneau
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

        # Pied de page sécurisé
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
        
        # Profil utilisateur
        st.markdown(f"""
        <div style='text-align:center; padding:20px; background:linear-gradient(135deg, #1f77b4, #2196F3); border-radius:15px; margin-bottom:20px;'>
            <div style='font-size:48px;'>👤</div>
            <div style='font-size:16px; font-weight:700; margin-top:10px;'>{st.session_state.nom_user}</div>
            <div style='font-size:12px; opacity:0.8;'>{st.session_state.role.upper()}</div>
        </div>
        """, unsafe_allow_html=True)

        # Badge de rôle
        if st.session_state.role == "admin":
            st.success("✅ Accès administrateur complet")
        elif st.session_state.role == "chef":
            st.info("⚙️ Mode Chef d'atelier")
        else:
            st.warning("👁️ Mode Lecture seule")

        st.markdown("---")
        st.markdown("### 🧭 Navigation")

        # Menu de navigation amélioré
        pages = {
            "🏠 Accueil": "Vue d'ensemble & alertes",
            "⚙️ TPS & Performance": "Taux de productivité",
            "📉 Analyse des Pertes": "Interruptions & pertes", 
            "📦 ADV Production": "Adhérence au volume",
            "🔍 Analyse par Machine": "Détail machine",
            "📋 Données Brutes": "Tableau & export"
        }

        if 'page_active' not in st.session_state:
            st.session_state.page_active = "🏠 Accueil"

        for page, desc in pages.items():
            if st.button(page, key=f"nav_{page}", use_container_width=True, help=desc):
                st.session_state.page_active = page
                st.rerun()

        st.markdown("---")
        st.markdown(f"### 🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        st.markdown("---")
        st.caption("LECTRA Dashboard v4.0")
        st.caption("Adient Morocco | PFE 2025")
        
        st.markdown("---")
        if st.button("🔓 Déconnexion", use_container_width=True, type="secondary"):
            st.session_state.authentifie = False
            st.session_state.page_active = "🏠 Accueil"
            st.rerun()

# ==================== CHARGEMENT DES DONNÉES ====================
@st.cache_data(ttl=300)
def charger_donnees():
    """Charge les données depuis le fichier Excel avec mise en cache"""
    excel_path = "modele_lectra.xlsx"
    
    if not os.path.exists(excel_path):
        # Données de démonstration si fichier inexistant
        return generer_donnees_demo()
    
    try:
        all_sheets = pd.read_excel(excel_path, sheet_name=None)
        dataframes = []
        for sheet_name, df in all_sheets.items():
            if df is not None and not df.empty:
                df['Machine'] = sheet_name
                dataframes.append(df)
        
        if dataframes:
            df = pd.concat(dataframes, ignore_index=True)
            
            # Nettoyage des données
            if 'CUTTING TIME' in df.columns:
                df['CUTTING TIME'] = pd.to_numeric(df['CUTTING TIME'], errors='coerce').fillna(0)
            if 'INTERRUPTIONS TIME' in df.columns:
                df['INTERRUPTIONS TIME'] = pd.to_numeric(df['INTERRUPTIONS TIME'], errors='coerce').fillna(0)
            if 'DATE' in df.columns:
                df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
            
            return df
        else:
            return generer_donnees_demo()
            
    except Exception as e:
        st.error(f"Erreur de chargement: {e}")
        return generer_donnees_demo()

def generer_donnees_demo():
    """Génère des données de démonstration pour tester le dashboard"""
    np.random.seed(42)
    
    machines = ["Machine A", "Machine B", "Machine C", "Machine D"]
    dates = pd.date_range(start="2025-06-01", end="2025-06-03", freq="D")
    
    data = []
    for machine in machines:
        for date in dates:
            for marker in range(1, 6):
                data.append({
                    'DATE': date,
                    'Machine': machine,
                    'Marker': f"M{marker}",
                    'CUTTING TIME': np.random.randint(30, 120),
                    'INTERRUPTIONS TIME': np.random.randint(0, 45),
                    'TPS Shift': np.random.uniform(60, 85),
                    'ADV': np.random.uniform(70, 110),
                    'STATE': np.random.choice(["OK", "NOK", "Alerte"], p=[0.7, 0.15, 0.15])
                })
    
    return pd.DataFrame(data)

def calculer_tps_adv(df):
    """Calcule les indicateurs TPS et ADV par machine"""
    if df is None or df.empty:
        return pd.DataFrame()
    
    resultats = []
    
    for machine in sorted(df['Machine'].unique()):
        df_m = df[df['Machine'] == machine]
        
        # TPS (dernière valeur)
        tps_vals = df_m['TPS Shift'].dropna() if 'TPS Shift' in df_m.columns else pd.Series()
        tps = float(tps_vals.iloc[-1]) if len(tps_vals) > 0 else np.random.uniform(60, 85)
        
        # ADV
        adv_vals = df_m['ADV'].dropna() if 'ADV' in df_m.columns else pd.Series()
        adv = float(adv_vals.iloc[-1]) if len(adv_vals) > 0 else np.random.uniform(70, 110)
        
        # Temps
        cutting = df_m['CUTTING TIME'].sum() if 'CUTTING TIME' in df_m.columns else 0
        interruptions = df_m['INTERRUPTIONS TIME'].sum() if 'INTERRUPTIONS TIME' in df_m.columns else 0
        
        resultats.append({
            'Machine': machine,
            'TPS (%)': round(tps, 1),
            'Objectif (%)': 75,
            'Écart (%)': round(tps - 75, 1),
            'ADV (%)': round(adv, 1),
            'Cutting (min)': round(cutting, 1),
            'Interruptions (min)': round(interruptions, 1),
            'DT_POSIT (min)': round(interruptions * 0.3, 1),
            'ΔT_Matelas (min)': round(interruptions * 0.2, 1),
            'Statut': "✅ OK" if tps >= 75 else "⚠️ NOK"
        })
    
    return pd.DataFrame(resultats)

def page_header(icon, titre, sous_titre):
    st.markdown(f"""
    <div class="page-header">
        <h1 style='margin:0; font-size:28px;'>{icon} {titre}</h1>
        <p style='margin:8px 0 0; opacity:0.9; font-size:14px;'>{sous_titre}</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== PAGE ACCUEIL ====================
def page_accueil(df, df_tps):
    page_header("🏠", "Tableau de Bord", "Vue d'ensemble de la performance atelier")
    
    if df_tps.empty:
        st.warning("Aucune donnée disponible")
        return
    
    # KPIs
    tps_moyen = df_tps['TPS (%)'].mean()
    adv_moyen = df_tps['ADV (%)'].mean()
    machines_nok = len(df_tps[df_tps['TPS (%)'] < 75])
    total_interruptions = df_tps['Interruptions (min)'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("⚙️ TPS Moyen Atelier", f"{tps_moyen:.1f}%", 
                  delta=f"{tps_moyen - 75:.1f}%" if tps_moyen != 75 else None,
                  delta_color="inverse")
    
    with col2:
        st.metric("📦 ADV Moyenne", f"{adv_moyen:.1f}%",
                  delta=f"{adv_moyen - 100:.1f}%" if adv_moyen != 100 else None)
    
    with col3:
        st.metric("🚨 Machines sous objectif", f"{machines_nok}/{len(df_tps)}")
    
    with col4:
        st.metric("⚠️ Total Interruptions", f"{total_interruptions:.0f} min")
    
    st.markdown("---")
    
    # Graphiques
    col_left, col_right = st.columns([1, 1.5])
    
    with col_left:
        st.markdown('<div class="section-title">🎯 TPS par Machine</div>', unsafe_allow_html=True)
        
        # Graphique en barres
        colors = ['#d62728' if t < 40 else '#ff7f0e' if t < 75 else '#2ca02c' 
                  for t in df_tps['TPS (%)']]
        
        fig = go.Figure(data=[
            go.Bar(x=df_tps['Machine'], y=df_tps['TPS (%)'], 
                   marker_color=colors, text=df_tps['TPS (%)'].apply(lambda x: f"{x:.1f}%"),
                   textposition='outside')
        ])
        fig.add_hline(y=75, line_dash="dash", line_color="red", 
                      annotation_text="Objectif 75%")
        fig.update_layout(height=400, margin=dict(t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        st.markdown('<div class="section-title">🚨 Alertes Machines</div>', unsafe_allow_html=True)
        
        # Alertes
        critiques = df_tps[df_tps['TPS (%)'] < 40]
        attention = df_tps[(df_tps['TPS (%)'] >= 40) & (df_tps['TPS (%)'] < 75)]
        ok_machines = df_tps[df_tps['TPS (%)'] >= 75]
        
        tabs = st.tabs(["🔴 Critique", "🟠 À surveiller", "🟢 OK"])
        
        with tabs[0]:
            if len(critiques) == 0:
                st.success("✅ Aucune machine critique")
            for _, row in critiques.iterrows():
                st.error(f"**{row['Machine']}** - TPS: {row['TPS (%)']:.1f}%")
        
        with tabs[1]:
            if len(attention) == 0:
                st.success("✅ Aucune machine à surveiller")
            for _, row in attention.iterrows():
                st.warning(f"**{row['Machine']}** - TPS: {row['TPS (%)']:.1f}%")
        
        with tabs[2]:
            for _, row in ok_machines.iterrows():
                st.success(f"**{row['Machine']}** - TPS: {row['TPS (%)']:.1f}%")
    
    st.markdown("---")
    st.markdown('<div class="section-title">📊 Résumé Performance</div>', unsafe_allow_html=True)
    st.dataframe(df_tps[['Machine', 'TPS (%)', 'ADV (%)', 'Statut']], 
                 use_container_width=True, hide_index=True)

# ==================== PAGE TPS & PERFORMANCE ====================
def page_tps(df, df_tps):
    page_header("⚙️", "TPS & Performance", "Analyse détaillée du Taux de Productivité Synthétique")
    
    if df_tps.empty:
        st.warning("Aucune donnée disponible")
        return
    
    # Graphique principal
    st.markdown('<div class="section-title">📊 Performance par Machine</div>', unsafe_allow_html=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='TPS Réel',
        x=df_tps['Machine'], 
        y=df_tps['TPS (%)'],
        marker_color=['#2ca02c' if x >= 75 else '#ff7f0e' if x >= 40 else '#d62728' 
                      for x in df_tps['TPS (%)']],
        text=df_tps['TPS (%)'].apply(lambda x: f"{x:.1f}%"),
        textposition='outside'
    ))
    
    fig.add_trace(go.Scatter(
        name='Objectif 75%',
        x=df_tps['Machine'],
        y=[75] * len(df_tps),
        mode='lines',
        line=dict(color='#1f77b4', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title="TPS par Machine",
        yaxis_title="TPS (%)",
        yaxis_range=[0, 100],
        height=450,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Jauges individuelles
    st.markdown("---")
    st.markdown('<div class="section-title">🎯 Jauges individuelles</div>', unsafe_allow_html=True)
    
    cols = st.columns(min(3, len(df_tps)))
    for idx, (_, row) in enumerate(df_tps.iterrows()):
        with cols[idx % 3]:
            color = "#2ca02c" if row['TPS (%)'] >= 75 else "#ff7f0e" if row['TPS (%)'] >= 40 else "#d62728"
            
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=row['TPS (%)'],
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [0, 40], 'color': '#ffe0e0'},
                        {'range': [40, 75], 'color': '#fff3cd'},
                        {'range': [75, 100], 'color': '#d4edda'}
                    ],
                    'threshold': {
                        'line': {'color': 'red', 'width': 2},
                        'thickness': 0.75,
                        'value': 75
                    }
                },
                title={'text': f"<b>{row['Machine']}</b>"}
            ))
            fig_gauge.update_layout(height=250, margin=dict(t=50, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)

# ==================== PAGE PERTES ====================
def page_pertes(df, df_tps):
    page_header("📉", "Analyse des Pertes", "Identification des sources de perte de productivité")
    
    if df_tps.empty:
        st.warning("Aucune donnée disponible")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-title">📊 Pertes par Machine</div>', unsafe_allow_html=True)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Interruptions', x=df_tps['Machine'], 
                             y=df_tps['Interruptions (min)'], marker_color='#d62728'))
        fig.add_trace(go.Bar(name='DT_POSIT', x=df_tps['Machine'], 
                             y=df_tps['DT_POSIT (min)'], marker_color='#ff7f0e'))
        fig.add_trace(go.Bar(name='ΔT Matelas', x=df_tps['Machine'], 
                             y=df_tps['ΔT_Matelas (min)'], marker_color='#9467bd'))
        
        fig.update_layout(barmode='stack', height=400, yaxis_title="Minutes")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<div class="section-title">🥧 Répartition Globale</div>', unsafe_allow_html=True)
        
        total_int = df_tps['Interruptions (min)'].sum()
        total_dt = df_tps['DT_POSIT (min)'].sum()
        total_matelas = df_tps['ΔT_Matelas (min)'].sum()
        
        fig_pie = px.pie(
            values=[total_int, total_dt, total_matelas],
            names=['Interruptions', 'DT_POSIT', 'ΔT Matelas'],
            color_discrete_sequence=['#d62728', '#ff7f0e', '#9467bd'],
            hole=0.4
        )
        fig_pie.update_traces(textinfo='percent+label')
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Pareto
    st.markdown("---")
    st.markdown('<div class="section-title">📊 Diagramme de Pareto</div>', unsafe_allow_html=True)
    
    pareto_data = pd.DataFrame({
        'Cause': ['Interruptions', 'DT_POSIT', 'ΔT Matelas'],
        'Minutes': [total_int, total_dt, total_matelas]
    }).sort_values('Minutes', ascending=False)
    
    pareto_data['Cumul %'] = pareto_data['Minutes'].cumsum() / pareto_data['Minutes'].sum() * 100
    
    fig_pareto = go.Figure()
    
    fig_pareto.add_trace(go.Bar(
        x=pareto_data['Cause'],
        y=pareto_data['Minutes'],
        name='Minutes',
        marker_color='#1f77b4',
        text=pareto_data['Minutes'].apply(lambda x: f"{x:.0f} min"),
        textposition='outside'
    ))
    
    fig_pareto.add_trace(go.Scatter(
        x=pareto_data['Cause'],
        y=pareto_data['Cumul %'],
        name='Cumul (%)',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='#d62728', width=2),
        marker=dict(size=10)
    ))
    
    fig_pareto.add_hline(y=80, line_dash="dash", line_color="green", 
                         annotation_text="80%", yref='y2')
    
    fig_pareto.update_layout(
        yaxis=dict(title="Minutes"),
        yaxis2=dict(title="Cumul (%)", overlaying='y', side='right', range=[0, 110]),
        height=450
    )
    
    st.plotly_chart(fig_pareto, use_container_width=True)

# ==================== PAGE ADV ====================
def page_adv(df, df_tps):
    page_header("📦", "ADV Production", "Adhérence au Volume de Production")
    
    if df_tps.empty:
        st.warning("Aucune donnée disponible")
        return
    
    # KPIs ADV
    adv_moyen = df_tps['ADV (%)'].mean()
    adv_min = df_tps['ADV (%)'].min()
    adv_max = df_tps['ADV (%)'].max()
    machines_sous_objectif = len(df_tps[df_tps['ADV (%)'] < 100])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 ADV Moyenne", f"{adv_moyen:.1f}%")
    col2.metric("📈 ADV Maximale", f"{adv_max:.1f}%")
    col3.metric("📉 ADV Minimale", f"{adv_min:.1f}%")
    col4.metric("⚠️ Sous objectif", f"{machines_sous_objectif}/{len(df_tps)}")
    
    st.markdown("---")
    
    # Graphique ADV par machine
    st.markdown('<div class="section-title">🏭 ADV par Machine</div>', unsafe_allow_html=True)
    
    colors_adv = ['#2ca02c' if x >= 100 else '#d62728' for x in df_tps['ADV (%)']]
    
    fig = go.Figure(data=[
        go.Bar(x=df_tps['Machine'], y=df_tps['ADV (%)'], 
               marker_color=colors_adv,
               text=df_tps['ADV (%)'].apply(lambda x: f"{x:.1f}%"),
               textposition='outside')
    ])
    
    fig.add_hline(y=100, line_dash="dash", line_color="orange", 
                  annotation_text="Objectif 100%")
    
    fig.update_layout(height=450, yaxis_title="ADV (%)", yaxis_range=[0, 130])
    st.plotly_chart(fig, use_container_width=True)
    
    # Tableau ADV
    st.markdown("---")
    st.markdown('<div class="section-title">📋 Détail ADV</div>', unsafe_allow_html=True)
    st.dataframe(df_tps[['Machine', 'ADV (%)', 'TPS (%)', 'Statut']], 
                 use_container_width=True, hide_index=True)

# ==================== PAGE MACHINE ====================
def page_machine(df, df_tps):
    page_header("🔍", "Analyse par Machine", "Détail complet par machine")
    
    if df.empty or df_tps.empty:
        st.warning("Aucune donnée disponible")
        return
    
    machine_selection = st.selectbox("🏭 Sélectionner une machine", sorted(df['Machine'].unique()))
    
    df_machine = df[df['Machine'] == machine_selection]
    df_tps_machine = df_tps[df_tps['Machine'] == machine_selection].iloc[0]
    
    # KPIs machine
    col1, col2, col3, col4 = st.columns(4)
    
    tps_color = "🟢" if df_tps_machine['TPS (%)'] >= 75 else "🟠" if df_tps_machine['TPS (%)'] >= 40 else "🔴"
    
    col1.metric("⚙️ TPS", f"{df_tps_machine['TPS (%)']:.1f}%", 
                delta=f"{df_tps_machine['Écart (%)']:.1f}%")
    col2.metric("📦 ADV", f"{df_tps_machine['ADV (%)']:.1f}%")
    col3.metric("⏱️ Temps de coupe", f"{df_tps_machine['Cutting (min)']:.0f} min")
    col4.metric("⚠️ Interruptions", f"{df_tps_machine['Interruptions (min)']:.0f} min")
    
    st.markdown("---")
    
    # Évolution temporelle
    if 'DATE' in df_machine.columns:
        st.markdown('<div class="section-title">📈 Évolution Temporelle</div>', unsafe_allow_html=True)
        
        evol_data = df_machine.groupby('DATE').agg({
            'CUTTING TIME': 'sum',
            'INTERRUPTIONS TIME': 'sum'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=evol_data['DATE'], y=evol_data['CUTTING TIME'], 
                                 name='Temps de coupe', mode='lines+markers',
                                 line=dict(color='#2ca02c', width=2)))
        fig.add_trace(go.Scatter(x=evol_data['DATE'], y=evol_data['INTERRUPTIONS TIME'],
                                 name='Interruptions', mode='lines+markers',
                                 line=dict(color='#d62728', width=2)))
        
        fig.update_layout(height=400, yaxis_title="Minutes")
        st.plotly_chart(fig, use_container_width=True)
    
    # Données détaillées
    st.markdown("---")
    st.markdown('<div class="section-title">📋 Données Détaillées</div>', unsafe_allow_html=True)
    
    cols_affichage = [c for c in ['DATE', 'Marker', 'CUTTING TIME', 'INTERRUPTIONS TIME', 'STATE'] 
                      if c in df_machine.columns]
    st.dataframe(df_machine[cols_affichage], use_container_width=True, hide_index=True)

# ==================== PAGE DONNÉES BRUTES ====================
def page_donnees(df, df_tps):
    page_header("📋", "Données Brutes", "Export et analyse des données")
    
    if df.empty:
        st.warning("Aucune donnée disponible")
        return
    
    # Filtres
    col1, col2 = st.columns(2)
    
    with col1:
        machines = ['Toutes'] + sorted(df['Machine'].unique().tolist())
        filtre_machine = st.selectbox("🏭 Filtrer par machine", machines)
    
    with col2:
        if 'DATE' in df.columns:
            dates = ['Toutes'] + sorted(df['DATE'].dt.strftime('%Y-%m-%d').unique().tolist(), reverse=True)
            filtre_date = st.selectbox("📅 Filtrer par date", dates)
        else:
            filtre_date = 'Toutes'
    
    # Application filtres
    df_filtre = df.copy()
    if filtre_machine != 'Toutes':
        df_filtre = df_filtre[df_filtre['Machine'] == filtre_machine]
    if filtre_date != 'Toutes' and 'DATE' in df.columns:
        df_filtre = df_filtre[df_filtre['DATE'].dt.strftime('%Y-%m-%d') == filtre_date]
    
    st.info(f"📊 **{len(df_filtre)} lignes** affichées sur {len(df)} total")
    
    # Affichage des données
    cols_affichage = [c for c in ['DATE', 'Machine', 'Marker', 'CUTTING TIME', 
                                   'INTERRUPTIONS TIME', 'TPS Shift', 'ADV', 'STATE'] 
                      if c in df_filtre.columns]
    
    if st.session_state.role == "admin":
        st.caption("✏️ Mode édition - Double-cliquez pour modifier")
        st.data_editor(df_filtre[cols_affichage], use_container_width=True, hide_index=True)
    else:
        st.dataframe(df_filtre[cols_affichage], use_container_width=True, hide_index=True)
    
    # Export
    st.markdown("---")
    st.markdown('<div class="section-title">📥 Export des données</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = df_filtre.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📎 Exporter données filtrées (CSV)",
            data=csv_data,
            file_name=f"lectra_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        csv_tps = df_tps.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📊 Exporter TPS/ADV (CSV)",
            data=csv_tps,
            file_name=f"tps_adv_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# ==================== MAIN ====================
def main():
    """Fonction principale"""
    
    if not verifier_mot_de_passe():
        return
    
    sidebar_navigation()
    
    # Chargement des données
    with st.spinner("Chargement des données..."):
        df = charger_donnees()
    
    if df is None or df.empty:
        st.error("❌ Impossible de charger les données. Vérifiez le fichier Excel.")
        st.stop()
    
    df_tps = calculer_tps_adv(df)
    
    # Navigation
    page = st.session_state.get('page_active', '🏠 Accueil')
    
    if page == "🏠 Accueil":
        page_accueil(df, df_tps)
    elif page == "⚙️ TPS & Performance":
        page_tps(df, df_tps)
    elif page == "📉 Analyse des Pertes":
        page_pertes(df, df_tps)
    elif page == "📦 ADV Production":
        page_adv(df, df_tps)
    elif page == "🔍 Analyse par Machine":
        page_machine(df, df_tps)
    elif page == "📋 Données Brutes":
        page_donnees(df, df_tps)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <p style='text-align:center; color:#888; font-size:12px;'>
        🏭 Adient Morocco — LECTRA Dashboard v4.0 | Projet PFE 2025 | Tiflet
    </p>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
