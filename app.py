from logic.email_sender import EmailSender
from logic.date_parser import DataParser
from logic.flight_checker import FlightChecker
from logic.data_grabber import DataGrabber


if __name__ == "__main__":
    month = input("Podaj miesiąc wylotu: ")
    year = input("Podaj rok wylotu:")
    target_departure, arrivalDate = DataParser.formatowanie_daty(month, year)
    response = DataGrabber.api_connector(target_departure, arrivalDate)
    DataGrabber.pobierz_dane(response)
    if FlightChecker.sprawdzanie_lotow(target_departure):
        subject = f'Znaleziono loty na {month} {year}'
        plainText = 'Znaleziono loty'
        print(f'Znaleziono loty na {month} {year}')
        EmailSender.send_email(subject, plainText)
    else:
        print(f'Nie ma jeszcze lotów dostępnych na {month} {year}')

