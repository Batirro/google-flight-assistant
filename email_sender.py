from azure.communication.email import EmailClient
import os
from dotenv import load_dotenv

#Ładowanie danych z .env
load_dotenv()


def send_email(subject, plainText):
    try:
        connection_string = os.getenv("AZURE_CONNECTION_STRING")
        client = EmailClient.from_connection_string(connection_string)

        message = {
            "senderAddress": "DoNotReply@" + os.getenv("MAIL_SENDER"),
            "recipients": {
                "to": [{"address": os.getenv("MY_MAIL")}]
            },
            "content": {
                "subject": subject,
                "plainText": plainText,
            },
            
        }

        poller = client.begin_send(message)
        result = poller.result()
        print(f"ID wiadomości: {result['id']}")

    except Exception as ex:
        print(ex)
