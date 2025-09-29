import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

    DB_USER = os.getenv('DBUSER')
    DB_PASSWORD = os.getenv('DBPASSWD')
    DB_HOST = os.getenv('HOSTIP')
    DB_PORT = os.getenv('DBPORT')
    DB_NAME = os.getenv('DBNAME')

    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"