import psycopg2
import os
from dotenv import load_dotenv

class Database:
    def __init__(self) -> None:
        load_dotenv()
        self.connection = psycopg2.connect(
            user=os.getenv('DBUSER'),
            password=os.getenv('DBPASSWD'),
            host=os.getenv('HOSTIP'),
            port=os.getenv('DBPORT'),
            dbname='flight-assistant-database'
        )
        self.cursor = self.connection.cursor()

    def users_query(self, email: str, telegram_tag:str) -> int:
        """
        Inserts a new user into the database or does nothing if user already exists.
        
        Args:
            email: User's email address
            telegram_tag: User's telegram tag/handle
            
        Returns:
            user_id: The ID of the user in the database
            
        The function closes database connection after execution.
        """
        insert_query = """
        INSERT INTO users (email, telegram_tag) VALUES (%s, %s)
        ON CONFLICT (email) DO NOTHING
        """
        # Executing query
        self.cursor.execute(insert_query, (email, telegram_tag))
        # Confirming changes
        self.connection.commit()
        #Fetching user_id for use in the tabels using this key
        user_id = self.cursor.fetchone()[0] # type: ignore

        self.cursor.close()
        self.connection.close()

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
    
    def flight_preferences(self, user_id: int, prefs: dict) -> None:
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
        columns = ['user_id'] + list(prefs.keys())
        values_placeholder = ['%s'] * len(columns)
        values = [user_id] + list(prefs.values())
        insert_query = f"""
        INSERT INTO flight_preferences ({', '.join(columns)}) VALUES ({', '.join(values_placeholder)})
        """
        # Executing query
        self.cursor.execute(insert_query, values)
        # Confirming changes
        self.connection.commit()

        self.cursor.close()
        self.connection.close()