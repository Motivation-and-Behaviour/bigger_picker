import hashlib
import hmac
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from rich.console import Console

from bigger_picker.airtable import AirtableManager
from bigger_picker.asana import AsanaManager
from bigger_picker.openai import OpenAIManager
from bigger_picker.rayyan import RayyanManager
from bigger_picker.sync import IntegrationManager

load_dotenv()

app = Flask(__name__)

WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")


def run_sync():
    console = Console()

    integration = IntegrationManager(
        asana_manager=AsanaManager(),
        airtable_manager=AirtableManager(),
        openai_manager=OpenAIManager(),
        rayyan_manager=RayyanManager(),
        console=console,
        debug=os.environ.get("DEBUG", "false").lower() == "true",
    )

    console.log("Starting sync via webhook...")
    integration.sync()
    console.log("Sync complete")
    return True


@app.route("/", methods=["GET"])
def home():
    return "Bigger Picker Webhook Handler is running! 🚀", 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/webhook", methods=["POST"])
def handle_webhook():
    # Check if this is the initial handshake
    handshake_secret = request.headers.get("X-Hook-Secret")
    if handshake_secret:
        print("🤝 Webhook handshake received!")
        print(f"Add this to Render env vars as WEBHOOK_SECRET: {handshake_secret}")

        # Respond with the same secret to confirm
        return app.response_class(
            status=200, headers={"X-Hook-Secret": handshake_secret}
        )

    # Normal webhook event - verify signature
    if WEBHOOK_SECRET:
        signature = request.headers.get("X-Hook-Signature")
        body = request.data

        computed = hmac.new(
            WEBHOOK_SECRET.encode("utf-8"), body, hashlib.sha256
        ).hexdigest()

        if not signature or not hmac.compare_digest(computed, str(signature)):
            return "Unauthorized", 401

    # Process webhook
    try:
        data = request.json
        events = data.get("events", []) if data else []

        if events:
            run_sync()
            return jsonify({"status": "success"}), 200

        return jsonify({"status": "no events"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
