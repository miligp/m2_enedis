from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np
import os
import pathlib



# Variables numériques à standardiser
Variable_Standardisee = ['hauteur_sous_plafond', 'surface_habitable_logement']

# Variables OHE/booléennes (celles qui sont 0/1 ou encodées)
Data_OHE_Boolean = [
    'qualite_isolation_murs', 'etiquette_dpe', 'periode_construction', 'nombre_appartement_cat', 'type_batiment_immeuble', 
    'type_batiment_maison', 'type_energie_principale_chauffage_Charbon', 'type_energie_principale_chauffage_Fioul', 
    'type_energie_principale_chauffage_Gaz (GPL/Propane/Butane)', 'type_energie_principale_chauffage_Gaz naturel', 
    'type_energie_principale_chauffage_Réseau de chauffage urbain', 'type_energie_principale_chauffage_Électricité', 
    'type_energie_n1_Charbon', 'type_energie_n1_Fioul', 'type_energie_n1_Gaz (GPL/Propane/Butane)', 
    'type_energie_n1_Gaz naturel', 'type_energie_n1_Réseau de chauffage urbain', 'type_energie_n1_Électricité', 'logement_neuf'
]

All_Data = Variable_Standardisee + Data_OHE_Boolean

Qualite_Isolation_Mapping = {
    'Insuffisante': 0,
    'Moyenne': 1,
    'bonne': 2,
    'très bonne': 3
}

Periode_Construction_Mapping = {
    "avant 1948": 0, "1948-1974": 1, "1975-1977": 2, "1978-1982": 3, 
    "1983-1988": 4, "1989-2000": 5, "2001-2005": 6, "2006-2012": 7, 
    "2013-2021": 8, "après 2021": 9
}

Nombre_App_Mapping = {
    "Maison(Unitaire ou 2 à 3 logements)": 0,
    "Petit Collectif(4 à 9 logements)": 1, 
    "Moyen Collectif(10 à 30 logements)": 2, 
    "Grand Collectif(> 30 logements)": 3
}

# Le reste des variables (énergie, type de bâtiment, logement) doit être traité comme OHE/Booléen (0/1)

# ----------------------------------------------------
# 2. INITIALISATION ET CHARGEMENT DES ASSETS
# ----------------------------------------------------

app = Flask(__name__)

# Définition des chemins absolus (Méthode robuste avec pathlib)
Current_DIR = pathlib.Path(__file__).parent
Model_PATH = Current_DIR / 'lr_model.pkl'
Imput_PATH = Current_DIR / 'lr_imputer.pkl'
Scaler_PATH = Current_DIR / 'lr_scaler.pkl'

lr_model = None
lr_imputer = None
lr_scaler = None

def Verif_Chemin():
    global lr_model, lr_imputer, lr_scaler
    try:
        lr_model = joblib.load(Model_PATH)
        lr_imputer = joblib.load(Imput_PATH)
        lr_scaler = joblib.load(Scaler_PATH)
        print("Modèle de Régression Linéaire chargé avec succès sur le port 5000.")
    except Exception as e:
        print(f"ERREUR FATALE: Échec du chargement des assets (port 5000). Vérifiez les fichiers .pkl. Erreur: {e}")
        # On force les assets à None pour un contrôle dans la route
        lr_model = None
        lr_imputer = None
        lr_scaler = None

Verif_Chemin()

# ----------------------------------------------------
# 3. ROUTE DE PRÉDICTION (/predict_conso)
# ----------------------------------------------------

@app.route('/predict_conso', methods=['POST'])
def predict_conso():
    
    if lr_model is None:
        return jsonify({"error": "Modèle de Consommation non chargé ou indisponible."}), 503

    try:
        data_brute = request.get_json(force=True)
    except:
        return jsonify({"error": "Format JSON invalide ou manquant dans la requête.(donnée du questionnaire n'ont pas été chargé.)"}), 400

    # --- ÉTAPE 1 : PRÉPARATION ET CONVERSION  ---
    
    # Créer un dictionnaire 
    data_dico = {} 

    # Assurez-vous que toutes les features attendues sont dans le JSON, sinon on met 0 par défaut
    for feature in All_Data :
        data_dico[feature] = 0 

    # 1. Mise à jour des valeurs numériques/brutes
    data_dico['hauteur_sous_plafond'] = data_brute.get('hauteur_sous_plafond', 0)
    data_dico['surface_habitable_logement'] = data_brute.get('surface_habitable_logement', 0)

    # 2. Conversion des chaînes en indices numériques 
    try:
        data_dico['qualite_isolation_murs'] = Qualite_Isolation_Mapping[data_brute['qualite_isolation_murs']]
        data_dico['periode_construction'] = Periode_Construction_Mapping[data_brute['periode_construction']]
        data_dico['nombre_appartement_cat'] = Nombre_App_Mapping[data_brute['nombre_appartement_cat']]
        
        # 3. Ajout de l'étiquette DPE PRÉDITE (reçue de l'API 5001)
        # Ceci est la clé du flux séquentiel
        data_dico['etiquette_dpe'] = data_brute['etiquette_dpe'] 

    except KeyError as e:
        # Erreur si une catégorie n'est pas reconnue
        return jsonify({"Vérifiez la cohérence des chaînes de caractères."}), 500
    
    # 4. Conversion des OHE/Booléennes (logement, type_batiment, énergie)
    
    # Logement (Neuf/Ancien)
    if data_brute.get('logement') == 'Neuf':
        data_dico['logement_neuf'] = 1

    # Énergie (Même logique pour l'API de Régression que pour la DPE)
    energie_chauffage = data_brute.get('type_energie_principale_chauffage', '').strip()
    energie_n1 = data_brute.get('type_energie_n1', '').strip()

    if energie_chauffage:
        key = f'type_energie_principale_chauffage_{energie_chauffage}'.replace(' ', '_')
        if key in data_dico:
             data_dico[key] = 1

    if energie_n1:
        key = f'type_energie_n1_{energie_n1}'.replace(' ', '_')
        if key in data_dico:
             data_dico[key] = 1


    # --- ÉTAPE 2 : PRÉ-TRAITEMENT SCALARISATION (Manuel) ---

    df_input = pd.DataFrame([data_dico])

    try:
        X_standard_input = df_input[Variable_Standardisee]
        X_passthrough_input = df_input[Data_OHE_Boolean ]

        # Imputation 
        X_imputed = lr_imputer.transform(X_standard_input)

        # Standardisation 
        X_scaled = lr_scaler.transform(X_imputed)

        # Reconstruction de la matrice finale 
        X_final_matrix = np.hstack((X_scaled, X_passthrough_input.values))

        # --- ÉTAPE 3 : PRÉDICTION ---
        prediction_brute = lr_model.predict(X_final_matrix)[0]
        prediction_finale = max(0, prediction_brute)

        return jsonify({
            "conso_predite_kwh": float(f"{prediction_finale:.2f}")
        }), 200

    except Exception as e:
        # Erreur lors du pré-traitement scikit-learn ou de la prédiction
        print(f"Erreur scikit-learn/prédiction : {str(e)}")
        # Vous pouvez décommenter pour voir la matrice finale
        # print("Matrice finale envoyée au modèle:", X_final_matrix) 
        return jsonify({"error": f"Erreur interne lors de la prédiction : {str(e)}"}), 500


# ----------------------------------------------------
# 4. EXÉCUTION
# ----------------------------------------------------

if __name__ == '__main__':
    # Lancez cette API sur le port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)