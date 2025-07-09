# Plan implementacji PoC: Audio-driven animations

## Faza 1: Podstawy analizy audio (TDD) ✅ COMPLETE

### 1.1 Setup testów ✅
- [x] Utworzenie `tests/test_audio_analyzer.py`
- [x] Przygotowanie fixtures z przykładowym audio
- [x] Konfiguracja pytest markers dla testów audio

### 1.2 Testy jednostkowe AudioAnalyzer ✅
- [x] Test: inicjalizacja klasy
- [x] Test: lazy loading bibliotek (librosa, scipy)
- [x] Test: obsługa braku bibliotek
- [x] Test: podstawowa analiza audio (tempo, beats)
- [x] Test: detekcja granic sekcji
- [x] Test: filtrowanie onsetów
- [x] Test: analiza pasm częstotliwości
- [x] Test: znajdowanie szczytów energii
- [x] Test: zapis wyników do JSON

### 1.3 Implementacja AudioAnalyzer ✅
- [x] Klasa AudioAnalyzer z lazy loading
- [x] Metoda analyze_for_animation()
- [x] Metody pomocnicze (_detect_boundaries, etc.)
- [x] Obsługa błędów i logowanie

## Faza 2: Integracja z systemem ✅ COMPLETE

### 2.1 Testy integracyjne ✅
- [x] Test: AudioAnalyzer z rzeczywistym plikiem audio
- [x] Test: integracja z FileStructureManager
- [x] Test: przekazywanie danych do BlenderProjectManager

### 2.2 Rozszerzenie BlenderProjectManager ✅
- [x] Test: dodanie parametrów audio do env vars
- [x] Implementacja: rozszerzenie _prepare_environment()
- [x] Test: sprawdzenie czy analiza audio jest opcjonalna

### 2.3 CLI dla analizy audio ✅
- [x] Test: nowe polecenie CLI analyze_audio
- [x] Implementacja: cli/analyze_audio.py
- [x] Test: integracja z istniejącym blend_setup

## Faza 3: Animacje w Blenderze

### 3.1 Testy dla rozszerzonego skryptu Blender
- [ ] Mock Blender API (bpy) for testing
- [ ] Test: load_animation_data() z env vars
- [ ] Test: generowanie keyframes dla różnych właściwości
- [ ] Test: calculate_pip_positions() - grid layout
- [ ] Test: różne tryby animacji (beat-switch, energy-pulse)

### 3.2 Rozszerzenie blender_vse_script.py - Core Functions
- [ ] Funkcja: load_animation_data() - odczyt JSON z BLENDER_VSE_AUDIO_ANALYSIS
- [ ] Funkcja: create_pip_animations() - główny orchestrator animacji
- [ ] Funkcja: calculate_pip_positions() - layout PiP w grid 2x2
- [ ] Funkcja: create_keyframe_sequence() - helper do wstawiania keyframe'ów
- [ ] Funkcja: setup_animation_timeline() - przygotowanie timeline dla animacji

### 3.3 Animation Mode Implementations
- [ ] animate_beat_switch() - przełączanie blend_alpha na beat events
- [ ] animate_energy_pulse() - skalowanie transform.scale_x/y na energy_peaks
- [ ] animate_section_transitions() - płynne przejścia na sections
- [ ] animate_multi_pip() - wszystkie PiP widoczne z różnymi efektami

### 3.4 Blender VSE API Integration
- [ ] Keyframe helpers - wrappers dla strip.keyframe_insert()
- [ ] PiP positioning - kontrola transform.offset_x/y
- [ ] Timeline management - konwersja seconds → frames
- [ ] Strip property animation - blend_alpha, scale, offset

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
- Poniedziałek: Integracja z systemem ✅ COMPLETE
- Wtorek-Środa: Rozszerzenie Blender script (Phase 3)
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
   - Ryzyko: różne wersje Blendera, zmiany w VSE API
   - Mitygacja: sprawdzanie wersji, kompatybilność wsteczna, fallback dla właściwości
   - Aktualizacja: Znamy kluczowe API - bpy.context.scene.sequence_editor, strip.keyframe_insert()

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