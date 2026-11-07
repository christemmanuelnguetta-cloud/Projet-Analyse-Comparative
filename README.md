# Comparateur de prix et analyse de marché

Projet de **Data Analysis en Python** (L2 Informatique, séance 3).

Un client veut acheter de l'électronique et de l'électroménager à Abidjan et hésite entre trois enseignes.
Le programme collecte leurs données, les nettoie, les rapproche d'un catalogue commun, compare les prix
et aide à décider où et quand acheter.

> Toutes les données sont **fictives** (enseignes, produits et prix créés pour l'exercice).

| Enseigne | Type | Fichier | Format |
|---|---|---|---|
| Marché Lagune | site marchand | `marche_lagune.csv` | CSV (séparateur `;`) |
| Baobab Shop | application mobile | `baobab_shop.json` | JSON |
| Comptoir Ivoire | boutique d'Adjamé | `comptoir_ivoire.xlsx` | Excel |

Deux autres fichiers complètent les données : `catalogue_reference.csv` (30 produits, P01 à P30)
et `historique_prix.csv` (20 876 lignes, du 01/11/2025 au 31/10/2026).

---

## Installation

Prérequis : Python 3.10 ou plus récent.

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
pip install -r requirements.txt
```

Bibliothèques utilisées : `pandas`, `openpyxl` (lecture Excel), `rich` (affichage du menu).

## Lancement

Depuis la racine du projet :

```bash
python app.py
```

Un menu interactif s'affiche :

| Choix | Action |
|---|---|
| 1 | Recharger et nettoyer à nouveau les données |
| 2 | Tableau comparatif des produits |
| 3 | Synthèse par enseigne et Top 3 des écarts |
| 4 | Panier de rentrée |
| 5 | Historique et analyse du Black Friday |
| 6 | Test de complexité (liste O(n) contre dictionnaire O(1)) |
| 7 | Journal de nettoyage |
| 0 | Quitter |

Les données sont chargées automatiquement au premier choix. Les fichiers CSV de résultats
sont écrits à la racine du projet à chaque chargement.

---

## Architecture (MVC)

```
Projet_Prix/
├── app.py                  point d'entrée
├── requirements.txt
├── donnees/                fichiers sources
├── modele/                 MODÈLE : données et calculs (aucun affichage)
│   ├── config.py           chemins, panier, dates, règles de rapprochement
│   ├── utils.py            conversion texte -> nombre, normalisation des noms
│   ├── journal.py          journal de nettoyage partagé
│   ├── chargement.py       lecture et nettoyage des 3 enseignes
│   ├── rapprochement.py    association article -> produit_id, tableau unique
│   ├── analyse.py          comparatif, synthèse, panier
│   ├── historique.py       historique, Black Friday, prix par mois
│   ├── complexite.py       mesure liste contre dictionnaire
│   └── pipeline.py         enchaîne toutes les étapes et exporte les CSV
├── vue/
│   └── console.py          VUE : affichage avec rich (aucun calcul)
└── controleur/
    └── menu.py             CONTRÔLEUR : lit le choix, appelle le modèle, envoie à la vue
```

- Le **modèle** charge, nettoie, rapproche et calcule. Il n'affiche rien.
- La **vue** affiche les menus et les tableaux. Elle ne calcule rien.
- Le **contrôleur** reçoit le choix de l'utilisateur, appelle le modèle puis la vue.

---

## Méthode

1. **Chargement** : CSV (`sep=";"`), JSON (`json_normalize`) et Excel (`header=2`) dans une même structure.
2. **Nettoyage** : chaque problème est noté dans un journal (`journal.csv`).
3. **Rapprochement** : chaque article reçoit un `produit_id` grâce à un dictionnaire de règles par mots-clés
   (`REGLES` dans `config.py`) appliqué à des noms normalisés (minuscules, sans accents).
4. **Prix payé réel** :
   - Lagune : prix affiché (livraison incluse) ;
   - Baobab : `amount + delivery_fee` ;
   - Comptoir : prix catalogue x (1 - remise / 100).
5. **Comparatif** : seuls les produits avec au moins 2 offres utilisables (en stock, avec un prix) sont comparés.
   Un produit en rupture ou sans prix n'est jamais retenu comme « le moins cher ».

### Problèmes de données traités

| Enseigne | Problème | Traitement |
|---|---|---|
| Lagune | 2 lignes en double (ML-1000, ML-1147) | supprimées |
| Lagune | prix en texte (`102 900 FCFA`), notes avec virgule | convertis en nombres |
| Lagune | « Prix sur demande » et prix vide | exclus du comparatif |
| Lagune | Tecno Spark 20 à 779 000 (supérieur à l'ancien prix 88 700) | divisé par 10, soit 77 900 |
| Lagune | noms en minuscules, articles en rupture | normalisés, non retenus comme moins chers |
| Baobab | Philips Steam Iron avec prix `null` | exclu du comparatif |
| Baobab | 3 articles avec stock à 0 | non retenus comme moins chers |
| Baobab | titres en anglais, modèle avant la marque | rapprochés par mots-clés |
| Comptoir | prix en texte (`279 300`) | converti en nombre |
| Comptoir | « Samsun », noms incomplets, 2 stocks à 0 | rapprochés par mots-clés, ruptures exclues |

La correction du prix de Lagune a été **vérifiée** : l'historique donne 77 900 FCFA pour ce produit
fin octobre 2026.

---

## Résultats

### Comparatif et synthèse (23 produits comparables)

| Enseigne | Fois la moins chère | Écart moyen au prix le plus bas |
|---|---|---|
| Comptoir Ivoire | 10 | 6 667 FCFA (2,8 %) |
| Baobab Shop | 9 | 2 702 FCFA (4,7 %) |
| Marché Lagune | 6 | 7 771 FCFA (3,8 %) |

Les deux égalités (souris Logitech et fer Philips) comptent pour les deux enseignes concernées,
d'où un total de 25 victoires. Les enseignes n'ont pas le même nombre de produits comparés
(20, 18 et 19), donc les écarts moyens se comparent avec prudence.

**Top 3 des produits où comparer rapporte le plus :**

| Produit | Moins cher | Écart |
|---|---|---|
| HP 250 G9 | Baobab | 52 800 FCFA (14,9 %) |
| iPhone 13 128 Go | Baobab | 26 500 FCFA (6,4 %) |
| Climatiseur LG 1 CV | Baobab | 26 000 FCFA (10,3 %) |

### Panier de rentrée (Spark 20, IdeaPad 3, 2 clés USB, disque Seagate, micro-ondes)

| Enseigne | Total |
|---|---|
| Marché Lagune | 504 300 FCFA |
| Baobab Shop | 491 500 FCFA |
| Comptoir Ivoire | **484 075 FCFA** |
| Meilleur prix par article (panier mixte) | **477 575 FCFA** |

Acheter chaque article là où il est le moins cher économise **6 500 FCFA** par rapport à Comptoir seul.

### Historique : quand acheter ?

Prix moyen de la semaine du 24 au 30 novembre 2025 comparé à la moyenne de l'année :

| Enseigne | Variation | Produits moins chers que la moyenne |
|---|---|---|
| Baobab Shop | -11,7 % | 26 sur 26 |
| Marché Lagune | -11,3 % | 28 sur 28 |
| Comptoir Ivoire | +3,8 % | 0 sur 22 |

Chez Baobab et Lagune, le Black Friday est le meilleur moment pour acheter. Chez Comptoir, aucune baisse
sur les prix catalogue ; le mois le moins cher est septembre 2026 (comme pour les deux autres enseignes,
dont l'indice de prix est alors d'environ 95,5 pour une moyenne de 100).

### Complexité

Recherche d'un prix dans l'historique (20 876 lignes), 300 recherches aléatoires :

| Méthode | Complexité | Temps mesuré (ordre de grandeur) |
|---|---|---|
| Parcours d'une liste | O(n) par recherche | 0,07 à 0,25 s |
| Dictionnaire indexé par `(source, produit, date)` | O(1) en moyenne | environ 0,0003 s |

Le dictionnaire est de **300 à 700 fois plus rapide** selon les lancements. Sa construction (environ 0,008 s,
une seule fois) est rentabilisée dès les premières recherches. Le temps total du programme est inférieur à 1 seconde.

Autres structures utilisées : dictionnaire `REGLES` pour le rapprochement, `set` des mots d'un nom pour tester
les mots-clés rapidement, liste `JOURNAL` pour tracer les problèmes.

---

## Hypothèses et limites

- Le prix aberrant de Lagune a été corrigé en divisant par 10 (confirmé par l'historique).
- Chez Baobab, la **livraison est comptée par article** (pour 2 clés USB : 2 x (5 800 + 1 500)).
- Un panier mixte oblige à passer dans plusieurs enseignes, et Comptoir impose de venir en boutique.
- L'historique contient les prix **affichés** ; pour Comptoir, c'est le prix catalogue sans la remise,
  donc l'analyse du Black Friday ne dit rien sur les remises en boutique.
- Les prix baissent légèrement au fil de l'année, donc comparer à la moyenne annuelle est approximatif,
  mais un écart de -11 % est trop grand pour venir de cette seule tendance.

## Fichiers produits

| Fichier | Contenu |
|---|---|
| `comparatif.csv` | prix par enseigne, moins cher, écart en FCFA et en % |
| `synthese.csv` | victoires et écarts moyens par enseigne |
| `panier.csv` | détail du panier par enseigne |
| `black_friday.csv` | variation du Black Friday par produit et par enseigne |
| `prix_par_mois.csv` | indice de prix par mois |
| `journal.csv` | journal de nettoyage |

## Auteur

*Nom, prénom : à compléter* — L2 Computer Science, DA Python.
