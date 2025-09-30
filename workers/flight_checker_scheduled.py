import time
import sys
import os
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask.templating import render_template
from app import app, db
from services.models import User, FlightPreference
from services.schemas import FlightSearchParams
from services.database import Database
from logic.date_parser import changeMonthForAbbreviation
from logic.email_sender import EmailSender
from logic.flight_checker import FlightChecker
from logic.data_grabber import DataGrabber
from apscheduler.schedulers.blocking import BlockingScheduler

flight_checker = FlightChecker()
email_sender = EmailSender()
data_grabber = DataGrabber()
database = Database()

def get_preferences_for_flight(preference: FlightPreference):
    target_date = preference.target_departure.strftime('%Y-%m-%d')

    if flight_checker.sprawdzanie_lotow(target_date):
        found_flight_data = {
            "departure_airport": preference.departure_airport,
            "arrival_airport": preference.arrival_airport,
            "target_departure": target_date,
            "return_date": preference.return_date.strftime('%Y-%m-%d')
        }
        return found_flight_data
    return None



def check_flights_and_notify():
    with app.app_context():
        today = date.today()
        preferences_to_check = db.session.query(
            FlightPreference,
            User.email
        ).join(
            User, FlightPreference.user_id == User.user_id
        ).filter(
            FlightPreference.target_departure >= today
        ).all()

        print(f"Znaleziono {len(preferences_to_check)} preferencji lotów do sprawdzenia.")

        for preference, user_email in preferences_to_check:
            print(f"Pobieranie danych dla preferencji ID: {preference.preference_id}...")
            search_params = FlightSearchParams(
                departure_airport=preference.departure_airport,
                arrival_airport=preference.arrival_airport,
                target_departure=preference.target_departure.strftime('%Y-%m-%d'),
                return_date=preference.return_date.strftime('%Y-%m-%d'),
                currency="PLN",
                seat_class="1"
            )

            flight_data_response = data_grabber.api_connector(search_params)
            data_grabber.pobierz_dane(flight_data_response)

            flight_info = get_preferences_for_flight(preference)

            if flight_info:
                link = flight_checker.info_extractor()
                departureDate = changeMonthForAbbreviation(flight_info["target_departure"])
                returnDate = changeMonthForAbbreviation(flight_info["return_date"])
                print(f"Znaleziono lot dla {user_email}! Przygotowuję e-mail.")

                html_body = render_template('email-template.html', flight=flight_info, flight_link=link, departure_date=departureDate, return_date=returnDate)

                email_sender.send_email(
                    recipient_email=user_email,
                    subject=f"Znaleźliśmy dla Ciebie lot: {preference.departure_airport} -> {preference.arrival_airport}",
                    html_message=html_body
                    )

                print(f"Usuwanie preferencji ID: {preference.preference_id} po wysłaniu powiadomienia.")
                if not database.delete_flight_preference(preference):
                    print(f"Nie udało się usunąć preferencji ID: {preference.preference_id}")

                time.sleep(2)
            else:
                print(f"Brak lotów pasujących do preferencji ID: {preference.preference_id} dla {user_email}.")

        print("--- Zakończono sprawdzanie lotów ---")

if __name__ == '__main__':
    check_flights_and_notify()
    scheduler = BlockingScheduler(timezone="Europe/Warsaw")
    scheduler.add_job(check_flights_and_notify, 'cron', hour=8, minute=0)
    print("Harmonogram uruchomiony. Naciśnij Ctrl+C, aby zakończyć.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass