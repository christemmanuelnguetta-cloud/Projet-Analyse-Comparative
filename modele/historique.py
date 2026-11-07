"""Historique des prix : nettoyage, contrôle, Black Friday, prix par mois."""
import pandas as pd

from modele import config
from modele.journal import noter


def charger_historique():
    hist = pd.read_csv(config.FICHIER_HISTORIQUE)
    print("Lignes :", len(hist))
    print("Sources :", list(hist["source"].unique()))
    print("Valeurs manquantes :\n", hist.isna().sum())
    print("Doublons :", hist.duplicated().sum())

    hist["date"] = pd.to_datetime(hist["date"])
    hist["prix_fcfa"] = pd.to_numeric(hist["prix_fcfa"], errors="coerce")

    nb_doublons = int(hist.duplicated().sum())
    if nb_doublons:
        noter("Historique", "-", f"{nb_doublons} lignes en double", "supprimées")
    hist = hist.drop_duplicates()

    nb_sans_prix = int(hist["prix_fcfa"].isna().sum())
    if nb_sans_prix:
        noter("Historique", "-", f"{nb_sans_prix} prix manquants ou illisibles",
              "lignes supprimées")
    return hist.dropna(subset=["prix_fcfa"])


def controler_aberrants(hist):
    """Affiche les séries dont un prix s'éloigne trop de la médiane."""
    rapport = hist.groupby(["source", "produit_id"])["prix_fcfa"].agg(["min", "median", "max"])
    rapport["max_sur_mediane"] = rapport["max"] / rapport["median"]
    rapport["min_sur_mediane"] = rapport["min"] / rapport["median"]
    suspects = rapport[(rapport["max_sur_mediane"] > 1.5) | (rapport["min_sur_mediane"] < 0.5)]
    if suspects.empty:
        print("Aucun prix aberrant détecté.")
    else:
        print(suspects)
        noter("Historique", "-", f"{len(suspects)} séries avec des prix suspects", "à vérifier")


def analyser_black_friday(hist):
    """Renvoie (detail par produit, resume par enseigne, moyenne annuelle)."""
    semaine = hist[(hist["date"] >= config.BLACK_FRIDAY_DEBUT)
                   & (hist["date"] <= config.BLACK_FRIDAY_FIN)]
    moy_bf = semaine.groupby(["source", "produit_id"])["prix_fcfa"].mean()
    moy_an = hist.groupby(["source", "produit_id"])["prix_fcfa"].mean()

    bf = pd.DataFrame({"prix_bf": moy_bf, "prix_annee": moy_an}).dropna()
    bf["variation_pct"] = (bf["prix_bf"] / bf["prix_annee"] - 1) * 100

    # Une variation par produit d'abord, puis la moyenne par enseigne
    resume_bf = bf.groupby("source").agg(
        nb_produits=("variation_pct", "size"),
        variation_moyenne_pct=("variation_pct", "mean"),
        nb_moins_chers_que_la_moyenne=("variation_pct", lambda s: int((s < 0).sum())),
    ).round(1)
    return bf, resume_bf, moy_an


def prix_par_mois(hist, moy_an):
    """Indice de prix par mois (100 = prix moyen de l'année)."""
    h = hist.copy()
    h["mois"] = h["date"].dt.to_period("M")
    h = h.merge(moy_an.rename("prix_annee").reset_index(), on=["source", "produit_id"])
    h["indice"] = h["prix_fcfa"] / h["prix_annee"] * 100
    return h.pivot_table(index="mois", columns="source",
                         values="indice", aggfunc="mean").round(1)