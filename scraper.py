import requests
import json
from datetime import datetime, timedelta


url = "https://google-flights4.p.rapidapi.com/date-grid/for-roundtrip"

target_departure = "02.08.2025"  #input("Podaj datę wylotu (DD.MM.YYYY): ")
FormatedDate = datetime.strptime(target_departure, "%d.%m.%Y")
date_obj = FormatedDate.strftime("%Y-%m-%d")
FormatedArrivalDate = datetime.strptime(date_obj, "%Y-%m-%d") + timedelta(days=1)
arrivalDate = FormatedArrivalDate.strftime("%Y-%m-%d")


querystring = {
    "departureId": "MUC",
    "arrivalId": "HND",
    "departureDate": date_obj,
    "arrivalDate": arrivalDate,
    "currency": "PLN",
    "cabinClass": 1,
}

headers = {
    "x-rapidapi-key": "b5fbffba64msh669c8db73430afbp12758fjsn2dd2b16c5ad5",
    "x-rapidapi-host": "google-flights4.p.rapidapi.com",
}

response = requests.get(url, headers=headers, params=querystring)

if response.status_code == 200:
    data = response.json()
    with open("loty.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print("✅ Dane zapisane do 'loty.json'")
else:
    print(f"❌ Error: HTTP {response.status_code}")


with open("loty.json", "r", encoding="utf-8") as file:
    loty_data = json.load(file)

matching_loty = [
    lot
    for lot in loty_data["data"]["prices"]
    if lot["departureDate"] == date_obj
]

if matching_loty:
    print(f"Znaleziono {len(matching_loty)} lotów od {target_departure}:")
    for lot in matching_loty:
        print(f"  - Powrót: {lot['returnDate']}, Cena: {lot['price']} zł.")
else:
    print(f"Loty na {target_departure} nie są jeszcze dostępne.")
