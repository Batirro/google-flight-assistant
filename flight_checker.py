import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from email_sender import send_email


# Ładowanie zmienych z .env
load_dotenv()

url = "https://google-flights4.p.rapidapi.com/date-grid/for-roundtrip"

target_departure = input("Podaj datę wylotu (DD.MM.YYYY): ")
FormatedDate = datetime.strptime(target_departure, "%d.%m.%Y")
date_obj = FormatedDate.strftime("%Y-%m-%d")
FormatedArrivalDate = datetime.strptime(date_obj, "%Y-%m-%d") + timedelta(days=1)
arrivalDate = FormatedArrivalDate.strftime("%Y-%m-%d")
TripLenght = int(input("Podaj długość wycieczki: "))

querystring = {
    "departureId": "MUC",
    "arrivalId": "HND",
    "departureDate": date_obj,
    "arrivalDate": arrivalDate,
    "returnDateFrom": datetime.strftime(FormatedDate + timedelta(days=TripLenght), "%Y-%m-%d"),
    "returnDateTo": datetime.strftime(FormatedDate + timedelta(days=TripLenght), "%Y-%m-%d"),
    "currency": "PLN",
    "location": "PL",
    "cabinClass": 1,
}

headers = {
    "x-rapidapi-key": os.getenv("RAPIDAPI_API"),
    "x-rapidapi-host": "google-flights4.p.rapidapi.com",
}

response = requests.get(url, headers=headers, params=querystring)

if response.status_code == 200:
    data = response.json()
    with open("flights_dates.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print("✅ Dane zapisane do 'flights_dates.json'")
else:
    print(f"❌ Error: HTTP {response.status_code}")


with open("flights_dates.json", "r", encoding="utf-8") as file:
    loty_data = json.load(file)

matching_loty = [
    lot
    for lot in loty_data["data"]["prices"]
    if lot["departureDate"] == date_obj
]

if matching_loty:
    subject = 'Loty są dostępne'
    plainText = f"Znaleziono {len(matching_loty)} lotów od {target_departure}."
    send_email(subject=subject, plainText=plainText)
else:
    print(f"Loty na {target_departure} nie są jeszcze dostępne.")
