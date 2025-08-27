import time
from app import app, db
from services.models import User, FlightPreference, NotificationPreference
from logic.email_sender import EmailSender
from logic.flight_checker import FlightChecker
from apscheduler.schedulers.blocking import BlockingScheduler

flight_checker = FlightChecker()
email_sender = EmailSender()

def get_preferences_for_flight(preference: FlightPreference):
    if flight_checker.sprawdzanie_lotow(preference.arrival_airport):
        found_flight_data = {
            "from": preference.departure_airport,
            "to": preference.arrival_airport,
            "date": preference.target_departure.strftime('%Y-%m-%d')
        }

        return found_flight_data

def check_flights_and_notify():
    with app.app_context():
        preferences_to_check = db.session.query(
            FlightPreference,
            User.email
        ).join(
            User, FlightPreference.user_id == User.user_id
        ).join(
            NotificationPreference, User.user_id == NotificationPreference.user_id
        ).filter(
            NotificationPreference.method == 'email',
            NotificationPreference.enabled == True
        ).all()
    print(f"Znaleziono {len(preferences_to_check)} preferencji lotów do sprawdzenia.")

    for preference, user_email in preferences_to_check:
        flight_info = check_flights_and_notify(preference)
        link = flight_checker.info_extractor()
        if flight_info:
            print(f"Znaleziono lot dla {user_email}! Przygotowuję e-mail.")

            html_body = render_template('email_template.html', flight=flight_info, flight_link=link)

            email_sender.send_email(
                recipient_email=user_email,
                subject=f"Znaleźliśmy dla Ciebie lot: {flight_info['from']} -> {flight_info['to']}",
                html_message=html_body
                )
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