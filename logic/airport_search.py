from typing import List, Dict, Optional
from airportfinder.airportfinder import Airports
from deep_translator import GoogleTranslator
import time
import asyncio


class AirportSearch:
    def __init__(self):
        """
        Inicjalizuje serwis wyszukiwania lotnisk używając biblioteki airports-py
        """
        self.airports_cache = None
        self.translator = GoogleTranslator(source='auto', target='en')
        self.translation_cache = {}  # Cache dla tłumaczeń
        self._load_airports()

    def _load_airports(self):
        """
        Ładuje dane lotnisk do cache'u dla szybszego wyszukiwania
        """
        try:
            self.airports_cache = True
        except Exception as e:
            print(f"Błąd podczas ładowania danych lotnisk: {e}")
            self.airports_cache = False

    async def _translate_to_english(self, text: str) -> List[str]:
        """
        Tłumaczy tekst na angielski używając deep_translator

        Returns:
            Lista wariantów (oryginał + przetłumaczone)
        """
        text_lower = text.lower().strip()

        # Sprawdź cache
        if text_lower in self.translation_cache:
            return self.translation_cache[text_lower]

        variants = [text]  # Zawsze dodaj oryginał

        try:
            # Przywróć automatyczne tłumaczenie na angielski
            print(f"🔄 Tłumaczę '{text}' na angielski...")
            translated_text = self.translator.translate(text)

            if translated_text and translated_text.lower() != text_lower:
                print(f"✅ Przetłumaczono '{text}' → '{translated_text}'")

                # Dodaj warianty przetłumaczonego tekstu
                variants.extend([
                    translated_text,
                    translated_text.capitalize(),
                    translated_text.title(),
                    translated_text.upper(),
                    translated_text.lower()
                ])
            else:
                print(f"ℹ️ Tekst '{text}' już jest w języku angielskim lub nie wymagał tłumaczenia")

            # Dodaj też warianty oryginalnego tekstu
            variants.extend([
                text.capitalize(),
                text.title(),
                text.upper(),
                text.lower()
            ])

        except Exception as e:
            print(f"❌ Błąd tłumaczenia '{text}': {e}")
            # W przypadku błędu, użyj tylko oryginalnego tekstu i jego wariantów
            variants.extend([
                text.capitalize(),
                text.title(),
                text.upper(),
                text.lower()
            ])

        # Usuń duplikaty
        unique_variants = []
        seen = set()
        for variant in variants:
            variant_clean = variant.strip()
            if variant_clean and variant_clean.lower() not in seen:
                unique_variants.append(variant_clean)
                seen.add(variant_clean.lower())

        # Cache wynik
        self.translation_cache[text_lower] = unique_variants

        # Małe opóźnienie żeby nie przeciążyć API tłumaczenia
        await asyncio.sleep(0.1)

        return unique_variants

    async def search_airports(self, query: str, limit: int = 10) -> List[Dict]:
            """
            Wyszukuje lotniska na podstawie nazwy miasta, kodu IATA lub nazwy lotniska

            Args:
                query: Zapytanie wyszukiwania (nazwa miasta, kod IATA, nazwa lotniska)
                limit: Maksymalna liczba wyników

            Returns:
                Lista słowników z danymi lotnisk
            """
            print(f"🔍 Wyszukiwanie lotnisk dla: '{query}'")
            airports = Airports()

            # Zmniejsz minimalną długość zapytania z 2 na 1 znak
            if not query or len(query.strip()) < 1:
                print("❌ Query za krótkie")
                return []

            if not self.airports_cache:
                print("❌ Cache lotnisk niedostępny")
                return []

            query = query.strip()
            results = []
            seen_codes = set()

            try:
                # Dla bardzo krótkich zapytań (1-2 znaki) szukaj tylko po kodzie IATA i bez tłumaczenia
                if len(query) <= 2:
                    print(f"🔤 Krótkie zapytanie - wyszukiwanie tylko po kodzie IATA: {query.upper()}")

                    # Wyszukaj po kodzie IATA
                    if len(query) == 3 and query.isalpha():
                        airport_info = airports.airports_iata.get(query.upper())
                        if airport_info:
                            airport_formatted = self._format_airport(airport_info)
                            if airport_formatted:
                                results.append(airport_formatted)
                                seen_codes.add(airport_formatted['code'])
                                print(f"✅ Znaleziono dokładny kod IATA: {airport_formatted['code']}")

                    # Dla 1-2 znaków, szukaj kodów IATA zaczynających się od tych liter
                    elif query.isalpha():
                        query_upper = query.upper()
                        print(f"🔍 Szukam kodów IATA zaczynających się od: {query_upper}")

                        matching_codes = [code for code in airports.airports_iata.keys()
                                        if code.startswith(query_upper)][:limit]

                        for code in matching_codes:
                            if len(results) >= limit:
                                break
                            airport_info = airports.airports_iata.get(code)
                            if airport_info:
                                airport_formatted = self._format_airport(airport_info)
                                if airport_formatted and airport_formatted['code'] not in seen_codes:
                                    results.append(airport_formatted)
                                    seen_codes.add(airport_formatted['code'])
                                    print(f"✅ Dodano lotnisko przez prefiks IATA: {airport_formatted['code']}")

                    return results[:limit]

                # Dla dłuższych zapytań użyj pełnej logiki z tłumaczeniem
                # Pobierz warianty językowe zapytania tylko dla zapytań >= 3 znaki
                query_variants = await self._translate_to_english(query)
                print(f"🌐 Warianty wyszukiwania: {query_variants}")

                for search_query in query_variants:
                    if len(results) >= limit:
                        break

                    # 1. Wyszukaj po kodzie IATA (jeśli query wygląda jak kod i ma dokładnie 3 znaki)
                    if len(search_query) == 3 and search_query.isalpha():
                        print(f"🔤 Wyszukiwanie po kodzie IATA: {search_query.upper()}")
                        airport_info = airports.airports_iata.get(search_query.upper())
                        print(f"📍 Znaleziono przez IATA: {1 if airport_info else 0} wyników")

                        if airport_info:
                            airport_formatted = self._format_airport(airport_info)
                            if airport_formatted and airport_formatted['code'] not in seen_codes:
                                results.append(airport_formatted)
                                seen_codes.add(airport_formatted['code'])
                                print(f"✅ Dodano lotnisko: {airport_formatted['code']} - {airport_formatted['city']}")

                    # 2. Wyszukuj po nazwach miast w kodach IATA (fallback dla długich zapytań)
                    if len(results) < limit and len(search_query) >= 3:
                        print(f"🏙️ Wyszukiwanie po nazwie miasta w bazie IATA: {search_query}")
                        search_lower = search_query.lower()

                        # Przeszukaj wszystkie lotniska w poszukiwaniu pasujących miast/nazw
                        matched_codes = []
                        for code, airport_data in airports.airports_iata.items():
                            if not airport_data:
                                continue

                            city = airport_data.get('city', '').lower()
                            name = airport_data.get('name', '').lower()
                            country = airport_data.get('country', '').lower()

                            # Sprawdź czy zapytanie pasuje do miasta, nazwy lotniska lub kraju
                            if (search_lower in city or
                                search_lower in name or
                                city.startswith(search_lower) or
                                name.startswith(search_lower)):
                                matched_codes.append(code)
                                if len(matched_codes) >= limit:
                                    break

                        print(f"📍 Znaleziono przez wyszukiwanie w bazie: {len(matched_codes)} kodów")

                        for code in matched_codes:
                            if len(results) >= limit:
                                break
                            if code not in seen_codes:
                                airport_info = airports.airports_iata.get(code)
                                if airport_info:
                                    airport_formatted = self._format_airport(airport_info)
                                    if airport_formatted:
                                        results.append(airport_formatted)
                                        seen_codes.add(airport_formatted['code'])
                                        print(f"✅ Dodano lotnisko: {airport_formatted['code']} - {airport_formatted['city']}")

                    # 3. Próba użycia airport_name() jako backup (może nie działać we wszystkich przypadkach)
                    if len(results) < limit and len(search_query) >= 3:
                        print(f"🔍 Próba użycia airport_name(): {search_query}")
                        try:
                            airports_by_name = airports.airport_name(search_query)

                            # Sprawdź czy wynik to lista czy pojedynczy element
                            if airports_by_name:
                                if isinstance(airports_by_name, dict):
                                    airports_by_name = [airports_by_name]
                                elif not isinstance(airports_by_name, list):
                                    airports_by_name = []

                                print(f"📍 Znaleziono przez airport_name(): {len(airports_by_name) if airports_by_name else 0} wyników")

                                if airports_by_name:
                                    for airport_info in airports_by_name:
                                        if len(results) >= limit:
                                            break
                                        airport_formatted = self._format_airport(airport_info)
                                        if (airport_formatted and
                                            airport_formatted['code'] not in seen_codes):
                                            results.append(airport_formatted)
                                            seen_codes.add(airport_formatted['code'])
                                            print(f"✅ Dodano lotnisko przez airport_name: {airport_formatted['code']} - {airport_formatted['city']}")
                        except Exception as e:
                            print(f"❌ Błąd w airport_name() dla '{search_query}': {e}")
                            continue

                # 3. Sortuj wyniki - dokładne dopasowania najpierw
                results = self._sort_results(results, query)
                print(f"📊 Zwracam {len(results)} wyników")

            except Exception as e:
                print(f"❌ Błąd podczas wyszukiwania lotnisk: {e}")
                import traceback
                traceback.print_exc()
                return []

            return results[:limit]

    def _format_airport(self, airport_info: Dict) -> Optional[Dict]:
            """
            Formatuje dane lotniska z airports-py do standardowego formatu
            """
            try:
                print(f"🛠️ Formatowanie lotniska: {airport_info}")

                if not airport_info or not isinstance(airport_info, dict):
                    print("❌ Brak danych lotniska lub nieprawidłowy format")
                    return None

                # Sprawdź czy ma kod IATA
                iata_code = airport_info.get('code')
                if not iata_code or len(iata_code) != 3:
                    print(f"❌ Brak kodu IATA lub nieprawidłowy: {iata_code}")
                    return None

                # Wyciągnij potrzebne dane
                airport_name = airport_info.get('name', '')
                city = airport_info.get('city', '')
                country = airport_info.get('country', '')

                # Jeśli brakuje miasta, spróbuj wyciągnąć je z nazwy lotniska
                if not city and airport_name:
                    # Prosta heurystyka: weź pierwsze słowo z nazwy lotniska
                    city_from_name = airport_name.split(' ')[0]
                    # Sprawdź, czy to nie jest słowo typu "International"
                    if city_from_name.lower() not in ['international', 'airport']:
                        city = city_from_name
                        print(f"ℹ️ Brak miasta, użyto z nazwy lotniska: '{city}'")

                # Filtruj niepełne dane
                if not airport_name or not city:
                    print(f"❌ Niepełne dane - nazwa: '{airport_name}', miasto: '{city}'")
                    return None

                formatted = {
                    'code': iata_code.upper(),
                    'name': airport_name,
                    'city': city,
                    'country': country
                }

                print(f"✅ Sformatowano: {formatted}")
                return formatted

            except Exception as e:
                print(f"❌ Błąd formatowania lotniska: {e}")
                import traceback
                traceback.print_exc()
                return None

    def _sort_results(self, results: List[Dict], query: str) -> List[Dict]:
        """
        Sortuje wyniki - dokładne dopasowania miast/kodów na początku
        """
        query_lower = query.lower()

        exact_matches = []
        partial_matches = []

        for airport in results:
            city_lower = airport['city'].lower()
            code_lower = airport['code'].lower()

            if (city_lower == query_lower or
                code_lower == query_lower or
                city_lower.startswith(query_lower) or
                code_lower.startswith(query_lower)):
                exact_matches.append(airport)
            else:
                partial_matches.append(airport)

        return exact_matches + partial_matches

    def get_airport_by_code(self, iata_code: str) -> Optional[Dict]:
        """
        Pobiera lotnisko po kodzie IATA
        """
        airports = Airports()
        try:
            if not iata_code or len(iata_code) != 3:
                return None

            # airports_iata to słownik - używaj get() zamiast wywołania funkcji
            airport_info = airports.airports_iata.get(iata_code.upper())
            if airport_info:
                return self._format_airport(airport_info)
            return None

        except Exception as e:
            print(f"Błąd podczas pobierania lotniska {iata_code}: {e}")
            return None

    def validate_iata_code(self, iata_code: str) -> bool:
        """
        Waliduje czy podany kod to właściwy kod IATA
        """
        try:
            airport = self.get_airport_by_code(iata_code)
            return airport is not None
        except Exception:
            return False

    def get_airport_info(self, iata_code: str) -> Optional[Dict]:
        """
        Pobiera szczegółowe informacje o lotnisku po kodzie IATA
        """
        return self.get_airport_by_code(iata_code)
