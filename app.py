from email_sender import send_email
from date_parser import formatowanie_daty
from flight_checker import sprawdzanie_lotow
from data_grabber import api_connector, pobierz_dane


if __name__ == "__main__":
    month = input("Podaj miesiąc wylotu: ")
    year = input("Podaj rok wylotu:")
    target_departure, arrivalDate = formatowanie_daty(month, year)
    response = api_connector(target_departure, arrivalDate)
    pobierz_dane(response)
    if sprawdzanie_lotow(target_departure):
        subject = f'Znaleziono loty na {month} {year}'
        plainText = 'Znaleziono loty'
        print(f'Znaleziono loty na {month} {year}')
        send_email(subject, plainText)
    else:
        print(f'Nie ma jeszcze lotów dostępnych na {month} {year}')

