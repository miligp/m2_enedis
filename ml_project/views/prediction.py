import streamlit as st
import pandas as pd
import numpy as np
import os
import base64
import plotly.graph_objects as go
import requests
import json
import time

# --- CONFIGURATION DES APIs ---
API_URL_DPE = "http://127.0.0.1:5001/predict_dpe"
API_URL_CONSO = "http://127.0.0.1:5000/predict_conso"
API_HEALTH_DPE = "http://127.0.0.1:5001/health"
API_HEALTH_CONSO = "http://127.0.0.1:5000/health"

# Mappings DPE
CLASSES_DPE_MAPPING = ["G", "F", "E", "D", "C", "B", "A"]
COLORS_DPE = ["#c0392b", "#8e44ad", "#e74c3c", "#e67e22", "#f1c40f", "#27ae60", "#2ecc71"]
CO2_FACTOR = 0.25

def check_api_health():
    """Vérifie si les APIs sont disponibles"""
    status = {'dpe': False, 'conso': False}
    
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
    """Crée la jauge Plotly pour la classe DPE"""
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

def show_page():
    # Logo et en-tête
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

    # Message d'erreur si APIs non disponibles
    if not api_status['conso'] or not api_status['dpe']:
        st.error("""
        ❌ **Les APIs ne sont pas disponibles**
        
        **Pour résoudre le problème :**
        
        1. **Ouvrez deux terminaux et démarrez les APIs :**
        ```bash
        # Terminal 1 - API Consommation (Port 5000)
        python API_Lineaire_Reg.py
        
        # Terminal 2 - API DPE (Port 5001)  
        python API_Random_Forest.py
        ```
        
        2. **Attendez les messages de confirmation :**
        - "Modele de Regression Lineaire charge avec succes sur le port 5000."
        - "Modele DPE (Classification) charge avec succes."
        
        3. **Actualisez cette page**
        """)
        
        if st.button("🔄 Vérifier à nouveau le statut"):
            st.rerun()
        return

    # --- FORMULAIRE UNIQUE ---
    st.markdown("<h3 style='color:#f1c40f; text-align:center;'>Caractéristiques du logement</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        surface_habitable_logement = st.number_input("Surface habitable (m²) :", min_value=10, max_value=500, value=80, step=5)
        periode_construction = st.selectbox("Période de construction :", [
            "avant 1948", "1948-1974", "1975-1977", "1978-1982", "1983-1988", 
            "1989-2000", "2001-2005", "2006-2012", "2013-2021", "après 2021"
        ])
        hauteur_sous_plafond = st.number_input("Hauteur sous plafond (m) :", min_value=2.0, max_value=5.0, value=2.5, step=0.1)
        nombre_appartement_cat = st.selectbox("Type de bâtiment :", [
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
        logement = st.selectbox("Âge du bâtiment :", ["Neuf", "Ancien"])
        
    # UN SEUL BOUTON DE PRÉDICTION
    st.markdown("<div style='text-align:center; margin-top:30px;'>", unsafe_allow_html=True)
    predict_button = st.button("🚀 Lancer la prédiction complète", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- DOUBLE PRÉDICTION AUTOMATIQUE ---
    if predict_button:
        
        # Préparation des données pour l'API DPE
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

        # Container pour les résultats
        results_container = st.container()
        
        # 1. PRÉDICTION DPE
        dpe_prediction = None
        classe_dpe = None
        
        try:
            with st.spinner("🔮 Étape 1/2 : Calcul de la classe DPE..."):
                response_dpe = requests.post(API_URL_DPE, json=data_initial, timeout=30)
                
                if response_dpe.status_code == 200:
                    dpe_result = response_dpe.json()
                    dpe_prediction = dpe_result.get("prediction_DPE_index")
                    
                    if dpe_prediction is not None:
                        classe_dpe = CLASSES_DPE_MAPPING[dpe_prediction]
                        st.success(f"✅ Classe DPE déterminée : **{classe_dpe}**")
                    else:
                        st.error("❌ Erreur : Clé 'prediction_DPE_index' manquante dans la réponse")
                        return
                else:
                    st.error(f"❌ Erreur API DPE ({response_dpe.status_code}): {response_dpe.text}")
                    return
                    
        except requests.exceptions.ConnectionError:
            st.error("❌ Impossible de se connecter à l'API DPE sur le port 5001")
            return
        except requests.exceptions.Timeout:
            st.error("⏰ Timeout de l'API DPE")
            return
        except Exception as e:
            st.error(f"❌ Erreur inattendue API DPE: {e}")
            return

        # 2. PRÉDICTION CONSOMMATION (avec étiquette DPE)
        data_for_conso = data_initial.copy()
        data_for_conso['etiquette_dpe'] = dpe_prediction

        conso_pred = None
        
        try:
            with st.spinner("💡 Étape 2/2 : Estimation de la consommation énergétique..."):
                response_conso = requests.post(API_URL_CONSO, json=data_for_conso, timeout=30)
                
                if response_conso.status_code == 200:
                    conso_result = response_conso.json()
                    conso_pred = conso_result.get("conso_predite_kwh")
                    
                    if conso_pred is not None:
                        st.success("✅ Consommation énergétique estimée avec succès!")
                    else:
                        st.error("❌ Erreur : Clé 'conso_predite_kwh' manquante dans la réponse")
                        return
                else:
                    st.error(f"❌ Erreur API Consommation ({response_conso.status_code}): {response_conso.text}")
                    return
                    
        except requests.exceptions.ConnectionError:
            st.error("❌ Impossible de se connecter à l'API Consommation sur le port 5000")
            return
        except requests.exceptions.Timeout:
            st.error("⏰ Timeout de l'API Consommation")
            return
        except Exception as e:
            st.error(f"❌ Erreur inattendue API Consommation: {e}")
            return

        # 3. AFFICHAGE DES RÉSULTATS COMPLETS
        if dpe_prediction is not None and conso_pred is not None:
            conso_pred = max(50, round(conso_pred, 1))
            co2_pred = round(conso_pred * CO2_FACTOR, 1)
            
            with results_container:
                st.markdown("---")
                st.markdown("<h2 style='text-align:center; color:#2ecc71;'>📊 Résultats de la Prédiction</h2>", unsafe_allow_html=True)
                
                # Jaunes côte à côte
                fig_dpe, classe_pred = create_dpe_gauge(dpe_prediction)
                fig_conso = create_conso_gauge(conso_pred)

                col_chart1, col_chart2 = st.columns(2)
                with col_chart1:
                    st.plotly_chart(fig_dpe, use_container_width=True)
                with col_chart2:
                    st.plotly_chart(fig_conso, use_container_width=True)

                # Métriques détaillées
                st.markdown("### 📈 Détails des performances")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        label="**Classe DPE**",
                        value=classe_dpe,
                        delta="Performance énergétique"
                    )
                with col2:
                    st.metric(
                        label="**Consommation annuelle**", 
                        value=f"{conso_pred:,.0f} kWh",
                        delta="Énergie estimée"
                    )
                with col3:
                    st.metric(
                        label="**Émissions CO₂**",
                        value=f"{co2_pred:,.0f} kg", 
                        delta="Impact environnemental"
                    )

                # Coût estimé
                prix_kwh = 0.18  # €/kWh moyen
                cout_annuel = conso_pred * prix_kwh
                
                st.info(f"""
                **💶 Coût énergétique estimé :** {cout_annuel:,.0f} €/an
                *Basé sur un prix moyen de {prix_kwh} €/kWh*
                """)

                # Sauvegarde historique
                save_path = os.path.join(os.path.dirname(__file__), "..", "Data", "historique_predictions.csv")
                
                new_row = pd.DataFrame({
                    "surface_habitable_logement": [surface_habitable_logement],
                    "periode_construction": [periode_construction],
                    "type_energie_n1": [type_energie_n1],
                    "type_energie_principale_chauffage": [type_energie_principale_chauffage],
                    "Classe_predite": [classe_dpe],
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
                st.markdown("### 📋 Historique des simulations")
                st.dataframe(historique.tail(5).iloc[::-1], use_container_width=True)

if __name__ == "__main__":
    show_page()