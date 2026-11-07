"""Application console interactive pour le comparateur de prix."""
import time
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich import print as rprint
from rich import box

from modele import config
from modele import journal
from modele import chargement
from modele import rapprochement
from modele import analyse
from modele import historique
from modele import complexite

console = Console()

def afficher_banniere():
    console.print(Panel.fit(
        "[bold cyan]🛒 COMPARATEUR DE PRIX & ANALYSE DE MARCHÉ[/bold cyan]\n"
        "[italic yellow]Gestion intelligente des enseignes (Lagune, Baobab, Comptoir)[/italic yellow]",
        border_style="blue",
        padding=(1, 2)
    ))

def charger_donnees_globales():
    with console.status("[bold green]Chargement, nettoyage et génération automatique des CSV...", spinner="dots"):
        try:
            catalogue = chargement.charger_catalogue()
            lagune = chargement.charger_lagune()
            baobab = chargement.charger_baobab()
            comptoir = chargement.charger_comptoir()
            
            tout = rapprochement.tableau_unique(lagune, baobab, comptoir)
            
            # Comparatif + export CSV
            prix, comparatif = analyse.construire_comparatif(tout, catalogue)
            comparatif.to_csv("comparatif.csv", sep=";", encoding="utf-8-sig")
            
            # Synthèse + export CSV
            resume, top3 = analyse.construire_synthese(prix, comparatif)
            resume.to_csv("synthese.csv", sep=";", encoding="utf-8-sig")
            
            # Panier + export CSV
            lignes, totaux, total_mixte = analyse.calculer_panier(prix, catalogue)
            lignes.to_csv("panier.csv", sep=";", encoding="utf-8-sig")
            
            # Journal + export CSV
            journal.exporter("journal.csv")
            
            return catalogue, tout, prix, comparatif, resume, top3, lignes, totaux, total_mixte
        except Exception as e:
            console.print(f"[bold red]Erreur lors du chargement des données : {e}[/bold red]")
            return None

