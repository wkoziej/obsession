# Plan realizacji integracji MIDI z OBSession

## Cel projektu
Rozszerzenie systemu OBSession o możliwość sterowania nagrywaniem przez kontroler MIDI oraz automatyczną ekstrakcję źródeł po zakończeniu nagrania.

## Zakres funkcjonalności

### 1. Integracja MIDI
- **Sterowanie nagrywaniem**: Start/stop nagrywania przez kontroler MIDI (RC-600)
- **Konfiguracja**: Elastyczna konfiguracja przypisań MIDI CC do akcji
- **Monitoring**: Ciągłe monitorowanie urządzenia MIDI w tle
- **Obsługa błędów**: Graceful handling rozłączeń i błędów komunikacji

### 2. Automatyczna ekstrakcja
- **Trigger**: Automatyczne uruchomienie ekstrakcji po zatrzymaniu nagrania
- **Organizacja plików**: Utworzenie katalogu o nazwie pliku nagrania
- **Format wyjściowy**: Separacja audio (.m4a) i video (.mp4) zgodnie z capabilities źródeł
- **Integracja z OBS**: Wykorzystanie istniejących metadanych z OBS script

## Architektura docelowa

```
obsession/
├── src/
│   ├── midi_integration/
│   │   ├── __init__.py
│   │   ├── midi_config.py      # Konfiguracja MIDI
│   │   ├── midi_controller.py  # Główny kontroler MIDI
│   │   └── auto_extractor.py   # Automatyczna ekstrakcja
│   ├── obs_integration/
│   │   ├── obs_script.py       # Rozszerzony o auto-ekstrakcję
│   │   └── ...
│   └── ...
├── tests/
│   ├── midi_integration/
│   │   ├── test_midi_config.py
│   │   ├── test_midi_controller.py
│   │   └── test_auto_extractor.py
│   └── ...
└── ...
```

## Etapy realizacji

### Etap 1: Przygotowanie środowiska
- [x] Utworzenie brancha `feature/midi-integration`
- [x] Napisanie planu realizacji
- [ ] Utworzenie struktury katalogów
- [ ] Przeniesienie i adaptacja plików MIDI

### Etap 2: Integracja MIDI
- [ ] Adaptacja `MidiConfig` do struktury OBSession
- [ ] Simplifikacja `MidiController` (usunięcie zależności od daemon)
- [ ] Integracja z OBS WebSocket API
- [ ] Aktualizacja testów jednostkowych

### Etap 3: Automatyczna ekstrakcja
- [ ] Badanie OBS events (timing zakończenia nagrania)
- [ ] Implementacja `AutoExtractor` 
- [ ] Integracja z istniejącym `obs_script.py`
- [ ] Logika tworzenia katalogów wyjściowych

### Etap 4: Testy i integracja
- [ ] Testy jednostkowe dla nowych komponentów
- [ ] Testy integracyjne z rzeczywistym kontrolerem MIDI
- [ ] Testy end-to-end całego workflow
- [ ] Dokumentacja użytkowania

### Etap 5: Finalizacja
- [ ] Aktualizacja dokumentacji projektu
- [ ] Przykłady konfiguracji
- [ ] Instrukcje instalacji i konfiguracji

## Zależności techniczne

### Biblioteki Python
- `mido` - komunikacja MIDI
- `obswebsocket` - komunikacja z OBS Studio
- `ffmpeg-python` - istniejąca integracja

### Wymagania systemowe
- OBS Studio z zainstalowanym skryptem OBSession
- Kontroler MIDI (RC-600 lub kompatybilny)
- Python 3.9+
- FFmpeg 4.4+

## Konfiguracja docelowa

```python
# Przykład konfiguracji MIDI
midi_config = {
    "enabled": True,
    "device_name": "RC-600:RC-600 MIDI 1 28:0",
    "channel": 15,
    "start_recording_cc": 64,
    "stop_recording_cc": 65,
    "auto_extract": True,
    "output_base_dir": "./recordings"
}
```

## Workflow użytkownika

1. **Przygotowanie**:
   - Uruchomienie OBS Studio ze skryptem OBSession
   - Podłączenie kontrolera MIDI (RC-600)
   - Uruchomienie modułu MIDI w tle

2. **Nagrywanie**:
   - Wciśnięcie przycisku na kontrolerze MIDI → Start nagrywania
   - OBS rozpoczyna nagrywanie + zbieranie metadanych
   - Ponowne wciśnięcie przycisku → Stop nagrywania

3. **Automatyczna ekstrakcja**:
   - System wykrywa zakończenie nagrania
   - Automatyczne uruchomienie ekstrakcji źródeł
   - Utworzenie katalogu `nazwa_nagrania/`
   - Separacja plików audio/video według capabilities

## Metryki sukcesu

- ✅ Bezproblemowe sterowanie nagrywaniem przez MIDI
- ✅ Automatyczna ekstrakcja bez interwencji użytkownika
- ✅ Pokrycie testami > 80%
- ✅ Dokumentacja kompletna i aktualna
- ✅ Kompatybilność z istniejącą funkcjonalnością OBSession