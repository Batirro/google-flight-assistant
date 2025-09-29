from sqlalchemy import or_
from datetime import datetime

# Importujemy centralny obiekt db, a nie tworzymy własnego silnika
from services.db_instance import db
from services.models import User, FlightPreference, NotificationPreference
from services.schemas import FlightPreferences

def create_tables(app):
    """Funkcja pomocnicza do tworzenia tabel w kontekście aplikacji."""
    with app.app_context():
        db.create_all()

class Database:
    """
    Klasa operująca na bazie danych przy użyciu centralnego obiektu
    Flask-SQLAlchemy (db.session).
    """

    # Nie potrzebujemy już __init__ i __del__ do zarządzania sesją!
    # Flask-SQLAlchemy robi to za nas automatycznie w tle dla każdego żądania.

    def users_query(self, email: str | None, telegram_tag: str | None) -> tuple[int | None, bool]:
        """Znajduje lub tworzy użytkownika i zwraca jego ID."""
        try:
            query_filter = []
            if email:
                query_filter.append(User.email == email)
            if telegram_tag:
                query_filter.append(User.telegram_tag == telegram_tag)

            # Używamy db.session, które jest zarządzane przez Flask-SQLAlchemy
            user = db.session.query(User).filter(or_(*query_filter)).first()

            if user:
                if email and not user.email: user.email = email
                if telegram_tag and not user.telegram_tag: user.telegram_tag = telegram_tag
                db.session.commit()
                return user.user_id, True
            else:
                new_user = User(email=email, telegram_tag=telegram_tag)
                db.session.add(new_user)
                db.session.commit()
                return new_user.user_id, True
        except Exception as e:
            db.session.rollback()
            print(f"Błąd przy zapisie użytkownika: {e}")
            return None, False

    def notification_preferences_query(self, user_id: int, method: str) -> bool:
        """Dodaje preferencje powiadomień dla użytkownika."""
        try:
            existing_pref = db.session.query(NotificationPreference).filter_by(user_id=user_id, method=method).first()
            if not existing_pref:
                new_pref = NotificationPreference(user_id=user_id, method=method, enabled=True)
                db.session.add(new_pref)
                db.session.commit()
                return True
            else:
                return True
        except Exception as e:
            db.session.rollback()
            print(f"Błąd przy zapisie preferencji powiadomień: {e}")
            return False

    def flight_preferences(self, user_id: int, flight_prefs: FlightPreferences) -> bool:
        """Zapisuje w bazie nowe preferencje lotu."""
        try:
            dep_date = datetime.strptime(flight_prefs.target_departure, '%Y-%m-%d').date()
            ret_date = datetime.strptime(flight_prefs.return_date, '%Y-%m-%d').date()

            new_flight_pref = FlightPreference(
                user_id=user_id,
                target_departure=dep_date, return_date=ret_date,
                departure_airport=flight_prefs.departure_airport, arrival_airport=flight_prefs.arrival_airport,
                currency=flight_prefs.currency, seat_class=flight_prefs.seat_class,
                max_price=flight_prefs.max_price, preferred_airline=flight_prefs.preferred_airline
            )
            db.session.add(new_flight_pref)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Błąd przy zapisie preferencji lotu: {e}")
            return False
