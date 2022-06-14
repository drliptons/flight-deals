import requests
import json


class NotificationManager:
    def __init__(self):
        """
        Initialize the NotificationManager class. The class is used for sending messages to a target endpoint.
        The url is saved on the local machine's database.
        """
        with open("account_file.json") as af:
            self.account_file = json.load(af)
        self.url = self.account_file["discord_webhook_stock"]

    def send_msg(self, message):
        """

        :param message: (str) message that want to send
        """
        data = {"content": message}
        response = requests.post(url=self.url, json=data)
        print(response.text)
