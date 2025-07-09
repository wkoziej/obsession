# Plan implementacji PoC: Audio-driven animations

## Faza 1: Podstawy analizy audio (TDD)

### 1.1 Setup testów
- [ ] Utworzenie `tests/test_audio_analyzer.py`
- [ ] Przygotowanie fixtures z przykładowym audio
- [ ] Konfiguracja pytest markers dla testów audio

### 1.2 Testy jednostkowe AudioAnalyzer
- [ ] Test: inicjalizacja klasy
- [ ] Test: lazy loading bibliotek (librosa, scipy)
- [ ] Test: obsługa braku bibliotek
- [ ] Test: podstawowa analiza audio (tempo, beats)
- [ ] Test: detekcja granic sekcji
- [ ] Test: filtrowanie onsetów
- [ ] Test: analiza pasm częstotliwości
- [ ] Test: znajdowanie szczytów energii
- [ ] Test: zapis wyników do JSON

### 1.3 Implementacja AudioAnalyzer
- [ ] Klasa AudioAnalyzer z lazy loading
- [ ] Metoda analyze_for_animation()
- [ ] Metody pomocnicze (_detect_boundaries, etc.)
- [ ] Obsługa błędów i logowanie

## Faza 2: Integracja z systemem

### 2.1 Testy integracyjne
- [ ] Test: AudioAnalyzer z rzeczywistym plikiem audio
- [ ] Test: integracja z FileStructureManager
- [ ] Test: przekazywanie danych do BlenderProjectManager

### 2.2 Rozszerzenie BlenderProjectManager
- [ ] Test: dodanie parametrów audio do env vars
- [ ] Implementacja: rozszerzenie _prepare_environment()
- [ ] Test: sprawdzenie czy analiza audio jest opcjonalna

### 2.3 CLI dla analizy audio
- [ ] Test: nowe polecenie CLI analyze_audio
- [ ] Implementacja: cli/analyze_audio.py
- [ ] Test: integracja z istniejącym blend_setup

## Faza 3: Animacje w Blenderze

### 3.1 Testy dla rozszerzonego skryptu Blender
- [ ] Test: odczyt danych animacji z env vars
- [ ] Test: generowanie keyframes dla PiP
- [ ] Test: różne tryby animacji

### 3.2 Rozszerzenie blender_vse_script.py
- [ ] Funkcja: load_animation_data()
- [ ] Funkcja: create_pip_animations()
- [ ] Funkcja: animate_beat_switch()
- [ ] Funkcja: animate_energy_pulse()
- [ ] Funkcja: animate_section_transitions()

### 3.3 Pomocnicze funkcje Blender
- [ ] Keyframe helpers
- [ ] Easing functions (smooth transitions)
- [ ] PiP layout calculator

## Faza 4: Demonstracja i dokumentacja

### 4.1 Skrypt demonstracyjny
- [ ] demo_audio_animation.py
- [ ] Przykładowe nagranie z muzyką
- [ ] Automatyczne generowanie wszystkich trybów

### 4.2 Dokumentacja
- [ ] README dla PoC
- [ ] Przykłady użycia
- [ ] Screencasty z rezultatami

## Timeline

### Tydzień 1 (Faza 1)
- Poniedziałek-Wtorek: Setup i testy jednostkowe
- Środa-Czwartek: Implementacja AudioAnalyzer
- Piątek: Testy integracyjne

### Tydzień 2 (Faza 2-3)
- Poniedziałek: Integracja z systemem
- Wtorek-Środa: Rozszerzenie Blender script
- Czwartek: Testowanie end-to-end
- Piątek: Bugfixing i optymalizacja

### Tydzień 3 (Faza 4)
- Poniedziałek-Wtorek: Skrypt demo
- Środa: Dokumentacja
- Czwartek-Piątek: Prezentacja i feedback

## Ryzyka i mitygacje

1. **Librosa compatibility**
   - Ryzyko: konflikt wersji z OBS Python
   - Mitygacja: opcjonalna analiza, fallback na prostsze metody

2. **Blender API zmiany**
   - Ryzyko: różne wersje Blendera
   - Mitygacja: sprawdzanie wersji, kompatybilność wsteczna

3. **Performance**
   - Ryzyko: długa analiza dużych plików
   - Mitygacja: cache wyników, analiza przyrostowa

4. **Synchronizacja**
   - Ryzyko: desynchronizacja audio-video
   - Mitygacja: dokładne timestampy, kompensacja opóźnień

## Definition of Done

- [ ] Wszystkie testy przechodzą (unit, integration, e2e)
- [ ] Coverage > 80% dla nowego kodu
- [ ] Dokumentacja kompletna
- [ ] Demo działa na przykładowym nagraniu
- [ ] Code review zaliczone
- [ ] Brak regression w istniejącej funkcjonalności