import os
import gdown

FILE_MAPPING = {
    'random_forest_dpe_final_weighted.joblib': 'https://drive.google.com/uc?id=1B41zmP2dw1UBBoWiMiKa1Brt95e2fgvR'
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