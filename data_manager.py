import time

from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
import os
from datetime import datetime, timedelta

from flight_search import FlightSearch


class DataManager:
    def __init__(self):
        """
        Initialize DataManager class
        """
        self.data_sheet = []  # empty array to contain flights data
        self.flight_search = FlightSearch()

        # Read and init credentials
        with open("account_file.json") as af:
            self.account_file = json.load(af)

        # Setup google api
        self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        self.credentials = service_account.Credentials.from_service_account_file(
            "service_file.json", scopes=self.scopes)
        self.service = build("sheets", "v4", credentials=self.credentials)

        # Call google sheet api
        self.sheet = self.service.spreadsheets()
        result = self.sheet.values().get(spreadsheetId=self.account_file["spread_sheet_id"],
                                         range=self.account_file["spreadsheet_range"]).execute()

        # Store retrieved google sheet data
        sheet_data = result.get('values', {})

        # Remove old data
        try:
            os.remove("data.json")
        except FileNotFoundError:
            pass

        # Create a temporal file to store the data on local machine
        try:
            with open("data.json", "r") as data_file:
                json.load(data_file)
        except FileNotFoundError:
            with open("data.json", "w") as data_file:
                json.dump(sheet_data, data_file, indent=4)
        except json.decoder.JSONDecodeError:
            with open("data.json", "w") as data_file:
                json.dump(sheet_data, data_file, indent=4)

        self.data_sheet = sheet_data  # save the tmp data file to a global variable
        self.verification_alert = []  # contain new (updated) flight information to send an alert
        self.new_lowest_price = []  # contain new price
        self.is_updating_data = True  # parameter to check if the price update is running
        self.is_error = False  # Terminate and log the error to console for future debugging

    def verify_data(self):
        """
        Verify the data validity in the database
        :return: None
        """
        update_city_codes = 0  # count of city names that need to be updated
        row = 0  # row count
        for city in self.data_sheet:
            # Verify correctness of city names
            try:
                # Check origin city name
                if city[1] == "":
                    self.data_sheet[row][1] = FlightSearch.get_destination_code(city[0])
                    update_city_codes += 1
                # Check destination city name
                if city[3] == "":
                    self.data_sheet[row][3] = FlightSearch.get_destination_code(city[2])
                    update_city_codes += 1
            except:
                # City name may not exist
                self.is_error = True
                self.verification_alert.append("City name error")
                print(self.verification_alert)
                return

            row += 1

        # Update city names if required
        if update_city_codes != 0:
            self.update_city_name()
        else:
            self.is_updating_data = False

        # Show error if no data exist in the database
        if row == 0:
            alert_msg = "There are no cities in your list. Please enter at least on city to use this program"
            self.is_error = True
            self.verification_alert.append(alert_msg)

    def check_price(self):
        """
        Check the price of the flight routes contained in the database
        :return: None
        """
        # Waiting to verify data
        req_time_out = 10
        while self.is_updating_data:
            time.sleep(2)
            req_time_out -= 1
            if req_time_out < 0:
                # Send error msg to discord
                self.is_error = True
                print("Error: can't retrieve flight data from server")
                return

        # Set data variables
        tomorrow = datetime.now() + timedelta(days=1)
        six_month_from_today = datetime.now() + timedelta(days=(6 * 30))

        # Check flight prices
        destination_count = 0
        for route in self.data_sheet:
            # Check if origin city is given
            if route[1] == "":
                origin_iata = self.account_file["default_origin_IATA_code"]
            else:
                origin_iata = route[1]

            # skip first row, because of the header
            if destination_count > 0:
                flight = self.flight_search.check_flights(
                    origin_city_code=origin_iata,
                    destination_city_code=route[3],
                    destination_city_name=route[2],
                    from_time=tomorrow,
                    to_time=six_month_from_today
                )

                # Check if flight is found
                if flight is not None:
                    route[6] = flight.price
                    route[7] = f"{tomorrow.strftime('%d/%m/%Y')}"
                    if len(route) == 9:
                        route[8] = " "
                    else:
                        route.append(" ")

                    # Check lowest price
                    if int(flight.price) < int(route[4]):
                        route[4] = flight.price
                        route[5] = f"{tomorrow.strftime('%d/%m/%Y')}"

                        # Set the msg for sending a notification
                        msg = f"Low price alert 🥳 ! 💶 Only €{flight.price} to fly from 🛫  {flight.origin_city}-"\
                              f"{flight.origin_airport} to 🛬 {flight.destination_city}-{flight.destination_airport}, "\
                              f"🗓 from {flight.out_date} to {flight.return_date}."

                        # Save new lowest price
                        self.new_lowest_price.append(msg)
                else:
                    route[6] = 0
                    route[7] = f"{tomorrow.strftime('%d/%m/%Y')}"
                    if len(route) == 9:
                        route[8] = f"Flight not found on {datetime.today().strftime('%d/%m/%Y')}"
                    else:
                        route.append(f"Flight not found on {datetime.today().strftime('%d/%m/%Y')}")
            destination_count += 1

    def update_destination_price(self):
        """
        Update destination price to the remote database
        """
        with open("data.json", "w") as data_file:
            json.dump(self.data_sheet, data_file, indent=4)
        body = {
            "values": self.data_sheet
        }
        request = self.service.spreadsheets().values().update(
            spreadsheetId=self.account_file["spread_sheet_id"],
            range=self.account_file["spreadsheet_range"],
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()

    def update_city_name(self):
        """
        Update the city names to the database on the local machine
        """
        with open("data.json", "w") as data_file:
            json.dump(self.data_sheet, data_file, indent=4)

        self.is_updating_data = False
