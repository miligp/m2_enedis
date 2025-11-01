import streamlit as st
import pandas as pd
import numpy as np
import os
import folium
from folium.plugins import MarkerCluster
import streamlit.components.v1 as components # Pour l'affichage de la carte Folium
import requests # <-- AJOUTÉ : Pour le téléchargement HTTP

# Constantes pour le chemin de données
DATA_FILENAME = "df_logement_sample_250k.csv" # Nom du fichier lourd sur le Drive
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# NOUVEAU : Chemins et Variables d'environnement
# Lecture de la variable d'environnement qui contient l'URL de téléchargement Drive
CSV_DOWNLOAD_URL = os.environ.get("https://drive.google.com/file/d/1mskVr6nmrH7R-NvQrOU2zKsi5gN5xmFF/view?usp=sharing")
# Le fichier sera sauvegardé localement dans le dossier Data du conteneur
LOCAL_CSV_PATH = os.path.join(CURRENT_DIR, '..', 'Data', DATA_FILENAME)

# Taille maximale pour la cartographie
N_MAX_POINTS = 50000 

def download_csv(url, local_path):
    """Télécharge le CSV lourd depuis l'URL Drive."""
    if not url:
        st.error("ERREUR: La variable d'environnement CSV_DOWNLOAD_URL est vide. Assurez-vous de la configurer sur la plateforme d'hébergement.")
        return False
    
    # Créer le répertoire Data s'il n'existe pas
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    # Vérification pour Streamlit: Si le fichier est déjà là (suite à un premier chargement), on évite de le télécharger à nouveau.
    if os.path.exists(local_path):
        print(f"Fichier CSV déjà présent localement: {local_path}. Chargement direct.")
        return True

    st.info(f"Téléchargement du fichier de données ({DATA_FILENAME}) en cours...")
    try:
        # Utilisation de requests pour récupérer le fichier
        r = requests.get(url, stream=True, timeout=600) # 10 minutes de timeout pour 600k Ko
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
def load_data():
    """Charge le fichier de données simulé, prend un échantillon et applique les prétraitements/simulations nécessaires."""
    
    # 1. TÉLÉCHARGEMENT
    if not download_csv(CSV_DOWNLOAD_URL, LOCAL_CSV_PATH):
        return pd.DataFrame() 
        
    try:
        # 2. CHARGEMENT LOCAL (après téléchargement)
        df = pd.read_csv(LOCAL_CSV_PATH, sep=';', low_memory=False)
        df.columns = df.columns.str.strip() 

        # --- RENOMMAGE SÉCURISÉ DES COLONNES CRITIQUES ---
        RENAME_MAP = {
            'etiquette_dpe': 'classe_dpe',
            'conso_5_usages_ef': 'conso_energie_kwh',
        }
        df.rename(columns={k: v for k, v in RENAME_MAP.items() if k in df.columns}, inplace=True)
        
        # --- ÉCHANTILLONNAGE (simple pour la cartographie) ---
        if len(df) > N_MAX_POINTS:
            df = df.sample(n=N_MAX_POINTS, random_state=42)
        # ----------------------------------------------------

        # --- SÉCURISATION (Création de colonnes si manquantes après renommage) ---
        rng = np.random.default_rng(42)
        
        if 'classe_dpe' not in df.columns:
            df['classe_dpe'] = np.random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G'], len(df))
            
        if 'conso_energie_kwh' not in df.columns:
            df['conso_energie_kwh'] = np.random.uniform(5000, 30000, len(df))
            
        if "latitude" not in df.columns or "longitude" not in df.columns:
            # Simuler des coordonnées dans une zone générale (Lyon, par exemple)
            df["latitude"] = 45.75 + rng.random(len(df)) * 0.2     
            df["longitude"] = 4.83 + rng.random(len(df)) * 0.2
        
        if 'co2_emission' not in df.columns:
             df['co2_emission'] = (df['conso_energie_kwh'] * 0.25).clip(lower=0).round(1)

        if "periode_construction" not in df.columns:
            df["periode_construction"] = np.random.choice(
                ["Avant 1960", "1960-1979", "1980-1999", "2000-2009", "2010+"],
                len(df)
            )
        
        # Définition des couleurs DPE pour les marqueurs Folium
        colors_map = {
            'A': '#2ecc71', 'B': '#3498db', 'C': '#f1c40f', 'D': '#e67e22', 
            'E': '#e74c3c', 'F': '#c0392b', 'G': '#8e44ad'
        }
        df["color"] = df["classe_dpe"].map(colors_map)
        
        # Créer le tooltip pour Folium (une seule colonne)
        df['tooltip_info'] = 'Classe DPE: ' + df['classe_dpe'].astype(str) + '<br>' + \
                             'Conso (kWh/an): ' + df['conso_energie_kwh'].fillna('N/A').astype(str)
        
        return df.dropna(subset=['latitude', 'longitude', 'classe_dpe']).copy()

    except FileNotFoundError:
        st.error(f"Fichier de données non trouvé localement après téléchargement : {LOCAL_CSV_PATH}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur lors du chargement des données ou de l'application des mappings : {e}")
        return pd.DataFrame()


