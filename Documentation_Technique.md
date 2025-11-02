# 📚 Documentation Technique de l'Application : Eco Scan

## 1. 🏗️ Architecture et Composants

Cette section présente une vue d'ensemble de l'architecture de l'application. Eco Scan est une application web d'analyse et de prédiction énergétique, conteneurisée pour un déploiement fiable.

### Structure de l'Application

```bash
ml_project/
├── app.py                    # POINT D'ENTRÉE PRINCIPAL
├── requirements.txt          # DÉPENDANCES PYTHON
├── file_loader.py           # CHARGEUR DE FICHIERS
├── API_Random_Forest.py     # API MODÈLE RANDOM FOREST
├── API_Lineaire_Reg.py      # API RÉGRESSION LINÉAIRE
├── api_manager.py           # GESTIONNAIRE D'APIS UNIFIÉ
├── docker-compose.yml       # ORCHESTRATION DOCKER
├── Dockerfile               # CONFIGURATION DOCKER
├── start_app.py             # SCRIPT DE DÉMARRAGE
├── .gitignore              # EXCLUSIONS GIT
├── feature_columns_final.pkl # SCHÉMA DES FEATURES
├── lr_imputer.pkl          # IMPUTEUR VALEURS MANQUANTES
├── lr_model.pkl            # MODÈLE RÉGRESSION LINÉAIRE
├── lr_scaler.pkl           # NORMALISATEUR FEATURES
├── Data/                   # DONNÉES BRUTES ET TRAITÉES
│   ├── df_logement.parquet  # Dataset principal
│   └── df_test.parquet      # Dataset de test
├── img/                    # RESSOURCES VISUELLES
│   └── Logo.png            # Logo de l'application
├── views/                  # MODULES INTERFACE UTILISATEUR
│   ├── __init__.py         # INITIALISATION VIEWS
│   ├── prediction.py       # INTERFACE PRÉDICTIONS
│   ├── analyse.py          # STATISTIQUES DESCRIPTIVES
│   ├── apropos.py          # DESCRIPTION PROJET
│   ├── cartographic.py     # CARTE INTERACTIVE
│   └── contexte.py         # EXPLICATIONS PRÉDICTIONS
└── streamlit/              # CONFIGURATION STREAMLIT
    └── config.toml         # THÈME ET PARAMÈTRES
```

### Schéma Architecture

```bash
┌─────────────────────────────────────────────────┐
│                 UTILISATEUR                     │
└─────────────────────────┬───────────────────────┘
                          │
┌─────────────────────────▼───────────────────────┐
│              INTERFACE STREAMLIT                │
│                (app.py)                         │
└─────────────┬─────────────┬─────────────────────┘
              │             │
┌─────────────▼─────┐ ┌─────▼─────────────────────┐
│   GESTIONNAIRE    │ │     MODULES VUES          │
│      API          │ │  (prediction, analyse,    │
│ (api_manager.py)  │ │   cartographic, etc.)     │
└─────────┬─────────┘ └───────────────────────────┘
          │
    ┌─────┴─────────────────────────────────┐
    │                                       │
┌───▼───────────┐                   ┌───────▼─────────┐
│ RANDOM FOREST │                   │ RÉGRESSION      │
│   (API)       │                   │ LINÉAIRE (API)  │
└───────────────┘                   └─────────────────┘
```

## 2. 📦 Prérequis et Guide d'Installation

L'application peut être exécutée de manière isolée via une image Docker pré-construite ou à partir du code source.

### 2.1. Outils Système (Prérequis Postes)

Ces outils doivent être installés sur la machine hôte :

- **Git** : Pour le clonage du dépôt
- **Docker Desktop** : Requis pour construire l'image et lancer le conteneur

### 2.2. Packages Python (Dépendances de l'Application)

Les dépendances sont listées dans `requirements.txt` et sont gérées automatiquement par Docker lors de la construction. Elles incluent : Streamlit, scikit-learn, Pandas/NumPy et joblib/pickle.

### 2.3. Guide d'Installation Conteneurisée

#### A. 🐳 Déploiement Rapide à partir de l'Image Docker (Recommandé pour l'exécution)

Cette méthode ne nécessite pas le code source du projet.


##### 1. Télécharger l'image

```bash
docker pull miligp12/ml-project-streamlit:latest
```

##### 2. Lancer l'application

```bash
docker run -d -p 8501:8501 miligp12/ml-project-streamlit:latest
```

##### 3. Accéder à l'application

Ouvrir un navigateur web à l'adresse : http://localhost:8501

##### B. 🔧 Installation à partir du Code Source (Développement/Docker Compose)

Cette méthode permet de reconstruire l'environnement pour le développement.

#### 1. Clonage du Dépôt et Navigation

```bash
git clone https://github.com/miligp/m2_enedis.git
```
```bash
cd m2_enedis
```


#### 2. Lancement (Build & Run)

La commande suivante construit l'image et démarre le service en arrière-plan

```bash
docker-compose up --build -d
```

### 3. Accès à l'application

Ouvrir un navigateur web à l'adresse : http://localhost:8501

### Schéma de Déploiement Docker

```bash
┌─────────────────────────────────────────┐
│           MACHINE HÔTE                  │
│                                         │
│  ┌─────────────────────────────────────┐│
│  │        CONTAINER DOCKER             ││
│  │                                     ││
│  │  ┌─────────────────────────────┐    ││
│  │  │    APPLICATION ECO SCAN     │    ││
│  │  │                             │    ││
│  │  │  • Streamlit Server         │    ││
│  │  │  • Modèles ML               │    ││
│  │  │  • Données                  │    ││
│  │  │  • Dépendances Python       │    ││
│  │  └─────────────────────────────┘    ││
│  │                                     ││
│  │  Port Mapping: 8501:8501           ││
│  └─────────────────────────────────────┘│
│                                         │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│        NAVIGATEUR WEB                   │
│      http://localhost:8501              │
└─────────────────────────────────────────┘
```

## 3. 🌐 Accès Public (Streamlit Cloud)
### C. 🚀 Déploiement Cloud Public

L'application est également déployée publiquement et accessible sans installation :

URL Streamlit Cloud :
https://m2enedis-u6bk7ax22n5cevhr2y9chf.streamlit.app/