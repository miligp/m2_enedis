FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 1. Copier requirements d'abord (pour le cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copier TOUS les fichiers (y compris le modèle lourd)
COPY . .

EXPOSE 5000
EXPOSE 5001  
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]