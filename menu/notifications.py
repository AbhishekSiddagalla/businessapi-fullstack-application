import requests

def _validate_webhook_url(url: str):
    if not url.startswith("https://clientservertech1.webhook.office.com/"):
        raise ValueError("Invalid Teams Webhook URL")

def send_message_to_teams(url: str, message: str):
    _validate_webhook_url(url)

    headers = {"Content-Type": "application/json"}
    _payload = {"text": message}
    response = requests.post(url, headers=headers, json=_payload)
    return {
        "response_status": response.status_code,
        "response": response.text
    }
