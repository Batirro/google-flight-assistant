from datetime import datetime, timedelta

def generuj_date_z_miesiaca(nazwa_miesiaca, rok):
    """
    Generates a date string in 'YYYY-MM-DD' format for the first day of a given month and year.
    Args:
        nazwa_miesiaca (str): Name of the month in Polish (e.g., 'Styczeń', 'Luty', etc.)
        rok (int): Year as a number (e.g., 2023)
    Returns:
        str: Date string in 'YYYY-MM-DD' format representing the first day of the specified month and year
    Raises:
        ValueError: If the provided month name is not recognized
    Examples:
        >>> generuj_date_z_miesiaca('Styczeń', 2023)
        '2023-01-01'
        >>> generuj_date_z_miesiaca('Grudzień', 2024)
        '2024-12-01'
    """
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

def formatowanie_daty(month, year):
    """
    Formats and generates a pair of consecutive dates based on given month and year.
    Args:
        month (str): Month name in Polish (e.g., 'styczeń', 'luty', etc.)
        year (int): Year as a four-digit number
    Returns:
        tuple: A pair of consecutive dates (target_departure, arrival_date) in 'YYYY-MM-DD' format
            - target_departure (str): The departure date generated from the given month and year
            - arrival_date (str): The date following the departure date
    Raises:
        ValueError: If the date generation fails for the given month and year
    Example:
        >>> formatowanie_daty('styczeń', 2024)
        ('2024-01-01', '2024-01-02')
    """
    target_departure = generuj_date_z_miesiaca(month, year)
    if target_departure is None:
        raise ValueError("Nie udało się wygenerować daty.")
    
    arrival_date = (datetime.strptime(target_departure, "%Y-%m-%d") 
                   + timedelta(days=1))
    arrival_date = arrival_date.strftime("%Y-%m-%d")
    
    return target_departure, arrival_date
