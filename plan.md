# Plan implementacji: Reorganizacja plików po nagraniu

## Faza 1: Modyfikacja obs_script.py

### 1.1 Dodanie funkcji do pobierania ścieżki nagrania
```python
def get_recording_output_path():
    """Pobiera katalog wyjściowy nagrania z OBS API"""
    # Zwraca katalog wyjściowy, nie pełną ścieżkę do pliku
    
def find_latest_recording_file(output_dir):
    """Znajduje najnowszy plik nagrania w katalogu wyjściowym"""
    # Szuka plików wideo utworzonych w ciągu ostatnich 30 sekund
    # Zwraca pełną ścieżkę do najnowszego pliku
```

### 1.2 Dodanie funkcji reorganizacji plików
```python
def reorganize_files_after_recording(recording_path, metadata_path):
    """Reorganizuje pliki po nagraniu - tworzy strukturę katalogów"""
    # Implementacja tworzenia struktury katalogów
    # Przenoszenie pliku nagrania
    # Przenoszenie metadanych
    # Tworzenie katalogu extracted/
```

### 1.3 Modyfikacja collect_and_save_metadata()
- Dodanie wywołania `get_recording_output_path()` na początku funkcji
- Dodanie wywołania `reorganize_files_after_recording()` na końcu funkcji
- Zapisanie metadanych w nowej lokalizacji

### 1.4 Dodanie opcji konfiguracyjnej
- Dodanie checkboxa "Enable file reorganization" w script_properties()
- Dodanie zmiennej globalnej `file_reorganization_enabled`
- Aktualizacja script_update() i script_defaults()

## Faza 2: Aktualizacja advanced_scene_switcher_extractor.py

### 2.1 Modyfikacja find_latest_recording()
- Aktualizacja ścieżek wyszukiwania - szukanie w strukturze katalogów
- Zmiana obsługi struktury plików

### 2.2 Aktualizacja run_extraction()
- Przekazanie informacji o strukturze katalogów do CLI
- Obsługa nowej ścieżki do metadanych

## Faza 3: Aktualizacja extract.py

### 3.1 Modyfikacja find_metadata_file()
- Zmiana obsługi nowej struktury katalogów
- Szukanie metadata.json w katalogu nagrania
- Nie robimy Fallback do starych wzorców

### 3.2 Aktualizacja extract_sources()
- Modyfikacja domyślnej ścieżki wyjściowej
- Tworzenie katalogu `extracted/` w katalogu nagrania

## Faza 4: Testy i walidacja

### 4.1 Testy jednostkowe
- Test funkcji `get_recording_output_path()`
- Test funkcji `reorganize_files_after_recording()`
- Test kompatybilności z istniejącymi plikami

### 4.2 Testy integracyjne
- Test pełnego przepływu: nagranie → reorganizacja → ekstrakcja
- Test z różnymi formatami plików
- Test obsługi błędów

### 4.3 Testy regresji
- Sprawdzenie że stary kod nadal działa
- Sprawdzenie że można wyłączyć reorganizację

## Harmonogram implementacji

### Tydzień 1: Analiza i przygotowanie
- [x] Analiza OBS API
- [x] Przygotowanie specyfikacji
- [x] Przygotowanie planu
- [x] Przygotowanie testów

### Tydzień 2: Implementacja core'a
- [x] Implementacja funkcji pobierania ścieżki nagrania
- [x] Implementacja funkcji reorganizacji
- [x] Testy jednostkowe funkcji

### Tydzień 3: Integracja
- [x] Modyfikacja obs_script.py
- [x] Modyfikacja advanced_scene_switcher_extractor.py
- [ ] Modyfikacja extract.py
- [ ] Testy integracyjne

### Tydzień 4: Finalizacja
- [ ] Testy regresji
- [ ] Dokumentacja
- [ ] Optymalizacja i bug fixes

## Pliki do modyfikacji

1. **src/obs_integration/obs_script.py**
   - Dodanie funkcji pobierania ścieżki nagrania
   - Dodanie funkcji reorganizacji plików
   - Modyfikacja collect_and_save_metadata()
   - Dodanie opcji konfiguracyjnej

2. **src/obs_integration/advanced_scene_switcher_extractor.py**
   - Modyfikacja find_latest_recording()
   - Aktualizacja logiki wyszukiwania plików

3. **src/cli/extract.py**
   - Modyfikacja find_metadata_file()
   - Aktualizacja domyślnej ścieżki wyjściowej

4. **tests/** (nowe pliki testów)
   - test_file_reorganization.py
   - test_integration_reorganization.py

## Potencjalne problemy i rozwiązania



## Kryteria sukcesu

1. ✅ Pliki są reorganizowane zgodnie ze specyfikacją
4. ✅ Obsługa błędów nie crashuje systemu
5. ✅ Testy pokrywają 90%+ funkcjonalności
6. ✅ Dokumentacja jest aktualna