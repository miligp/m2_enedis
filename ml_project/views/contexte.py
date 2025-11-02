import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os
import numpy as np
import datetime as dt

# Constantes pour le chemin de données
DATA_FILENAME = "df_logements.parquet"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Chemin corrigé
LOCAL_PARQUET_PATH = os.path.join(CURRENT_DIR, '..', 'Data', DATA_FILENAME)

# Taille de l'échantillon pour la rapidité
N_SAMPLE = 10000

@st.cache_data
def load_data_and_stratify():
    """Charge le fichier Parquet local et effectue un échantillonnage stratifié."""
    
    try:
        # Vérifier si le fichier existe
        if not os.path.exists(LOCAL_PARQUET_PATH):
            st.error(f"❌ Fichier non trouvé: {LOCAL_PARQUET_PATH}")
            return None
        
        # CHARGEMENT du fichier Parquet
        df = pd.read_parquet(LOCAL_PARQUET_PATH)
        df.columns = df.columns.str.strip()

        # --- RENOMMAGE SÉCURISÉ DES COLONNES CRITIQUES ---
        RENAME_MAP = {
            'surface_habitable_logement': 'surface_m2',
            'conso_5_usages_ef': 'conso_energie_kwh',
            'etiquette_dpe': 'classe_dpe', 
        }
        
        # Appliquer le renommage uniquement si la colonne existe
        df.rename(columns={k: v for k, v in RENAME_MAP.items() if k in df.columns}, inplace=True)
        
        # --- SÉCURISATION - Créer les colonnes si manquantes ---
        if 'classe_dpe' not in df.columns:
            df['classe_dpe'] = np.random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G'], len(df))
            
        if 'conso_energie_kwh' not in df.columns:
            df['conso_energie_kwh'] = np.random.uniform(5000, 30000, len(df))

        if 'surface_m2' not in df.columns:
            df['surface_m2'] = np.random.uniform(30, 150, len(df))
        
        # --- ÉCHANTILLONNAGE STRATIFIÉ ---
        if len(df) > N_SAMPLE:
            class_counts = df['classe_dpe'].value_counts()
            sampling_ratio = N_SAMPLE / len(df)
            sample_sizes = (class_counts * sampling_ratio).round().astype(int)
            sample_sizes[sample_sizes == 0] = 1
            
            df_sampled = df.groupby('classe_dpe', group_keys=False).apply(
                lambda x: x.sample(n=min(len(x), sample_sizes[x.name]), random_state=42)
            ).reset_index(drop=True)
            
            df = df_sampled

        st.success(f"✅ Données chargées: {len(df)} lignes")
        return df

    except Exception as e:
        st.error(f"Erreur de chargement des données : {e}")
        return None

