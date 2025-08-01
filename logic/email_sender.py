from azure.communication.email import EmailClient
import os
from dotenv import load_dotenv
import telepot
#Ładowanie danych z .env
load_dotenv()

class EmailSender:
    def __init__(self):
        self.connection_string = os.getenv("AZURE_CONNECTION_STRING")
        if not self.connection_string:
            raise ValueError("AZURE_CONNECTION_STRING environment variable is not set")
        self.client = EmailClient.from_connection_string(self.connection_string)
        mail_sender = os.getenv("MAIL_SENDER")
        if not mail_sender:
            raise ValueError("MAIL_SENDER environment variable is not set")
        self.sender_address = "DoNotReply@" + mail_sender
        self.recipient = os.getenv("MY_MAIL")

    def send_email(self, subject, plainText):
        try:
            message = {
                "senderAddress": self.sender_address,
                "recipients": {
                    "to": [{"address": self.recipient}]
                },
                "content": {
                    "subject": subject,
                    "plainText": plainText,
                }
            }

            poller = self.client.begin_send(message)
            result = poller.result()
            print(f"ID wiadomości: {result['id']}")

        except Exception as ex:
            print(ex)

class TelegramSender:
    def __init__(self):
        self.chat_id = os.getenv('TELEGRAM_BOT_CHAT_ID')
        self.token = os.getenv('TELEGRAM_BOT_API')
        self.bot = telepot.Bot(token=self.token)
    def send_bot_massage(self, text):
        self.bot.sendMessage(self.chat_id, text)


