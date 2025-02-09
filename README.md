# GitHub Trending Notification Project

This project is designed to notify you on Discord about trending GitHub repositories.  
Referenced: [GitHub Trending](https://github.com/trending)  
It uses the API from [github-trending-api](https://github.com/huchenme/github-trending-api).  
**Make sure** that no other process is using ports 5010 or 5011.

If you want to manage notifications without editing the configuration JSON directly, you can create a Discord bot:
- Go to the [Discord Developer Portal](https://discord.com/developers/applications)
- Create a new application.
- Navigate to the "Bot" section and click "Add Bot."
- Copy the bot token (never share it).
- Go to "OAuth2" → "URL Generator," check the "bot" and "Send Messages" permissions, and then invite the bot to your server.

_This script is set up in UTC+1, executing every day at 20:00, every Saturday at 20:00, and on the last day of the month at 20:00._

---

## CONFIG

Below is an example configuration. Update these values in your `config.json` file:
Create one if needed.

```json
{
  "API_URL": "http://localhost:5010/repositories", // Enter the URL of your local API
  "DISCORD_WEBHOOK_URL_FOR_DAILY": "<https://discord.com/api/webhooks/for_daily>", // Webhook URL for daily GitHub project notifications
  "DISCORD_WEBHOOK_URL_FOR_weekly": "<https://discord.com/api/webhooks/for_weekly>", // Webhook URL for weekly GitHub project notifications
  "DISCORD_WEBHOOK_URL_FOR_monthly": "<https://discord.com/api/webhooks/for_monthly>", // Webhook URL for monthly GitHub project notifications
  "BOT_TOKEN": "", // Your Discord bot token if you want to manage the webhook easily; otherwise, leave empty.
  "language": "" // The default language for filtering repositories; leave empty to include all.
}
```

---

## Prerequisites

- **Python 3.9+**
- **Node.js & npm** (for the API in `API/github-trending-api`)
- **A Discord account and Bot Token** (configured via the [Discord Developer Portal](https://discord.com/developers/applications))
- **Docker** (optional, for deploying the application in a container)

---

## Configuration

- **config.json**  
  Update the file `config.json` with your information:
  - `"BOT_TOKEN"`: Your Discord bot token.
  - `"DISCORD_WEBHOOK_URL_FOR_DAILY"`, `"DISCORD_WEBHOOK_URL_FOR_weekly"`, and `"DISCORD_WEBHOOK_URL_FOR_monthly"` as needed.
  - `"language"`: Default language to filter trending repositories (optional).

---

## Installation

### Prerequisites

- **Python 3.7+** (recommended)
- **pip**
- **git** (to clone the repository)
- **Node.js and npm** (if your GitHub Trending API relies on an npm-based project)

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/github-trending-project.git
   cd github-trending-project
   ```

2. **Create a Virtual Environment (Optional but Recommended)**

   ```bash
   # On Unix-based systems:
   python -m venv venv
   source venv/bin/activate

   # On Windows:
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies**

   A `requirements.txt` should be provided. If not, install the necessary packages manually:

   ```bash
   pip install flask discord requests rich schedule click
   ```

4. **Set Up Node.js (For GitHub Trending API)**

   If your setup requires the GitHub Trending API to run via `npm start` (as referenced in `main.py`), ensure Node.js is installed. Then navigate to the `API/github-trending-api` directory and run:

   ```bash
   cd API/github-trending-api
   npm install
   npm start
   ```

   The Flask scheduler will verify and launch this process if it isn't running.

---

## Configuration File Example

Create or update the `config.json` file in the root directory with your settings. Below is an example:

```json
{
  "BOT_TOKEN": "your_discord_bot_token",
  "API_URL": "http://localhost:5011/repositories",
  "DISCORD_WEBHOOK_URL_FOR_DAILY": "your_discord_webhook_url_for_daily",
  "DISCORD_WEBHOOK_URL_FOR_WEEKLY": "your_discord_webhook_url_for_weekly",
  "DISCORD_WEBHOOK_URL_FOR_MONTHLY": "your_discord_webhook_url_for_monthly",
  "language": ""
}
```

- **BOT_TOKEN**: Your Discord bot token.
- **API_URL**: URL to fetch trending repositories (as provided by your GitHub Trending API).
- **DISCORD_WEBHOOK_URL_FOR_***: Webhook URLs for sending Discord messages for the respective periods.
- **language**: Default programming language filter for trending repositories (leave empty for all).

---

## Installation & Execution

### Local Execution (Without Docker)

1. **Install Python Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Install Node.js Dependencies**:

   ```bash
   cd API/github-trending-api
   npm install
   cd ../..
   ```

3. **Run the Project**:

   You can start both processes simultaneously using the startup script:

   ```bash
   bash start.sh
   ```

   Alternatively, run `main.py` and `bot.py` in separate terminal windows.

### Execution with Docker

1. **Build the Docker Image**:

   ```bash
   docker build -t github-trending-notification .
   ```

2. **Run the Container**:

   ```bash
   docker run -p 5010:5010 -p 5011:5011 github-trending-notification
   ```

   - **5010**: Port for the Flask API (`/set_language` endpoint).
   - **5011**: Port for the Node.js GitHub Trending API.

---

## Usage

### Discord Bot Commands

- **`/display_trending <period> <language>`**  
  Displays trending GitHub repositories for the specified period (e.g., `daily`) along with an optional language filter.  
  **Example**: `/display_trending daily python`

- **`/set_language <language>`**  
  Changes the default language for trending repositories.  
  **Example**: `/set_language javascript`

- **`/help`**  
  Displays the list of available commands.

### API Endpoints

- **POST `/set_language`**  
  Allows you to update the default language in the configuration.
  - **Example JSON Payload**:
    ```json
    {
      "language": "python"
    }
    ```
  - The API is accessible at: [http://localhost:5010/set_language](http://localhost:5010/set_language)

---

## Troubleshooting

- **Occupied Ports**:  
  If you encounter errors related to ports (5010 or 5011), ensure they are not being used by another process on your machine or modify the port mappings when launching the Docker container.

- **npm Not Found**:  
  The Dockerfile installs Node.js and npm. If running locally and npm is not recognized, ensure it is installed and added to your PATH.

- **Discord Responses**:  
  Confirm that your bot responds correctly to interactions by using the asynchronous methods in the Discord API (see `bot.py` for details on handling commands and responses).

---

Feel free to contribute or adapt this project to your needs!
