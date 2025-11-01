from flask import Flask, request, jsonify
import pickle
import pandas as pd
from joblib import load
import os 
import pathlib 
import requests 

# -----------------------------
# CONFIGURATION DES FICHIERS
# -----------------------------

app_dpe = Flask(__name__)

# 1. DÉTERMINER LE RÉPERTOIRE ACTUEL ET LES CHEMINS LOCAUX
CURRENT_DIR = pathlib.Path(__file__).parent 

# Le modèle lourd sera téléchargé à cet emplacement
MODEL_FILE_LOCAL = CURRENT_DIR / 'random_forest_dpe_final_weighted.joblib'
# Le fichier de colonnes est supposé être dans le dépôt Git (petit fichier)
COLUMNS_FILE_LOCAL = CURRENT_DIR / 'feature_columns_final.pkl' 

# Récupération de l'URL du modèle lourd (variable d'environnement obligatoire)
# Le lien vers le fichier .pkl n'est plus nécessaire car il est dans Git
MODEL_URL = os.environ.get("https://drive.google.com/drive/folders/1kvCQkLbgWnHg0z8hWe3_KYSqHrFoU3qY?usp=sharing") 

model = None
FEATURE_COLUMNS = []

# --- FONCTION DE TÉLÉCHARGEMENT (Télécharge uniquement le gros fichier) ---
def download_file(url, local_path):
    """Télécharge un fichier depuis une URL et l'enregistre localement."""
    if not url:
        print(f"ERREUR: La variable d'environnement MODEL_DOWNLOAD_URL est vide.")
        return False
        
    print(f"Tentative de téléchargement de {local_path.name} depuis le Drive...")
    
    try:
        # Utilisation de requests pour récupérer le fichier
        # Timeout étendu à 5 minutes (300 secondes) pour les gros fichiers
        r = requests.get(url, stream=True, timeout=300) 
        r.raise_for_status() # Lève une exception pour les erreurs HTTP (4xx ou 5xx)

        # Écriture du fichier sur le système de fichiers temporaire du conteneur
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Téléchargement terminé pour {local_path.name}.")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"ERREUR LORS DU TÉLÉCHARGEMENT du modèle: {e}")
        print("Vérifiez l'URL de téléchargement direct de Google Drive et les permissions.")
        return False
    except Exception as e:
        print(f"ERREUR inattendue: {e}")
        return False


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
    
    # 1. TÉLÉCHARGEMENT DU MODÈLE LOURD (le Joblib)
    # On utilise MODEL_FILE_LOCAL comme chemin de destination
    model_downloaded = download_file(MODEL_URL, MODEL_FILE_LOCAL)
    
    if not model_downloaded:
        print("Échec du téléchargement du modèle. Le service sera indisponible.")
        model = None
        return

    try:
        # 2. CHARGEMENT DU MODÈLE (téléchargé localement dans le conteneur)
        model = load(MODEL_FILE_LOCAL)
        
        # 3. CHARGEMENT DES COLONNES (disponible dans le conteneur car inclus dans Git)
        with open(COLUMNS_FILE_LOCAL, 'rb') as f:
            FEATURE_COLUMNS = pickle.load(f)
        
        print("Modèle DPE et colonnes chargés avec succès.")

    except FileNotFoundError as e:
        print(f"ERREUR FATALE: Fichier local non trouvé (modèle téléchargé ou colonnes .pkl): {e}.")
        model = None
    except Exception as e:
        print(f"ERREUR FATALE DPE lors du chargement: {e}")
        model = None

# Lancement du chargement au démarrage de l'application
load_dpe() 


@app_dpe.route('/predict_dpe', methods=['POST'])
def predict_dpe():
    
    if model is None:
        # Le modèle n'a pas pu être chargé ou téléchargé au démarrage
        return jsonify({"error": "Modèle DPE non chargé ou non disponible. (Code 503)"}), 503
    
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Format JSON invalide ou manquant."}), 400

    try:
        input_df = pd.DataFrame([data])
        df_processed = input_df.copy()
        
        # 2. PRÉ-TRAITEMENT MANUEL
        
        # A. Encodage Ordinal
        for col, categories in ORDINAL_CATEGORIES.items():
            mapping = {category: i for i, category in enumerate(categories)}
            df_processed[col] = df_processed[col].map(mapping).fillna(-1) 
        
        # B. Encodage One-Hot
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
    # Ceci est utilisé uniquement pour les tests locaux (non en production via gunicorn)
    # Assurez-vous d'avoir les fichiers localement pour ce test.
    app_dpe.run(host='0.0.0.0', port=5001, debug=True)
