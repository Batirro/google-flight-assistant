import json


class FlightChecker:
    
    def sprawdzanie_lotow(self, target_departure: str) -> bool:
        with open("flights_dates.json", "r",encoding="utf-8") as file:
            loty_data = json.load(file)

        for flight_group in loty_data.get("best_flights", []):
            for lot in flight_group.get("flights", []):
                departure_time = lot.get("departure_airport", {}).get("time", "")
                departure_date = departure_time.split(" ")[0] if departure_time else ""

                if departure_date == target_departure:
                    return True

        return False
    
    def info_extractor(self) -> str:
        with open("flights_dates.json", "r", encoding="utf-8") as file:
            loty_data = json.load(file)
        
        link = loty_data.get("search_metadata", []).get("google_flights_url", {})
        return link
                
        

