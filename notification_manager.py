import requests
import json


class NotificationManager:
    def __init__(self):
        with open("account_file.json") as af:
            self.account_file = json.load(af)
        self.url = self.account_file["discord_webhook_stock"]

    def send_msg(self, message):
        data = {"content": message}
        response = requests.post(url=self.url, json=data)
        print(response.text)
