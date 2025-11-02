import streamlit as st
import pandas as pd
import numpy as np
import os
import base64
import plotly.graph_objects as go
import requests
import json
import time

# --- 1. CONFIGURATION DES ENDPOINTS ET CONSTANTES ---

# URLs des APIs - exactement comme dans vos fichiers
API_URL_DPE = "http://localhost:5001/predict_dpe" 
API_URL_CONSO = "http://localhost:5000/predict_conso"
API_HEALTH_DPE = "http://localhost:5001/health"
API_HEALTH_CONSO = "http://localhost:5000/health"

# Mappings pour l'affichage
CLASSES_DPE_MAPPING = ["G", "F", "E", "D", "C", "B", "A"]
COLORS_DPE = ["#c0392b", "#8e44ad", "#e74c3c", "#e67e22", "#f1c40f", "#27ae60", "#2ecc71"] 
CO2_FACTOR = 0.25  # Facteur d'émission CO2 (kg/kWh)

# --- 2. FONCTIONS AUXILIAIRES ---

def check_api_health():
    """Vérifie si les APIs sont disponibles"""
    status = {
        'dpe': False,
        'conso': False
    }
    
    try:
        response = requests.get(API_HEALTH_DPE, timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            status['dpe'] = status_data.get('model_loaded', False)
    except:
        status['dpe'] = False
        
    try:
        response = requests.get(API_HEALTH_CONSO, timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            status['conso'] = status_data.get('model_loaded', False)
    except:
        status['conso'] = False
        
    return status

def create_dpe_gauge(index):
    """Crée la jauge Plotly pour la classe DPE à partir de l'index prédit (0=G, 6=A)."""
    # S'assure que l'index est dans la plage pour éviter les erreurs d'indice
    safe_index = max(0, min(len(CLASSES_DPE_MAPPING) - 1, index))
    classe_label = CLASSES_DPE_MAPPING[safe_index]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=safe_index + 1,
        gauge={
            'axis': {'range': [1, 7], 'tickvals': list(range(1, 8)), 'ticktext': CLASSES_DPE_MAPPING}, 
            'bar': {'color': COLORS_DPE[safe_index]},
            'steps': [{'range': [i + 1, i + 2], 'color': COLORS_DPE[i]} for i in range(len(CLASSES_DPE_MAPPING))],
        },
        title={'text': f"Classe DPE : {classe_label}", 'font': {'color': COLORS_DPE[safe_index], 'size': 20}}
    ))
    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=20, r=20, t=60, b=20))
    return fig, classe_label

def create_conso_gauge(conso_pred):
    """Crée la jauge Plotly pour la consommation estimée."""
    max_conso_chart = 30000 
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=conso_pred,
        gauge={
            'axis': {'range': [0, max_conso_chart], 'tickvals': [0, 5000, 15000, max_conso_chart]}, 
            'bar': {'color': '#3498db'},
            'steps': [
                {'range': [0, 5000], 'color': "rgba(46, 204, 113, 0.2)"}, 
                {'range': [5000, 15000], 'color': "rgba(52, 152, 219, 0.2)"},
                {'range': [15000, max_conso_chart], 'color': "rgba(231, 76, 60, 0.2)"}
            ],
        },
        title={'text': "Consommation Estimée (kWh/an)", 'font': {'color': '#3498db', 'size': 20}}
    ))
    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=20, r=20, t=60, b=20))
    return fig

# --- 3. FONCTION PRINCIPALE ---

