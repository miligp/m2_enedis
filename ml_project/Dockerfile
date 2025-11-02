
FROM python:3.11-slim

WORKDIR /app

# Copier les fichiers essentiels
COPY requirements.txt .
COPY app.py .
COPY file_loader.py .
COPY api_manager.py .
COPY start_app.py .
COPY lr_imputer.pkl .
COPY lr_model.pkl .
COPY lr_scaler.pkl .
COPY feature_columns_final.pkl .

# Copier les APIs
COPY API_Lineaire_Reg.py .
COPY API_Random_Forest.py .

# Copier les views
COPY views/ ./views/

#Copier les datas
COPY Data/ ./Data/

# Copier les images
COPY img/ ./img/

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Créer les dossiers nécessaires
RUN mkdir -p Data models

# Exposer les ports
EXPOSE 8501 5000 5001

# Commande de démarrage
CMD ["python", "start_app.py"]