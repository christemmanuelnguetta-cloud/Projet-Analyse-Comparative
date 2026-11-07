"""Petites fonctions utilitaires."""
import re
import unicodedata
import pandas as pd


def texte_en_nombre(valeur):
    """'102 900 FCFA' -> 102900 ; 'Prix sur demande' -> None"""
    if pd.isna(valeur):
        return None
    chiffres = re.sub(r"\D", "", str(valeur))
    return int(chiffres) if chiffres else None


def normaliser(texte):
    """minuscules + sans accents"""
    texte = unicodedata.normalize("NFD", str(texte))
    texte = "".join(c for c in texte if unicodedata.category(c) != "Mn")
    return texte.lower()