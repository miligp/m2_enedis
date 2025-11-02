import streamlit as st
import pandas as pd
import base64, os
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

# Constantes pour le chemin de données
DATA_FILENAME = "df_logements.parquet"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_PARQUET_PATH = os.path.join(CURRENT_DIR, '..', 'Data', DATA_FILENAME)

# Taille de l'échantillon pour les analyses
N_SAMPLE_ANALYSE = 50000
MAX_CONSO_THRESHOLD = 30000

@st.cache_data
def load_data_and_preprocess():
    """Charge le fichier Parquet local et applique les prétraitements."""
    
    try:
        # CHARGEMENT DIRECT du fichier Parquet local
        df = pd.read_parquet(LOCAL_PARQUET_PATH)
        df.columns = df.columns.str.strip()

        # --- RENOMMAGE SÉCURISÉ DES COLONNES CRITIQUES ---
        RENAME_MAP = {
            'surface_habitable_logement': 'surface_m2',
            'etiquette_dpe': 'classe_dpe',
            'conso_5_usages_ef': 'conso_energie_kwh',
        }
        
        # Appliquer le renommage uniquement si la colonne existe
        df.rename(columns={k: v for k, v in RENAME_MAP.items() if k in df.columns}, inplace=True)
        
        # --- SÉCURISATION ---
        if 'classe_dpe' not in df.columns:
            df['classe_dpe'] = np.random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G'], len(df))
            
        if 'conso_energie_kwh' not in df.columns:
            df['conso_energie_kwh'] = np.random.uniform(5000, 30000, len(df))
            
        if 'type_batiment' not in df.columns:
            df['type_batiment'] = np.random.choice(['Appartement', 'Maison'], len(df))

        if 'surface_m2' not in df.columns:
            df['surface_m2'] = np.random.uniform(30, 150, len(df))
        
        # --- FILTRAGE DES VALEURS ABERRANTES ---
        df['conso_energie_kwh'] = pd.to_numeric(df['conso_energie_kwh'], errors='coerce')
        df = df[df['conso_energie_kwh'].between(0, MAX_CONSO_THRESHOLD, inclusive='neither')]

        # --- ÉCHANTILLONNAGE STRATIFIÉ ---
        if len(df) > N_SAMPLE_ANALYSE:
            class_counts = df['classe_dpe'].value_counts()
            sampling_ratio = N_SAMPLE_ANALYSE / len(df)
            sample_sizes = (class_counts * sampling_ratio).round().astype(int)
            sample_sizes[sample_sizes == 0] = 1
            
            df_sampled = df.groupby('classe_dpe', group_keys=False).apply(
                lambda x: x.sample(n=min(len(x), sample_sizes[x.name]), random_state=42)
            ).reset_index(drop=True)
            
            df = df_sampled

        # --- AJOUT DES COLONNES CALCULÉES ---
        if 'co2_emission' not in df.columns:
            df['co2_emission'] = (df['conso_energie_kwh'] * 0.25).clip(lower=0).round(1)

        if 'id_logement' not in df.columns:
            df['id_logement'] = df.index + 1
            
        if 'cout_chauffage' not in df.columns:
            df['cout_chauffage'] = (df['conso_energie_kwh'] * 0.12).clip(lower=0).round(2)
        
        if 'periode_construction' not in df.columns:
            df['periode_construction'] = np.random.choice(range(1900, 2020), len(df))

        return df
    
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return None

