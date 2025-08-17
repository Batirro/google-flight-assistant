from flask import Flask, render_template, request
from logic.email_sender import EmailSender, TelegramSender
from logic.date_parser import DataParser
from logic.flight_checker import FlightChecker
from logic.data_grabber import DataGrabber
from services.database import Database

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        month = request.form["month"]
        year = request.form["year"]
        trip_length = int(request.form["trip_length"])
        departure_airport = request.form["departure_airport"]
        arrival_airport = request.form["arrival_airport"]
        currency = request.form["currency"]
        seat_class = request.form["seat_class"]


        data_parser = DataParser()
        data_grabber = DataGrabber()
        flight_checker = FlightChecker()
        telegram_sender = TelegramSender()
        db = Database()
        

        target_departure, return_date = data_parser.formatowanie_daty(month, year, trip_length)
        response = data_grabber.api_connector(target_departure, return_date, departure_airport, arrival_airport, currency)
        data_grabber.pobierz_dane(response)

        if flight_checker.sprawdzanie_lotow(target_departure):
            subject = f'Znaleziono loty na {month} {year}\n Link do lotów: {flight_checker.info_extractor()}'
            # EmailSender().send_email(subject, "Znaleziono loty")
            telegram_sender.send_bot_massage(subject)
            return render_template("result.html", result="Znaleziono loty!", link=flight_checker.info_extractor())
        else:
            return render_template("result.html", result=f"Brak lotów na {month} {year}", link=None)
    return render_template("form.html")
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)

