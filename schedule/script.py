import requests
from rich.console import Console
from rich.panel import Panel
import datetime
import json
import sys

def load_config():
    with open("./config.json", "r") as f:
        return json.load(f)

config = load_config()

# Check CLI arguments validity
valid_since_values = {"daily", "weekly", "monthly"}
# Retrieve arguments (language and period)
language = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] not in valid_since_values else None
since = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] in valid_since_values else "daily"

API_URL = config.get("API_URL", "http://localhost:5011/repositories")
DISCORD_WEBHOOK_URL = config.get(f"DISCORD_WEBHOOK_URL_FOR_{since}")

# Verify that the 'since' argument is valid
if since not in valid_since_values:
    print(f"❌ Error: 'since' must be one of the following values: {valid_since_values}")
    sys.exit(1)

console = Console()

def get_trending_repositories(language: str, since: str):
    params = {"since": since}
    if language:  # Add the language parameter if defined
        params["language"] = language

    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error retrieving data: {e}[/red]")
        return []

def send_summary_to_discord(count, since):
    today_date = datetime.datetime.now().strftime("%d/%m/%Y")
    embed = {
        "embeds": [{
            "title": f"📅 GitHub Trending ({since.capitalize()}) - {today_date}",
            "description": f"🔍 **{count} repositories detected!**",
            "color": 0x5865F2,
            "footer": {"text": "Data fetched from GitHub Trending"}
        }]
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=embed)
    if response.status_code == 204:
        console.print(f"[green]Summary successfully sent to Discord![/green]")
    else:
        console.print(f"[red]Error sending summary to Discord.[/red] {response.text}")

def send_embed_to_discord(repo):
    language_field = repo['language'] if 'language' in repo else "Not specified"
    
    embed = {
        "embeds": [{
            "title": repo["name"],
            "url": repo["url"],
            "description": repo.get("description", "No description"),
            "color": 0x5865F2,
            "fields": [
                {"name": "🌟 Stars", "value": str(repo["stars"]), "inline": True},
                {"name": f"📈 {since.capitalize()} Stars", "value": str(repo["currentPeriodStars"]), "inline": True},
                {"name": "📝 Language", "value": language_field or "Not specified", "inline": True}
            ],
            "author": {"name": repo["author"], "icon_url": repo["avatar"]},
            "footer": {"text": "Trending repository on GitHub"}
        }]
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=embed)
    if response.status_code == 204:
        console.print(f"[green]Message successfully sent to Discord![/green]")
    else:
        console.print(f"[red]Error sending message to Discord.[/red] {response.text}")

def display_and_send_repositories(repositories, since):
    if not repositories:
        console.print("[yellow]No repositories found.[/yellow]")
        return

    count = len(repositories)
    send_summary_to_discord(count, since)

    for repo in repositories:
        panel = Panel(
            f"[bold green]Name:[/bold green] {repo['name']}\n"
            f"[blue]URL:[/blue] {repo['url']}\n"
            f"[yellow]Stars:[/yellow] {repo['stars']}\n"
            f"[bold cyan]{since.capitalize()} Stars:[/bold cyan] {repo['currentPeriodStars']}\n"
            f"[purple]Description:[/purple] {repo.get('description', 'No description')}",
            title=f"Repository: {repo['name']}",
            subtitle=f"Language: {repo.get('language', 'Not specified')}",
            expand=True,
        )

        console.print(panel)
        send_embed_to_discord(repo)

def main(language, since):
    console.print(f"\n🔍 [bold cyan]Searching for trending repositories[/bold cyan] for [bold yellow]{since}[/bold yellow] in [bold green]{language if language else 'all languages'}[/bold green]...\n")
    
    repositories = get_trending_repositories(language, since)
    display_and_send_repositories(repositories, since)

if __name__ == "__main__":
    main(language, since)
