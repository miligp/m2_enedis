import os
import base64
import requests
import zipfile
import streamlit as st
from streamlit_option_menu import option_menu
from views import contexte, analyse, cartographie, prediction, apropos

def check_and_download_data():
    """Vérifie et télécharge les données si nécessaire"""
    # Vérifie si les données existent déjà
    data_dir = "/app/data"
    if os.path.exists(data_dir) and any(fname.endswith('.csv') for fname in os.listdir(data_dir)):
        return  # Les données existent déjà
    
    url = os.environ.get("CSV_DOWNLOAD_URL")
    if not url:
        st.warning("Données manquantes et CSV_DOWNLOAD_URL non configuré")
        return
    
    try:
        with st.spinner("Téléchargement des données depuis Google Drive..."):
            # Créer le dossier data s'il n'existe pas
            os.makedirs(data_dir, exist_ok=True)
            
            # Téléchargement
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            zip_path = os.path.join(data_dir, "dataset.zip")
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Extraction
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(data_dir)
            
            # Nettoyage
            os.remove(zip_path)
            
            st.success("Données téléchargées et extraites avec succès!")
            
    except Exception as e:
        st.error(f"Erreur lors du téléchargement: {e}")

# Configuration générale 
st.set_page_config(
    page_title="EcoScan Dashboard",
    page_icon="img/logo.png",
    layout="wide",
)

# Masquer les éléments par défaut de Streamlit
st.markdown("""
    <style>
    #MainMenu, header, footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Style sidebar 
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #121417;
        padding-top: 0.5rem !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
    }
    .logo-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: -10px;
        margin-bottom: 10px;
    }
    .footer {
        position: fixed;
        bottom: 15px;
        left: 20px;
        color: #cccccc;
        font-size: 13px;
        font-style: italic;
    }
    ul.nav.nav-pills {
        background: none !important;
        box-shadow: none !important;
    }
    .nav-pills .nav-link {
        border-radius: 10px !important;
        margin-top: 3px;
        margin-bottom: 3px;
        transition: all 0.2s ease-in-out;
        text-align: left;
        width: 180px;
    }
    .nav-pills .nav-link:hover {
        transform: translateX(3px);
    }
    </style>
""", unsafe_allow_html=True)

# Encodage du logo
def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Logo 
logo_path = os.path.join(os.path.dirname(__file__), "img", "Logo.png")
encoded_logo = get_base64_image(logo_path)

st.sidebar.markdown(
    f"""
    <div class="logo-container">
        <img src="data:image/png;base64,{encoded_logo}" width="120" style="margin:auto;">
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
        menu_icon=None,
        default_index=0,
        orientation="vertical",
    )

# Palette des couleurs selon la page
color_map = {
    "Contexte": "#28b463",      # Vert
    "Analyse": "#3498db",       # Bleu
    "Cartographie": "#e67e22",  # Orange
    "Prédiction": "#9b59b6",    # Violet
    "À propos": "#e74c3c"       # Rouge
}

# Couleur active actuelle 
active_color = color_map.get(selected, "#f9f621")

st.markdown(
    f"""
    <style>
    /* Applique la couleur active dynamiquement */
    .nav-pills .nav-link.active {{
        background-color: {active_color} !important;
        color: white !important;
    }}
    /* Harmonise aussi la couleur au survol */
    .nav-pills .nav-link:hover {{
        background-color: {active_color}33 !important;  /* couleur légère au hover */
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Pied de page 
st.sidebar.markdown(
    "<div class='footer'>Miléna, Marvin & Mazilda's Dashboard</div>",
    unsafe_allow_html=True
)

# Appeler la fonction de téléchargement des données après la configuration de l'interface
check_and_download_data()

# Affichage dynamique des pages 
if selected == "Contexte":
    contexte.show_page()
elif selected == "Analyse":
    analyse.show_page()
elif selected == "Cartographie":
    cartographie.show_page()
elif selected == "Prédiction":
    prediction.show_page()
elif selected == "À propos":
    apropos.show_page()