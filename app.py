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
        user_id, error = save_user_data(database, email_notify, telegram_notify, email, telegram_tag)
        if error:
            return render_template("form.html", error=error)

        assert user_id is not None

        # 6. Zapisz preferencje lotu
        error = save_flight_preferences(database, user_id, flight_preferences)
        if error:
            return render_template("form.html", error=error)

        # 7. Sukces!
        return render_template("result.html", result="Wszystkie preferencje poprawnie zapisane")

    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {str(e)}")
        return render_template("form.html", error=f"Wystąpił nieoczekiwany błąd: {str(e)}")

    return render_template("form.html")
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
