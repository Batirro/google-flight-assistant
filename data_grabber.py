import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Ładowanie danych z .env
load_dotenv()


def api_connector(target_departure, arrivalDate):
    """Fetch flight information from the Google Flights API for a round trip.

    This function makes a GET request to the Google Flights API to retrieve pricing information
    for round trip flights between specified airports on given dates.

    Args:
        target_departure (str): Departure date in 'YYYY-MM-DD' format
        arrivalDate (str): Return date in 'YYYY-MM-DD' format

    Returns:
        requests.Response: Response object containing the API response data

    Note:
        - Requires RAPIDAPI_API environment variable to be set with valid API key
        - Currently hardcoded for Munich (MUC) to Tokyo (HND) route
        - Uses PLN (Polish Złoty) as currency and Poland as location
        - Cabin class is set to 1 (Economy)
    """
    url = "https://google-flights4.p.rapidapi.com/date-grid/for-roundtrip"

    querystring = {
        "departureId": "MUC",
        "arrivalId": "HND",
        "departureDate": target_departure,
        "arrivalDate": arrivalDate,
        "departureDateFrom": datetime.strftime(datetime.strptime(target_departure, "%Y-%m-%d") - timedelta(days=1), "%Y-%m-%d"),
        "currency": "PLN",
        "location": "PL",
        "cabinClass": 1,
    }

    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_API"),
        "x-rapidapi-host": "google-flights4.p.rapidapi.com",
    }

    response = requests.get(url, headers=headers, params=querystring)
    return response


def pobierz_dane(response):
    """Saves the response data to a JSON file.

    This function checks if the HTTP response was successful (status code 200) and if so,
    saves the JSON response data to 'flights_dates.json' file with proper formatting.
    If the response was not successful, it prints an error message with the status code.

    Args:
        response: HTTP response object containing JSON data

    Returns:
        None

    Side effects:
        - Creates/overwrites 'flights_dates.json' file
        - Prints success/error message to console
    """
    if response.status_code == 200:
        data = response.json()
        with open("flights_dates.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print("✅ Dane zapisane do 'flights_dates.json'")
    else:
        print(f"❌ Error: HTTP {response.status_code}")