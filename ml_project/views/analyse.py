import streamlit as st
import pandas as pd
import base64, os
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import io
import requests # <-- NOUVEAU : Pour le téléchargement HTTP

# Constantes pour le chemin de données
DATA_FILENAME = "df_logement_sample_250k.csv" # Nom du fichier lourd sur le Drive
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# NOUVEAU : Chemins et Variables d'environnement
# Lecture de la variable d'environnement qui contient l'URL de téléchargement Drive
CSV_DOWNLOAD_URL = os.environ.get("https://drive.google.com/file/d/1mskVr6nmrH7R-NvQrOU2zKsi5gN5xmFF/view?usp=sharing")
# Le fichier sera sauvegardé localement dans le dossier Data
LOCAL_CSV_PATH = os.path.join(CURRENT_DIR, '..', 'Data', DATA_FILENAME) # Chemin de destination

# Taille de l'échantillon pour les analyses (plus grand que le contexte)
N_SAMPLE_ANALYSE = 50000

# Seuil de nettoyage des outliers (max réaliste pour la consommation annuelle en kWh)
MAX_CONSO_THRESHOLD = 30000 

def download_csv(url, local_path):
    """Télécharge le CSV lourd depuis l'URL Drive."""
    if not url:
        st.error("ERREUR: La variable d'environnement CSV_DOWNLOAD_URL est vide. Assurez-vous de la configurer sur la plateforme d'hébergement.")
        return pd.DataFrame() # Retourne vide pour éviter un crash
    
    # Créer le répertoire Data s'il n'existe pas
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    # Vérification pour Streamlit: Si le fichier est déjà là, on évite de le télécharger à nouveau.
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
def load_data_and_preprocess():
    """Charge le fichier de données sécurisé, prend un échantillon stratifié et applique les renommages/simulations nécessaires."""
    
    # 1. TÉLÉCHARGEMENT
    if not download_csv(CSV_DOWNLOAD_URL, LOCAL_CSV_PATH):
        return pd.DataFrame() 

    try:
        # 2. CHARGEMENT LOCAL (après téléchargement)
        df = pd.read_csv(LOCAL_CSV_PATH, sep=';', low_memory=False)
        df.columns = df.columns.str.strip()

        # --- RENOMMAGE SÉCURISÉ DES COLONNES CRITIQUES (Correction de l'erreur) ---
        RENAME_MAP = {
            'surface_habitable_logement': 'surface_m2',
            'etiquette_dpe': 'classe_dpe',
            'conso_5_usages_ef': 'conso_energie_kwh',
            'annee_recherche': 'annee_construction', 
            'cout_total_5_usages': 'cout_chauffage'
        }
        # Appliquer le renommage uniquement si la colonne brute existe
        df.rename(columns={k: v for k, v in RENAME_MAP.items() if k in df.columns}, inplace=True)
        
        # --- SÉCURISATION (Création de colonnes si manquantes après renommage) ---
        rng = np.random.default_rng(42)
        
        # S'assurer que les colonnes 'classe_dpe' et 'conso_energie_kwh' existent pour la stratification et les calculs
        if 'classe_dpe' not in df.columns:
            st.warning("Colonne 'classe_dpe' manquante. Simulation.")
            df['classe_dpe'] = np.random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G'], len(df))
            
        if 'conso_energie_kwh' not in df.columns:
            df['conso_energie_kwh'] = np.random.uniform(5000, 30000, len(df))
            
        if 'type_batiment' not in df.columns:
            df['type_batiment'] = np.random.choice(['Appartement', 'Maison'], len(df))

        if 'surface_m2' not in df.columns:
             df['surface_m2'] = np.random.uniform(30, 150, len(df))
        
        # --- FILTRAGE/NETTOYAGE DES VALEURS ABERRANTES (OUTLIERS) ---
        # Convertir en numérique et remplacer les non-numériques par NaN, puis filtrer
        df['conso_energie_kwh'] = pd.to_numeric(df['conso_energie_kwh'], errors='coerce')
        df = df[df['conso_energie_kwh'].between(0, MAX_CONSO_THRESHOLD, inclusive='neither')]
        # -----------------------------------------------------------

        # --- ÉCHANTILLONNAGE STRATIFIÉ (par classe DPE) ---
        if len(df) > N_SAMPLE_ANALYSE:
            class_counts = df['classe_dpe'].value_counts()
            
            # Recalculer la taille de l'échantillon car des lignes ont pu être filtrées
            current_len = len(df)
            sampling_ratio = N_SAMPLE_ANALYSE / current_len if current_len > 0 else 0
            
            sample_sizes = (class_counts * sampling_ratio).round().astype(int)
            sample_sizes[sample_sizes == 0] = 1 # Assurer un minimum de 1
            
            # Échantillonner en s'assurant de ne pas demander plus de lignes que disponible
            df_sampled = df.groupby('classe_dpe', group_keys=False).apply(
                lambda x: x.sample(n=min(len(x), sample_sizes[x.name]), random_state=42)
            ).reset_index(drop=True)
            
            df = df_sampled
        # ----------------------------------------------------

        # --- AJOUT DES COLONNES CALCULÉES/SIMULÉES ---
        if 'co2_emission' not in df.columns:
            df['co2_emission'] = (df['conso_energie_kwh'] * 0.25).clip(lower=0).round(1)

        if 'id_logement' not in df.columns:
            df['id_logement'] = df.index + 1
            
        if 'cout_chauffage' not in df.columns or df['cout_chauffage'].isnull().all():
             df['cout_chauffage'] = (df['conso_energie_kwh'] * 0.12) + rng.normal(0, 20, len(df))
             df["cout_chauffage"] = df["cout_chauffage"].clip(lower=0).round(2)
        
        df["cout_chauffage"] = df["cout_chauffage"].fillna(df["cout_chauffage"].mean())
        # 'conso_5_usages' est nécessaire pour le subset des énergivores
        df["conso_5_usages"] = df["conso_energie_kwh"] 
        
        if 'periode_construction' not in df.columns:
            df['periode_construction'] = np.random.choice(range(1900, 2020), len(df))

        return df
    
    except FileNotFoundError:
        # Cette erreur indique que le téléchargement n'a pas réussi à enregistrer le fichier
        st.error(f"Fichier de données non trouvé localement après téléchargement : {LOCAL_CSV_PATH}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur lors du chargement des données ou de l'application des mappings : {e}")
        return pd.DataFrame()


