from datetime import datetime, timedelta

class DataParser:
    @staticmethod
    def generuj_date_z_miesiaca(nazwa_miesiaca, rok):
        miesiace = {
            'Styczeń': 1, 'Luty': 2, 'Marzec': 3, 'Kwiecień': 4,
            'Maj': 5, 'Czerwiec': 6, 'Lipiec': 7, 'Sierpień': 8,
            'Wrzesień': 9, 'Październik': 10, 'Listopad': 11, 'Grudzień': 12
        }
        
        nazwa_miesiaca = nazwa_miesiaca.capitalize()
        if nazwa_miesiaca in miesiace:
            return f"{rok}-{miesiace[nazwa_miesiaca]:02d}-01"
        else:
            raise ValueError(f"Nieznana nazwa miesiąca: {nazwa_miesiaca}")

    @staticmethod
    def formatowanie_daty(month, year, TripLenght):
        target_departure = DataParser.generuj_date_z_miesiaca(month, year)
        if target_departure is None:
            raise ValueError("Nie udało się wygenerować daty.")
        
        returnDate = (datetime.strptime(target_departure, "%Y-%m-%d") 
                       + timedelta(days=TripLenght))
        returnDate = returnDate.strftime("%Y-%m-%d")
        
        return target_departure, returnDate
