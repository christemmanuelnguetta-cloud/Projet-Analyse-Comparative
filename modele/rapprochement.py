"""Rapprochement des articles avec le catalogue et tableau unique."""
import re
import pandas as pd

from modele import config
from modele.journal import noter
from modele.utils import normaliser


def trouver_produit(nom):
    """Renvoie le produit_id si UN SEUL produit correspond, sinon None."""
    mots = set(re.findall(r"[a-z0-9]+", normaliser(nom)))
    trouves = [pid for pid, regle in config.REGLES.items()
               if all(mots & set(exig.split("|")) for exig in regle)]
    return trouves[0] if len(trouves) == 1 else None


def tableau_unique(lagune, baobab, comptoir):
    """Réunit les 3 enseignes : enseigne, nom_brut, prix_paye, en_stock, produit_id."""
    t_lagune = pd.DataFrame({
        "enseigne": "Lagune",
        "nom_brut": lagune["designation"],
        "prix_paye": lagune["prix_nb"],
        "en_stock": lagune["en_stock"],
    })
    t_baobab = pd.DataFrame({
        "enseigne": "Baobab",
        "nom_brut": baobab["title"],
        "prix_paye": baobab["prix_paye"],
        "en_stock": baobab["stock"] > 0,
    })
    t_comptoir = pd.DataFrame({
        "enseigne": "Comptoir",
        "nom_brut": comptoir["article"],
        "prix_paye": comptoir["prix_paye"],
        "en_stock": comptoir["stock"] > 0,
    })
    tout = pd.concat([t_lagune, t_baobab, t_comptoir], ignore_index=True)
    tout["produit_id"] = tout["nom_brut"].apply(trouver_produit)

    for _, r in tout[tout["produit_id"].isna()].iterrows():
        noter(r["enseigne"], r["nom_brut"], "aucun produit du catalogue trouvé", "à vérifier")
    return tout