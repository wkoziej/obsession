# Lista zadań - Integracja MIDI z OBSession

## Status: 🚀 W trakcie realizacji

### 🔥 Wysokie priorytety - Etap 1

- [x] **Utworzenie brancha** `feature/midi-integration`
- [x] **Napisanie planu realizacji** - `plan.md`
- [x] **Utworzenie listy zadań** - `todo.md`
- [ ] **Wypchnięcie brancha do repo**

### 🟡 Średnie priorytety - Etap 2

- [ ] **Kopiowanie plików MIDI** 
  - Skopiowanie `midi.py`, `midi_service.py` z `midi_to_integrate/`
  - Adaptacja do struktury `src/midi_integration/`

- [ ] **Dostosowanie struktury**
  - Adaptacja `MidiConfig` do OBSession
  - Simplifikacja `MidiController` (usunięcie zależności daemon)
  - Integracja z OBS WebSocket API

- [ ] **Weryfikacja testów**
  - Przeniesienie `test_midi_service.py` 
  - Sprawdzenie które testy działają po przeniesieniu
  - Aktualizacja importów i zależności

- [ ] **Badanie OBS events**
  - Sprawdzenie dokumentacji OBS Studio
  - Ustalenie timing events zakończenia nagrania
  - Analiza `obs_frontend_add_event_callback`

### 🔵 Niskie priorytety - Etap 3

- [ ] **Implementacja automatycznej ekstrakcji**
  - Utworzenie `AutoExtractor` class
  - Integracja z istniejącym `obs_script.py`
  - Event handling dla zakończenia nagrania

- [ ] **Tworzenie katalogów wyjściowych**
  - Logika nazewnictwa katalogów (nazwa pliku nagrania)
  - Tworzenie struktury katalogów
  - Obsługa błędów i kolizji nazw

---

## 📋 Szczegółowe zadania

### Etap 2: Integracja MIDI

#### 2.1 Struktura katalogów
```
src/midi_integration/
├── __init__.py
├── midi_config.py      # Uproszczona konfiguracja MIDI
├── midi_controller.py  # Kontroler MIDI bez daemon dependencies
└── auto_extractor.py   # Automatyczna ekstrakcja
```

#### 2.2 Zależności do usunięcia/zastąpienia
- `src.daemon.config` → lokalna konfiguracja
- `src.daemon.services.recording_service` → OBS WebSocket
- `src.session.operations` → uproszczone operacje

#### 2.3 Biblioteki do dodania
- `obswebsocket` - komunikacja z OBS
- `mido` - już w istniejącym kodzie

### Etap 3: Automatyczna ekstrakcja

#### 3.1 OBS Events do zbadania
- `OBS_FRONTEND_EVENT_RECORDING_STOPPED`
- `OBS_FRONTEND_EVENT_RECORDING_STOPPING` 
- Timing między eventem a dostępnością pliku

#### 3.2 AutoExtractor funkcjonalność
- Monitoring eventów OBS
- Mapowanie nazw plików nagrania → katalogi wyjściowe
- Integracja z `src.core.extractor.extract_sources`
- Obsługa błędów i logowanie

---

## 🎯 Milestones

### Milestone 1: Środowisko przygotowane ✅
- [x] Branch utworzony
- [x] Plan napisany
- [x] Todo lista utworzona
- [ ] Kod wypchnięty do repo

### Milestone 2: MIDI działa 🔄
- [ ] Pliki MIDI przeniesione i zintegrowane
- [ ] Testy przechodzą
- [ ] Komunikacja z OBS funkcjonuje
- [ ] Sterowanie nagrywaniem działa

### Milestone 3: Auto-ekstrakcja działa 🔄
- [ ] OBS events zbadane
- [ ] AutoExtractor zaimplementowany
- [ ] Katalogi wyjściowe tworzone poprawnie
- [ ] End-to-end workflow funkcjonuje

### Milestone 4: Gotowe do produkcji 🔄
- [ ] Wszystkie testy przechodzą
- [ ] Dokumentacja zaktualizowana
- [ ] Przykłady konfiguracji
- [ ] Instrukcje instalacji

---

## 🔬 Criteria akceptacji

### Dla funkcjonalności MIDI:
- ✅ Kontroler MIDI (RC-600) steruje nagrywaniem
- ✅ Konfiguracja MIDI jest elastyczna
- ✅ Obsługa błędów komunikacji
- ✅ Testy pokrywają > 80% kodu

### Dla automatycznej ekstrakcji:
- ✅ Ekstrakcja uruchamia się automatycznie po zatrzymaniu nagrania
- ✅ Katalogi wyjściowe mają nazwy plików nagrania
- ✅ Separacja audio/video działa poprawnie
- ✅ Integracja z istniejącym kodem OBSession

---

## 📝 Notatki do implementacji

### Uproszczenia względem oryginalnego kodu:
1. **Brak daemon architecture** - bezpośrednie sterowanie OBS
2. **Brak session management** - skupienie na nagrywaniu
3. **Lokalna konfiguracja** - brak zewnętrznych config files
4. **Simplified logging** - wykorzystanie standardowego logging

### Zachowane funkcjonalności:
1. **MIDI device detection** - automatyczne znajdowanie urządzeń
2. **Channel filtering** - obsługa konkretnych kanałów MIDI
3. **CC message handling** - reakcja na Control Change
4. **Reconnection logic** - obsługa rozłączeń urządzenia

---

## 🧪 Plan testowania

### Testy jednostkowe:
- [x] `TestMidiConfig` - konfiguracja MIDI
- [ ] `TestMidiController` - logika sterowania  
- [ ] `TestAutoExtractor` - automatyczna ekstrakcja

### Testy integracyjne:
- [ ] MIDI + OBS komunikacja
- [ ] Auto-ekstrakcja + FFmpeg
- [ ] End-to-end workflow

### Testy z rzeczywistym sprzętem:
- [ ] RC-600 kontroler MIDI
- [ ] OBS Studio nagrywanie
- [ ] Kompletny workflow

---

*Ostatnia aktualizacja: 2025-01-05*