def show_page():
    
    # Configuration du logo et de l'en-tête
    logo_path = os.path.join(os.path.dirname(__file__), "..", "img", "Logo.png")
    try:
        with open(logo_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        logo_base64 = ""

    st.markdown(f"""
        <div style='text-align:center;'>
            <img src='data:image/png;base64,{logo_base64}' width='180'>
            <h1 style='color:#2ecc71; font-size:42px; font-weight:900;'>
                Prédiction du DPE & de la Consommation Énergétique
            </h1>
            <p style='color:#bbbbbb; font-style:italic; font-size:17px;'>
                Saisis les caractéristiques de ton logement pour estimer sa performance énergétique.
            </p>
            <hr style='border:1px solid #333; width:80%; margin:auto; margin-bottom:25px;'>
        </div>
    """, unsafe_allow_html=True)

    # Vérification du statut des APIs
    st.subheader("📊 Statut des APIs")
    api_status = check_api_health()
    
    col1, col2 = st.columns(2)
    
    with col1:
        status_color = "🟢" if api_status['conso'] else "🔴"
        status_text = "EN LIGNE" if api_status['conso'] else "HORS LIGNE"
        st.markdown(f"""
            <div style='background-color: {"#d4edda" if api_status['conso'] else "#f8d7da"}; 
                        padding: 15px; border-radius: 5px; text-align: center;'>
                <h4>API Consommation (Port 5000)</h4>
                <h3>{status_color} {status_text}</h3>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        status_color = "🟢" if api_status['dpe'] else "🔴"
        status_text = "EN LIGNE" if api_status['dpe'] else "HORS LIGNE"
        st.markdown(f"""
            <div style='background-color: {"#d4edda" if api_status['dpe'] else "#f8d7da"}; 
                        padding: 15px; border-radius: 5px; text-align: center;'>
                <h4>API DPE (Port 5001)</h4>
                <h3>{status_color} {status_text}</h3>
            </div>
        """, unsafe_allow_html=True)

    if not api_status['conso'] or not api_status['dpe']:
        st.error("""
        ❌ **Les APIs ne sont pas toutes disponibles :**
        - Vérifiez que les APIs sont démarrées sur les ports 5000 et 5001
        - Utilisez le gestionnaire d'APIs pour les lancer
        - Vérifiez les logs pour identifier les problèmes
        """)
        
        if st.button("🔄 Vérifier à nouveau le statut"):
            st.rerun()
        return

    # --- Formulaire utilisateur ---
    st.markdown("<h3 style='color:#f1c40f; text-align:center;'>Données du logement</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        surface_habitable_logement = st.number_input("Surface habitable (m²) :", min_value=10, max_value=500, value=80, step=5)
        periode_construction = st.selectbox("Période de construction :", [
            "avant 1948", "1948-1974", "1975-1977", "1978-1982", "1983-1988", 
            "1989-2000", "2001-2005", "2006-2012", "2013-2021", "après 2021"
        ])
        hauteur_sous_plafond = st.number_input("Hauteur sous plafond (m) :", min_value=2.0, max_value=5.0, value=2.5, step=0.1)
        nombre_appartement_cat = st.selectbox("Nombre d'appartement :", [
            "Maison(Unitaire ou 2 à 3 logements)",
            "Petit Collectif(4 à 9 logements)", 
            "Moyen Collectif(10 à 30 logements)", 
            "Grand Collectif(> 30 logements)"
        ])
        
    with col2:
        type_energie_n1 = st.selectbox("Type d'énergie principale (l'année dernière) :", [
            "Gaz naturel", "Électricité", "Réseau de chauffage urbain", 
            "Bois et biomasse", "Fioul", "Gaz (GPL/Propane/Butane)", "Charbon"
        ])
        type_energie_principale_chauffage = st.selectbox("Type d'énergie principale (cette année) :", [
            "Gaz naturel", "Électricité", "Réseau de chauffage urbain", 
            "Bois et biomasse", "Fioul", "Gaz (GPL/Propane/Butane)", "Charbon"
        ])
        qualite_isolation_murs = st.selectbox("Qualité de l'isolation des murs :", [
            "Insuffisante", "Moyenne", "bonne", "très bonne"
        ])
        logement = st.selectbox("Bâtiment :", ["Neuf", "Ancien"])
        
    st.markdown("<div style='text-align:center; margin-top:30px;'>", unsafe_allow_html=True)
    predict_button = st.button("🚀 Lancer la double prédiction", type="primary")
    st.markdown("</div>", unsafe_allow_html=True)

    
    # --- LOGIQUE DE DOUBLE PRÉDICTION ET D'AFFICHAGE ---
    if predict_button:
        
        # 1. Construction des données initiales pour l'API DPE
        data_initial = {
            "surface_habitable_logement": surface_habitable_logement,
            "periode_construction": periode_construction, 
            "hauteur_sous_plafond": hauteur_sous_plafond,
            "nombre_appartement_cat": nombre_appartement_cat,
            "type_energie_n1": type_energie_n1,
            "type_energie_principale_chauffage": type_energie_principale_chauffage,
            "qualite_isolation_murs": qualite_isolation_murs,
            "logement": logement
        }

        # --- A. APPEL 1 : CLASSIFICATION (DPE) ---
        dpe_prediction = None
        
        try:
            with st.spinner("1/2: Estimation de la Classe DPE... (API 5001)"):
                response_dpe = requests.post(API_URL_DPE, json=data_initial, timeout=30)
                
                # Vérification du JSON
                try:
                    dpe_result = response_dpe.json()
                except json.JSONDecodeError:
                    st.error("❌ L'API DPE (5001) n'a PAS retourné de JSON valide.")
                    st.text(f"Statut HTTP: {response_dpe.status_code}")
                    st.text(f"Contenu brut de la réponse (non-JSON) : {response_dpe.text[:500]}")
                    return

                if response_dpe.status_code == 200:
                    dpe_prediction = dpe_result.get("prediction_DPE_index")
                    
                    if dpe_prediction is None:
                        st.error("API DPE : La clé 'prediction_DPE_index' est manquante ou NULL. Arrêt du traitement.")
                        return
                        
                    st.success(f"✅ Classe DPE prédite: {CLASSES_DPE_MAPPING[dpe_prediction]}")
                        
                else:
                    st.error(f"Erreur API DPE ({response_dpe.status_code}): {dpe_result.get('error', 'Erreur inconnue')}. Arrêt du traitement.")
                    return
                    
        except requests.exceptions.ConnectionError:
            st.error(f"❌ Échec de la connexion à l'API DPE sur {API_URL_DPE}. Est-elle lancée sur le port 5001?")
            return
        except requests.exceptions.Timeout:
            st.error("⏰ Timeout lors de l'appel à l'API DPE. Le modèle met trop de temps à répondre.")
            return
            
        
        # 2. ENRICHISSEMENT DES DONNÉES pour l'étape de Régression
        data_for_conso = data_initial.copy()
        
        # AJOUTER L'ÉTIQUETTE DPE PRÉDITE (exactement comme attendu par votre API)
        data_for_conso['etiquette_dpe'] = dpe_prediction

        # --- B. APPEL 2 : RÉGRESSION (CONSOMMATION) ---
        conso_pred = None
        
        try:
            with st.spinner("2/2: Estimation de la Consommation... (API 5000)"):
                response_conso = requests.post(API_URL_CONSO, json=data_for_conso, timeout=30)
                
                # Vérification du JSON
                try:
                    conso_result = response_conso.json()
                except json.JSONDecodeError:
                    st.error("❌ L'API Consommation (5000) n'a PAS retourné de JSON valide.")
                    st.text(f"Statut HTTP: {response_conso.status_code}")
                    st.text(f"Contenu brut de la réponse (non-JSON) : {response_conso.text[:500]}")
                    return

                if response_conso.status_code == 200:
                    conso_pred = conso_result.get("conso_predite_kwh")
                    
                    if conso_pred is None:
                        st.error("API Consommation : La clé 'conso_predite_kwh' est manquante ou NULL.")
                        return

                    st.success("✅ Consommation estimée avec succès!")

                else:
                    st.error(f"Erreur API Consommation ({response_conso.status_code}): {conso_result.get('error', 'Erreur inconnue')}")
                    return
                    
        except requests.exceptions.ConnectionError:
            st.error(f"❌ Échec de la connexion à l'API Consommation sur {API_URL_CONSO}. Est-elle lancée sur le port 5000?")
            return
        except requests.exceptions.Timeout:
            st.error("⏰ Timeout lors de l'appel à l'API Consommation. Le modèle met trop de temps à répondre.")
            return


        # 3. Affichage des résultats
        if dpe_prediction is not None and conso_pred is not None:
            # Finalisation des métriques
            conso_pred = max(50, round(conso_pred, 1))
            co2_pred = round(conso_pred * CO2_FACTOR, 1) 
            
            # Affichage DPE
            fig_dpe, classe_pred = create_dpe_gauge(dpe_prediction)
            fig_conso = create_conso_gauge(conso_pred)

            st.markdown("""
                <div style='background-color:rgba(255,255,255,0.05); 
                            border:2px solid rgba(52,152,219,0.6);
                            border-radius:20px;
                            padding:25px;
                            text-align:center;
                            width:100%;
                            margin:30px auto 10px auto;
                            box-shadow:0 0 15px rgba(52,152,219,0.2);'>
                    <h3 style='color:#3498db; font-weight:800;'>Synthèse des Performances Estimées</h3>
                </div>
            """, unsafe_allow_html=True)
            
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.plotly_chart(fig_dpe, use_container_width=True)
            with col_chart2:
                st.plotly_chart(fig_conso, use_container_width=True)

            # Affichage des résultats numériques
            st.markdown(f"""
                <div style='text-align:center; color:#ecf0f1; font-size:18px; margin-top:20px;'>
                    <p><b>Classe DPE prédite :</b> <span style='color:{COLORS_DPE[max(0, min(len(COLORS_DPE)-1, dpe_prediction))]}; font-size:22px; font-weight:bold;'>{classe_pred}</span></p>
                    <p><b>Consommation estimée :</b> <span style='color:#3498db; font-size:22px; font-weight:bold;'>{conso_pred:,.1f} kWh/an</span></p>
                    <p><b>Émissions CO₂ estimées :</b> <span style='font-size:22px;'>{co2_pred} kg/an</span></p>
                </div>
            """, unsafe_allow_html=True)

            # Sauvegarde dans l'historique
            save_path = os.path.join(os.path.dirname(__file__), "..", "Data", "historique_predictions.csv")
            
            new_row = pd.DataFrame({
                "surface_habitable_logement": [surface_habitable_logement],
                "periode_construction": [periode_construction],
                "type_energie_n1": [type_energie_n1],
                "type_energie_principale_chauffage": [type_energie_principale_chauffage],
                "Classe_predite": [classe_pred],
                "qualite_isolation_murs": [qualite_isolation_murs],
                "hauteur_sous_plafond": [hauteur_sous_plafond],
                "nombre_appartement_cat": [nombre_appartement_cat], 
                "logement": [logement],
                "Conso_estimee_kWh": [conso_pred],
                "CO2_estime_kg": [co2_pred],
                "Date": [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")]
            })

            if os.path.exists(save_path):
                historique = pd.read_csv(save_path)
                historique = pd.concat([historique, new_row], ignore_index=True)
            else:
                historique = new_row

            historique.to_csv(save_path, index=False)

            # Historique des simulations 
            st.markdown("""
                <hr style='border:1px solid rgba(255,255,255,0.1); margin-top:40px;'>
                <h4 style='text-align:center; color:#f1c40f;'>Historique des simulations (10 dernières)</h4>
            """, unsafe_allow_html=True)

            st.dataframe(historique.tail(10).iloc[::-1], use_container_width=True)

    # Section informations techniques
    with st.expander("🔧 Informations techniques"):
        st.markdown("""
        **Architecture des prédictions :**
        - 🎯 **API DPE (Port 5001)** : Classification Random Forest
        - 📊 **API Consommation (Port 5000)** : Régression Linéaire
        - 🔄 **Séquence** : DPE → puis Consommation (avec DPE en feature)
        
        **Endpoints utilisés :**
        - `POST /predict_dpe` → Prédiction classe DPE
        - `POST /predict_conso` → Prédiction consommation
        - `GET /health` → Vérification statut API
        
        **Données transmises :**
        - Features brutes du formulaire → API DPE
        - Features + étiquette DPE prédite → API Consommation
        """)

# Point d'entrée pour Streamlit
if __name__ == "__main__":
    show_page()