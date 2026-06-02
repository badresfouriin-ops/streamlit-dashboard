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
    if 'authentifie' not in st.session_state:
        st.session_state.authentifie = False
        st.session_state.role = None
        st.session_state.nom_user = ""

    if not st.session_state.authentifie:
        # ---- ENCODAGE DE L'IMAGE D'ARRIÈRE-PLAN EN BASE64 ----
        bg_image_path = "background.png"  # Assurez-vous que l'image est à côté du script sous ce nom
        img_base64 = ""
        
        if os.path.exists(bg_image_path):
            with open(bg_image_path, "rb") as image_file:
                img_base64 = base64.b64encode(image_file.read()).decode()
            bg_css = f"background: url(data:image/png;base64,{img_base64}) no-repeat center center fixed !important; background-size: cover !important;"
        else:
            # Dégradé par défaut si l'image est manquante
            bg_css = "background: linear-gradient(135deg, #0a0f1e 0%, #1a2332 50%, #0d1b2a 100%) !important;"

        # ---- CSS PAGE LOGIN AVEC TRANSPARENCE ET FILTRE ----
        st.markdown(f"""
        <style>
        .stApp {{ 
            {bg_css}
        }}
        
        /* Overlay sombre pour masquer légèrement l'atelier et augmenter la lisibilité */
        .stApp::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(10, 15, 30, 0.6);
            z-index: -1;
        }}
        
        .login-wrapper {{
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .login-left {{
            background: linear-gradient(135deg, rgba(21, 101, 192, 0.9) 0%, rgba(31, 119, 180, 0.9) 100%);
            border-radius: 20px 0 0 20px;
            padding: 50px 40px;
            color: white;
            text-align: center;
        }}
        
        .login-right {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 0 20px 20px 0;
            padding: 50px 40px;
        }}

        .brand-logo {{
            font-size: 64px;
            margin-bottom: 15px;
            display: block;
        }}

        .brand-title {{
            font-size: 26px;
            font-weight: 800;
            margin-bottom: 8px;
            letter-spacing: 1px;
        }}

        .brand-sub {{
            font-size: 13px;
            opacity: 0.85;
            margin-bottom: 30px;
            line-height: 1.6;
        }}

        .stat-box {{
            background: rgba(255,255,255,0.15);
            border-radius: 12px;
            padding: 14px;
            margin: 8px 0;
            text-align: left;
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .stat-icon {{ font-size: 22px; }}
        .stat-label {{ font-size: 12px; opacity: 0.8; }}
        .stat-value {{ font-size: 16px; font-weight: 700; }}

        .login-title {{
            font-size: 24px;
            font-weight: 700;
            color: #1a2332;
            margin-bottom: 6px;
        }}

        .login-sub {{
            font-size: 13px;
            color: #888;
            margin-bottom: 30px;
        }}

        .role-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            margin: 3px;
        }}

        .badge-admin {{ background: #e8f4fd; color: #1f77b4; }}
        .badge-chef  {{ background: #fff3e0; color: #e65100; }}
        .badge-invite{{ background: #e8f5e9; color: #2e7d32; }}

        .divider {{
            border: none;
            height: 1px;
            background: linear-gradient(to right, transparent, #ddd, transparent);
            margin: 20px 0;
        }}

        .footer-login {{
            text-align: center;
            font-size: 11px;
            color: #bbb;
            margin-top: 20px;
        }}
        </style>
        """, unsafe_allow_html=True)

        # Layout : gauche = branding, droite = formulaire
        col_left, col_center, col_right = st.columns([1, 3, 1])
        with col_center:
            st.markdown("<br><br>", unsafe_allow_html=True)

            left, right = st.columns([1, 1])

            # ---- COLONNE GAUCHE : BRANDING ----
            with left:
                st.markdown("""
                <div style='
                    background: linear-gradient(160deg, rgba(21, 101, 192, 0.88) 0%, rgba(31, 119, 180, 0.88) 40%, rgba(2, 136, 209, 0.88) 100%);
                    border-radius: 20px 0 0 20px;
                    padding: 45px 30px;
                    color: white;
                    height: 100%;
                    min-height: 520px;
                '>
                    <div style='font-size:60px; text-align:center; margin-bottom:15px;'>🏭</div>
                    <div style='font-size:22px; font-weight:800; text-align:center; letter-spacing:1px; margin-bottom:6px;'>
                        LECTRA Dashboard
                    </div>
                    <div style='font-size:13px; opacity:0.85; text-align:center; margin-bottom:25px; line-height:1.6;'>
                        Adient Morocco — Tiflet<br>
                        <span style='font-size:11px; opacity:0.7;'>Atelier de Coupe | Projet MMA</span>
                    </div>

                    <hr style='border:none; height:1px; background:rgba(255,255,255,0.2); margin:20px 0;'>

                    <div style='background:rgba(255,255,255,0.12); border-radius:10px; padding:12px 15px; margin:8px 0;'>
                        <div style='font-size:11px; opacity:0.75;'>Machines suivies</div>
                        <div style='font-size:20px; font-weight:700;'>6 Machines Lectra</div>
                    </div>
                    <div style='background:rgba(255,255,255,0.12); border-radius:10px; padding:12px 15px; margin:8px 0;'>
                        <div style='font-size:11px; opacity:0.75;'>Indicateurs clés</div>
                        <div style='font-size:20px; font-weight:700;'>TPS | ADV | Pertes</div>
                    </div>
                    <div style='background:rgba(255,255,255,0.12); border-radius:10px; padding:12px 15px; margin:8px 0;'>
                        <div style='font-size:11px; opacity:0.75;'>Projet</div>
                        <div style='font-size:20px; font-weight:700;'>MMA / Mercedes</div>
                    </div>

                    <hr style='border:none; height:1px; background:rgba(255,255,255,0.2); margin:20px 0;'>

                    <div style='font-size:11px; opacity:0.6; text-align:center;'>
                        © 2025 Adient Morocco<br>Projet PFE — ESFOURI Badr
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # ---- COLONNE DROITE : FORMULAIRE ----
            with right:
                st.markdown("""
                <div style='
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 0 20px 20px 0;
                    padding: 45px 35px;
                    min-height: 200px;
                '>
                    <div style='font-size:28px; font-weight:800; color:#1a2332; margin-bottom:4px;'>
                        Connexion
                    </div>
                    <div style='font-size:13px; color:#888; margin-bottom:28px;'>
                        Entrez vos identifiants pour accéder au dashboard
                    </div>
                    <hr style='border:none; height:1px; background:#f0f0f0; margin-bottom:25px;'>
                </div>
                """, unsafe_allow_html=True)

                mot_de_passe = st.text_input(
                    "🔐 Mot de passe",
                    type="password",
                    placeholder="••••••••••",
                )

                st.markdown("<br>", unsafe_allow_html=True)

                if st.button("🚀  SE CONNECTER", use_container_width=True, type="primary"):
                    if mot_de_passe in USERS:
                        st.session_state.authentifie = True
                        st.session_state.role = USERS[mot_de_passe]["role"]
                        st.session_state.nom_user = USERS[mot_de_passe]["nom"]
                        st.success(f"✅ Bienvenue {USERS[mot_de_passe]['nom']} !")
                        st.rerun()
                    elif mot_de_passe:
                        st.error("❌ Mot de passe incorrect. Réessayez.")

                st.markdown("""
                <hr style='border:none; height:1px; background:#f0f0f0; margin:20px 0;'>
                <div style='font-size:12px; color:#aaa; margin-bottom:8px;'>Niveaux d'accès disponibles :</div>
                """, unsafe_allow_html=True)

                col_b1, col_b2, col_b3 = st.columns(3)
                with col_b1:
                    st.markdown("""
                    <div style='background:#e8f4fd; border-radius:8px; padding:8px; text-align:center;'>
                        <div style='font-size:18px;'>👑</div>
                        <div style='font-size:11px; color:#1f77b4; font-weight:600;'>Admin</div>
                        <div style='font-size:10px; color:#888;'>Accès complet</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_b2:
                    st.markdown("""
                    <div style='background:#fff3e0; border-radius:8px; padding:8px; text-align:center;'>
                        <div style='font-size:18px;'>⚙️</div>
                        <div style='font-size:11px; color:#e65100; font-weight:600;'>Chef</div>
                        <div style='font-size:10px; color:#888;'>Suivi atelier</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_b3:
                    st.markdown("""
                    <div style='background:#e8f5e9; border-radius:8px; padding:8px; text-align:center;'>
                        <div style='font-size:18px;'>👁️</div>
                        <div style='font-size:11px; color:#2e7d32; font-weight:600;'>Invité</div>
                        <div style='font-size:10px; color:#888;'>Lecture seule</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("""
                <div style='font-size:10px; color:#ccc; text-align:center; margin-top:20px;'>
                    LECTRA Dashboard v4.0 | Adient Morocco
                </div>
                """, unsafe_allow_html=True)

        return False
    return True


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
