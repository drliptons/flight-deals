class FlightData:
    def __init__(self, price, origin_city, origin_airport, destination_city, destination_airport, out_date,
                 return_date):
        """
        FlightData class is used for storing temporarily flight deals data.
        :param price: (str) price of the best deal
        :param origin_city: (str) city name of the oirgin airport
        :param origin_airport: (str) origin airport IATA code
        :param destination_city: (str) city name of the destination airport
        :param destination_airport: (str) destination airport IATA code
        :param out_date: (str) first day of the trip
        :param return_date: (str) date of the last day of the trip
        """
        self.price = price
        self.origin_city = origin_city
        self.origin_airport = origin_airport
        self.destination_city = destination_city
        self.destination_airport = destination_airport
        self.out_date = out_date
        self.return_date = return_date
