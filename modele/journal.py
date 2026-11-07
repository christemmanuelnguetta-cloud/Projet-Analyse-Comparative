"""Journal de nettoyage : une liste partagée par tous les modules."""
import pandas as pd

JOURNAL = []


def noter(enseigne, article, probleme, action):
    JOURNAL.append({"enseigne": enseigne, "article": article,
                    "probleme": probleme, "action": action})


def exporter(chemin="journal.csv"):
    pd.DataFrame(JOURNAL).to_csv(chemin, sep=";", index=False, encoding="utf-8-sig")