from logic.email_sender import EmailSender
from logic.email_sender import TelegramSender
from logic.date_parser import DataParser
from logic.flight_checker import FlightChecker
from logic.data_grabber import DataGrabber


if __name__ == "__main__":
    DataGrabber = DataGrabber()
    FlightChecker = FlightChecker()
    TelegramSender = TelegramSender ()
    month = input("Podaj miesiąc wylotu: ")
    year = input("Podaj rok wylotu: ")
    TripLenght = int(input("Podaj długość wycieczki: "))
    target_departure, return_date = DataParser.formatowanie_daty(month, year, TripLenght)
    response = DataGrabber.api_connector(target_departure, return_date)
    DataGrabber.pobierz_dane(response)
    if FlightChecker.sprawdzanie_lotow(target_departure):
        subject = f'Znaleziono loty na {month} {year}'
        plainText = 'Znaleziono loty'
        print(f'Znaleziono loty na {month} {year}')
        # EmailSender.send_email(subject, plainText)
        TelegramSender.send_bot_massage(subject)
    else:
        print(f'Nie ma jeszcze lotów dostępnych na {month} {year}')

