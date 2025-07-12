import json

class FlightChecker:
    def sprawdzanie_lotow(self, target_departure):
        """
        Check if any flights exist for a given departure date.

        This function reads flight data from a JSON file and checks if there are any flights
        scheduled for the specified departure date.

        Args:
            target_departure (str): The target departure date to check for flights.
                Expected format is as defined in the flights_dates.json file.

        Returns:
            bool: True if flights exist for the target date, False otherwise.

        Example:
            >>> checker = FlightChecker()
            >>> checker.sprawdzanie_lotow("2024-01-01")
            True
        """
        with open("flights_dates.json", "r", encoding="utf-8") as file:
            loty_data = json.load(file)

        matching_loty = [
            lot
            for lot in loty_data["data"]["prices"]
            if lot["departureDate"] == target_departure
        ]

        if matching_loty:
            return True
        else:
            return False