def menu_principal():
    donnees = charger_donnees_globales()
    if donnees:
        console.print("[bold green]✔ Données chargées et fichiers CSV générés avec succès ![/bold green]")
        time.sleep(1)
    
    while True:
        console.clear()
        afficher_banniere()
        
        console.print("\n[bold underline]MENU PRINCIPAL[/bold underline]\n")
        console.print("[1] 🔄 Recharger et nettoyer à nouveau les données")
        console.print("[2] 📊 Afficher le Tableau Comparatif des produits")
        console.print("[3] 🏆 Afficher la Synthèse par enseigne & Top 3 des écarts")
        console.print("[4] 🛒 Analyser le Panier de rentrée")
        console.print("[5] 📈 Historique & Analyse Black Friday")
        console.print("[6] ⚡ Tester la Complexité (Recherche Liste O(n) vs Dict O(1))")
        console.print("[7] 📝 Consulter le Journal de nettoyage")
        console.print("[0] 🚪 Quitter\n")
        
        choix = IntPrompt.ask("Votre choix", choices=["0", "1", "2", "3", "4", "5", "6", "7"], default=0)
        
        if choix == 0:
            console.print("[bold green]Au revoir ![/bold green]")
            break
            
        elif choix == 1:
            donnees = charger_donnees_globales()
            if donnees:
                console.print("[bold green]✔ Données rechargées et fichiers CSV mis à jour avec succès ![/bold green]")
            Prompt.ask("\nAppuyez sur Entrée pour continuer...")
            
        elif choix == 2:
            if donnees is None:
                console.print("[yellow]Aucune donnée disponible.[/yellow]")
            else:
                _, _, _, comparatif, _, _, _, _, _ = donnees
                table = Table(title="Tableau Comparatif des Produits", show_header=True, header_style="bold magenta", box=box.ROUNDED, show_lines=True)
                for col in comparatif.columns:
                    table.add_column(str(col))
                for _, row in comparatif.head(15).iterrows():
                    table.add_row(*[str(val) if pd.notna(val) else "-" for val in row])
                console.print(table)
                console.print("[italic]Affichage limité aux 15 premiers produits pour plus de clarté.[/italic]")
            Prompt.ask("\nAppuyez sur Entrée pour continuer...")
            
        elif choix == 3:
            if donnees is None:
                console.print("[yellow]Aucune donnée disponible.[/yellow]")
            else:
                _, _, _, _, resume, top3, _, _, _ = donnees
                
                t_resume = Table(title="Synthèse par Enseigne", show_header=True, header_style="bold cyan", box=box.ROUNDED, show_lines=True)
                for col in resume.reset_index().columns:
                    t_resume.add_column(str(col))
                for _, row in resume.reset_index().iterrows():
                    t_resume.add_row(*[str(val) for val in row])
                console.print(t_resume)
                
                console.print("\n")
                
                t_top3 = Table(title="Top 3 des Écarts de Prix", show_header=True, header_style="bold cyan", box=box.ROUNDED, show_lines=True)
                for col in top3.columns:
                    t_top3.add_column(str(col))
                for _, row in top3.iterrows():
                    t_top3.add_row(*[str(val) if pd.notna(val) else "-" for val in row])
                console.print(t_top3)
                
            Prompt.ask("\nAppuyez sur Entrée pour continuer...")
            
        elif choix == 4:
            if donnees is None:
                console.print("[yellow]Aucune donnée disponible.[/yellow]")
            else:
                _, _, _, _, _, _, lignes, totaux, total_mixte = donnees
                
                t_lignes = Table(title="Détail du Panier de Rentrée", show_header=True, header_style="bold green", box=box.ROUNDED, show_lines=True)
                for col in lignes.reset_index().columns:
                    t_lignes.add_column(str(col))
                for _, row in lignes.reset_index().iterrows():
                    t_lignes.add_row(*[str(val) if pd.notna(val) else "-" for val in row])
                console.print(t_lignes)
                
                console.print("\n")
                
                t_totaux = Table(title="Totaux par Enseigne", show_header=True, header_style="bold green", box=box.ROUNDED, show_lines=True)
                t_totaux.add_column("Enseigne")
                t_totaux.add_column("Total Panier (FCFA)")
                for ens, val in totaux.items():
                    t_totaux.add_row(str(ens), f"{val:,.0f}")
                console.print(t_totaux)
                
                console.print(f"\n[bold green]✔ Meilleure enseigne unique :[/bold green] {totaux.idxmin()} -> {totaux.min():,.0f} FCFA")
                console.print(f"[bold green]✔ Panier mixte (meilleur prix par article) :[/bold green] {total_mixte:,.0f} FCFA")
                console.print(f"[bold yellow]💡 Économie réalisée :[/bold yellow] {totaux.min() - total_mixte:,.0f} FCFA")
                
            Prompt.ask("\nAppuyez sur Entrée pour continuer...")
            
        elif choix == 5:
            with console.status("[bold green]Analyse de l'historique...", spinner="dots"):
                try:
                    hist = historique.charger_historique()
                    bf, resume_bf, moy_an = historique.analyser_black_friday(hist)
                    par_mois = historique.prix_par_mois(hist, moy_an)
                    
                    bf.to_csv("black_friday.csv", sep=";", encoding="utf-8-sig")
                    par_mois.to_csv("prix_par_mois.csv", sep=";", encoding="utf-8-sig")
                    
                    t_bf = Table(title="Résumé Black Friday vs Année", show_header=True, header_style="bold blue", box=box.ROUNDED, show_lines=True)
                    for col in resume_bf.reset_index().columns:
                        t_bf.add_column(str(col))
                    for _, row in resume_bf.reset_index().iterrows():
                        t_bf.add_row(*[str(val) for val in row])
                    console.print(t_bf)
                    
                    console.print("\n")
                    
                    t_mois = Table(title="Indice de Prix par Mois (100 = Moyenne annuelle)", show_header=True, header_style="bold blue", box=box.ROUNDED, show_lines=True)
                    for col in par_mois.reset_index().columns:
                        t_mois.add_column(str(col))
                    for _, row in par_mois.reset_index().iterrows():
                        t_mois.add_row(*[str(val) if pd.notna(val) else "-" for val in row])
                    console.print(t_mois)
                    
                except Exception as e:
                    console.print(f"[bold red]Erreur : {e}[/bold red]")
            Prompt.ask("\nAppuyez sur Entrée pour continuer...")
            
        elif choix == 6:
            with console.status("[bold green]Exécution du benchmark de complexité...", spinner="dots"):
                try:
                    hist = historique.charger_historique()
                    complexite.mesurer(hist)
                except Exception as e:
                    console.print(f"[bold red]Erreur : {e}[/bold red]")
            Prompt.ask("\nAppuyez sur Entrée pour continuer...")
            
        elif choix == 7:
            if not journal.JOURNAL:
                console.print("[yellow]Aucun journal enregistré pour l'instant.[/yellow]")
            else:
                table = Table(title="Journal de Nettoyage", show_header=True, header_style="bold blue", box=box.ROUNDED, show_lines=True)
                table.add_column("Enseigne")
                table.add_column("Article")
                table.add_column("Problème")
                table.add_column("Action")
                for entry in journal.JOURNAL[:20]:
                    table.add_row(entry["enseigne"], str(entry["article"]), entry["probleme"], entry["action"])
                console.print(table)
                console.print(f"[italic]Total des actions de nettoyage enregistrées : {len(journal.JOURNAL)}[/italic]")
            Prompt.ask("\nAppuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    menu_principal()