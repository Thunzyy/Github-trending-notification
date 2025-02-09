import requests
import json
from click import secho
from rich.console import Console
from rich.panel import Panel

# Charger les paramètres depuis un fichier JSON
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

config = load_config()
API_URL = config.get("API_URL", "http://localhost:5011/repositories")

console = Console()

# Fonction pour récupérer les dépôts tendances
def get_trending_repositories(language: str = None, since: str = "daily"):
    try:
        params = {"since": since}
        if language:
            params["language"] = language
        
        response = requests.get(API_URL, params=params)
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.RequestException as e:
        secho(f"Error retrieving data: {e}", fg="red")
        return []

# Fonction pour afficher les résultats
def display_repositories(repositories):
    if not repositories:
        secho("No repository found.", fg="yellow")
        return

    for repo in repositories:
        panel = Panel(
            f"[bold green]Nom:[/bold green] {repo['name']}\n"
            f"[blue]URL:[/blue] {repo['url']}\n"
            f"[yellow]Stars:[/yellow] {repo['stars']}\n"
            f"[bold cyan]Stars today:[/bold cyan] {repo['currentPeriodStars']}\n"
            f"[purple]Description:[/purple] {repo.get('description', 'Aucune description')}",
            title=f"Repository: {repo['name']}",
            subtitle=f"Langage: {repo.get('language', 'Unknown')}",
            expand=True,
        )

        console.print(panel)
        console.print("\n")


def main():
    language = input("Enter the programming language (python, javascript... Leave blank for all languages): ").strip()
    since = input("Enter the period (daily, weekly, monthly) : ").strip()
    
    if since not in ["daily", "weekly", "monthly"]:
        secho("Invalid period, using 'daily' by default.", fg="yellow")
        since = "daily"
    
    language = language if language else None  # Si vide, envoie None pour récupérer tous les langages
    
    repositories = get_trending_repositories(language, since)
    display_repositories(repositories)

if __name__ == "__main__":
    main()
