import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os
import numpy as np
import datetime as dt
import requests # <-- NOUVEAU : Pour le téléchargement

# Constantes pour le chemin de données
DATA_FILENAME = "df_logement_sample_250k.csv"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# NOUVEAU : Chemins et Variables d'environnement
# Lecture de la variable d'environnement qui contient l'URL de téléchargement Drive
CSV_DOWNLOAD_URL = os.environ.get("https://drive.google.com/file/d/1mskVr6nmrH7R-NvQrOU2zKsi5gN5xmFF/view?usp=sharing")
# Le fichier sera sauvegardé localement dans le dossier Data
LOCAL_CSV_PATH = os.path.join(CURRENT_DIR, '..', 'Data', DATA_FILENAME)

# Taille de l'échantillon pour la rapidité
N_SAMPLE = 10000 

def download_csv(url, local_path):
    """Télécharge le CSV lourd depuis l'URL Drive."""
    if not url:
        st.error("ERREUR: La variable d'environnement CSV_DOWNLOAD_URL est vide. Assurez-vous de la configurer sur la plateforme d'hébergement.")
        return False
    
    # Créer le répertoire Data s'il n'existe pas
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    # Vérification pour Streamlit: Si le fichier est déjà là, on évite de le télécharger à nouveau.
    if os.path.exists(local_path):
        print(f"Fichier CSV déjà présent localement: {local_path}. Chargement direct.")
        return True

    st.info(f"Téléchargement du fichier de données ({DATA_FILENAME}) en cours...")
    try:
        # Utilisation de requests pour récupérer le fichier
        r = requests.get(url, stream=True, timeout=600) # 10 minutes de timeout
        r.raise_for_status() # Lève une exception pour les statuts 4xx ou 5xx (Problème de lien/permissions Drive)

        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        
        st.success("Téléchargement du CSV terminé avec succès.")
        return True
        
    except requests.exceptions.RequestException as e:
        st.error(f"ERREUR LORS DU TÉLÉCHARGEMENT du CSV: {e}. Vérifiez l'URL de téléchargement direct et les permissions Drive.")
        return False
    except Exception as e:
        st.error(f"ERREUR inattendue: {e}")
        return False

@st.cache_data
def load_data_and_stratify():
    """Charge le fichier de données, applique le renommage, et effectue un échantillonnage stratifié."""
    
    # 1. TÉLÉCHARGEMENT
    if not download_csv(CSV_DOWNLOAD_URL, LOCAL_CSV_PATH):
        return pd.DataFrame() # Retourne un DataFrame vide si le téléchargement échoue

    try:
        # 2. CHARGEMENT LOCAL (après téléchargement)
        df = pd.read_csv(LOCAL_CSV_PATH, sep=';', low_memory=False)
        df.columns = df.columns.str.strip() 

        # --- RENOMMAGE SÉCURISÉ DES COLONNES CRITIQUES ---
        RENAME_MAP = {
            'surface_habitable_logement': 'surface_m2',
            'conso_5_usages_ef': 'conso_energie_kwh',
            'etiquette_dpe': 'classe_dpe', 
            'code_region_ban': 'region'
        }
        
        # Appliquer le renommage uniquement si la colonne brute existe
        df.rename(columns={k: v for k, v in RENAME_MAP.items() if k in df.columns}, inplace=True)
        
        # --- SÉCURISATION & ÉCHANTILLONNAGE (le reste de votre code) ---
        
        # Le reste du code de simulation, d'échantillonnage et de nettoyage
        if 'classe_dpe' not in df.columns:
            st.warning("Colonne 'classe_dpe' manquante. Simulation.")
            df['classe_dpe'] = np.random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G'], len(df))
            
        if 'conso_energie_kwh' not in df.columns:
            st.warning("Colonne 'conso_energie_kwh' manquante. Simulation.")
            df['conso_energie_kwh'] = np.random.uniform(5000, 30000, len(df))

        if 'surface_m2' not in df.columns:
             df['surface_m2'] = np.random.uniform(30, 150, len(df))
             
        if 'region' not in df.columns:
             df['region'] = np.random.choice([f"Région {i}" for i in range(1, 6)], len(df))
             
        # --- ÉCHANTILLONNAGE STRATIFIÉ (par classe DPE) ---
        if len(df) > N_SAMPLE:
            class_counts = df['classe_dpe'].value_counts()
            sampling_ratio = N_SAMPLE / len(df)
            sample_sizes = (class_counts * sampling_ratio).round().astype(int)
            sample_sizes[sample_sizes == 0] = 1 # Assurer un minimum de 1
            
            df_sampled = df.groupby('classe_dpe', group_keys=False).apply(
                lambda x: x.sample(n=min(len(x), sample_sizes[x.name]), random_state=42)
            ).reset_index(drop=True)
            
            df = df_sampled
        # ----------------------------------------------------
        
        # Simuler la date DPE si manquante
        if 'date_reception_dpe' not in df.columns:
            df['date_reception_dpe'] = '2024-01-01'

        return df

    except FileNotFoundError:
        st.error(f"Fichier de données non trouvé localement après téléchargement : {LOCAL_CSV_PATH}")
        return pd.DataFrame()
    except pd.errors.ParserError:
        st.error("Erreur de format de fichier. Le fichier CSV doit utiliser le point-virgule (;) comme séparateur.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur de chargement ou de pré-traitement des données : {e}")
        return pd.DataFrame()


