import json
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
JSON_FILE_PATH = os.path.join(PROJECT_ROOT, 'flights_dates.json')

class FlightChecker:
    
    def sprawdzanie_lotow(self, target_departure: str) -> bool:
        try:
            with open(JSON_FILE_PATH, "r", encoding="utf-8") as file:
                loty_data = json.load(file)
        except FileNotFoundError:
            print(f"Błąd: Plik {JSON_FILE_PATH} nie został znaleziony.")
            return False
        except json.JSONDecodeError:
            print(f"Błąd: Plik {JSON_FILE_PATH} jest pusty lub uszkodzony.")
            return False

        all_flights_groups = loty_data.get("best_flights", []) + loty_data.get("other_flights", [])

        if not all_flights_groups:
            print("Informacja: Brak sekcji 'best_flights' oraz 'other_flights' w odpowiedzi API.")
            return False

        for flight_group in all_flights_groups:
            for lot in flight_group.get("flights", []):
                departure_time = lot.get("departure_airport", {}).get("time", "")
                if departure_time:
                    departure_date = departure_time.split(" ")[0]
                    if departure_date == target_departure:
                        return True

        return False
    
    def info_extractor(self) -> str:
        try:
            with open(JSON_FILE_PATH, "r", encoding="utf-8") as file:
                loty_data = json.load(file)
        except FileNotFoundError:
            print(f"Błąd: Plik {JSON_FILE_PATH} nie został znaleziony.")
            return ""

        link = loty_data.get("search_metadata", []).get("google_flights_url", {})
        return link
