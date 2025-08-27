import os
import telepot
import smtplib
import ssl
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
#Ładowanie danych z .env
load_dotenv()

class EmailSender:
    def send_email(self, recipient_email, subject, html_message):

        sender_email = os.getenv('MAIL_SENDER')
        sender_passwd = os.getenv('MAIL_PASSWD')
        sender_name = os.getenv('MAIL_SENDER_NAME')

        if not sender_email or not sender_passwd:
            return False, "Nie znaleziono danych logowania w zmiennych środowiskowych."

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = formataddr((sender_name, sender_email))
        message["To"] = recipient_email

        part_html = MIMEText(html_message, "html")
        message.attach(part_html)

        context = ssl.create_default_context()

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
               server.login(sender_email, sender_passwd)
               server.sendmail(
                   sender_email, recipient_email, message.as_string()
               ) 
            return True, "Email został wysłany pomyślnie"
        except Exception as e:
            return False, f"Wystąpił błąd: {e}"

class TelegramSender:
    def __init__(self):
        self.chat_id = os.getenv('TELEGRAM_BOT_CHAT_ID')
        self.token = os.getenv('TELEGRAM_BOT_API')
        self.bot = telepot.Bot(token=self.token)
    def send_bot_massage(self, text):
        self.bot.sendMessage(self.chat_id, text)


