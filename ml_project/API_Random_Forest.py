from flask import Flask, request, jsonify
import pickle
import pandas as pd
import numpy as np 
from joblib import load
import os 
import pathlib 
from file_loader import setup_heavy_files

# -----------------------------
# CONFIGURATION DES FICHIERS
# -----------------------------

setup_heavy_files()

app_dpe = Flask(__name__)

# 1. DÉTERMINER LE RÉPERTOIRE ACTUEL DU FICHIER API
CURRENT_DIR = pathlib.Path(__file__).parent 

# 2. DÉFINIR LE RÉPERTOIRE CONTENANT LES MODÈLES
# 🚨 CORRECTION DÉFINITIVE : Si l'API et le modèle sont dans le même dossier,
# le répertoire des modèles est le répertoire courant du script.
MODELS_DIR = CURRENT_DIR 


# Les chemins absolus des fichiers de modèles
MODEL_FILE = MODELS_DIR / 'random_forest_dpe_final_weighted.joblib'
COLUMNS_FILE = MODELS_DIR / 'feature_columns_final.pkl'

model = None
FEATURE_COLUMNS = []

# --- DÉFINITION DU PRÉ-TRAITEMENT (CRITIQUE) ---

ORDINAL_CATEGORIES = {
    # L'ordre est CRITIQUE : 0 pour Insuffisante, 3 pour très bonne
    'qualite_isolation_murs': ['Insuffisante', 'Moyenne', 'bonne', 'très bonne'], 
    'nombre_appartement_cat': [
        'Maison(Unitaire ou 2 à 3 logements)',
        'Petit Collectif(4 à 9 logements)',
        'Moyen Collectif(10 à 30 logements)',
        'Grand Collectif(> 30 logements)'
    ]
}

def load_dpe():
    global model, FEATURE_COLUMNS
    try:
        # 1. Charger le modèle et la liste des colonnes
        model = load(MODEL_FILE)
        with open(COLUMNS_FILE, 'rb') as f:
            FEATURE_COLUMNS = pickle.load(f)
        
        print("Modèle DPE (Classification) chargé avec succès.")

    except FileNotFoundError as e:
        print(f"ERREUR FATALE: Fichier non trouvé lors du chargement: {e}. Le modèle ne sera pas disponible.")
        # Le modèle est mis à None si le chargement échoue.
        model = None
    except Exception as e:
        print(f"ERREUR FATALE DPE : {e}")
        model = None

load_dpe() 


@app_dpe.route('/predict_dpe', methods=['POST'])
def predict_dpe():
    if model is None:
        return jsonify({"error": "Modèle DPE non chargé ou non disponible."}), 503
    
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Format JSON invalide ou manquant."}), 400

    try:
        input_df = pd.DataFrame([data])
        df_processed = input_df.copy()
        
        # 2. PRÉ-TRAITEMENT MANUEL (Reproduire l'ordre et les étapes du Notebook)
        
        # A. Encodage Ordinal
        for col, categories in ORDINAL_CATEGORIES.items():
            # Remplace les valeurs catégorielles par leur index (0, 1, 2, ...)
            mapping = {category: i for i, category in enumerate(categories)}
            df_processed[col] = df_processed[col].map(mapping).fillna(-1) 
        
        # B. Encodage One-Hot des autres variables (Ex: periode_construction)
        # Note : pandas.get_dummies() est simple mais peut créer des problèmes de colonnes manquantes
        df_processed = pd.get_dummies(df_processed, drop_first=False) 
        
        # 3. Création de la matrice finale pour le modèle
        X_final = pd.DataFrame(0, index=[0], columns=FEATURE_COLUMNS)

        # Remplissage de la ligne finale avec les colonnes traitées et alignées
        for col in df_processed.columns:
            if col in X_final.columns:
                X_final.loc[0, col] = df_processed.loc[0, col]
        
        # 4. Prédiction
        prediction_numpy = model.predict(X_final)[0]
        prediction_DPE = int(prediction_numpy) 

        # 5. Renvoyer le résultat
        return jsonify({
            "prediction_DPE_index": prediction_DPE 
        }), 200

    except Exception as e:

        print(f"Erreur interne lors du pré-traitement : {str(e)}")
        return jsonify({f"Erreur lors de la prédiction : {str(e)}"}), 500


if __name__ == '__main__':
    # Lancez cette API sur le port 5001
    app_dpe.run(host='0.0.0.0', port=5001, debug=False)
