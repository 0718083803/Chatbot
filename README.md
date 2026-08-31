# School Chatbot

This is a small chatbot for a school website. It answers common questions using a local knowledge base and can be connected to Slack and WhatsApp-style messaging flows.

## What it does

- Answers school-related questions from the files in the knowledge base
- Serves a simple web page at the home route
- Exposes a health check and question endpoint
- Handles Slack events and slash commands
- Includes webhook support for WhatsApp integrations

## Project structure

- app/ - FastAPI app code
- knowledge_base/ - school information used for answers
- templates/ - simple frontend page
- tests/ - test files

## Setup

1. Create a virtual environment

   python -m venv .venv

2. Activate it

   On Windows:
   .venv\Scripts\activate

3. Install dependencies

   pip install -r requirements.txt

4. Start the app

   uvicorn app.main:app --reload

The app should be available at:

- http://localhost:8000/

## Useful routes

- /health - checks if the app is running
- /ask?question=What are the office hours? - returns an answer from the knowledge base
- /slack/events - Slack event webhook
- /slack/commands - Slack slash command handler

## Environment variables

You may need these if you want Slack or WhatsApp features enabled:

- SLACK_BOT_TOKEN
- SLACK_APP_TOKEN
- SLACK_SIGNING_SECRET
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- TWILIO_WHATSAPP_NUMBER
- META_WHATSAPP_TOKEN
- META_WHATSAPP_PHONE_NUMBER_ID

## Knowledge base

The answers come from the text file in:

- knowledge_base/school_info.txt

You can update this file to change the chatbot's responses.

## Notes

This project is intentionally simple and easy to extend. If you want to add more school info, just update the knowledge base or add new endpoints in the app.
