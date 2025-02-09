import discord
from discord.ext import commands
from discord import app_commands
import requests
import json
import subprocess
import threading
import asyncio

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

config = load_config()
TOKEN = config.get("BOT_TOKEN")
FLASK_URL = "http://localhost:5010/set_language"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Bot connected as {bot.user}')

def run_script_in_thread(command, interaction):
    """Function to execute the script in a separate thread."""
    try:
        # Execute the script in a thread without blocking the bot
        subprocess.run(command, check=True)
        message = f"📢 The script has been executed for the `{command[2]}` trends in `{command[1] if command[1] else 'all languages'}`."
    except subprocess.CalledProcessError as e:
        message = f"❌ Error executing the script: {e}"
    
    # Use run_coroutine_threadsafe to send the message via the interaction API
    asyncio.run_coroutine_threadsafe(interaction.followup.send(message), interaction.client.loop)

@bot.tree.command(name="display_trending", description="Display trending GitHub repositories")
@app_commands.describe(period="Choose the period", language="Choose the language (leave empty for all languages)")
async def display_trending(interaction: discord.Interaction, period: str, language: str = None):
    """Command to display trending repositories with period and language selection."""
    # Defer the response to signal to Discord that we will reply later
    await interaction.response.defer()

    # Send a confirmation message via followup
    await interaction.followup.send(
        f"📢 Executing script for `{period}` trends in `{language if language else 'all languages'}`..."
    )

    # Build the command and execute it in a separate thread to avoid blocking the bot
    command = ["python", "schedule/script.py", language or "", period]
    threading.Thread(target=run_script_in_thread, args=(command, interaction)).start()

@bot.tree.command(name="set_language", description="Change the language for GitHub repositories")
async def set_language(interaction: discord.Interaction, language: str):
    """Command to change the script's language."""
    payload = {"language": language}
    response = requests.post(FLASK_URL, json=payload)

    if response.status_code == 200:
        await interaction.channel.send(f"✅ Language changed to `{language}`.")
    else:
        await interaction.channel.send(f"❌ Error: {response.json().get('error', 'Problem updating the language.')}")

@bot.tree.command(name="help", description="Display available commands")
async def help(interaction: discord.Interaction):
    """Display the bot's commands."""
    help_message = """📌 **Available Commands**:
    🔹 `/set_language <language>` : Change the language for GitHub repositories
    🔹 `/display_trending <period> <language>` : Display trending repositories with period and language options
    """
    await interaction.response.send_message(help_message)

bot.run(TOKEN)