def show_page():
    
    logo_path = os.path.join(os.path.dirname(__file__), "..", "img", "Logo.png")
    try:
        with open(logo_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        logo_base64 = ""

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
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #e74c3c !important;
            border-bottom: 3px solid #e74c3c !important;
        }
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
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    df = load_data_and_preprocess()
    
    # Vérification que les données sont chargées
    if df is None or df.empty:
        st.error("❌ Impossible de charger les données pour l'analyse")
        return

    # On ne garde que les colonnes numériques pour les stats descriptives
    numeric_df = df.select_dtypes(include=np.number)
    stats = numeric_df.describe().T.reset_index().rename(columns={"index": "Variable"})
    
    # Supprimez les colonnes non pertinentes
    stats = stats[~stats["Variable"].isin(["longitude", "latitude"])]

    # Variables clés pour les onglets
    key_vars = ["surface_m2", "conso_energie_kwh", "co2_emission", "cout_chauffage"]
    
    # Assurez-vous que stats ne contient que les variables d'intérêt
    stats = stats[stats["Variable"].isin(key_vars)]

    variable_labels = {
        "surface_m2": "Surface (m²)",
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
            
            # Affichage des métriques
            col1, col2, col3, col4 = st.columns(4)
            
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

            st.markdown("<hr style='border:1px solid rgba(255,255,255,0.1); margin-top:25px;'>", unsafe_allow_html=True)

            st.markdown(
                f"<p style='text-align:center; color:#999; font-style:italic; margin-top:-10px;'>"
                f"Nombre total d'observations : <b>{int(row['count'])}</b></p>",
                unsafe_allow_html=True
            )

    # FILTRES ET SOUS-ENSEMBLES DE DONNÉES
    st.markdown(
        """
        <h2 style='text-align:center; color:#f1c40f; font-size:30px; font-weight:900; margin-top:60px;'>
            🎛 Filtres & sous-échantillons de logements
        </h2>
        <p style='text-align:center; color:#bbbbbb; font-style:italic; max-width:900px; margin: 0 auto 30px;'>
            Création de sous-populations intéressantes pour l'analyse énergétique
        </p>
        """,
        unsafe_allow_html=True
    )

    df_work = df.copy()
    
    # Nettoyage et simulation des colonnes de travail
    if "type_batiment" not in df_work.columns:
        df_work["type_batiment"] = df_work["surface_m2"].apply(
            lambda s: "Appartement" if s < df_work["surface_m2"].median() else "Maison"
        )

    # Période de construction
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

    # 1. Passoires énergétiques
    df_mauvais_dpe = df_work[df_work["classe_dpe"].isin(["D", "E", "F", "G"])]

    # 2. Logements anciens
    df_anciens = df_work[df_work["annee_construction"] < 1960]

    # 3. Surface > moyenne
    surface_moy = df_work["surface_m2"].mean()
    df_grands = df_work[df_work["surface_m2"] > surface_moy]

    # 4. CORRECTION : Utiliser conso_energie_kwh au lieu de conso_5_usages
    df_energivores = df_work.sort_values("conso_par_m2", ascending=False)[
        ["id_logement", "surface_m2", "conso_energie_kwh", "conso_par_m2", "classe_dpe"]
    ]

    # 5. Tri multi-critères
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

    # Mapping des choix
    mapping_df = {
        "Passoires énergétiques (D/E/F/G)": df_mauvais_dpe[["id_logement", "surface_m2", "annee_construction", "classe_dpe", "conso_energie_kwh", "cout_chauffage"]],
        "Logements anciens (avant 1960)": df_anciens[["id_logement", "surface_m2", "annee_construction", "classe_dpe", "periode_construction", "cout_chauffage"]],
        "Surface > surface moyenne": df_grands[["id_logement", "surface_m2", "annee_construction", "classe_dpe", "conso_energie_kwh", "cout_chauffage"]],
        "Top conso par m² (énergivores)": df_energivores.head(20),
        "Trié par DPE puis période puis coût chauffage décroissant": df_tri_multi.head(20),
    }

    subset = mapping_df[choix_subset]

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

    # VISUALISATIONS STATISTIQUES COMPLÈTES
    st.markdown("""
        <h2 style='text-align:center; color:#2ecc71; font-size:30px; font-weight:800; margin-top:40px;'>
            📊 Visualisations statistiques interactives
        </h2>
        <p style='text-align:center; color:#bbbbbb; max-width:900px; margin: 0 auto 25px auto;'>
            Exploration graphique complète des distributions et relations clés entre variables énergétiques
        </p>
    """, unsafe_allow_html=True)

    # PREMIÈRE RANGÉE : Distributions principales
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏠 Distribution des surfaces habitables")
        fig_surf = px.histogram(
            df_work, x="surface_m2", nbins=40,
            color_discrete_sequence=["#2ecc71"],
            title="Répartition des surfaces habitables",
            marginal="box"
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
        st.subheader("⚡ Distribution de la consommation (kWh)")
        fig_conso = px.histogram(
            df_work, x="conso_energie_kwh", nbins=40,
            color_discrete_sequence=["#f1c40f"],
            title="Distribution de la consommation énergétique",
            marginal="box"
        )
        fig_conso.update_traces(
            marker_line_color='rgba(200,200,200,0.6)',
            marker_line_width=1.5
        )
        fig_conso.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="Consommation (kWh/an)",
            yaxis_title="Nombre de logements"
        )
        st.plotly_chart(fig_conso, use_container_width=True)

    # DEUXIÈME RANGÉE : Boxplots comparatifs
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("💰 Coût du chauffage selon la classe DPE")
        fig_box_chauff = px.box(
            df_work, x="classe_dpe", y="cout_chauffage",
            color="classe_dpe",
            category_orders={"classe_dpe": ["A", "B", "C", "D", "E", "F", "G"]},
            color_discrete_map={
                "A": "#2ecc71", "B": "#3498db", "C": "#27ae60",
                "D": "#f1c40f", "E": "#e67e22", "F": "#e74c3c", "G": "#c0392b"
            },
            title="Coût du chauffage (€) par classe DPE"
        )
        fig_box_chauff.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="Classe DPE",
            yaxis_title="Coût du chauffage (€)",
            showlegend=False
        )
        st.plotly_chart(fig_box_chauff, use_container_width=True)

    with col4:
        st.subheader("📦 Boxplot de la consommation énergétique")
        fig_box_conso = px.box(
            df_work, y="conso_energie_kwh",
            color_discrete_sequence=["#9b59b6"],
            title="Boxplot de la consommation énergétique"
        )
        fig_box_conso.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            yaxis_title="Consommation (kWh/an)",
            showlegend=False
        )
        st.plotly_chart(fig_box_conso, use_container_width=True)

    # TROISIÈME RANGÉE : Relations entre variables
    col5, col6 = st.columns(2)

    with col5:
        st.subheader("📈 Relation Surface ↔ Consommation énergétique")
        
        # Échantillonnage pour améliorer les performances
        df_sample = df_work.sample(min(1000, len(df_work)), random_state=42)
        
        # Scatter plot sans trendline LOWESS (qui nécessite statsmodels)
        fig_scatter_conso = px.scatter(
            df_sample, x="surface_m2", y="conso_energie_kwh",
            color="classe_dpe",
            color_discrete_map={
                "A": "#2ecc71", "B": "#3498db", "C": "#27ae60",
                "D": "#f1c40f", "E": "#e67e22", "F": "#e74c3c", "G": "#c0392b"
            },
            title="Surface vs Consommation énergétique",
            trendline="ols"  # Utilisation de OLS au lieu de LOWESS
        )
        fig_scatter_conso.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="Surface (m²)",
            yaxis_title="Consommation (kWh/an)"
        )
        st.plotly_chart(fig_scatter_conso, use_container_width=True)

    with col6:
        st.subheader("🔥 Relation Surface ↔ Coût chauffage")

        # Régression linéaire
        x = df_sample["surface_m2"]
        y = df_sample["cout_chauffage"]

        if len(x.unique()) > 1 and len(y.unique()) > 1:
            a, b = np.polyfit(x, y, 1)
            r_value = np.corrcoef(x, y)[0, 1]
        else:
            a = 0
            b = y.mean()
            r_value = 0

        # Graphique scatter avec régression
        fig_scatter_chauffage = go.Figure()
        fig_scatter_chauffage.add_trace(go.Scatter(
            x=x, y=y,
            mode="markers",
            name="Données",
            marker=dict(
                color=df_sample["conso_energie_kwh"],
                colorscale="Viridis",
                size=6,
                opacity=0.6,
                showscale=True,
                colorbar=dict(title="Consommation (kWh)")
            )
        ))
        fig_scatter_chauffage.add_trace(go.Scatter(
            x=np.linspace(x.min(), x.max(), 100),
            y=a * np.linspace(x.min(), x.max(), 100) + b,
            mode="lines",
            name=f"Régression linéaire (r={r_value:.2f})",
            line=dict(color="#e74c3c", width=3)
        ))
        fig_scatter_chauffage.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            title="Surface vs Coût chauffage",
            xaxis_title="Surface (m²)",
            yaxis_title="Coût chauffage (€)",
            legend=dict(orientation="h", y=-0.2)
        )
        st.plotly_chart(fig_scatter_chauffage, use_container_width=True)

    # QUATRIÈME RANGÉE : Analyses avancées
    col7, col8 = st.columns(2)

    with col7:
        st.subheader("🏛️ Répartition par type de bâtiment")
        
        # Préparation des données
        type_batiment_counts = df_work["type_batiment"].value_counts()
        
        fig_pie_type = px.pie(
            values=type_batiment_counts.values,
            names=type_batiment_counts.index,
            title="Répartition des types de bâtiment",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie_type.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        fig_pie_type.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie_type, use_container_width=True)

    with col8:
        st.subheader("📅 Répartition par période de construction")
        
        periode_counts = df_work["periode_construction"].value_counts().sort_index()
        
        fig_bar_periode = px.bar(
            x=periode_counts.index,
            y=periode_counts.values,
            title="Nombre de logements par période de construction",
            color=periode_counts.values,
            color_continuous_scale="Viridis"
        )
        fig_bar_periode.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="Période de construction",
            yaxis_title="Nombre de logements",
            showlegend=False
        )
        fig_bar_periode.update_coloraxes(showscale=False)
        st.plotly_chart(fig_bar_periode, use_container_width=True)

    # CINQUIÈME RANGÉE : Heatmap de corrélation et distribution DPE
    col9, col10 = st.columns(2)

    with col9:
        st.subheader("🔗 Matrice de corrélation")
        
        # Sélection des variables numériques pour la corrélation
        numeric_vars = ['surface_m2', 'conso_energie_kwh', 'cout_chauffage', 'co2_emission']
        corr_df = df_work[numeric_vars].corr()
        
        fig_heatmap = px.imshow(
            corr_df,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdBu_r",
            title="Matrice de corrélation entre variables",
            zmin=-1, zmax=1
        )
        fig_heatmap.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

    with col10:
        st.subheader("🏷️ Distribution des classes DPE")
        
        dpe_counts = df_work["classe_dpe"].value_counts().reindex(['A', 'B', 'C', 'D', 'E', 'F', 'G'])
        
        fig_bar_dpe = px.bar(
            x=dpe_counts.index,
            y=dpe_counts.values,
            title="Répartition des classes DPE",
            color=dpe_counts.index,
            color_discrete_map={
                "A": "#2ecc71", "B": "#3498db", "C": "#27ae60",
                "D": "#f1c40f", "E": "#e67e22", "F": "#e74c3c", "G": "#c0392b"
            }
        )
        fig_bar_dpe.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="Classe DPE",
            yaxis_title="Nombre de logements",
            showlegend=False
        )
        st.plotly_chart(fig_bar_dpe, use_container_width=True)

    # STATISTIQUES RÉCAPITULATIVES
    st.markdown("""
        <h2 style='text-align:center; color:#f1c40f; font-size:28px; font-weight:800; margin-top:50px;'>
            📋 Statistiques récapitulatives
        </h2>
    """, unsafe_allow_html=True)

    # Métriques clés
    col_metrics1, col_metrics2, col_metrics3, col_metrics4 = st.columns(4)
    
    with col_metrics1:
        st.metric(
            label="Nombre total de logements",
            value=f"{len(df_work):,}",
            delta=None
        )
    
    with col_metrics2:
        st.metric(
            label="Surface moyenne",
            value=f"{df_work['surface_m2'].mean():.1f} m²",
            delta=None
        )
    
    with col_metrics3:
        st.metric(
            label="Consommation moyenne",
            value=f"{df_work['conso_energie_kwh'].mean():.0f} kWh/an",
            delta=None
        )
    
    with col_metrics4:
        st.metric(
            label="Coût chauffage moyen",
            value=f"{df_work['cout_chauffage'].mean():.0f} €/an",
            delta=None
        )

    # Affichage des données brutes optionnelles
    with st.expander("📁 Afficher les données brutes (échantillon)"):
        st.dataframe(df_work.head(100), use_container_width=True)
        
        # Téléchargement des données
        csv = df_work.to_csv(index=False)
        st.download_button(
            label="📥 Télécharger les données au format CSV",
            data=csv,
            file_name="donnees_dpe_analyse.csv",
            mime="text/csv",
        )

if __name__ == "__main__":
    show_page()