def show_page():
    
    logo_path = os.path.join(os.path.dirname(__file__), "..", "img", "Logo.png")
    try:
        with open(logo_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        logo_base64 = "" # Gérer l'absence du logo en développement

    st.markdown(
        f"""
        <div style='text-align:center; margin-top:-80px;'>
            <img src='data:image/png;base64,{logo_base64}' width='180'>
        </div>
        <h1 style='text-align:center; font-size:42px; font-weight:900;'>
            <span style='color:#2ecc71;'>Analyse descriptive</span> <span style='color:#f1c40f;'>des données DPE</span>
        </h1>
        <p style='text-align:center; color:#bbbbbb; font-style:italic;'>
            Explorer les indicateurs statistiques de chaque variable du dataset
        </p>
        <hr style='border:1px solid #333; width:80%; margin:auto; margin-bottom:20px;'>
        """,
        unsafe_allow_html=True
    )

    # CSS global 
    st.markdown(
        """
        <style>
        /* Centrage + style des onglets */
        div[data-baseweb="tab-list"] {
            justify-content: center !important;
        }
        button[data-baseweb="tab"] {
            font-weight: 700 !important;
            font-size: 20px !important;
            color: #dddddd !important;
            border: none !important;
            background: transparent !important;
        }
        button[data-baseweb="tab"]:hover {
            color: #f1c40f !important;
            transition: color 0.3s ease-in-out;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #e74c3c !important;
            border-bottom: 3px solid #e74c3c !important;
        }

        /* Animation des box */
        .stat-box {
            border: 2.5px solid rgba(255,255,255,0.15);
            border-radius: 18px;
            padding: 18px 10px;
            margin: 10px;
            text-align: center;
            background-color: rgba(255,255,255,0.04);
            min-height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            transition: all 0.3s ease-in-out;
        }
        .stat-box:hover {
            transform: scale(1.05);
            box-shadow: 0 0 15px rgba(255,255,255,0.25);
            border-color: rgba(241,196,15,0.8);
            background-color: rgba(255,255,255,0.07);
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    df = load_data_and_preprocess()
    if df.empty:
        return 

    # On ne garde que les colonnes numériques pour les stats descriptives
    numeric_df = df.select_dtypes(include=np.number)
    stats = numeric_df.describe().T.reset_index().rename(columns={"index": "Variable"})
    
    # Supprimez les colonnes non pertinentes (si elles existent dans le df numérique)
    stats = stats[~stats["Variable"].isin(["longitude", "latitude"])]

    # Variables clés pour les onglets
    key_vars = ["surface_m2", "conso_energie_kwh", "co2_emission", "cout_chauffage"]
    
    # Assurez-vous que stats ne contient que les variables d'intérêt
    stats = stats[stats["Variable"].isin(key_vars)]

    variable_labels = {
        "id_logement": "Logement",
        "surface_m2": "Surface (m²)",
        "annee_construction": "Année de construction",
        "conso_energie_kwh": "Consommation (kWh)",
        "co2_emission": "Émissions CO₂",
        "cout_chauffage": "Coût Chauffage (€)"
    }
    
    # Création des onglets 
    tabs = st.tabs([variable_labels.get(v, v) for v in stats["Variable"]])

    for i, var in enumerate(stats["Variable"]):
        label = variable_labels.get(var, var)
        with tabs[i]:
            row = stats.iloc[i]

            st.markdown(
                f"<h2 style='text-align:center; color:#2ecc71; font-size:34px; font-weight:900;'>{label}</h2>",
                unsafe_allow_html=True
            )
            
            # Affichage des métriques (unchanged logic)
            col1, col2, col3, col4 = st.columns(4)
            # ... (Votre code pour les boîtes statistiques) ...
            col1.markdown(f"""
                <div class='stat-box'>
                    <h4 style='color:#f1c40f; font-size:20px; font-weight:700; margin-bottom:10px;'>MIN</h4>
                    <p style='color:#27ae60; font-size:28px; font-weight:900; margin:0;'>{row['min']:.2f}</p>
                </div>
            """, unsafe_allow_html=True)
            col2.markdown(f"""
                <div class='stat-box'>
                    <h4 style='color:#f1c40f; font-size:20px; font-weight:700; margin-bottom:10px;'>25%</h4>
                    <p style='color:#2ecc71; font-size:28px; font-weight:900; margin:0;'>{row['25%']:.2f}</p>
                </div>
            """, unsafe_allow_html=True)
            col3.markdown(f"""
                <div class='stat-box'>
                    <h4 style='color:#f1c40f; font-size:20px; font-weight:700; margin-bottom:10px;'>50% (MÉDIANE)</h4>
                    <p style='color:#f1c40f; font-size:28px; font-weight:900; margin:0;'>{row['50%']:.2f}</p>
                </div>
            """, unsafe_allow_html=True)
            col4.markdown(f"""
                <div class='stat-box'>
                    <h4 style='color:#f1c40f; font-size:20px; font-weight:700; margin-bottom:10px;'>75%</h4>
                    <p style='color:#e67e22; font-size:28px; font-weight:900; margin:0;'>{row['75%']:.2f}</p>
                </div>
            """, unsafe_allow_html=True)

            col5, col6, col7, col8 = st.columns(4)
            col5.markdown(f"""
                <div class='stat-box'>
                    <h4 style='color:#f1c40f; font-size:20px; font-weight:700; margin-bottom:10px;'>MAX</h4>
                    <p style='color:#e74c3c; font-size:28px; font-weight:900; margin:0;'>{row['max']:.2f}</p>
                </div>
            """, unsafe_allow_html=True)
            col6.markdown(f"""
                <div class='stat-box'>
                    <h4 style='color:#f1c40f; font-size:20px; font-weight:700; margin-bottom:10px;'>MOYENNE</h4>
                    <p style='color:#3498db; font-size:28px; font-weight:900; margin:0;'>{row['mean']:.2f}</p>
                </div>
            """, unsafe_allow_html=True)
            col7.markdown(f"""
                <div class='stat-box'>
                    <h4 style='color:#f1c40f; font-size:20px; font-weight:700; margin-bottom:10px;'>ÉCART-TYPE</h4>
                    <p style='color:#9b59b6; font-size:28px; font-weight:900; margin:0;'>{row['std']:.2f}</p>
                </div>
            """, unsafe_allow_html=True)
            col8.markdown("", unsafe_allow_html=True)
            # ... (End of statistical boxes) ...

            st.markdown("<hr style='border:1px solid rgba(255,255,255,0.1); margin-top:25px;'>", unsafe_allow_html=True)

            st.markdown(
                f"<p style='text-align:center; color:#999; font-style:italic; margin-top:-10px;'>"
                f"Nombre total d’observations : <b>{int(row['count'])}</b></p>",
                unsafe_allow_html=True
            )


    # FILTRES ET SOUS-ENSEMBLES DE DONNÉES

    st.markdown(
        """
        <h2 style='text-align:center; color:#f1c40f; font-size:30px; font-weight:900; margin-top:60px;'>
            🎛 Filtres & sous-échantillons de logements
        </h2>
        <p style='text-align:center; color:#bbbbbb; font-style:italic; max-width:900px; margin: 0 auto 30px;'>
            Ici on crée des sous-populations intéressantes pour l'analyse énergétique :
            appartements, logements anciens, passoires énergétiques...
        </p>
        """,
        unsafe_allow_html=True
    )

    df_work = df.copy()
    
    # ---------------------------
    # Nettoyage et simulation des colonnes de travail
    # ---------------------------
    # Assurez-vous que df_work["type_batiment"] existe après le chargement/nettoyage
    if "type_batiment" not in df_work.columns:
        df_work["type_batiment"] = df_work["surface_m2"].apply(
            lambda s: "Appartement" if s < df_work["surface_m2"].median() else "Maison"
        )


    # Période de construction (basé sur une colonne existante ou simulée)
    if 'annee_construction' not in df_work.columns:
        df_work['annee_construction'] = np.random.choice(range(1900, 2020), len(df_work))
        
    def periode_from_year(y):
        if y < 1960:
            return "Avant 1960"
        elif y < 1980:
            return "1960-1979"
        elif y < 2000:
            return "1980-1999"
        elif y < 2010:
            return "2000-2009"
        else:
            return "2010+"
        
    df_work["periode_construction"] = df_work["annee_construction"].apply(periode_from_year)

    # Conso par m² 
    df_work["conso_par_m2"] = (df_work["conso_energie_kwh"] / df_work["surface_m2"]).clip(lower=0).round(2)

    # 2. DPE
    df_mauvais_dpe = df_work[df_work["classe_dpe"].isin(["D", "E", "F", "G"])]

    # 3. Logements anciens (avant 1960)
    df_anciens = df_work[df_work["annee_construction"] < 1960]

    # 4. Surface > moyenne
    surface_moy = df_work["surface_m2"].mean()
    df_grands = df_work[df_work["surface_m2"] > surface_moy]

    # 5. Tri par logement le + énergivore par m² 
    df_energivores = df_work.sort_values("conso_par_m2", ascending=False)[
        ["id_logement", "surface_m2", "conso_5_usages", "conso_par_m2", "classe_dpe"]
    ]

    # 6. Tri multi-critères 
    df_tri_multi = df_work.sort_values(
        by=["classe_dpe", "periode_construction", "cout_chauffage"],
        ascending=[True, True, False]
    )[
        ["id_logement", "classe_dpe", "periode_construction", "cout_chauffage", "surface_m2"]
    ]

    # Sélecteur pour afficher un sous-échantillon

    st.markdown(
        "<h3 style='text-align:center; color:#2ecc71; font-size:24px; font-weight:800;'>Explorer un sous-groupe</h3>",
        unsafe_allow_html=True
    )

    choix_subset = st.selectbox(
        "Choisir un sous-échantillon à afficher :",
        [
            "Passoires énergétiques (D/E/F/G)",
            "Logements anciens (avant 1960)",
            "Surface > surface moyenne",
            "Top conso par m² (énergivores)",
            "Trié par DPE puis période puis coût chauffage décroissant",
        ],
        index=0,
    )

    # mappe le choix utilisateur 
    mapping_df = {
        "Passoires énergétiques (D/E/F/G)": df_mauvais_dpe[["id_logement", "surface_m2", "annee_construction", "classe_dpe", "conso_5_usages", "cout_chauffage"]],
        "Logements anciens (avant 1960)": df_anciens[["id_logement", "surface_m2", "annee_construction", "classe_dpe", "periode_construction", "cout_chauffage"]],
        "Surface > surface moyenne": df_grands[["id_logement", "surface_m2", "annee_construction", "classe_dpe", "conso_5_usages", "cout_chauffage"]],
        "Top conso par m² (énergivores)": df_energivores.head(20),
        "Trié par DPE puis période puis coût chauffage décroissant": df_tri_multi.head(20),
    }

    subset = mapping_df[choix_subset]

    # résumé 
    st.markdown(
        f"""
        <p style='text-align:center; color:#bbbbbb; font-size:15px; max-width:800px; margin:10px auto 20px;'>
            Sous-échantillon : <b style="color:#f1c40f;">{choix_subset}</b><br>
            {subset.shape[0]} logements correspondants
        </p>
        """,
        unsafe_allow_html=True
    )

    st.dataframe(subset, use_container_width=True, height=300)

    st.markdown(
        "<hr style='border:1px solid rgba(255,255,255,0.1); margin-top:35px; margin-bottom:35px;'>",
        unsafe_allow_html=True
    )


    # VISUALISATIONS STATISTIQUES (sans statsmodels)

    st.markdown("""
        <h2 style='text-align:center; color:#2ecc71; font-size:30px; font-weight:800; margin-top:40px;'>
            Visualisations statistiques interactives
        </h2>
        <p style='text-align:center; color:#bbbbbb; max-width:900px; margin: 0 auto 25px auto;'>
            Exploration graphique des distributions et relations clés entre variables énergétiques.
        </p>
    """, unsafe_allow_html=True)


    # Distribution des surfaces habitables (Histogramme + Boxplot conso)
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distribution des surfaces habitables")
        fig_surf = px.histogram(
            df_work, x="surface_m2", nbins=40,
            color_discrete_sequence=["#2ecc71"],
            title="Répartition des surfaces habitables"
        )
        fig_surf.update_traces(
            marker_line_color='rgba(200,200,200,0.6)',
            marker_line_width=1.5
        )
        fig_surf.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="Surface (m²)",
            yaxis_title="Nombre de logements"
        )
        st.plotly_chart(fig_surf, use_container_width=True)

    with col2:
        st.subheader("Distribution de la consommation (kWh)")
        fig_box_conso = px.box(
            df_work, y="conso_energie_kwh",
            color_discrete_sequence=["#f1c40f"],
            title="Boxplot de la consommation énergétique"
        )
        fig_box_conso.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            yaxis_title="Consommation (kWh/an)"
        )
        st.plotly_chart(fig_box_conso, use_container_width=True)


    # Coût du chauffage / DPE et Logements par période

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Coût du chauffage selon la classe DPE")
        fig_box_chauff = px.box(
            df_work, x="classe_dpe", y="cout_chauffage",
            color="classe_dpe",
            # Ajout manuel des couleurs pour l'ordre G à A
            category_orders={"classe_dpe": ["G", "F", "E", "D", "C", "B", "A"]},
            color_discrete_map={
                "G": "#c0392b", "F": "#e74c3c", "E": "#e67e22", 
                "D": "#f1c40f", "C": "#27ae60", "B": "#3498db", "A": "#2ecc71"
            },
            title="Coût du chauffage (€) par classe DPE"
        )
        fig_box_chauff.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="Classe DPE",
            yaxis_title="Coût du chauffage (€)"
        )
        st.plotly_chart(fig_box_chauff, use_container_width=True)


    # Type d’énergie principale + Régression Surface ↔ Coût chauffage
    
    col5, col6 = st.columns(2)

    with col5:
        st.subheader("Répartition du type d’énergie principale")
        # Utiliser la colonne type_energie_principale_chauffage du petit-set
        if "type_energie_principale_chauffage" not in df_work.columns:
            energies = ["Électricité", "Gaz", "Fioul", "Bois", "Autre"]
            df_work["type_energie_principale_chauffage"] = np.random.choice(energies, len(df_work))

        df_energy = df_work["type_energie_principale_chauffage"].value_counts().reset_index()
        df_energy.columns = ["Type d’énergie", "Nombre"]

        fig_pie_energy = px.pie(
            df_energy, values="Nombre", names="Type d’énergie",
            color_discrete_sequence=px.colors.sequential.RdBu,
            hole=0.35
        )
        fig_pie_energy.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            title="Part des types d’énergie utilisés"
        )
        st.plotly_chart(fig_pie_energy, use_container_width=True)

    with col6:
        st.subheader("Relation Surface ↔ Coût chauffage")

        # Régression manuelle avec NumPy 
        x = df_work["surface_m2"]
        y = df_work["cout_chauffage"]

        # Calcul de la droite de régression (check for constant x or y)
        if len(x.unique()) > 1 and len(y.unique()) > 1:
            a, b = np.polyfit(x, y, 1)
        else:
            a = 0
            b = y.mean()

        # graphique 
        fig_scatter = go.Figure()
        fig_scatter.add_trace(go.Scatter(
            x=x, y=y,
            mode="markers",
            name="Données",
            marker=dict(color="#3498db", size=6, opacity=0.6)
        ))
        fig_scatter.add_trace(go.Scatter(
            x=np.linspace(x.min(), x.max(), 100),
            y=a * np.linspace(x.min(), x.max(), 100) + b,
            mode="lines",
            name="Régression linéaire",
            line=dict(color="#e74c3c", width=3)
        ))
        fig_scatter.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            title="Surface vs Coût chauffage (avec droite de régression)",
            xaxis_title="Surface (m²)",
            yaxis_title="Coût chauffage (€)",
            legend=dict(orientation="h", y=-0.2, x=0.3)
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