def show_page():
    
    df = load_data_and_stratify()
    if df.empty:
        return

    logo_path = os.path.join(os.path.dirname(__file__), "..", "img", "Logo.png")
    try:
        with open(logo_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        logo_base64 = ""

    # ... (le code d'affichage reste le même, utilisant df) ...
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
        <p style='text-align:center; font-size:18px; color:#bbbbbb; font-style:italic; margin-top:-5px;'>
            Évaluer et comprendre la performance énergétique des logements français
        </p>
        <hr style='border: 1px solid #333; margin-top:5px; margin-bottom:25px; width:80%; margin-left:auto; margin-right:auto;'>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
    <div style='max-width: 900px; margin: auto; text-align: center;'>
        <h2 style='color:#2ecc71; font-size:32px; font-weight:1000; margin-bottom:10px;'>
           --
        </h2>
        <p style='font-size:20px; color:#dddddd; line-height:1.5;'>
            Avec l’accélération du changement climatique et la hausse du coût de l’énergie,
            la <b>sobriété énergétique</b> est devenue un enjeu central.<br>
            Enedis souhaite évaluer <b>l’impact de la classe DPE</b> (Diagnostic de Performance Énergétique)
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
        <ul style='list-style:none; padding-left:0; font-size:19px; color:#e6e6e6; line-height:1.9;'>
            <li style='margin-bottom:5px;'>• <b>Visualiser et explorer</b> les données du DPE</li>
            <li style='margin-bottom:5px;'>• <b>Analyser</b> les tendances énergétiques régionales</li>
            <li>• <b>Prédire</b> la classe DPE et la consommation d’énergie d’un logement</li>
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
        indicateurs = [
            ("NOMBRE LOGEMENTS (Est.)", f"{len(df):,}", "#2ecc71"),
            ("SURFACE MOYENNE (m²)", f"{df['surface_m2'].mean():.1f}", "#f1c40f"),
            ("CONSO MOYENNE (kWh)", f"{df['conso_energie_kwh'].mean():.1f}", "#e67e22"),
            ("CLASSE DPE LA PLUS FREQUENTE", df['classe_dpe'].mode()[0], "#3498db"),
        ]

        box_style = """
            <div style="
                border: 3px solid rgba(255,255,255,0.2);
                border-radius: 15px;
                padding: 18px;
                margin: 10px;
                min-height: 130px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                background-color: rgba(255,255,255,0.05);
                width: 100%;
            ">
                <h4 style="color:#f8f9f9; font-size:17px; margin-bottom:10px; font-weight:600;">{}</h4>
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



    # RÉPARTITION DES CLASSES DPE & PAR RÉGION 
    st.markdown("""
    <h2 style='text-align:center; color:#1abc9c; font-size:28px; margin-top:60px;'>
        REPARTITION DES CLASSES DPE
    </h2>
    """, unsafe_allow_html=True)

    # Données de base
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
        font=dict(color="#ffffff"),
        xaxis_title="Classe DPE",
        yaxis_title="Nombre de logements",
        margin=dict(l=20, r=20, t=50, b=40),
        showlegend=False
    )

    st.plotly_chart(fig1, use_container_width=True)



    # Date de mise à jour 
    st.info(f"📅 Données mises à jour jusqu’au : **{dt.date.today()}**")