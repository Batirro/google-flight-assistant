import os
import json
from dotenv import load_dotenv
from serpapi import GoogleSearch

class DataGrabber:
    def __init__(self):
        load_dotenv()

    def api_connector(self, target_departure, return_date):
        params = {
            "engine": "google_flights",
            "departure_id": "CDG",
            "arrival_id": "AUS",
            "outbound_date": target_departure,
            "return_date": return_date,
            "currency": "PLN",
            "hl": "pl",
            "api_key": os.getenv("SERP_API")
            }

        search = GoogleSearch(params)
        results = search.get_dict()
        return results

    def pobierz_dane(self, response):
        data = response
        with open("flights_dates.json", "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
        print("✅ Dane zapisane do 'flights_dates.json'")
