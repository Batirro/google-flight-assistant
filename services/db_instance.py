from flask_sqlalchemy import SQLAlchemy
import telegram.ext
from config.config import DevelopmentConfig

db = SQLAlchemy()

# Inicjalizacja bota Telegram
# Upewnij się, że TELEGRAM_BOT_TOKEN jest ustawiony w pliku config.py
telegram_bot = (
    telegram.ext.Application.builder()
    .token(DevelopmentConfig.TELEGRAM_BOT_TOKEN)
    .build()
)
