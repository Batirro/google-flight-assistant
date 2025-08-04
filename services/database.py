import psycopg2
import os
from dotenv import load_dotenv

class Database:
    def __init__(self) -> None:
        load_dotenv()
        self.connection = psycopg2.connect(
            user=os.getenv('DBUSER'),
            password=os.getenv('DBPASSWD'),
            host='localhost',
            port='5432',
            dbname='flight-assistant-database'
        )
        self.cursor = self.connection.cursor()
    # TODO Add function inserting data about flight preferences to database
    # TODO Add function inserting data about notification preferences to database