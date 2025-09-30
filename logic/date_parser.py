from datetime import datetime, timedelta
import locale

def changeMonthForAbbreviation(date_str: str) -> str:
    try:
        locale.setlocale(locale.LC_TIME, 'pl_PL.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'polish')
        except locale.Error:
            print("Polska lokalizacja nie jest dostępna. Sprawdź ustawienia systemowe.")
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.strftime('%d %B %Y')
