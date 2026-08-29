**Project Overview**  
- **Description:** School Q&A chatbot adapted to Slack. Responds to slash commands and messages using a simple knowledge base.

**Prerequisites**  
- **Python:** 3.10+ (for the original FastAPI code and Python Socket Mode runner)  
- **Node.js:** 18+ (for the quick Socket Mode bot using `@slack/bolt`)  
- **Slack App:** App-level token (`xapp-...`) with `connections:write` and Bot token (`xoxb-...`) installed to your workspace.

**Files to know**  
- **Python runner:** socket_runner.py  
- **Node runner:** index.js  
- **Env example:** .env.example  
- **Python deps:** requirements.txt  
- **Node manifest:** package.json

**Environment variables**  
- **`SLACK_BOT_TOKEN`** — Bot User OAuth Token (starts with `xoxb-`)  
- **`SLACK_APP_TOKEN`** — App-Level Token for Socket Mode (starts with `xapp-`)  
- **`SLASH_COMMAND_NAME`** — Optional, slash command name to register (e.g. `/bot-ping`)

Copy .env.example to .env and paste your tokens. Do NOT commit .env.

**Install (Python runner)**  
- Install Python deps:
```bash
pip install -r requirements.txt
```

**Run (Python Socket Mode runner)**  
- Start Python runner:
```bash
python -m app.socket_runner
```
- This uses socket_runner.py and the knowledge base in knowledge_base.

**Install & Run (Node quick runner)**  
- Install Node deps:
```bash
npm install
# or for the single packages used:
npm install @slack/bolt dotenv axios
```
- Start the Node bot:
```bash
npm start
```
- The Node bot entrypoint is index.js and includes many school-aligned slash commands (e.g. `/bot-ping`, `/bot-joke`, `/bot-office-hours`).

**Commands included**  
- **Basic:** `/bot-ping`, `/bot-help`  
- **Fun:** `/bot-joke`  
- **School helpers:** `/bot-office-hours`, `/bot-uniform`, `/bot-admission`, `/bot-contact`, `/bot-calendar`, `/bot-lunch`, `/bot-directions`, `/bot-staff`, `/bot-holidays`

**Testing locally**  
- For Python tests:
```bash
# ensure PYTHONPATH includes the repo root
# PowerShell
$env:PYTHONPATH="."; pytest -q
```
- Manually test slash commands in Slack after installing the app and inviting the bot to a channel.

**Troubleshooting**  
- **`invalid_auth` / WebSocket errors:** tokens are incorrect or not installed/reinstalled. Reinstall the app in Slack (OAuth & Permissions → Install to Workspace) and regenerate the App-Level token (Basic Information → App-Level Tokens) with `connections:write`. Update .env and restart the runner.  
- **No response to slash commands:** ensure the command name in Slack matches `SLASH_COMMAND_NAME` and that the Slash Command is created in the Slack App dashboard. For Socket Mode you do NOT need a public URL.  
- **Multiple runners:** stop the other runner (Python or Node) to avoid duplicate connections while debugging.

**Security & deployment**  
- Never commit tokens. Use secrets manager or CI secrets for production. For production, prefer hosted deployment with managed secrets and restart supervision.

