import os

import requests
from dotenv import load_dotenv

import bigger_picker.config as config

load_dotenv()

ASANA_TOKEN = os.environ.get("ASANA_TOKEN")
PROJECT_GID = config.ASANA_PROJECT_ID
WEBHOOK_URL = config.RENDER_WEBHOOK_URL

response = requests.post(
    "https://app.asana.com/api/1.0/webhooks",
    headers={
        "Authorization": f"Bearer {ASANA_TOKEN}",
        "Content-Type": "application/json",
    },
    json={
        "data": {
            "resource": PROJECT_GID,
            "target": WEBHOOK_URL,
            "filters": [{"resource_type": "task", "action": "changed"}],
        }
    },
)

if response.status_code == 201:
    print("✅ Webhook created!")
    print("Check your Render logs for the WEBHOOK_SECRET")
    print(f"Webhook GID: {response.json()['data']['gid']}")
else:
    print(f"Error: {response.json()}")
