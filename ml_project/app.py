import os
import base64
import streamlit as st
from streamlit_option_menu import option_menu
from views import contexte, analyse, cartographie, apropos
from file_loader import setup_heavy_files
import requests
import json
import time

# ✅ Version cloud avec APIs réelles
print("🚀 Démarrage de l'application avec APIs...")

# Initialisation
if 'initialized' not in st.session_state:
    setup_heavy_files()
    st.session_state.initialized = True
    print("✅ Application initialisée")

# Configuration
st.set_page_config(
    page_title="EcoScan Dashboard - Cloud",
    page_icon="🏠",
    layout="wide",
)

# CSS et style
st.markdown("""
    <style>
    #MainMenu, header, footer {visibility: hidden;}
    .api-status {
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .api-ready {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .api-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    </style>
""", unsafe_allow_html=True)

# Gestionnaire d'APIs cloud
class CloudAPIClient:
    def __init__(self):
        self.base_urls = {
            'consumption': 'http://localhost:5000',
            'dpe': 'http://localhost:5001'
        }
        self.timeout = 30
    
    def check_api_health(self, api_name):
        """Vérifie si une API est disponible"""
        try:
            url = f"{self.base_urls[api_name]}/health"
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def predict_consumption(self, features):
        """Prédiction de consommation via API"""
        try:
            url = f"{self.base_urls['consumption']}/predict"
            response = requests.post(
                url, 
                json=features,
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API error: {response.status_code}"}
        except Exception as e:
            return {"error": f"Connection failed: {str(e)}"}
    
    def predict_dpe(self, features):
        """Prédiction DPE via API"""
        try:
            url = f"{self.base_urls['dpe']}/predict"
            response = requests.post(
                url, 
                json=features,
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API error: {response.status_code}"}
        except Exception as e:
            return {"error": f"Connection failed: {str(e)}"}

# Client API global
api_client = CloudAPIClient()

# Logo
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

logo_path = os.path.join(os.path.dirname(__file__), "img", "Logo.png")
encoded_logo = get_base64_image(logo_path)

st.sidebar.markdown(
    f"""
    <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; margin-top: -10px; margin-bottom: 10px;'>
        <img src="data:image/png;base64,{encoded_logo}" width="120">
    </div>
    """,
    unsafe_allow_html=True
)

# Menu de navigation
with st.sidebar:
    selected = option_menu(
        menu_title=None,
        options=["Contexte", "Analyse", "Cartographie", "Prédiction", "À propos"],
        icons=["house", "bar-chart-line", "map", "cpu", "info-circle"],
        default_index=0,
        orientation="vertical",
    )

# Couleurs
color_map = {
    "Contexte": "#28b463", "Analyse": "#3498db", "Cartographie": "#e67e22",
    "Prédiction": "#9b59b6", "À propos": "#e74c3c"
}
active_color = color_map.get(selected, "#f9f621")

css_style = f"""
    <style>
    .nav-pills .nav-link.active {{
        background-color: {active_color} !important;
        color: white !important;
    }}
    </style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# Pied de page
st.sidebar.markdown(
    "<div style='color:#cccccc; font-size:13px; font-style:italic;'>Miléna, Marvin & Mazilda's Dashboard</div>",
    unsafe_allow_html=True
)

# Pages
if selected == "Contexte":
    contexte.show_page()
    
elif selected == "Analyse":
    analyse.show_page()
    
elif selected == "Cartographie":
    cartographie.show_page()
    
elif selected == "Prédiction":
    st.title("🔮 Prédictions Énergétiques - APIs Réelles")
    
    # Vérification du statut des APIs
    st.subheader("📊 Statut des APIs")
    col1, col2 = st.columns(2)
    
    with col1:
        api_5000_status = api_client.check_api_health('consumption')
        status_text = "🟢 EN LIGNE" if api_5000_status else "🔴 HORS LIGNE"
        st.markdown(f"""
        <div class='api-status {'api-ready' if api_5000_status else 'api-error'}'>
            <strong>API Consommation (Port 5000)</strong><br>
            {status_text}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        api_5001_status = api_client.check_api_health('dpe')
        status_text = "🟢 EN LIGNE" if api_5001_status else "🔴 HORS LIGNE"
        st.markdown(f"""
        <div class='api-status {'api-ready' if api_5001_status else 'api-error'}'>
            <strong>API DPE (Port 5001)</strong><br>
            {status_text}
        </div>
        """, unsafe_allow_html=True)
    
    # Navigation entre les types de prédiction
    pred_type = st.radio(
        "Type de prédiction:",
        ["🏠 Consommation Énergétique", "📊 Diagnostic DPE"],
        horizontal=True
    )
    
    if pred_type == "🏠 Consommation Énergétique":
        st.subheader("Prédiction de Consommation Énergétique")
        
        if not api_5000_status:
            st.error("❌ L'API de consommation n'est pas disponible. Veuillez démarrer l'API sur le port 5000.")
        else:
            with st.form("consumption_form"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    surface_habitable = st.number_input("Surface habitable (m²)", min_value=10, max_value=500, value=80)
                    type_logement = st.selectbox(
                        "Type de logement",
                        ["Maison", "Appartement", "Studio"]
                    )
                    nombre_pieces = st.slider("Nombre de pièces", 1, 10, 3)
                    
                with col2:
                    annee_construction = st.slider("Année de construction", 1900, 2024, 1990)
                    type_chauffage = st.selectbox(
                        "Type de chauffage",
                        ["électrique", "gaz", "fioul", "bois", "pac"]
                    )
                    isolation = st.selectbox(
                        "Isolation",
                        ["mauvaise", "moyenne", "bonne", "excellente"]
                    )
                    
                with col3:
                    code_departement = st.selectbox(
                        "Département",
                        ["75", "13", "69", "59", "33", "92", "38", "67", "76", "44"]
                    )
                    altitude = st.number_input("Altitude (m)", min_value=0, max_value=2000, value=100)
                    orientation = st.selectbox(
                        "Orientation principale",
                        ["nord", "sud", "est", "ouest"]
                    )
                
                submitted = st.form_submit_button("🔮 Prédire la consommation")
                
                if submitted:
                    # Préparation des features pour l'API
                    features = {
                        "surface_habitable": surface_habitable,
                        "type_logement": type_logement.lower(),
                        "nombre_pieces": nombre_pieces,
                        "annee_construction": annee_construction,
                        "type_chauffage": type_chauffage,
                        "isolation": isolation,
                        "code_departement": code_departement,
                        "altitude": altitude,
                        "orientation": orientation
                    }
                    
                    with st.spinner("🔄 Appel de l'API de consommation..."):
                        result = api_client.predict_consumption(features)
                        
                        if "error" in result:
                            st.error(f"❌ Erreur lors de la prédiction: {result['error']}")
                        else:
                            st.success("✅ Prédiction terminée avec succès !")
                            
                            # Affichage des résultats
                            consommation = result.get('prediction', 0)
                            confidence = result.get('confidence', 0)
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric(
                                    "Consommation prédite", 
                                    f"{consommation:,.0f} kWh/an",
                                    delta=f"Confiance: {confidence:.1%}" if confidence else None
                                )
                            with col2:
                                cout_annuel = consommation * 0.18  # Prix moyen du kWh
                                st.metric("Coût estimé", f"{cout_annuel:,.0f} €/an")
                            with col3:
                                emissions = consommation * 0.05  # Facteur d'émission
                                st.metric("Émissions CO₂", f"{emissions:,.0f} kg/an")
                            
                            # Détails techniques
                            with st.expander("📋 Détails techniques de la prédiction"):
                                st.json(result)
    
    else:  # Prédiction DPE
        st.subheader("Prédiction du Diagnostic de Performance Énergétique (DPE)")
        
        if not api_5001_status:
            st.error("❌ L'API DPE n'est pas disponible. Veuillez démarrer l'API sur le port 5001.")
        else:
            with st.form("dpe_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    consommation_energie = st.number_input("Consommation énergétique (kWh/an)", min_value=1000, max_value=100000, value=15000)
                    surface_habitable = st.number_input("Surface habitable (m²)", min_value=10, max_value=500, value=80, key="dpe_surface")
                    type_batiment = st.selectbox(
                        "Type de bâtiment",
                        ["maison_individuelle", "appartement", "immeuble"],
                        key="dpe_type"
                    )
                    
                with col2:
                    annee_construction = st.slider("Année de construction", 1900, 2024, 1990, key="dpe_annee")
                    type_energie = st.selectbox(
                        "Énergie principale",
                        ["electricite", "gaz", "fioul", "bois"],
                        key="dpe_energie"
                    )
                    code_insee_commune = st.text_input("Code INSEE commune", value="75056")
                
                submitted = st.form_submit_button("🔮 Prédire le DPE")
                
                if submitted:
                    # Préparation des features pour l'API DPE
                    features = {
                        "consommation_energie": consommation_energie,
                        "surface_habitable": surface_habitable,
                        "type_batiment": type_batiment,
                        "annee_construction": annee_construction,
                        "type_energie": type_energie,
                        "code_insee_commune": code_insee_commune
                    }
                    
                    with st.spinner("🔄 Appel de l'API DPE..."):
                        result = api_client.predict_dpe(features)
                        
                        if "error" in result:
                            st.error(f"❌ Erreur lors de la prédiction DPE: {result['error']}")
                        else:
                            st.success("✅ Diagnostic DPE terminé avec succès !")
                            
                            # Affichage du résultat DPE
                            dpe_classe = result.get('prediction', 'G')
                            confidence = result.get('confidence', 0)
                            probabilites = result.get('probabilities', {})
                            
                            # Couleurs DPE
                            dpe_colors = {
                                'A': '#00FF00', 'B': '#90EE90', 'C': '#FFFF00', 
                                'D': '#FFA500', 'E': '#FF7F50', 'F': '#FF4500', 'G': '#FF0000'
                            }
                            
                            st.markdown(f"""
                            <div style='text-align: center; padding: 30px; border-radius: 10px; background-color: {dpe_colors.get(dpe_classe, '#CCCCCC')}; margin: 20px 0;'>
                                <h1 style='color: black; margin: 0; font-size: 48px;'>CLASSE {dpe_classe}</h1>
                                <p style='color: black; font-size: 18px;'>Diagnostic de Performance Énergétique</p>
                                <p style='color: black; font-size: 14px;'>Confiance: {confidence:.1%}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Probabilités par classe
                            if probabilites:
                                st.subheader("📊 Probabilités par classe DPE")
                                prob_df = pd.DataFrame(list(probabilites.items()), columns=['Classe', 'Probabilité'])
                                st.bar_chart(prob_df.set_index('Classe'))
                            
                            # Recommandations
                            st.subheader("💡 Recommandations d'amélioration")
                            if dpe_classe in ['F', 'G']:
                                st.error("""
                                **🚨 Actions prioritaires recommandées :**
                                - 🏗️ Isolation complète des murs et toiture
                                - 🔄 Remplacement du système de chauffage
                                - 🪟 Installation de double/triple vitrage
                                - 🔧 Audit énergétique complet
                                """)
                            elif dpe_classe in ['D', 'E']:
                                st.warning("""
                                **⚠️ Améliorations recommandées :**
                                - 🔧 Optimisation du système de chauffage
                                - 💡 Passage aux LED et appareils efficaces
                                - ☀️ Isolation complémentaire
                                - 🌡️ Régulation programmable
                                """)
                            else:
                                st.success("""
                                **✅ Votre logement est performant !**
                                - 🎯 Maintenir les bonnes pratiques
                                - 🔋 Envisager les énergies renouvelables
                                - 📊 Surveillance continue des consommations
                                """)
                            
                            # Détails techniques
                            with st.expander("📋 Détails techniques du diagnostic"):
                                st.json(result)
    
    # Section démarrage des APIs
    with st.expander("🔧 Gestion des APIs"):
        st.info("""
        **Pour utiliser les prédictions :**
        1. Assurez-vous que les APIs sont démarrées
        2. Vérifiez que les ports 5000 et 5001 sont disponibles
        3. Les modèles ML seront chargés automatiquement
        """)
        
        if st.button("🔄 Vérifier le statut des APIs"):
            st.rerun()
            
elif selected == "À propos":
    apropos.show_page()