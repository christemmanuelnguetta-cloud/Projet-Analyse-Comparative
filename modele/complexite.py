"""Mesure : recherche dans une liste (O(n)) contre un dictionnaire (O(1))."""
import random
import time


def mesurer(hist, nb_requetes=300):
    lignes_hist = list(zip(hist["source"], hist["produit_id"],
                           hist["date"], hist["prix_fcfa"]))

    # Méthode A : parcourir la liste ligne par ligne -> O(n) par recherche
    def chercher_liste(source, pid, date):
        for s, p, d, prix_ in lignes_hist:
            if s == source and p == pid and d == date:
                return prix_
        return None

    # Méthode B : dictionnaire indexé par (source, produit, date) -> O(1) par recherche
    t0 = time.perf_counter()
    index = {(s, p, d): prix_ for s, p, d, prix_ in lignes_hist}
    t_construction = time.perf_counter() - t0

    random.seed(1)
    requetes = [random.choice(lignes_hist)[:3] for _ in range(nb_requetes)]

    t0 = time.perf_counter()
    res_liste = [chercher_liste(*q) for q in requetes]
    t_liste = time.perf_counter() - t0

    t0 = time.perf_counter()
    res_dict = [index.get(q) for q in requetes]
    t_dict = time.perf_counter() - t0

    print("Mêmes résultats :", res_liste == res_dict)
    print(f"Parcours de liste : {t_liste:.4f} s pour {nb_requetes} recherches")
    print(f"Dictionnaire      : {t_dict:.6f} s pour {nb_requetes} recherches")
    print(f"Construction du dictionnaire (1 fois) : {t_construction:.4f} s")
    print(f"Le dictionnaire est environ {t_liste / t_dict:.0f} fois plus rapide")