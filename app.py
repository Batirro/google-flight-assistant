from flask import Flask, render_template, request
from logic.email_sender import EmailSender, TelegramSender
from logic.flight_checker import FlightChecker
from logic.data_grabber import DataGrabber
from logic.date_parser import DataParser
from services.database import Database
from services.schemas import FlightSearchParams, FlightPreferences, SeatClassEnum
from config.config import DevelopmentConfig
from services.db_instance import db


app = Flask(__name__)

app.config.from_object(DevelopmentConfig)
db.init_app(app)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        database = Database()
        try:
            form_data = {
                "target_departure": request.form.get("departure_date", ""),
                "return_date": request.form.get("return_date", ""),
                "departure_airport": request.form.get("departure_airport", ""),
                "arrival_airport": request.form.get("arrival_airport", ""),
                "currency": request.form.get("currency", ""),
                "seat_class": request.form.get("seat_class", "")
            }

            flight_preferences = FlightSearchParams(**form_data)

            # Sprawdzamy powiadomienia
            email_notify = request.form.get("email_notify") == "on"
            telegram_notify = request.form.get("telegram_notify") == "on"
            email = request.form.get("email", "").strip()
            telegram_tag = request.form.get("telegram_tag", "").strip()

            # Walidacja danych kontaktowych
            if not (email_notify or telegram_notify):
                return render_template("form.html", error="Wybierz przynajmniej jeden sposób powiadomień")
            if email_notify and not email:
                return render_template("form.html", error="Podaj adres email")
            if telegram_notify and not telegram_tag:
                return render_template("form.html", error="Podaj tag Telegram")

            # Pobieramy dane o lotach
            data_grabber = DataGrabber()
            response = data_grabber.api_connector(flight_preferences)

            if not response:
                return render_template("form.html", error="Nie udało się pobrać danych o lotach")

            data_grabber.pobierz_dane(response)

            user_id, user_saved = database.users_query(
                email=email if email_notify else None,
                telegram_tag=telegram_tag if telegram_notify else None
            )

            if not user_saved or user_id is None:
                return render_template("form.html", error="Nie udało się zapisać danych użytkownika.")

            notification_saved = True
            if email_notify:
                notification_saved &= database.notification_preferences_query(user_id, "email")
            if telegram_notify:
               notification_saved &= database.notification_preferences_query(user_id, "telegram")

            if not notification_saved:
                return render_template("form.html", error="Nie udało się zapisać preferencji powiadomień")

            # Zapisujemy preferencje lotów
            flight_prefs = FlightPreferences(
                target_departure=flight_preferences.target_departure,
                return_date=flight_preferences.return_date,
                departure_airport=flight_preferences.departure_airport,
                arrival_airport=flight_preferences.arrival_airport,
                currency=flight_preferences.currency,
                seat_class=SeatClassEnum.from_form(flight_preferences.seat_class),
                max_price=None,
                preferred_airline=None
            )
            flight_prefs_saved = database.flight_preferences(user_id, flight_prefs)

            if not flight_prefs_saved:
                return render_template("form.html", error="Nie udało się zapisać preferencji lotu.")

            return render_template("result.html", result="Wszystkie preferencje poprawnie zapisane")

        except Exception as e:
            print(f"Wystąpił błąd: {str(e)}")  # Debug
            return render_template("form.html", error=f"Wystąpił błąd: {str(e)}")

    return render_template("form.html")
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
