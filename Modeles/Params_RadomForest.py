import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
import numpy as np


# 1. Lecture et nettoyage CSV
df = pd.read_csv(r'.\m2_enedis\Dataset_Model\donnees_ml_preparees.csv', sep=',')
df.columns = df.columns.str.strip().str.lower()

y = df['etiquette_dpe']
X = df.drop(columns=['etiquette_dpe'])


# 2. Split train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)


# 3. Sous-échantillon stratifié pour RandomizedSearchCV
sample_size = 50000  # sous-échantillon pour limiter temps et mémoire car trop lourd

# On utilise train_test_split pour faire un échantillon stratifié
X_train_sample, _, y_train_sample, _ = train_test_split(
    X_train,
    y_train,
    train_size=sample_size,
    stratify=y_train,
    random_state=42
)


# 4. Définir le modèle et la grille
rf_clf = RandomForestClassifier(random_state=42)

param_grid = {
    'n_estimators': [100, 150, 200],
    'max_depth': [5, 10, None],
    'min_samples_split': [2, 5, 10]
}

# 5. RandomizedSearchCV réaliste
random_search = RandomizedSearchCV(
    estimator=rf_clf,
    param_distributions=param_grid,
    n_iter=5,                
    scoring='f1_weighted',
    cv=4,                    # moins de folds pour gagner du temps
    n_jobs=1,                # limiter la mémoire
    random_state=42,
    verbose=1
)

random_search.fit(X_train_sample, y_train_sample)

best_model = random_search.best_estimator_
best_params = random_search.best_params_
best_score = random_search.best_score_

print("Meilleurs paramètres :", best_params)
print("Score CV (sur échantillon) :", best_score)


# 6. Évaluer sur le test complet
y_pred = best_model.predict(X_test)
f1 = f1_score(y_test, y_pred, average='weighted')
print("F1-score test :", f1)


# 7. Importance des variables
feature_importances = pd.DataFrame(
    best_model.feature_importances_,
    index=X_train.columns,
    columns=['importance']
).sort_values(by='importance', ascending=False)

print("Top 10 variables les plus importantes :")
print(feature_importances.head(10))


# Fitting 4 folds for each of 5 candidates, totalling 20 fits
# Meilleurs paramètres : {'n_estimators': 100, 'min_samples_split': 5, 'max_depth': None}
# Score CV (sur échantillon) : 0.9274903301686294
# F1-score test : 0.9391319364401612
# Top 10 variables les plus importantes :
#                                 importance
# surface_habitable_logement        0.293281
# conso_5_usages_ef                 0.139925
# conso_5_usages_ef_energie_n1      0.130542
# cout_total_5_usages               0.115087
# cout_total_5_usages_energie_n1    0.113221
# qualite_isolation_murs            0.060687
# nombre_appartement_cat            0.022642
# hauteur_sous_plafond              0.022630
# logement_neuf                     0.022483
# type_energie_n1_gaz naturel       0.017938