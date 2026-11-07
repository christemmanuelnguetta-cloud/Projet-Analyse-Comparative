"""Comparatif, synthèse et panier."""
import pandas as pd

from modele import config


def construire_comparatif(tout, catalogue):
    """Renvoie (prix, comparatif). Ne garde que les offres en stock avec un prix."""
    offres = tout[tout["en_stock"] & tout["prix_paye"].notna()]
    prix = offres.pivot_table(index="produit_id", columns="enseigne",
                              values="prix_paye", aggfunc="first")
    # Au moins 2 enseignes pour pouvoir comparer
    prix = prix[prix.notna().sum(axis=1) >= 2]

    comparatif = pd.DataFrame(index=prix.index)
    comparatif["nom"] = catalogue.set_index("produit_id")["nom"]
    for e in config.ENSEIGNES:
        comparatif[e] = prix[e]

    # En cas d'égalité, on garde toutes les enseignes à égalité
    comparatif["moins_cher"] = prix.apply(
        lambda ligne: " / ".join(ligne[ligne == ligne.min()].index), axis=1)
    comparatif["prix_min"] = prix.min(axis=1)
    comparatif["prix_max"] = prix.max(axis=1)
    comparatif["ecart_fcfa"] = comparatif["prix_max"] - comparatif["prix_min"]
    comparatif["ecart_pct"] = (comparatif["ecart_fcfa"] / comparatif["prix_min"] * 100).round(1)
    return prix, comparatif


def construire_synthese(prix, comparatif):
    """Renvoie (resume par enseigne, top 3 des écarts)."""
    victoires = {e: int(comparatif["moins_cher"].str.contains(e).sum())
                 for e in config.ENSEIGNES}

    ecart_fcfa = prix.sub(prix.min(axis=1), axis=0)
    ecart_pct = ecart_fcfa.div(prix.min(axis=1), axis=0) * 100

    resume = pd.DataFrame({
        "nb_produits": prix.notna().sum(),
        "fois_moins_chere": pd.Series(victoires),
        "ecart_moyen_fcfa": ecart_fcfa.mean().round(0),
        "ecart_moyen_pct": ecart_pct.mean().round(1),
    })
    top3 = comparatif.sort_values("ecart_fcfa", ascending=False).head(3)[
        ["nom", "moins_cher", "prix_min", "prix_max", "ecart_fcfa", "ecart_pct"]]
    return resume, top3


def calculer_panier(prix, catalogue):
    """Renvoie (detail, totaux par enseigne, total en achetant au meilleur prix)."""
    enseignes = config.ENSEIGNES
    lignes = pd.DataFrame({
        "nom": catalogue.set_index("produit_id")["nom"].reindex(list(config.PANIER)),
        "quantite": pd.Series(config.PANIER),
    })
    for e in enseignes:
        lignes[e] = prix.loc[list(config.PANIER), e] * lignes["quantite"]

    if lignes[enseignes].isna().any().any():
        print("ATTENTION : un article du panier n'est pas disponible dans une enseigne")

    lignes["moins_cher"] = lignes[enseignes].idxmin(axis=1)
    lignes["cout_min"] = lignes[enseignes].min(axis=1)
    return lignes, lignes[enseignes].sum(), lignes["cout_min"].sum()