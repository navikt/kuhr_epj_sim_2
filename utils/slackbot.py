import os

import httpx

class SlackBot:

    def __init__(self):
        self.bot_token = os.getenv("SLACK_TOKEN")
        self.client = httpx.Client(
            headers={
                "Authorization": f"Bearer {self.bot_token}",
                "Content-Type": "application/json"
            }
        )

    def send_message(self, text: str):

        response = self.client.post(
            "https://slack.com/api/chat.postMessage",
            json={
                "channel": os.getenv("SLACK_CHANNEL"),
                "text": text
            }
        )

        response_json = response.json()

        if not response_json.get("ok", False):
            raise Exception(f"Slack error: {response_json.get('error')}")

        return response_json

    def close(self):
        self.client.close()
