from azure.communication.email import EmailClient
import os
from dotenv import load_dotenv
#Ładowanie danych z .env
load_dotenv()

class EmailSender:
    def __init__(self):
        self.connection_string = os.getenv("AZURE_CONNECTION_STRING")
        self.client = EmailClient.from_connection_string(self.connection_string)
        self.sender_address = "DoNotReply@" + os.getenv("MAIL_SENDER")
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
