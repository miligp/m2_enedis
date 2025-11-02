import os
import base64
import streamlit as st
from streamlit_option_menu import option_menu
from views import contexte, analyse, cartographie, apropos, prediction
from file_loader import setup_heavy_files
import requests

# ✅ Version avec APIs réelles
print("🚀 Démarrage de l'application avec APIs...")

# Initialisation
if 'initialized' not in st.session_state:
    setup_heavy_files()
    st.session_state.initialized = True
    print("✅ Application initialisée")

# Configuration
st.set_page_config(
    page_title="EcoScan Dashboard",
    page_icon="🏠",
    layout="wide",
)

# CSS et style
st.markdown("""
    <style>
    #MainMenu, header, footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

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
    # Utilise la page de prédiction unique
    prediction.show_page()
            
elif selected == "À propos":
    apropos.show_page()