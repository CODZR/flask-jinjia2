import os
from slack_sdk import WebClient

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGN_SECRET = os.getenv("SLACK_SIGN_SECRET")

slack_client = WebClient(token=SLACK_BOT_TOKEN)
