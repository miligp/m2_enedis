import os
import base64
import streamlit as st
from streamlit_option_menu import option_menu
from views import contexte, analyse, cartographie, apropos
from file_loader import setup_heavy_files

# ✅ Version optimisée pour Render
print("🚀 Démarrage de l'application sur Render...")

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
    </style>
""", unsafe_allow_html=True)

# Style sidebar 
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #121417;
        padding-top: 0.5rem !important;
    }
    .logo-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: -10px;
        margin-bottom: 10px;
    }
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
    <div class="logo-container">
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
    st.warning("🔧 Page Prédiction en maintenance")
    st.info("""
    **Version Cloud - Informations importantes**
    
    Les prédictions en temps réel ne sont pas disponibles dans cette version cloud 
    pour des raisons techniques.
    
    **Fonctionnalités disponibles :**
    - 📊 Analyse exploratoire des données
    - 🗺️ Visualisation cartographique
    - 📋 Contexte et méthodologie du projet
    
    **Pour les prédictions complètes :**
    Utilisez la version locale de l'application.
    """)
    
    # Vous pouvez afficher des statistiques ou analyses à la place
    st.subheader("📈 Statistiques globales")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Logements analysés", "45,000+")
    with col2:
        st.metric("Taux DPE A-B", "23%")
    with col3:
        st.metric("Consommation moyenne", "15,240 kWh/an")
        
elif selected == "À propos":
    apropos.show_page()