from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator
from typing import Optional, Any
from datetime import datetime, date
from enum import Enum


class SeatClassEnum(str, Enum):
    ECONOMY = "ECONOMY"
    PREMIUM_ECONOMY = "PREMIUM_ECONOMY"
    BUSINESS = "BUSINESS"
    FIRST = "FIRST"

    @classmethod
    def from_form(cls, value: str):
        mapping = {
            "1": cls.ECONOMY,
            "2": cls.PREMIUM_ECONOMY,
            "3": cls.BUSINESS,
            "4": cls.FIRST
        }
        if value not in mapping:
            raise ValueError("Nieprawidłowa klasa siedzenia.")
        return mapping[value]


class FlightSearchParams(BaseModel):
    # Wszystkie pola przyjmują stringi, bo to właśnie dostajemy z formularza HTML
    target_departure: str = Field(..., description="Data wylotu w formacie YYYY-MM-DD")
    return_date: str = Field(..., description="Data powrotu w formacie YYYY-MM-DD")
    departure_airport: str = Field(..., min_length=3, max_length=4, description="Kod IATA lotniska wylotu")
    arrival_airport: str = Field(..., min_length=3, max_length=4, description="Kod IATA lotniska przylotu")
    currency: str = Field(default="PLN", pattern="^[A-Z]{3}$")
    seat_class: str = Field(default="1", pattern="^[1-4]$")

    @field_validator('departure_airport', 'arrival_airport')
    @classmethod
    def validate_airport_code(cls, v):
            """
            Waliduje kod IATA lotniska używając biblioteki airports-py
            """
            if not v:
                raise ValueError("Kod lotniska nie może być pusty")

            v = v.strip().upper()

            if len(v) != 3:
                raise ValueError("Kod IATA musi mieć dokładnie 3 znaki")

            if not v.isalpha():
                raise ValueError("Kod IATA może zawierać tylko litery")

            try:
                from airports import airport_data
                airports_list = airport_data.get_airport_by_iata(v)

                if not airports_list or len(airports_list) == 0:
                    raise ValueError(f"Nieznany kod lotniska IATA: {v}")

                return v

            except ImportError:
                print("Ostrzeżenie: airports-py nie jest dostępne, pomijam walidację IATA")
                return v
            except ValueError:
                raise
            except Exception as e:
                raise ValueError(f"Błąd podczas walidacji kodu lotniska {v}: {str(e)}")
    @model_validator(mode='after')
    def validate_dates_and_airports(self) -> 'FlightSearchParams':
        """
        Waliduje daty i sprawdza czy lotniska wylotu i przylotu są różne
        """
        # Walidacja dat
        try:
            dep_date = datetime.strptime(self.target_departure, '%Y-%m-%d')
            ret_date = datetime.strptime(self.return_date, '%Y-%m-%d')

            if ret_date < dep_date:
                raise ValueError('Data powrotu musi być późniejsza niż data wylotu')

            # Sprawdź czy daty nie są w przeszłości
            today = datetime.now().date()
            if dep_date.date() < today:
                raise ValueError('Data wylotu nie może być w przeszłości')

        except ValueError as e:
            if any(phrase in str(e) for phrase in ['musi być późniejsza', 'przeszłości']):
                raise
            raise ValueError('Nieprawidłowy format daty. Użyj formatu YYYY-MM-DD') from e

        # Walidacja lotnisk
        if self.departure_airport == self.arrival_airport:
            raise ValueError('Lotnisko wylotu i przylotu muszą być różne')

        return self

    @field_validator('seat_class')
    @classmethod
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


class FlightPreferences(BaseModel):
    departure_airport: str = Field(..., min_length=3, max_length=4, description="Kod lotniska wylotu")
    arrival_airport: str = Field(..., min_length=3, max_length=4, description="Kod lotniska przylotu")
    target_departure: str = Field(..., description="Data wylotu w formacie YYYY-MM-DD")
    return_date: str = Field(..., description="Data powrotu w formacie YYYY-MM-DD")
    currency: str = Field(default="PLN", pattern="^[A-Z]{3}$", description="Kod waluty")
    seat_class: SeatClassEnum = Field(default=SeatClassEnum.ECONOMY, description="Klasa miejsca")
    max_price: Optional[float] = Field(None, gt=0, description="Maksymalna cena")
    preferred_airline: Optional[str] = Field(None, description="Preferowana linia lotnicza")

    @field_validator('departure_airport', 'arrival_airport')
    @classmethod
    def validate_airport_code(cls, v):
        """
        Waliduje kod IATA lotniska używając biblioteki airports-py
        """
        if not v:
            raise ValueError("Kod lotniska nie może być pusty")

        v = v.strip().upper()

        if len(v) != 3:
            raise ValueError("Kod IATA musi mieć dokładnie 3 znaki")

        if not v.isalpha():
            raise ValueError("Kod IATA może zawierać tylko litery")

        try:
            from airports import airport_data
            airports_list = airport_data.get_airport_by_iata(v)

            if not airports_list or len(airports_list) == 0:
                raise ValueError(f"Nieznany kod lotniska IATA: {v}")

            return v

        except ImportError:
            print("Ostrzeżenie: airports-py nie jest dostępne, pomijam walidację IATA")
            return v
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Błąd podczas walidacji kodu lotniska {v}: {str(e)}")

    @model_validator(mode='after')
    def validate_dates_and_airports(self):
        """
        Waliduje daty i lotniska
        """
        try:
            dep_date = datetime.strptime(self.target_departure, '%Y-%m-%d').date()
            ret_date = datetime.strptime(self.return_date, '%Y-%m-%d').date()

            if ret_date < dep_date:
                raise ValueError('Data powrotu musi być późniejsza niż data wylotu')
        except ValueError as e:
            if 'musi być późniejsza' in str(e):
                raise
            raise ValueError("Niepoprawny format daty, użyj YYYY-MM-DD.") from e

        if self.departure_airport == self.arrival_airport:
            raise ValueError('Lotnisko wylotu i przylotu muszą być różne')

        return self


# Schemat do tworzenia preferencji
class FlightPreferenceCreate(FlightPreferences):
    pass

# Schemat do zwracania preferencji z API
class FlightPreference(FlightPreferences):
    preference_id: int
    user_id: int

    class Config:
        from_attributes = True

# Schemat do tworzenia użytkownika
class UserCreate(BaseModel):
    email: EmailStr

# Schemat do wyświetlania użytkownika (zawiera ID i listę jego alertów)
class User(UserCreate):
    user_id: int
    flight_preferences: list[FlightPreference] = []

    class Config:
        from_attributes = True
