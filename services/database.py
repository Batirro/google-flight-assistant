import psycopg2
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime, date
# TODO: Change PostgreSQL to MySQL or something else or just change how I connect and grab data from it
# TODO: Add models for less error posibilities
class FlightPreferences(BaseModel):
    departure_airport: str = Field(..., min_length=3, max_length=4, description="Kod lotniska wylotu")
    arrival_airport: str = Field(..., min_length=3, max_length=4, description="Kod lotniska przylotu")
    target_departure: str = Field(..., description="Data wylotu")
    return_date: str = Field(..., description="Data powrotu")
    currency: str = Field(default="PLN", pattern="^[A-Z]{3}$", description="Kod waluty")
    seat_class: str = Field(
        default="1", 
        description="Klasa miejsca",
    )
    max_price: Optional[float] = Field(None, gt=0, description="Maksymalna cena")
    preferred_airline: Optional[str] = Field(None, description="Preferowana linia lotnicza")
    
    @field_validator('departure_airport', 'arrival_airport')
    def uppercase_airport(cls, v):
        return v.upper()
    
    @model_validator(mode='after')
    def validate_dates(self):
        try:
            dep_date = datetime.strptime(self.target_departure, '%Y-%m-%d').date()
            ret_date = datetime.strptime(self.return_date, '%Y-%m-%d').date()
            
            if ret_date < dep_date:
                raise ValueError('Data powrotu musi być późniejsza niż data wylotu')
        except ValueError as e:
            if 'musi być późniejsza' in str(e):
                raise
            raise ValueError("Niepoprawny format daty, użyj YYYY-MM-DD.") from e
            
        return self

class Database:
    def __init__(self) -> None:
        load_dotenv()
        self.connection = psycopg2.connect(
            user=os.getenv('DBUSER'),
            password=os.getenv('DBPASSWD'),
            host=os.getenv('HOSTIP'),
            port=os.getenv('DBPORT'),
            dbname='flight_assistant_db'
        )
        self.cursor = self.connection.cursor()

    def users_query(self, email: str | None, telegram_tag: str | None) -> int:
        """
        Dodaje lub aktualizuje użytkownika w bazie danych.
        Zwraca ID użytkownika.
        """
        # Najpierw próbujemy znaleźć istniejącego użytkownika
        select_query = """
        SELECT user_id FROM users 
        WHERE (email = %s AND email IS NOT NULL) 
        OR (telegram_tag = %s AND telegram_tag IS NOT NULL)
        """
        
        self.cursor.execute(select_query, (email, telegram_tag))
        existing_user = self.cursor.fetchone()
        
        if existing_user:
            # Aktualizuj istniejącego użytkownika
            update_query = """
            UPDATE users 
            SET email = COALESCE(%s, email),
                telegram_tag = COALESCE(%s, telegram_tag)
            WHERE user_id = %s
            RETURNING user_id
            """
            self.cursor.execute(update_query, (email, telegram_tag, existing_user[0]))
        else:
            # Dodaj nowego użytkownika
            insert_query = """
            INSERT INTO users (email, telegram_tag) 
            VALUES (%s, %s)
            RETURNING user_id
            """
            self.cursor.execute(insert_query, (email, telegram_tag))
        
        result = self.cursor.fetchone()
        if result is None:
            raise ValueError("Nie udało się pobrać ID użytkownika z bazy danych")
        user_id = result[0]
        self.connection.commit()
        
        return user_id

    def notification_preferences_query(self, user_id: int, method: str) -> None:
        """
        Inserts or updates notification preferences for a specific user.
        
        Args:
            user_id: The ID of the user in the database
            method: The notification method to be set
            
        The function sets the 'enabled' status as True by default for the specified notification method.
        Closes database connection after execution.
        """
        insert_query = """
        INSERT INTO notification_preferences(user_id, method, enabled) VALUES (%s, %s, %s)
        """
        # Executing query
        self.cursor.execute(insert_query, (user_id, method, True))
        # Confirming changes
        self.connection.commit()
        
        self.cursor.close()
        self.connection.close()


    def flight_preferences(self, user_id: int, prefs: FlightPreferences) -> None:
        """
        Inserts flight preferences for a specific user into the database.
        
        Args:
            user_id: The ID of the user in the database
            prefs: Dictionary containing flight preferences where keys are column names
                  and values are the preference values to be stored
                  
        The function:
        1. Creates a dynamic SQL query based on the preference dictionary keys
        2. Uses placeholder values (%s) for safe SQL parameter insertion
        3. Executes the query with user_id and preference values
        4. Closes database connection after execution
        """
        # Preferences parametres are implemented and passed trought this
        prefs_dict = prefs.model_dump(exclude_none=True)
    
        # Konwertuj daty na stringi dla bazy danych
        for key, value in prefs_dict.items():
            if isinstance(value, date):
                prefs_dict[key] = value.strftime('%Y-%m-%d')
        
        # Preferences parameters are implemented and passed through this
        columns = ['user_id'] + list(prefs_dict.keys())
        values_placeholder = ['%s'] * len(columns)
        values = [user_id] + list(prefs_dict.values())
    
        insert_query = f"""
        INSERT INTO flight_preferences ({', '.join(columns)}) VALUES ({', '.join(values_placeholder)})
        """
    
        # Executing query
        self.cursor.execute(insert_query, values)
        # Confirming changes
        self.connection.commit()
    
        self.cursor.close()
        self.connection.close()