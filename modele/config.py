"""Paramètres du projet : chemins, constantes et règles de rapprochement."""

DOSSIER_DONNEES = "donnees"
FICHIER_CATALOGUE = f"{DOSSIER_DONNEES}/catalogue_reference.csv"
FICHIER_LAGUNE = f"{DOSSIER_DONNEES}/marche_lagune.csv"
FICHIER_BAOBAB = f"{DOSSIER_DONNEES}/baobab_shop.json"
FICHIER_COMPTOIR = f"{DOSSIER_DONNEES}/comptoir_ivoire.xlsx"
FICHIER_HISTORIQUE = f"{DOSSIER_DONNEES}/historique_prix.csv"

ENSEIGNES = ["Lagune", "Baobab", "Comptoir"]

PANIER = {"P04": 1, "P12": 1, "P14": 2, "P15": 1, "P28": 1}

BLACK_FRIDAY_DEBUT = "2025-11-24"
BLACK_FRIDAY_FIN = "2025-11-30"

REGLES = {
    "P01": ["a15"],
    "P02": ["a25"],
    "P03": ["a55"],
    "P04": ["spark"],
    "P05": ["camon"],
    "P06": ["40i"],
    "P07": ["infinix", "note", "40"],
    "P08": ["itel"],
    "P09": ["iphone"],
    "P10": ["redmi"],
    "P11": ["250", "g9"],
    "P12": ["ideapad"],
    "P13": ["inspiron"],
    "P14": ["sandisk"],
    "P15": ["seagate"],
    "P16": ["logitech"],
    "P17": ["deskjet"],
    "P18": ["archer"],
    "P19": ["samsung", "ecran|monitor"],
    "P20": ["hisense", "frigo|fridge|refrigerateur"],
    "P21": ["nasco"],
    "P22": ["samsung", "tv", "43"],
    "P23": ["hisense", "tv"],
    "P24": ["lg", "clim|climatiseur|conditioner"],
    "P25": ["binatone"],
    "P26": ["moulinex", "mixeur|blender"],
    "P27": ["philips"],
    "P28": ["samsung", "micro|microwave"],
    "P29": ["bouilloire|kettle"],
    "P30": ["hisense", "clim|climatiseur|conditioner"],
}