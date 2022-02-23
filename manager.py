from data_manager import DataManager
from notification_manager import NotificationManager


class Manager:
    def __init__(self):
        # 1) Initialize and retrieve existing data
        self.data_manager = DataManager()
        self.notification_manager = NotificationManager()
        # 2) Verify Data
        DataManager.verify_data(self.data_manager)
        # 3) Check current data
        self.check_price()
        # 4) Update price on local and google sheet
        self.update_price()
        # 4) Send notification
        self.send_notification()

    def check_price(self):
        if not self.data_manager.is_error:
            self.data_manager.check_price()

    def update_price(self):
        if not self.data_manager.is_error:
            self.data_manager.update_city_name()
            self.data_manager.update_destination_price()

    def send_notification(self):
        if self.data_manager.is_error:
            print("Has error msg")
            for m in self.data_manager.verification_alert:
                self.notification_manager.send_msg(m)
        else:
            if len(self.data_manager.new_lowest_price) < 1:
                self.notification_manager.send_msg("There are no good deals just yet 😭")
            else:
                for m in self.data_manager.new_lowest_price:
                    self.notification_manager.send_msg(m)
