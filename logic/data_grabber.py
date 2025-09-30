import os
import json
from dotenv import load_dotenv
from serpapi import GoogleSearch
from services.schemas import FlightSearchParams

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
JSON_FILE_PATH = os.path.join(PROJECT_ROOT, 'flights_dates.json')

class DataGrabber:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("SERP_API")
        if not self.api_key:
            raise ValueError("Brak klucza API SERP_API w zmiennych środowiskowych")

    def api_connector(self, flight_params: FlightSearchParams):
        params = {
            "engine": "google_flights",
            "departure_id": flight_params.departure_airport,
            "arrival_id": flight_params.arrival_airport,
            "outbound_date": flight_params.target_departure,
            "return_date": flight_params.return_date,
            "currency": flight_params.currency,
            "hl": "pl",
            "travel_class": flight_params.seat_class,
            "api_key": self.api_key,
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        return results
    
    def pobierz_dane(self, response):
        data = response
        if "error" in data:
            print("!!! Otrzymano błąd z API SerpApi !!!")
            print(data["error"])
        with open(JSON_FILE_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print(f"✅ Dane zapisane do '{JSON_FILE_PATH}'")