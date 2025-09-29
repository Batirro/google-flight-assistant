from flask import Flask, render_template, request, jsonify
from logic.data_grabber import DataGrabber
from services.database import Database
from logic.airport_search import AirportSearch
from services.schemas import FlightSearchParams, FlightPreferences, SeatClassEnum
from config.config import DevelopmentConfig
from services.db_instance import db
from typing import Tuple, Optional, Any

app = Flask(__name__)

app.config.from_object(DevelopmentConfig)
db.init_app(app)

def validate_flight_params(form_data: dict) -> Tuple[Optional[FlightSearchParams], Optional[str]]:
    """
    Waliduje parametry lotu używając Pydantic

    Returns:
        Tuple[FlightSearchParams lub None, error_message lub None]
    """
    try:
        flight_preferences = FlightSearchParams(**form_data)

        print(f"🛫 Zwalidowane parametry wyszukiwania:")
        print(f"   Wylot: {flight_preferences.departure_airport}")
        print(f"   Przylot: {flight_preferences.arrival_airport}")
        print(f"   Data wylotu: {flight_preferences.target_departure}")
        print(f"   Data powrotu: {flight_preferences.return_date}")

        return flight_preferences, None

    except ValueError as e:
        error_message = str(e)

        # Dostosuj komunikaty błędów dla użytkownika
        if "Nieznany kod lotniska IATA" in error_message:
            error_message = "Wybrano nieprawidłowe lotnisko. Proszę wybrać lotnisko z listy podpowiedzi."
        elif "musi być różne" in error_message:
            error_message = "Lotnisko wylotu i przylotu muszą być różne."
        elif "Data wylotu nie może być w przeszłości" in error_message:
            error_message = "Data wylotu nie może być w przeszłości."

        return None, error_message


def validate_notifications(request_form) -> tuple[bool, bool, str, str, str] | tuple[bool, Any, None]:
    """
    Waliduje dane powiadomień z formularza

    Returns:
        Tuple[email_notify, telegram_notify, email, error_message]
    """
    email_notify = request_form.get("email_notify") == "on"
    email = request_form.get("email", "").strip()

    # Walidacja danych kontaktowych
    if email_notify and not email:
        return False, False, "", "", "Podaj adres email"

    return email_notify, email, None


def fetch_flight_data(flight_preferences: FlightSearchParams) -> Tuple[Optional[dict], Optional[str]]:
    """
    Pobiera dane o lotach z API

    Returns:
        Tuple[response_data lub None, error_message lub None]
    """
    try:
        data_grabber = DataGrabber()
        response = data_grabber.api_connector(flight_preferences)

        if not response:
            return None, "Nie udało się pobrać danych o lotach"

        data_grabber.pobierz_dane(response)
        return response, None

    except Exception as e:
        print(f"Błąd podczas pobierania danych lotów: {e}")
        return None, f"Błąd podczas pobierania danych lotów: {str(e)}"


def save_user_data(database: Database, email_notify: bool,
                  email: str) -> Tuple[Optional[int], Optional[str]]:
    """
    Zapisuje dane użytkownika i preferencje powiadomień

    Returns:
        Tuple[user_id lub None, error_message lub None]
    """
    try:
        user_id, user_saved = database.users_query(
            email=email if email_notify else None,
        )

        if not user_saved or user_id is None:
            return None, "Nie udało się zapisać danych użytkownika."

        notification_saved = True
        if email_notify:
            notification_saved &= database.notification_preferences_query(user_id, "email")

        if not notification_saved:
            return None, "Nie udało się zapisać preferencji powiadomień"

        return user_id, None

    except Exception as e:
        print(f"Błąd podczas zapisywania danych użytkownika: {e}")
        return None, f"Błąd podczas zapisywania danych użytkownika: {str(e)}"


def save_flight_preferences(database: Database, user_id: int,
                          flight_preferences: FlightSearchParams) -> Optional[str]:
    """
    Zapisuje preferencje lotu użytkownika

    Returns:
        error_message lub None
    """
    try:
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
            return "Nie udało się zapisać preferencji lotu."

        return None

    except Exception as e:
        print(f"Błąd podczas zapisywania preferencji lotu: {e}")
        return f"Błąd podczas zapisywania preferencji lotu: {str(e)}"

@app.route("/api/airport/<iata_code>", methods=["GET"])
def get_airport_info(iata_code):
    """Endpoint do pobierania szczegółowych informacji o lotnisku"""
    try:
        airport_search = AirportSearch()
        airport_info = airport_search.get_airport_info(iata_code)

        if airport_info:
            return jsonify(airport_info)
        else:
            return jsonify({"error": "Lotnisko nie znalezione"}), 404

    except Exception as e:
        print(f"Błąd w endpoint informacji o lotnisku: {e}")
        return jsonify({"error": "Błąd serwera"}), 500


@app.route("/api/airports", methods=["GET"])
async def search_airports():
    """Endpoint do wyszukiwania lotnisk używający airports-py"""
    query = request.args.get("q", "").strip()

    print(f"🌐 API call /api/airports?q={query}")

    if not query or len(query) < 2:
        print("❌ Query za krótkie lub puste")
        return jsonify([])

    try:
        airport_search = AirportSearch()
        results = await airport_search.search_airports(query, limit=10)

        print(f"📡 Zwracam {len(results)} wyników przez API")
        print(f"📄 Dane: {results}")

        return jsonify(results)
    except Exception as e:
        print(f"❌ Błąd w endpoint wyszukiwania lotnisk: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([]), 500



@app.route("/", methods=["GET", "POST"])
def index():
    """Główny endpoint obsługujący formularz wyszukiwania lotów"""
    if request.method == "GET":
        return render_template("form.html")

    # POST - obsługa formularza
    try:
        # 1. Przygotuj dane z formularza
        form_data = {
            "target_departure": request.form.get("departure_date", ""),
            "return_date": request.form.get("return_date", ""),
            "departure_airport": request.form.get("departure_airport", "").strip().upper(),
            "arrival_airport": request.form.get("arrival_airport", "").strip().upper(),
            "currency": request.form.get("currency", ""),
            "seat_class": request.form.get("seat_class", "")
        }

        # 2. Waliduj parametry lotu
        flight_preferences, error = validate_flight_params(form_data)
        if error or flight_preferences is None:
            return render_template("form.html", error=error)

        # 3. Waliduj powiadomienia
        email_notify, email, error = validate_notifications(request.form)
        if error:
            return render_template("form.html", error=error)

        # 4. Pobierz dane o lotach
        flight_data, error = fetch_flight_data(flight_preferences)
        if error:
            return render_template("form.html", error=error)

        # 5. Zapisz dane użytkownika
        database = Database()
        user_id, error = save_user_data(database, email_notify, email)
        if error:
            return render_template("form.html", error=error)

        assert user_id is not None

        # 6. Zapisz preferencje lotu
        error = save_flight_preferences(database, user_id, flight_preferences)
        if error:
            return render_template("form.html", error=error)

        # 7. Sukces!
        return render_template(
            "result.html",
            result="Wszystkie preferencje poprawnie zapisane",
        )

    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {str(e)}")
        return render_template("form.html", error=f"Wystąpił nieoczekiwany błąd: {str(e)}")

    return render_template("form.html")
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
