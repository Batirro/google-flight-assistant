from typing import List, Dict, Optional
from airports import airport_data
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
            # Tłumaczenie na angielski
            translated_text = self.translator.translate(text)
            translated_text = translated_text.lower()
            print(f"🔄 Przetłumaczono '{text}' → '{translated_text}'")

            if translated_text != text_lower:
                variants.extend([
                    translated_text,
                    translated_text.capitalize(),
                    translated_text.title()
                ])

            # Dodaj też warianty oryginalnego tekstu
            variants.extend([
                text.capitalize(),
                text.title(),
                text.upper()
            ])

        except Exception as e:
            print(f"❌ Błąd tłumaczenia '{text}': {e}")
            # W przypadku błędu, użyj tylko oryginalnego tekstu

        # Usuń duplikaty
        unique_variants = []
        seen = set()
        for variant in variants:
            if variant.lower() not in seen:
                unique_variants.append(variant)
                seen.add(variant.lower())

        # Cache wynik
        self.translation_cache[text_lower] = unique_variants

        # Małe opóźnienie żeby nie przeciążyć API
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

            if not query or len(query.strip()) < 2:
                print("❌ Query za krótkie")
                return []

            if not self.airports_cache:
                print("❌ Cache lotnisk niedostępny")
                return []

            query = query.strip()
            results = []
            seen_codes = set()

            # Pobierz warianty językowe zapytania
            query_variants = await self._translate_to_english(query)
            print(f"🌐 Warianty wyszukiwania: {query_variants}")

            try:
                for search_query in query_variants:
                    if len(results) >= limit:
                        break

                    # 1. Wyszukaj po kodzie IATA (jeśli query wygląda jak kod)
                    if len(search_query) == 3 and search_query.isalpha():
                        print(f"🔤 Wyszukiwanie po kodzie IATA: {search_query.upper()}")
                        airports_by_iata = airport_data.get_airport_by_iata(search_query.upper())
                        print(f"📍 Znaleziono przez IATA: {len(airports_by_iata) if airports_by_iata else 0} wyników")

                        if airports_by_iata:
                            for airport_info in airports_by_iata[:3]:  # Weź maksymalnie 3 wyniki
                                airport_formatted = self._format_airport(airport_info)
                                if airport_formatted and airport_formatted['code'] not in seen_codes:
                                    results.append(airport_formatted)
                                    seen_codes.add(airport_formatted['code'])
                                    print(f"✅ Dodano lotnisko: {airport_formatted['code']} - {airport_formatted['city']}")

                    # 2. Wyszukaj po nazwie (miasta/lotniska)
                    if len(results) < limit:  # Tylko jeśli potrzebujemy więcej wyników
                        print(f"🏙️ Wyszukiwanie po nazwie: {search_query}")
                        airports_by_name = airport_data.search_by_name(search_query)
                        print(f"📍 Znaleziono przez nazwę: {len(airports_by_name) if airports_by_name else 0} wyników")

                        if airports_by_name:
                            for airport_info in airports_by_name:
                                if len(results) >= limit:
                                    break
                                airport_formatted = self._format_airport(airport_info)
                                if (airport_formatted and
                                    airport_formatted['code'] not in seen_codes):
                                    results.append(airport_formatted)
                                    seen_codes.add(airport_formatted['code'])
                                    print(f"✅ Dodano lotnisko: {airport_formatted['code']} - {airport_formatted['city']}")

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
                iata_code = airport_info.get('iata')
                if not iata_code or len(iata_code) != 3:
                    print(f"❌ Brak kodu IATA lub nieprawidłowy: {iata_code}")
                    return None

                # Wyciągnij potrzebne dane
                airport_name = airport_info.get('airport', '')
                city = airport_info.get('city', '')
                country_code = airport_info.get('country_code', '')
                country = airport_info.get('country', country_code)

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
        try:
            if not iata_code or len(iata_code) != 3:
                return None

            airports_list = airport_data.get_airport_by_iata(iata_code.upper())
            if airports_list and len(airports_list) > 0:
                return self._format_airport(airports_list[0])
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
