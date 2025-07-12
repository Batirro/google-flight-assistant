import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

class DataGrabber:
    def __init__(self):
        """Initialize DataGrabber class and load environment variables."""
        load_dotenv()

    def api_connector(self, target_departure, arrivalDate):
        """Fetch flight information from the Google Flights API for a round trip.

        Args:
            target_departure (str): Departure date in 'YYYY-MM-DD' format
            arrivalDate (str): Return date in 'YYYY-MM-DD' format

        Returns:
            requests.Response: Response object containing the API response data
        """
        url = "https://google-flights4.p.rapidapi.com/date-grid/for-roundtrip"

        querystring = {
            "departureId": "MUC",
            "arrivalId": "HND",
            "departureDate": target_departure,
            "arrivalDate": arrivalDate,
            "departureDateFrom": datetime.strftime(datetime.strptime(target_departure, "%Y-%m-%d") - timedelta(days=1), "%Y-%m-%d"),
            "currency": "PLN",
            "location": "PL",
            "cabinClass": 1,
        }

        headers = {
            "x-rapidapi-key": os.getenv("RAPIDAPI_API"),
            "x-rapidapi-host": "google-flights4.p.rapidapi.com",
        }

        response = requests.get(url, headers=headers, params=querystring)
        return response

    def pobierz_dane(self, response):
        """Saves the response data to a JSON file.

        Args:
            response: HTTP response object containing JSON data

        Returns:
            None
        """
        if response.status_code == 200:
            data = response.json()
            with open("flights_dates.json", "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            print("✅ Dane zapisane do 'flights_dates.json'")
        else:
            print(f"❌ Error: HTTP {response.status_code}")
