from flask import Flask, request, jsonify
import pickle
import pandas as pd
import numpy as np 
from joblib import load
import os 
import pathlib 
from file_loader import setup_heavy_files

print("Initialisation de l'API DPE...")

setup_heavy_files()

app_dpe = Flask(__name__)

# 1. DÉTERMINER LE RÉPERTOIRE ACTUEL DU FICHIER API
CURRENT_DIR = pathlib.Path(__file__).parent 

# 2. DÉFINIR LE RÉPERTOIRE CONTENANT LES MODÈLES
MODELS_DIR = CURRENT_DIR 

# Les chemins absolus des fichiers de modèles
MODEL_FILE = MODELS_DIR / 'random_forest_dpe_final_weighted.joblib'
COLUMNS_FILE = MODELS_DIR / 'feature_columns_final.pkl'

model = None
FEATURE_COLUMNS = []

# --- DÉFINITION DU PRÉ-TRAITEMENT (CRITIQUE) ---

ORDINAL_CATEGORIES = {
    'qualite_isolation_murs': ['Insuffisante', 'Moyenne', 'bonne', 'tres bonne'], 
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
        print("Chargement du modele DPE...")
        # 1. Charger le modèle et la liste des colonnes
        model = load(MODEL_FILE)
        print("Modele DPE charge")
        
        with open(COLUMNS_FILE, 'rb') as f:
            FEATURE_COLUMNS = pickle.load(f)
        print("Features columns chargees")
        
        print("Modele DPE (Classification) charge avec succes.")

    except FileNotFoundError as e:
        print(f"ERREUR FATALE: Fichier non trouve lors du chargement: {e}")
        model = None
    except Exception as e:
        print(f"ERREUR FATALE DPE : {e}")
        model = None

print("Demarrage du chargement du modele DPE...")
load_dpe() 

@app_dpe.route('/predict_dpe', methods=['POST'])
def predict_dpe():
    if model is None:
        return jsonify({"error": "Modele DPE non charge ou non disponible."}), 503
    
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Format JSON invalide ou manquant."}), 400

    try:
        input_df = pd.DataFrame([data])
        df_processed = input_df.copy()
        
        # 2. PRÉ-TRAITEMENT MANUEL
        for col, categories in ORDINAL_CATEGORIES.items():
            mapping = {category: i for i, category in enumerate(categories)}
            df_processed[col] = df_processed[col].map(mapping).fillna(-1) 
        
        df_processed = pd.get_dummies(df_processed, drop_first=False) 
        
        # 3. Création de la matrice finale pour le modèle
        X_final = pd.DataFrame(0, index=[0], columns=FEATURE_COLUMNS)

        for col in df_processed.columns:
            if col in X_final.columns:
                X_final.loc[0, col] = df_processed.loc[0, col]
        
        # 4. Prédiction
        prediction_numpy = model.predict(X_final)[0]
        prediction_DPE = int(prediction_numpy) 

        return jsonify({
            "prediction_DPE_index": prediction_DPE 
        }), 200

    except Exception as e:
        print(f"Erreur interne lors du pre-traitement : {str(e)}")
        return jsonify({f"Erreur lors de la prediction : {str(e)}"}), 500

# Ajouter une route de santé pour vérifier que l'API est prête
@app_dpe.route('/health', methods=['GET'])
def health_check():
    if model is None:
        return jsonify({"status": "not ready", "model_loaded": False}), 503
    return jsonify({"status": "ready", "model_loaded": True}), 200

@app_dpe.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "API de Prediction DPE",
        "status": "running",
        "port": 5001
    }), 200

if __name__ == '__main__':
    print("Lancement de l'API DPE sur le port 5001...")
    app_dpe.run(host='0.0.0.0', port=5001, debug=False)