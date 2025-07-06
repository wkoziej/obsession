# Specyfikacja: Reorganizacja plików po nagraniu

## Cel
Uporządkowanie struktury plików po nagraniu i ekstrakcji - utworzenie jednego katalogu na nagranie zawierającego wszystkie powiązane pliki.

## Docelowa struktura katalogów
```
/ścieżka/do/nagrań/
├── nagranie_2025-01-06_15-30-00/
│   ├── nagranie_2025-01-06_15-30-00.mkv    # oryginalny plik nagrania
│   ├── metadata.json                        # metadane zebrane przez OBS script
│   └── extracted/                           # katalog z wyciągniętymi plikami
│       ├── source1_video.mp4
│       ├── source2_audio.m4a
│       ├── source3_video.mp4
│       └── source3_audio.m4a
```

## Funkcjonalność

### 1. Pobieranie ścieżki nagrania
- Wykorzystanie `obs_frontend_get_current_record_output_path()` w `obs_script.py` - zwraca katalog wyjściowy
- Po zakończeniu nagrania: wyszukanie najnowszego pliku wideo w katalogu wyjściowym
- Filtrowanie plików na podstawie czasu modyfikacji (ostatnie 30 sekund)

### 2. Tworzenie struktury katalogów
- Tworzenie katalogu głównego na podstawie nazwy pliku nagrania
- Przeniesienie pliku nagrania do nowego katalogu
- Zapisanie metadanych w tym samym katalogu
- Utworzenie podkatalogu `extracted/` dla wyciągniętych plików

### 3. Moment reorganizacji
- **Miejsce**: `obs_script.py` w funkcji `collect_and_save_metadata()`
- **Timing**: Zaraz po zakończeniu nagrania, przed processingiem przez Advanced Scene Switcher

### 4. Aktualizacja procesów
- `advanced_scene_switcher_extractor.py` będzie szukał plików w nowej strukturze
- `extract.py` będzie zapisywał wyciągnięte pliki do katalogu `extracted/`

## Scenariusze użycia

### Scenariusz 1: Podstawowe nagranie
1. Użytkownik kończy nagranie w OBS
2. `obs_script.py` pobiera ścieżkę nagrania
3. Tworzy katalog `nazwa_nagrania/`
4. Przenosi plik nagrania do katalogu
5. Zapisuje `metadata.json` w tym katalogu
6. Advanced Scene Switcher wywołuje ekstrakcję
7. Pliki wyciągnięte trafiają do `extracted/`

### Scenariusz 2: Nagranie bez ekstrakcji
1. Użytkownik kończy nagranie w OBS
2. System reorganizuje pliki (nagranie + metadane)
3. Ekstrakcja może być uruchomiona później ręcznie

## Wymagania techniczne

### Zależności
- OBS Studio Frontend API
- Python `pathlib` dla manipulacji ścieżkami
- `shutil` dla przenoszenia plików

### Obsługa błędów
- Graceful handling gdy nie można utworzyć katalogu
- Fallback do oryginalnej ścieżki jeśli reorganizacja nie powiedzie się
- Logowanie wszystkich operacji

### Kompatybilność
- Nie zachowujem kompatybilności z istniejącym kodem. Obsługa tylko nowej ścieżki

## Korzyści
- Lepsze uporządkowanie plików
- Łatwiejsze zarządzanie nagraniami
- Wszystkie powiązane pliki w jednym miejscu
- Czytelna struktura dla użytkownika