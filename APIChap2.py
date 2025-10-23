import requests
import pandas as pd
import time

# URL de l'API ADEME
base_url = "https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/lines"

# Charger ton CSV et extraire les codes postaux uniques
df_local = pd.read_csv("adresses-69.csv", sep=";", low_memory=False)
liste_cp = df_local["code_postal"].drop_duplicates().tolist()

# Liste des années (2000 → 2025)
annees = list(range(2021, 2025))

# Résultats cumulés
all_results = []

# Fonction pour récupérer les données avec pagination
def fetch_dpe(cp, annee, size=1000):
    results = []
    page = 1
    while True:
        date_debut = f"{annee}-01-01"
        date_fin = f"{annee}-12-31"

        params = {
            "page": page,
            "size": size,
            "select": "numero_dpe,date_reception_dpe,code_postal_ban,etiquette_dpe",
            "q": str(cp),
            "q_fields": "code_postal_ban",
            "qs": f"date_reception_dpe:[{date_debut} TO {date_fin}]"
        }

        try:
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            content = response.json()
        except requests.exceptions.Timeout:
            print(f"⏳ Timeout pour CP {cp}, année {annee}, page {page}")
            break
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Erreur requête : {e}")
            break

        if "results" not in content or not content["results"]:
            break

        # Ajouter infos CP + année
        for r in content["results"]:
            r["code_postal_source"] = cp
            r["annee"] = annee
        results.extend(content["results"])

        # Vérifier si on doit continuer (pagination)
        if page * size >= content.get("total", 0):
            break
        page += 1
        time.sleep(0.2)  # attendre un peu pour respecter quota

    return results


# Boucles principales
for cp in liste_cp[:10]:  # ⚠️ limite à 5 CP pour tester
    for annee in annees:
        print(f"📌 Traitement CP {cp}, année {annee} ...")
        data = fetch_dpe(cp, annee)
        all_results.extend(data)
        time.sleep(0.2)  # pause entre chaque appel

# Conversion en DataFrame
df_api = pd.DataFrame(all_results)

print("✅ Nombre total de lignes récupérées :", len(df_api))
print(df_api.head())

