import os
import json
from datetime import datetime
from dotenv import load_dotenv
from serpapi import GoogleSearch
from pydantic import BaseModel, Field, field_validator, model_validator

class FlightSearchParams(BaseModel):
    target_departure: str = Field(..., description="Data wylotu")
    return_date: str = Field(..., description="Data powrotu")
    departure_airport: str = Field(..., min_length=3, max_length=4, description="Kod lotniska wylotu")
    arrival_airport: str = Field(..., min_length=3, max_length=4, description="Kod lotniska przylotu")
    currency: str = Field(default="PLN", pattern="^[A-Z]{3}$", description="Kod waluty ISO 4217")
    seat_class: str = Field(
        default="1", 
        description="Klasa miejsca (1-ekonomiczna, 2-premium, 3-biznes, 4-pierwsza)",
        pattern="^[1-4]$"
    )
    
    @field_validator('departure_airport', 'arrival_airport')
    def validate_airport_code(cls, v):
        return v.upper()
    
    @model_validator(mode='after')
    def validate_dates(self) -> 'FlightSearchParams':
        try:
            ret_date = datetime.strptime(self.return_date, '%Y-%m-%d')
            dep_date = datetime.strptime(self.target_departure, '%Y-%m-%d')
            
            if ret_date < dep_date:
                raise ValueError('Data powrotu musi być późniejsza niż data wylotu')
                
            return self
            
        except ValueError as e:
            raise ValueError('Nieprawidłowy format daty. Użyj formatu YYYY-MM-DD') from e
    
    @field_validator('seat_class')
    def convert_seat_class(cls, v):
        seat_class_mapping = {
            "1": "1",  # Economy
            "2": "2",  # Premium economy
            "3": "3",  # Business
            "4": "4"   # First
        }
        if v not in seat_class_mapping:
            raise ValueError("Nieprawidłowa klasa siedzenia. Wybierz wartość od 1 do 4.")
        return seat_class_mapping[v]

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
        with open("flights_dates.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print("✅ Dane zapisane do 'flights_dates.json'")  