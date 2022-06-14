import requests
from flight_data import FlightData
import json


class FlightSearch:
    def __init__(self):
        """
        Initialize the FlightSearch class. This class is responsible for searching flight prices
        """
        # Open local saved account information file
        with open("account_file.json") as af:
            self.account_file = json.load(af)
        # Save endpoint api information to a global variable for later use
        self.endpoint = self.account_file["tq_endpoint"]
        self.api_key = self.account_file["tq_api_key"]

    def get_destination_code(self, city_name):
        """
        Get the airport IATA code
        :param city_name: (str) Full city name
        :return: (str) airport code
        """
        location_endpoint = f"{self.endpoint}/locations/query"
        headers = {"apikey": self.api_key}
        query = {
            "term": city_name,
            "location_types": "city"
        }
        response = requests.get(url=location_endpoint, headers=headers, params=query)
        result = response.json()["locations"]
        code = result[0]["code"]
        return code

    def check_flights(self, origin_city_code, destination_city_code, destination_city_name, from_time, to_time):
        """
        Check flight price from through an api call
        :param origin_city_code: (str) origin airport IATA code
        :param destination_city_code: (str) destination airport IATA code
        :param destination_city_name: (str) destination airport full name
        :param from_time: (str) first day of the traveling period in a DD/MM/YYYY format
        :param to_time: (str) last day of the traveling period in a DD/MM/YYYY format
        :return: (FlightDate) a list containing updated flight information
        """

        # Set up the api call
        headers = {"apikey": self.api_key}
        query = {
            "fly_from": origin_city_code,
            "fly_to": destination_city_code,
            "date_from": from_time.strftime("%d/%m/%Y"),
            "date_to": to_time.strftime("%d/%m/%Y"),
            "nights_in_dst_from": 7,
            "nights_in_dst_to": 28,
            "flight_type": "round",
            "one_for_city": 1,
            "max_stopovers": 0,
            "curr": "EUR"
        }
        # Send an api call
        response = requests.get(url=f"{self.endpoint}/v2/search", headers=headers, params=query)
        try:
            data = response.json()["data"][0]
        except IndexError:
            print(f"No flight found for {destination_city_code} ({destination_city_name}).")
            return None

        # Save updated flight data
        flight_data = FlightData(
            price=data["price"],
            origin_city=data["route"][0]["cityFrom"],
            origin_airport=data["route"][0]["flyFrom"],
            destination_city=data["route"][0]["cityTo"],
            destination_airport=data["route"][0]["flyTo"],
            out_date=data["route"][0]["local_departure"].split("T")[0],
            return_date=data["route"][1]["local_departure"].split("T")[0]
        )
        print(f"{flight_data.destination_city}: €{flight_data.price}")

        # Return flight data
        return flight_data