def show_page():
    st.markdown("""
        <div style='text-align:center;'>
            <h1 style='font-size:42px; font-weight:900; color:#e67e22; margin-bottom:-10px;'>
                Cartographie Interactive des DPE (Folium)
            </h1>
            <p style='color:#bbbbbb; font-style:italic;'>
                Explorez géographiquement les logements selon leur performance énergétique.
                La carte est entièrement zoomable et interactive (API CarteZoom).
            </p>
            <hr style='border:1px solid #333; width:80%; margin:auto; margin-bottom:20px;'>
        </div>
    """, unsafe_allow_html=True)

    df = load_data()

    if df.empty:
        return

    # 1. Filtres utilisateur
    col_filter1, col_filter2 = st.columns(2)

    with col_filter1:
        classe_filter = st.multiselect(
            "Filtrer par classe DPE :",
            options=sorted(df["classe_dpe"].dropna().unique()),
            default=sorted(df["classe_dpe"].dropna().unique()),
            key="dpe_filter_map"
        )
    
    with col_filter2:
        periode_filter = st.multiselect(
            "Filtrer par période de construction :",
            options=sorted(df["periode_construction"].unique()),
            default=sorted(df["periode_construction"].unique()),
            key="periode_filter_map"
        )

    df_filtered = df[
        (df["classe_dpe"].isin(classe_filter)) &
        (df["periode_construction"].isin(periode_filter))
    ]

    # 2. Création de la carte Folium (L'implémentation de la "CarteZoom" est ici)

    # Calculer le centre de la carte (moyenne des coordonnées filtrées)
    if not df_filtered.empty:
        center_lat = df_filtered["latitude"].mean()
        center_lon = df_filtered["longitude"].mean()
    else:
        # Centre par défaut (centre France)
        center_lat, center_lon = 46.603354, 1.888334

    # Initialisation de la carte Folium 
    m = folium.Map(
        location=[center_lat, center_lon], 
        zoom_start=6, 
        tiles="cartodbpositron" 
    )

    # 3. Ajout des marqueurs groupés (MarkerCluster pour la performance)
    marker_cluster = MarkerCluster().add_to(m)

    for idx, row in df_filtered.iterrows():
        
        # Ajout du marqueur au cluster
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=5,
            popup=row['tooltip_info'],
            tooltip=row['tooltip_info'],
            color=row['color'],
            fill=True,
            fill_color=row['color'],
            fill_opacity=0.8
        ).add_to(marker_cluster)

    # 4. Affichage de la carte
    st.subheader(f"Affichage de {len(df_filtered):,} logements (échantillon)")

    # Utiliser le composant HTML pour afficher la carte Folium dans Streamlit
    map_html = m._repr_html_()
    components.html(map_html, height=500)

    st.markdown("""
        <hr style='border:1px solid rgba(255,255,255,0.1); margin-top:30px;'>
        <p style='color:#bbbbbb;'>
            💡 La carte utilise Folium et le <b>Marker Clustering</b> pour une navigation fluide et un affichage efficace des points. 
            Le nombre de logements affichés est limité à 50 000 pour la performance.
        </p>
    """, unsafe_allow_html=True)