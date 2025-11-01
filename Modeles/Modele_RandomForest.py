from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
from joblib import dump, load

# -----------------------------
# 🔧 1. Chargement des données
# -----------------------------
file_path = r'.\m2_enedis\Dataset_Model\donnees_ml_preparees.csv'
df = pd.read_csv(file_path, sep=',')
df.columns = df.columns.str.strip().str.lower()

# Colonnes à exclure pour éviter les fuites
leakage_columns = [
    "conso_5_usages_ef",
    "conso_5_usages_ef_energie_n1",
    "cout_total_5_usages",
    "cout_total_5_usages_energie_n1"
]

# Séparation X / y
X = df.drop(columns=["etiquette_dpe"] + leakage_columns)
y = df["etiquette_dpe"]

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# -----------------------------
# ✅ 2. Meilleurs hyperparamètres
# -----------------------------
# Ajout de 'class_weight': 'balanced' dans les hyperparamètres pour contrer le déséquilibre de classes.
best_params = {'n_estimators': 100, 'min_samples_split': 5, 'max_depth': None, 'class_weight': 'balanced'}

# -----------------------------
# 🔁 3. Entraînement sur 10 runs
# -----------------------------
n_runs = 10
scores = []
last_model = None  # Pour sauvegarder le dernier modèle

print("🔁 Entraînement sur 10 runs...\n")

for i in range(n_runs):
    # Utilisation des best_params mis à jour incluant class_weight='balanced'
    model = RandomForestClassifier(**best_params, random_state=i, n_jobs=-1)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    f1 = f1_score(y_test, y_pred, average='weighted')
    scores.append(f1)
    print(f"Run {i+1:2d}: F1-score = {f1:.4f}")
    last_model = model  # Sauvegarde du dernier modèle

mean_f1 = np.mean(scores)
std_f1 = np.std(scores)
print("\n✅ Moyenne des F1-scores :", round(mean_f1, 4))
print("📉 Écart-type :", round(std_f1, 4))

# -----------------------------
# 4. Évaluation du dernier modèle
# -----------------------------
y_pred_last = last_model.predict(X_test)

# Matrice de confusion
cm = confusion_matrix(y_test, y_pred_last, labels=last_model.classes_)
cm_df = pd.DataFrame(cm, index=last_model.classes_, columns=last_model.classes_)

print("\nMatrice de confusion :")
print(cm_df)

print("\nRapport de classification :")
print(classification_report(y_test, y_pred_last))

# Heatmap avec normalisation pour mieux visualiser les proportions
plt.figure(figsize=(8, 6))
sns.heatmap(cm_df, annot=True, fmt='d', cmap='Blues', linewidths=.5, cbar_kws={'label': 'Nombre d\'échantillons'})
plt.title("Matrice de confusion - Dernier run (Class Weight: Balanced)")
plt.ylabel("Vraies classes")
plt.xlabel("Prédites")
plt.show()

# -----------------------------
# 5. Sauvegarde du modèle et des colonnes
# -----------------------------
MODEL_FILE = 'random_forest_dpe_final_weighted.joblib'  # extension .joblib
COLUMNS_FILE = 'feature_columns_final.pkl'  # pas besoin de changer si pickle pour la liste ok

# Sauvegarde du modèle avec joblib
dump(last_model, MODEL_FILE)
print(f"\n✅ Modèle sauvegardé sous : {MODEL_FILE}")

# Sauvegarde des colonnes avec pickle (reste pareil)
with open(COLUMNS_FILE, 'wb') as f:
    pickle.dump(X.columns.tolist(), f)
print(f"✅ Liste des colonnes sauvegardée sous : {COLUMNS_FILE}")

print("\n✅ Script terminé, prêt pour l’API Flask.")
# 🔁 Entraînement sur 10 runs...

# Run  1: F1-score = 0.7528
# Run  2: F1-score = 0.7526
# Run  3: F1-score = 0.7524
# Run  4: F1-score = 0.7528
# Run  5: F1-score = 0.7524
# Run  6: F1-score = 0.7529
# Run  7: F1-score = 0.7533
# Run  8: F1-score = 0.7528
# Run  9: F1-score = 0.7531
# Run 10: F1-score = 0.7527

# ✅ Moyenne des F1-scores : 0.7528
# 📉 Écart-type : 0.0003

# Matrice de confusion :
#       0     1      2      3      4     5     6
# 0  4536   630    220     52      3     9     3
# 1  1429  7085    835    293     31     4     0
# 2  2877  3906  21543   3415    437    22     2
# 3  2390  4407   9302  39163   4466   550    28
# 4   387   835   3812   7341  69192  4404   427
# 5    24    10     23     39    324  9071   554
# 6     1     0      0      3      7   155  4367

# Rapport de classification :
#               precision    recall  f1-score   support

#            0       0.39      0.83      0.53      5453
#            1       0.42      0.73      0.53      9677
#            2       0.60      0.67      0.63     32202
#            3       0.78      0.65      0.71     60306
#            4       0.93      0.80      0.86     86398
#            5       0.64      0.90      0.75     10045
#            6       0.81      0.96      0.88      4533

#     accuracy                           0.74    208614
#    macro avg       0.65      0.79      0.70    208614
# weighted avg       0.78      0.74      0.75    208614


# ✅ Modèle sauvegardé sous : random_forest_dpe_final_weighted.pkl
# ✅ Liste des colonnes sauvegardée sous : feature_columns_final.pkl

# ✅ Script terminé, prêt pour l’API Flask.