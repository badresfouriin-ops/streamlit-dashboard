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

# ==================== CSS ====================
st.markdown("""
<style>
    .main { background-color: #f0f2f6; }
    
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

    .section-title {
        font-size: 20px; 
        font-weight: 700; 
        color: #2d3748;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 8px; 
        margin-bottom: 20px;
    }

    .page-header {
        background: linear-gradient(135deg, #1f77b4, #2196F3);
        color: white; 
        padding: 20px 25px; 
        border-radius: 12px;
        margin-bottom: 25px;
    }

    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #1a1f2e 0%, #0f1420 100%);
    }
    [data-testid="stSidebar"] * { 
        color: #e2e8f0 !important; 
    }
    
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
</style>
""", unsafe_allow_html=True)

# ==================== AUTHENTIFICATION ====================
USERS = {
    "admin123": {"role": "admin", "nom": "Administrateur", "password": "admin123"},
    "chef123": {"role": "chef", "nom": "Chef d'atelier", "password": "chef123"},
    "invite123": {"role": "invite", "nom": "Invité", "password": "invite123"},
}

def verifier_mot_de_passe():
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
            border-radius: 8px !important;
            height: 42px !important;
            font-size: 14px !important;
            padding: 0 12px !important;
        }}
        
        .stButton button {{
            background: #003f52 !important;
            color: white !important;
            height: 42px !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            width: 100% !important;
        }}
        
        .stCheckbox label p {{
            font-size: 12px !important;
        }}
    </style>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("""
        <div style="
            background: white;
            border-radius: 20px;
            padding: 40px 35px;
            margin: 80px auto;
            max-width: 400px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
            position: relative;
            z-index: 10;
            text-align: center;
        ">
            <div style="font-size: 28px; font-weight: 800; color: #00334e; margin-bottom: 15px;">
                <span style="color: #9cc31a;">/</span>ADIENT
            </div>
            <div style="font-size: 20px; font-weight: 800; color: #00334e; margin-bottom: 8px;">
                PERFORMANCE
            </div>
            <div style="font-size: 14px; font-weight: 700; color: #9cc31a; margin-bottom: 25px;">
                ATELIER DE COUPE
            </div>
            <div style="height: 2px; background: linear-gradient(90deg, transparent, #9cc31a, transparent); margin-bottom: 25px;"></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<p style='text-align: left; font-size: 13px; font-weight: 600; color: #333; margin-bottom: 5px;'>👤 Nom d'utilisateur</p>", unsafe_allow_html=True)
        username = st.text_input("", placeholder="Entrez votre nom d'utilisateur", key="login_user", label_visibility="collapsed")

        st.markdown("<p style='text-align: left; font-size: 13px; font-weight: 600; color: #333; margin-top: 15px; margin-bottom: 5px;'>🔐 Mot de passe</p>", unsafe_allow_html=True)
        password = st.text_input("", type="password", placeholder="Entrez votre mot de passe", key="login_pwd", label_visibility="collapsed")

        col1, col2 = st.columns([1, 1])
        with col1:
            st.checkbox("Se souvenir de moi")
        with col2:
            st.markdown("<div style='text-align: right; padding-top: 5px;'><a href='#' style='color: #9cc31a; font-size: 12px;'>Mot de passe oublié ?</a></div>", unsafe_allow_html=True)

        if st.button("🔓 SE CONNECTER", use_container_width=True):
            if password in USERS:
                st.session_state.authentifie = True
                st.session_state.role = USERS[password]["role"]
                st.session_state.nom_user = USERS[password]["nom"]
                st.rerun()
            elif password:
                st.error("❌ Identifiants incorrects")

        st.markdown("""
            <div style="text-align: center; margin-top: 25px; padding-top: 15px; border-top: 1px solid #eee;">
                <span style="color: #9cc31a;">🛡️</span>
                <span style="color: #888; font-size: 11px;"> Accès sécurisé</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div style="color: white; margin-top: 120px; padding: 40px; position: relative; z-index: 10;">
            <div style="background: rgba(0,0,0,0.35); backdrop-filter: blur(12px); border-radius: 20px; padding: 40px; border: 1px solid rgba(255,255,255,0.1);">
                <p style="color: #9cc31a; font-size: 11px; letter-spacing: 3px; margin-bottom: 10px;">ADIENT MOROCCO — TIFLET</p>
                <h1 style="font-size: 36px; margin: 15px 0; line-height: 1.2;">
                    UNE PERFORMANCE<br>
                    <span style="color: #9cc31a;">QUI FAIT LA DIFFÉRENCE</span>
                </h1>
                <div style="display: flex; gap: 25px; margin: 25px 0; flex-wrap: wrap;">
                    <div style="font-size: 12px;"><span style="color: #9cc31a;">⏱️</span> TEMPS RÉEL</div>
                    <div style="font-size: 12px;"><span style="color: #9cc31a;">📊</span> KPIs</div>
                    <div style="font-size: 12px;"><span style="color: #9cc31a;">🎯</span> OBJECTIFS</div>
                    <div style="font-size: 12px;"><span style="color: #9cc31a;">📈</span> AMÉLIORATION</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    return False

# ==================== SIDEBAR NAVIGATION ====================
def sidebar_navigation():
    with st.sidebar:
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='text-align:center; padding:20px; background:linear-gradient(135deg, #1f77b4, #2196F3); border-radius:15px; margin-bottom:20px;'>
            <div style='font-size:48px;'>👤</div>
            <div style='font-size:16px; font-weight:700; margin-top:10px;'>{st.session_state.nom_user}</div>
            <div style='font-size:12px; opacity:0.8;'>{st.session_state.role.upper()}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.role == "admin":
            st.success("✅ Accès administrateur complet")
        elif st.session_state.role == "chef":
            st.info("⚙️ Mode Chef d'atelier")
        else:
            st.warning("👁️ Mode Lecture seule")

        st.markdown("---")
        st.markdown("### 🧭 Navigation")

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
        if st.button("🔓 Déconnexion", use_container_width=True):
            st.session_state.authentifie = False
            st.session_state.page_active = "🏠 Accueil"
            st.rerun()

# ==================== CHARGEMENT DES DONNÉES ====================
@st.cache_data(ttl=300)
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
                
                if 'TPS Shift' in df.columns:
                    df['TPS Shift'] = pd.to_numeric(df['TPS Shift'], errors='coerce')
                if 'ADV' in df.columns:
                    df['ADV'] = pd.to_numeric(df['ADV'], errors='coerce')
                if 'CUTTING TIME' in df.columns:
                    df['CUTTING TIME'] = pd.to_numeric(df['CUTTING TIME'], errors='coerce')
                if 'INTERRUPTIONS TIME' in df.columns:
                    df['INTERRUPTIONS TIME'] = pd.to_numeric(df['INTERRUPTIONS TIME'], errors='coerce')
                if 'DATE' in df.columns:
                    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
                
                dataframes.append(df)
        
        if dataframes:
            df = pd.concat(dataframes, ignore_index=True)
            return df
        else:
            return generer_donnees_demo()
    except Exception as e:
        return generer_donnees_demo()

def generer_donnees_demo():
    np.random.seed(42)
    machines = ["Machine A", "Machine B", "Machine C", "Machine D", "Machine E", "Machine F"]
    dates = pd.date_range(start="2025-06-01", end="2025-06-07", freq="D")
    
    data = []
    for machine in machines:
        for date in dates:
            for _ in range(5):
                tps = np.random.uniform(55, 85)
                data.append({
                    'DATE': date,
                    'Machine': machine,
                    'CUTTING TIME': np.random.randint(30, 150),
                    'INTERRUPTIONS TIME': np.random.randint(0, 60),
                    'TPS Shift': tps,
                    'ADV': np.random.uniform(70, 110),
                    'STATE': 'OK' if tps >= 75 else 'NOK'
                })
    return pd.DataFrame(data)

def calculer_tps_adv(df):
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
        
        resultats.append({
            'Machine': machine,
            'TPS (%)': round(tps_moyen, 1),
            'Objectif (%)': 75,
            'Écart (%)': round(tps_moyen - 75, 1),
            'ADV (%)': round(adv_moyen, 1),
            'Cutting (min)': round(cutting, 1),
            'Interruptions (min)': round(interruptions, 1),
            'Statut': "✅ OK" if tps_moyen >= 75 else "⚠️ NOK"
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
    
    tps_moyen = df_tps['TPS (%)'].mean()
    adv_moyen = df_tps['ADV (%)'].mean()
    machines_nok = len(df_tps[df_tps['TPS (%)'] < 75])
    total_interruptions = df_tps['Interruptions (min)'].sum()
    total_markers = len(df)
    jours = df['DATE'].nunique() if 'DATE' in df.columns else 1

    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("⚙️ TPS Moyen", f"{tps_moyen:.1f}%", 
                  delta=f"{tps_moyen - 75:.1f}%" if tps_moyen != 75 else None,
                  delta_color="inverse")
    with col2:
        st.metric("📦 ADV Moyenne", f"{adv_moyen:.1f}%")
    with col3:
        st.metric("🚨 Machines NOK", f"{machines_nok}/{len(df_tps)}")
    with col4:
        st.metric("⚠️ Interruptions", f"{total_interruptions:.0f} min")
    with col5:
        st.metric("🗂️ Total Markers", f"{total_markers}")
    
    st.markdown("---")
    
    col_left, col_right = st.columns([1.5, 1])
    
    with col_left:
        st.markdown('<div class="section-title">📊 TPS par Machine</div>', unsafe_allow_html=True)
        colors = ['#d62728' if t < 40 else '#ff7f0e' if t < 75 else '#2ca02c' for t in df_tps['TPS (%)']]
        fig = go.Figure(data=[go.Bar(x=df_tps['Machine'], y=df_tps['TPS (%)'], marker_color=colors, 
                                     text=df_tps['TPS (%)'].apply(lambda x: f"{x:.1f}%"), textposition='outside')])
        fig.add_hline(y=75, line_dash="dash", line_color="red", annotation_text="Objectif 75%")
        fig.update_layout(height=400, yaxis_title="TPS (%)", yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        st.markdown('<div class="section-title">🚨 Alertes Machines</div>', unsafe_allow_html=True)
        critiques = df_tps[df_tps['TPS (%)'] < 40]
        attention = df_tps[(df_tps['TPS (%)'] >= 40) & (df_tps['TPS (%)'] < 75)]
        
        for _, row in critiques.iterrows():
            st.error(f"🔴 **{row['Machine']}** - TPS: {row['TPS (%)']:.1f}%")
        for _, row in attention.iterrows():
            st.warning(f"🟠 **{row['Machine']}** - TPS: {row['TPS (%)']:.1f}%")
        if len(critiques) == 0 and len(attention) == 0:
            st.success("✅ Toutes les machines sont aux normes")
    
    st.markdown("---")
    st.dataframe(df_tps[['Machine', 'TPS (%)', 'ADV (%)', 'Statut']], use_container_width=True, hide_index=True)

# ==================== PAGE TPS & PERFORMANCE ====================
def page_tps(df, df_tps):
    page_header("⚙️", "TPS & Performance", "Analyse détaillée du Taux de Productivité Synthétique")
    
    if df_tps.empty:
        st.warning("Aucune donnée disponible")
        return
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='TPS Réel', x=df_tps['Machine'], y=df_tps['TPS (%)'],
                         marker_color=['#2ca02c' if x >= 75 else '#ff7f0e' if x >= 40 else '#d62728' for x in df_tps['TPS (%)']],
                         text=df_tps['TPS (%)'].apply(lambda x: f"{x:.1f}%"), textposition='outside'))
    fig.add_trace(go.Scatter(name='Objectif 75%', x=df_tps['Machine'], y=[75] * len(df_tps), 
                             mode='lines', line=dict(color='#1f77b4', width=2, dash='dash')))
    fig.update_layout(title="TPS par Machine", yaxis_title="TPS (%)", yaxis_range=[0, 100], height=450)
    st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE PERTES ====================
def page_pertes(df, df_tps):
    page_header("📉", "Analyse des Pertes", "Identification des sources de perte de productivité")
    
    if df_tps.empty:
        st.warning("Aucune donnée disponible")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Interruptions', x=df_tps['Machine'], y=df_tps['Interruptions (min)'], marker_color='#d62728'))
        fig.update_layout(height=400, yaxis_title="Minutes")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        total_int = df_tps['Interruptions (min)'].sum()
        fig_pie = px.pie(values=[total_int], names=['Interruptions'], color_discrete_sequence=['#d62728'], hole=0.4)
        fig_pie.update_traces(textinfo='percent+label')
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)

# ==================== PAGE ADV ====================
def page_adv(df, df_tps):
    page_header("📦", "ADV Production", "Adhérence au Volume de Production")
    
    if df_tps.empty:
        st.warning("Aucune donnée disponible")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 ADV Moyenne", f"{df_tps['ADV (%)'].mean():.1f}%")
    col2.metric("📈 ADV Maximale", f"{df_tps['ADV (%)'].max():.1f}%")
    col3.metric("📉 ADV Minimale", f"{df_tps['ADV (%)'].min():.1f}%")
    col4.metric("⚠️ Sous objectif", f"{len(df_tps[df_tps['ADV (%)'] < 100])}/{len(df_tps)}")
    
    st.markdown("---")
    colors_adv = ['#2ca02c' if x >= 100 else '#d62728' for x in df_tps['ADV (%)']]
    fig = go.Figure(data=[go.Bar(x=df_tps['Machine'], y=df_tps['ADV (%)'], marker_color=colors_adv,
                                 text=df_tps['ADV (%)'].apply(lambda x: f"{x:.1f}%"), textposition='outside')])
    fig.add_hline(y=100, line_dash="dash", line_color="orange", annotation_text="Objectif 100%")
    fig.update_layout(height=450, yaxis_title="ADV (%)", yaxis_range=[0, 130])
    st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE MACHINE ====================
def page_machine(df, df_tps):
    page_header("🔍", "Analyse par Machine", "Détail complet par machine")
    
    if df.empty or df_tps.empty:
        st.warning("Aucune donnée disponible")
        return
    
    machine = st.selectbox("🏭 Sélectionner une machine", sorted(df['Machine'].unique()))
    df_m = df[df['Machine'] == machine]
    df_tps_m = df_tps[df_tps['Machine'] == machine].iloc[0]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("⚙️ TPS", f"{df_tps_m['TPS (%)']:.1f}%", delta=f"{df_tps_m['Écart (%)']:.1f}%")
    col2.metric("📦 ADV", f"{df_tps_m['ADV (%)']:.1f}%")
    col3.metric("⏱️ Temps de coupe", f"{df_tps_m['Cutting (min)']:.0f} min")
    col4.metric("⚠️ Interruptions", f"{df_tps_m['Interruptions (min)']:.0f} min")

# ==================== PAGE DONNÉES BRUTES ====================
def page_donnees(df, df_tps):
    page_header("📋", "Données Brutes", "Export et analyse des données")
    
    if df.empty:
        st.warning("Aucune donnée disponible")
        return
    
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
    
    df_f = df.copy()
    if filtre_machine != 'Toutes':
        df_f = df_f[df_f['Machine'] == filtre_machine]
    if filtre_date != 'Toutes' and 'DATE' in df.columns:
        df_f = df_f[df_f['DATE'].dt.strftime('%Y-%m-%d') == filtre_date]
    
    st.info(f"📊 **{len(df_f)} lignes** affichées")
    
    cols = [c for c in ['DATE', 'Machine', 'CUTTING TIME', 'INTERRUPTIONS TIME', 'TPS Shift', 'ADV', 'STATE'] if c in df_f.columns]
    
    if st.session_state.role == "admin":
        st.data_editor(df_f[cols], use_container_width=True, hide_index=True)
    else:
        st.dataframe(df_f[cols], use_container_width=True, hide_index=True)
    
    st.markdown("---")
    csv = df_f.to_csv(index=False).encode('utf-8')
    st.download_button("📎 Exporter CSV", csv, f"lectra_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv", use_container_width=True)

# ==================== MAIN ====================
def main():
    if not verifier_mot_de_passe():
        return
    
    sidebar_navigation()
    
    with st.spinner("Chargement des données..."):
        df = charger_donnees()
    
    if df is None or df.empty:
        st.error("❌ Impossible de charger les données")
        st.stop()
    
    df_tps = calculer_tps_adv(df)
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
    
    st.markdown("---")
    st.markdown("""
    <p style='text-align:center; color:#888; font-size:12px;'>
        🏭 Adient Morocco — LECTRA Dashboard v4.0 | Projet PFE 2025 | Tiflet
    </p>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