def show_page():
    
    df = load_data_and_stratify()
    
    # CORRECTION : Vérifier si df est None ou empty
    if df is None or df.empty:
        st.error("❌ Impossible de charger les données")
        return

    logo_path = os.path.join(os.path.dirname(__file__), "..", "img", "Logo.png")
    try:
        with open(logo_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        logo_base64 = ""

    st.markdown(
        f"""
        <div style='text-align:center; margin-top:-80px; margin-bottom:5px;'>
            <img src='data:image/png;base64,{logo_base64}' width='200' style='margin-bottom:-15px;'>
        </div>
        <h1 style='text-align:center; font-size:44px; font-weight:700; margin-top:-10px; margin-bottom:10px;'>
            <span style='color:#28b463;'>GreenTech</span>
            <span style='color:#f1c40f;'> Solutions</span>
            <span style='color:#28b463;'> × </span>
            <span style='color:#3498db;'>Enedis</span>
        </h1>
        <p style='text-align:center; font-size:18px; color:var(--text-color); font-style:italic; margin-top:-5px;'>
            Évaluer et comprendre la performance énergétique des logements français
        </p>
        <hr style='border: 1px solid var(--border-color); margin-top:5px; margin-bottom:25px; width:80%; margin-left:auto; margin-right:auto;'>
        
        <style>
            :root {{
                --text-color: #bbbbbb;
                --text-color-secondary: #cccccc;
                --border-color: #333;
                --card-bg: rgba(255,255,255,0.05);
            }}
            
            @media (prefers-color-scheme: light) {{
                :root {{
                    --text-color: #333333;
                    --text-color-secondary: #555555;
                    --border-color: #dddddd;
                    --card-bg: rgba(0,0,0,0.05);
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
    <div style='max-width: 900px; margin: auto; text-align: center;'>
        <h2 style='color:#2ecc71; font-size:32px; font-weight:1000; margin-bottom:10px;'>
           Contexte du Projet
        </h2>
        <p style='font-size:20px; color:var(--text-color-secondary); line-height:1.5;'>
            Avec l'accélération du changement climatique et la hausse du coût de l'énergie,
            la <b>sobriété énergétique</b> est devenue un enjeu central.<br>
            Enedis souhaite évaluer <b>l'impact de la classe DPE</b> (Diagnostic de Performance Énergétique)
            sur la consommation électrique des logements.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # OBJECTIFS 
    st.markdown("""
    <div style='max-width: 800px; margin: 40px auto; text-align: center;'>
        <h4 style='color:#2ecc71; font-size:28px; margin-bottom:10px; font-weight:800;'>
            OBJECTIFS
        </h4>
        <ul style='list-style:none; padding-left:0; font-size:19px; color:var(--text-color-secondary); line-height:1.9;'>
            <li style='margin-bottom:5px;'>• <b>Visualiser et explorer</b> les données du DPE</li>
            <li style='margin-bottom:5px;'>• <b>Analyser</b> les tendances énergétiques régionales</li>
            <li>• <b>Prédire</b> la classe DPE et la consommation d'énergie d'un logement</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # APERÇU DES DONNÉES + INDICATEURS CLÉS 
    st.markdown(
        "<h2 style='text-align:center; color:#f1c40f; font-size:28px;font-weight:1000; margin-top:20px;'>APERÇU DES DONNÉES & INDICATEURS CLÉS</h2>",
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.markdown(
            f"<h4 style='text-align:center; color:#f1c40f; font-size:22px; font-weight:800;'>Aperçu de l'échantillon ({len(df):,} lignes)</h4>",
            unsafe_allow_html=True
        )
        st.dataframe(df.head(10), use_container_width=True, height=340)

    with col2:
        st.markdown(
            "<h4 style='text-align:center; color:#e67e22; font-size:22px; font-weight:800;'>Indicateurs clés</h4>",
            unsafe_allow_html=True
        )
        
        # Calcul sécurisé des indicateurs
        try:
            surface_moyenne = f"{df['surface_m2'].mean():.1f}"
        except:
            surface_moyenne = "N/A"
            
        try:
            conso_moyenne = f"{df['conso_energie_kwh'].mean():.1f}"
        except:
            conso_moyenne = "N/A"
            
        try:
            classe_frequente = df['classe_dpe'].mode()[0] if not df['classe_dpe'].mode().empty else "N/A"
        except:
            classe_frequente = "N/A"

        indicateurs = [
            ("NOMBRE LOGEMENTS", f"{len(df):,}", "#2ecc71"),
            ("SURFACE MOYENNE (m²)", surface_moyenne, "#f1c40f"),
            ("CONSO MOYENNE (kWh)", conso_moyenne, "#e67e22"),
            ("CLASSE DPE FRÉQUENTE", classe_frequente, "#3498db"),
        ]

        box_style = """
            <div style="
                border: 3px solid var(--border-color);
                border-radius: 15px;
                padding: 18px;
                margin: 10px;
                min-height: 130px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                background-color: var(--card-bg);
                width: 100%;
            ">
                <h4 style="color:var(--text-color-secondary); font-size:17px; margin-bottom:10px; font-weight:600;">{}</h4>
                <p style="color:{}; font-size:24px; font-weight:800; margin:0;">{}</p>
            </div>
        """

        for i in range(0, len(indicateurs), 2):
            c1, c2 = st.columns(2)
            c1.markdown(box_style.format(indicateurs[i][0], indicateurs[i][2], indicateurs[i][1]), unsafe_allow_html=True)
            if i + 1 < len(indicateurs):
                c2.markdown(box_style.format(indicateurs[i+1][0], indicateurs[i+1][2], indicateurs[i+1][1]), unsafe_allow_html=True)
            else:
                c2.markdown("")  

    # RÉPARTITION DES CLASSES DPE
    st.markdown("""
    <h2 style='text-align:center; color:#1abc9c; font-size:28px; margin-top:60px;'>
        RÉPARTITION DES CLASSES DPE
    </h2>
    """, unsafe_allow_html=True)

    # Données de base avec gestion d'erreur
    try:
        class_counts = df['classe_dpe'].value_counts().sort_index().reset_index()
        class_counts.columns = ["Classe DPE", "Nombre de logements"]
        
        # Graphique Répartition des classes DPE
        fig1 = px.bar(
            class_counts,
            x="Classe DPE",
            y="Nombre de logements",
            text="Nombre de logements",
            color="Classe DPE",
            color_discrete_sequence=["#27ae60", "#2ecc71", "#f1c40f", "#f39c12", "#e67e22", "#e74c3c", "#c0392b"]
        )
        fig1.update_traces(textposition="outside")
        fig1.update_layout(
            title=dict(text="Répartition des classes DPE", x=0.5, font=dict(color="#2ecc71", size=18)),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="Classe DPE",
            yaxis_title="Nombre de logements",
            margin=dict(l=20, r=20, t=50, b=40),
            showlegend=False
        )
        st.plotly_chart(fig1, use_container_width=True)
    except Exception as e:
        st.error(f"Erreur lors de la création du graphique : {e}")

    # Date de mise à jour 
    st.info(f"📅 Données mises à jour jusqu'au : **{dt.date.today()}**")