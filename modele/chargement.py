"""Chargement et nettoyage des trois enseignes (avec écriture dans le journal)."""
import json
import pandas as pd

from modele import config
from modele.journal import noter
from modele.utils import texte_en_nombre


def charger_catalogue():
    return pd.read_csv(config.FICHIER_CATALOGUE)


def charger_lagune():
    lagune = pd.read_csv(config.FICHIER_LAGUNE, sep=";")

    for _, r in lagune[lagune.duplicated()].iterrows():
        noter("Lagune", r["designation"], "ligne en double", "supprimée")
    lagune = lagune.drop_duplicates().reset_index(drop=True)

    noter("Lagune", "(tous les articles)", "prix écrits en texte ('102 900 FCFA')",
          "convertis en nombres")
    noter("Lagune", "(tous les articles)", "notes avec virgule décimale ('4,0')",
          "converties en nombres")

    lagune["prix_nb"] = lagune["prix"].apply(texte_en_nombre)
    lagune["ancien_prix_nb"] = lagune["ancien_prix"].apply(texte_en_nombre)

    for _, r in lagune[lagune["prix_nb"].isna()].iterrows():
        noter("Lagune", r["designation"], f"prix inutilisable ({r['prix']})",
              "exclu du comparatif")

    # Prix aberrant : le prix actuel dépasse l'ancien prix barré
    masque = lagune["prix_nb"] > lagune["ancien_prix_nb"]
    for i, r in lagune[masque].iterrows():
        noter("Lagune", r["designation"],
              f"prix aberrant ({r['prix_nb']:.0f} > ancien prix {r['ancien_prix_nb']:.0f})",
              "divisé par 10")
        lagune.loc[i, "prix_nb"] = r["prix_nb"] / 10

    lagune["note_clients"] = lagune["note_clients"].str.replace(",", ".").astype(float)

    # Noms avec une casse irrégulière
    for nom in lagune.loc[lagune["designation"] != lagune["designation"].str.upper(),
                          "designation"]:
        noter("Lagune", nom, "nom en minuscules", "mis en majuscules")
    lagune["designation"] = lagune["designation"].str.upper().str.strip()

    lagune["en_stock"] = lagune["disponibilite"] != "Rupture"
    for _, r in lagune[~lagune["en_stock"]].iterrows():
        noter("Lagune", r["designation"], "en rupture", "non retenu comme moins cher")

    return lagune


def charger_comptoir():
    comptoir = pd.read_excel(config.FICHIER_COMPTOIR, header=2)
    comptoir.columns = ["code", "article", "rayon", "prix_catalogue",
                        "remise", "stock", "date_maj"]

    for _, r in comptoir.iterrows():
        if isinstance(r["prix_catalogue"], str):
            noter("Comptoir", r["article"],
                  f"prix en texte ('{r['prix_catalogue']}')", "converti en nombre")
    comptoir["prix_catalogue"] = comptoir["prix_catalogue"].apply(texte_en_nombre)

    noter("Comptoir", "(tous les articles)", "remise (%) à déduire du prix catalogue",
          "prix payé = prix catalogue x (1 - remise/100)")
    comptoir["prix_paye"] = (comptoir["prix_catalogue"]
                             * (1 - comptoir["remise"] / 100)).round()

    for _, r in comptoir[comptoir["stock"] == 0].iterrows():
        noter("Comptoir", r["article"], "stock à 0", "non retenu comme moins cher")

    # Noms abîmés ou incomplets
    noter("Comptoir", "Samsun Galaxy A15 128Go", "faute de frappe (« Samsun »)",
          "rapproché grâce au mot-clé 'a15'")
    for nom_court in ["Mixeur Moulinex", "Bouilloire 1,7L", "Fer Philips"]:
        noter("Comptoir", nom_court, "nom incomplet (marque ou modèle manquant)",
              "rapproché par mots-clés")

    return comptoir


def charger_baobab():
    with open(config.FICHIER_BAOBAB, encoding="utf-8") as f:
        data = json.load(f)
    baobab = pd.json_normalize(data["items"])
    baobab = baobab.rename(columns={"pricing.amount": "amount",
                                    "pricing.delivery_fee": "livraison"})

    for _, r in baobab[baobab["amount"].isna()].iterrows():
        noter("Baobab", r["title"], "prix manquant (null)", "exclu du comparatif")

    for _, r in baobab[baobab["stock"] == 0].iterrows():
        noter("Baobab", r["title"], "stock à 0", "non retenu comme moins cher")

    noter("Baobab", "(tous les articles)", "titres en anglais, modèle avant la marque",
          "rapprochés par mots-clés")
    noter("Baobab", "(tous les articles)", "livraison facturée en plus du prix",
          "prix payé = amount + delivery_fee")

    # Le client paie le prix + la livraison
    baobab["prix_paye"] = baobab["amount"] + baobab["livraison"]
    return baobab