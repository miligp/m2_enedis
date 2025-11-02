import os
import gdown

FILE_MAPPING = {
    'random_forest_dpe_final_weighted.joblib': 'https://drive.google.com/uc?id=1B41zmP2dw1UBBoWiMiKa1Brt95e2fgvR',
    'feature_columns_final.pkl': 'https://drive.google.com/uc?id=1VOTDSGpYq9JdHf8K7Q9Y9q4N9eXq9Y9X',  # ✅ AJOUT
    'lr_model.pkl': 'https://drive.google.com/uc?id=1YOUR_MODEL_ID_HERE',  # ✅ AJOUT
    'lr_imputer.pkl': 'https://drive.google.com/uc?id=1YOUR_IMPUTER_ID_HERE',  # ✅ AJOUT  
    'lr_scaler.pkl': 'https://drive.google.com/uc?id=1YOUR_SCALER_ID_HERE',  # ✅ AJOUT
}

def setup_heavy_files():
    print("🔍 Vérification des fichiers lourds...")
    
    for filename, drive_url in FILE_MAPPING.items():
        if not os.path.exists(filename):
            print(f"📥 Téléchargement de {filename}...")
            try:
                gdown.download(drive_url, filename, quiet=False)
                print(f"✅ {filename} téléchargé avec succès!")
            except Exception as e:
                print(f"❌ Erreur lors du téléchargement de {filename}: {e}")
        else:
            print(f"✅ {filename} déjà présent")
    
    print("🎯 Tous les fichiers lourds sont prêts!")