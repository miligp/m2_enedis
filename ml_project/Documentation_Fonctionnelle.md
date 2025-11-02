# 🧩 Documentation fonctionnelle — Application **EcoScan Dashboard**

---

## 🌍 Contexte général du projet

**EcoScan Dashboard** est une application interactive de **visualisation, d’analyse et de prédiction énergétique** développée dans le cadre du module *Machine Learning* du Master **SISE – Université Lumière Lyon 2**.  

Conçue comme un outil d’aide à la décision, elle permet de **comprendre les performances énergétiques des logements français** et de **relier la consommation, le coût et la classe DPE** à des facteurs concrets comme la surface, l’année de construction ou le type d’énergie.  

L’objectif du projet n’était pas seulement de représenter des données, mais de **rendre ces informations parlantes**, accessibles et interactives, afin d’accompagner la réflexion autour de la transition énergétique.

---

## 🏠 Page 1 — Contexte

Cette première page pose les bases du projet en présentant la problématique énergétique et le cadre d’analyse.  
Elle offre une **vue d’ensemble claire du dataset**, tout en permettant à l’utilisateur de situer la portée et les limites des données.  

L’approche retenue favorise un **équilibre entre performance et représentativité** : les données sont échantillonnées pour garantir une expérience fluide, tout en conservant la diversité des profils énergétiques.  

La page contextualise le tableau de bord et introduit la **structure des données étudiées**.  
L’utilisateur peut également accéder au dataset complet pour explorer les informations brutes et mieux comprendre la nature du jeu de données utilisé.  

> Cette introduction sert de point d’entrée analytique, préparant le lecteur à interpréter les résultats visibles dans les pages suivantes.

---

## 📊 Page 2 — Analyse descriptive

Cette section constitue le **cœur analytique** du tableau de bord.  
Elle présente une série de visualisations permettant de **comprendre les tendances énergétiques générales** et de repérer les comportements caractéristiques du parc immobilier français.  

Les graphiques permettent d’explorer la **répartition des surfaces**, la **consommation énergétique**, le **coût du chauffage** et les **émissions de CO₂**, tout en mettant en lumière les **liens entre ces différentes variables**.  

Des filtres interactifs donnent la possibilité de se concentrer sur certaines catégories de logements (par exemple, ceux classés dans les catégories énergétiques les plus faibles) et d’observer leurs spécificités.  

Cette page ne se limite pas à montrer des chiffres : elle **raconte la réalité énergétique** à travers des graphiques clairs, des relations visibles et une approche progressive qui guide l’analyse.  
C’est également ici que nous avons **identifié les variables les plus pertinentes** pour entraîner nos modèles de prédiction dans la page suivante.

---

## 🗺️ Page 3 — Cartographie

La page de cartographie ajoute une **dimension spatiale essentielle** à la compréhension du DPE.  
Elle permet de **visualiser la répartition des logements sur le territoire** à travers une carte interactive.  

Chaque point coloré représente un logement, et les filtres permettent de sélectionner selon la **classe énergétique** ou la **période de construction**.  
Ainsi, l’utilisateur peut repérer en un coup d’œil les **zones à forte concentration de passoires énergétiques** et observer comment les caractéristiques régionales influencent la performance énergétique.  

> Le chargement peut être légèrement plus long à cause du volume de données, mais cette exhaustivité garantit une représentation fidèle et utile du territoire.

Cette page relie directement la donnée à l’espace, confirmant que la géographie est un facteur majeur de variation énergétique en France.

---

## 🤖 Page 4 — Prédiction

Cette page met en avant la partie **intelligente et dynamique** du projet.  
L’utilisateur peut saisir les caractéristiques d’un logement pour **simuler sa performance énergétique**.  
Deux modèles de machine learning travaillent en parallèle :
- un modèle de **régression** pour estimer la consommation énergétique,  
- et un modèle de **classification** pour prédire la classe DPE correspondante.  

Les résultats apparaissent sous forme de **jauges visuelles**, rendant la lecture intuitive et immédiate.  
Cette expérience interactive permet de comprendre **l’influence directe de chaque paramètre** (surface, isolation, énergie utilisée, année de construction) sur la performance finale du logement.

Un **historique de simulation** conserve les essais précédents pour permettre la comparaison entre plusieurs scénarios (avant/après rénovation, changement d’énergie, etc.).  
Ainsi, cette page transforme la donnée en **outil de décision concret et pédagogique**.

---

## 💡 Page 5 — À propos

Le projet **EcoScan Dashboard** est le fruit d’une collaboration entre **Miléna GORDIEN-PIQUET**, **Marvin CURTY** et **Mazilda ZEHRAOUI**.  
Nous avons tous contribué à la conception, à l’analyse et au développement technique de l’application, dans une logique de complémentarité et de réflexion commune.  

La dernière page réunit également les **liens utiles** (GitHub, documentation, présentation) et décrit les **objectifs futurs** du projet :  
- enrichir le modèle avec des **données climatiques et contextuelles**,  
- automatiser la **mise à jour des données** et le **réentraînement des modèles**,  
- et rendre la plateforme **accessible au public** dans une optique de durabilité et de sensibilisation énergétique.

---

Projet réalisé dans le cadre du module **Machine Learning – Master SISE**, *Université Lumière Lyon 2*,  
en partenariat fictif avec **GreenTech Solutions × Enedis**.
