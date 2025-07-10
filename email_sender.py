import os
from mailjet_rest import Client
from dotenv import load_dotenv

# Ładowanie API_KEY z .env
load_dotenv()

API_KEY_PUBLIC = os.getenv("MAIL_JET_SENDER_PUBLIC")
API_KEY_PRIVATE = os.getenv("MAIL_JET_SENDER_PRIVATE")
MAIL = os.getenv("MY_MAIL")
SENDER_MAIL = os.getenv("MAIL_JET_SENDER")

def wysli_mail(sender_email, recipient_email, subject, message):
    mailjet = Client(auth=(API_KEY_PUBLIC,API_KEY_PRIVATE), version='v3.1')

    data = {
        'Messeges': [
            {
                "From": {"Email": sender_email, "Name": "Twój Nadawca"},
                "To": [{"Email": recipient_email, "Name": "Odbiorca"}],
                "Subject": subject,
                "TextPart": message
            }
        ]
    }

    try:
            response = mailjet.send.create(data=data)
            if response.status_code == 200:
                print("E-mail wysłany pomyślnie!")
                print("Status:", response.json())
            else:
                print("Błąd wysyłki:", response.status_code)
                print("Odpowiedź API:", response.json())
    except Exception as e:
            print("Krytyczny błąd:", str(e))

if __name__ == "__main__":
    wysli_mail(
        sender_email=SENDER_MAIL,  # Musi być zweryfikowany w Mailjet!
        recipient_email=MAIL,
        subject="Test Mailjet z Pythonem",
        message="To jest testowa wiadomość wysłana przez Mailjet API."
    )
