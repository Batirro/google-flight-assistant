import os
import json
from dotenv import load_dotenv
from serpapi import GoogleSearch

class DataGrabber:
    def __init__(self):
        load_dotenv()

    def api_connector(self, target_departure, return_date, departure_airport, arrival_airport, currency):
        params = {
            "engine": "google_flights",
            "departure_id": departure_airport,
            "arrival_id": arrival_airport,
            "outbound_date": target_departure,
            "return_date": return_date,
            "currency": currency,
            "hl": "pl",
            "api_key": os.getenv("SERP_API")
            }

        search = GoogleSearch(params)
        results = search.get_dict()
        return results
    # TODO: Switch to something safer and more relaiable than basic .json file
    def pobierz_dane(self, response):
        data = response
        with open("flights_dates.json", "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
        print("✅ Dane zapisane do 'flights_dates.json'")
