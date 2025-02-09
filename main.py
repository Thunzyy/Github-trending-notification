from flask import Flask, request
import json
from datetime import datetime, timedelta
import subprocess
from threading import Thread
import schedule
import time
import requests
import threading

app = Flask(__name__)

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def save_config(config):
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

def run_github_trending_script(since="daily"):
    """Runs the script with the specified `since` parameter."""
    config = load_config()
    language = config.get("language", None)
    print(f"[INFO] Running the script with language: {language}, period: {since} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    subprocess.run(["python", "schedule/script.py", language, since], check=True)

@app.route("/set_language", methods=["POST"])
def set_language():
    data = request.json
    new_language = data.get("language")
    if new_language:
        config = load_config()
        config["language"] = new_language 
        save_config(config)
        # Restart the script with the new language in a separate thread
        Thread(target=lambda: run_github_trending_script("daily")).start()
        return {"message": f"Language updated: {new_language}"}, 200
    return {"error": "No language provided"}, 400

# -------------------------------------------------------------------
# Functions to check and launch the GitHub Trending API via npm start
# -------------------------------------------------------------------

def is_api_running():
    """
    Tests if the API is accessible by making a request to a known endpoint.
    Returns True if the server responds correctly, otherwise False.
    """
    try:
        response = requests.get("http://localhost:8888/repositories?since=daily", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def ensure_trending_api():
    """
    Checks if the GitHub Trending API is running.
    If not, launches the API via 'npm start' in the 'API/github-trending-api' folder.
    Returns the launched process, or None if the API was already running.
    """
    if not is_api_running():
        print("[INFO] GitHub Trending API not running. Launching via npm start...")
        # Using shell=True so that npm can be found via the Windows shell
        process = subprocess.Popen("npm start", cwd="API/github-trending-api", shell=True)
        # Wait a few seconds for the API to be operational
        time.sleep(2)
        return process
    else:
        print("[INFO] GitHub Trending API is already running.")
        return None

# -------------------------------------------------------------------
# Task Scheduling
# -------------------------------------------------------------------

# Daily execution at 8:00 PM (French time)
schedule.every().day.at("19:00").do(lambda: run_github_trending_script("daily"))  # 19:00 UTC = 20:00 French time

# Weekly execution every Sunday at 8:00 PM for `weekly`
schedule.every().sunday.at("19:00").do(lambda: run_github_trending_script("weekly"))

# Execution on the last day of the month at 8:00 PM
def check_and_run_monthly():
    """Checks if today is the last day of the month and runs the script if so."""
    today = datetime.now()
    next_day = today + timedelta(days=1)
    
    if next_day.day == 1:  # Checks if tomorrow is the first day of the month
        print("[INFO] Running the `monthly` script today.")
        run_github_trending_script("monthly")

# Check every day at 8:00 PM if it's the last day of the month
schedule.every().day.at("19:00").do(check_and_run_monthly)  # 19:00 UTC = 20:00 French time

print("[INFO] Scheduler running. Waiting...")

if __name__ == "__main__":
    # Check if the API is running and launch it via npm start if needed
    api_process = ensure_trending_api()
    
    # Start the Flask server for /set_language in a separate thread on port 5010
    threading.Thread(target=lambda: app.run(port=5010)).start()

    try:
        while True:
            schedule.run_pending()
            time.sleep(60) 
    except KeyboardInterrupt:
        print("Program terminated.")
    finally:
        if api_process:
            api_process.terminate()
