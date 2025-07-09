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

## Faza 3A: MVP - Beat Switch Animation (Highest Risk First)

### 3A.1 Fundamenty MVP (TDD)
- [ ] Mock Blender API (bpy) for testing - focus na VSE sequence_editor
- [ ] Test: load_animation_data() tylko dla beat events
- [ ] Test: calculate_pip_positions() - prosty hardcoded 2x2 grid
- [ ] Test: animate_beat_switch() - przełączanie blend_alpha na beat timing

### 3A.2 Implementacja MVP
- [ ] load_animation_data() - tylko beat events + basic validation
- [ ] calculate_pip_positions() - hardcoded 2x2 grid layout (4 pozycje)
- [ ] animate_beat_switch() - blend_alpha keyframes na beat events
- [ ] Minimalna integracja z BlenderVSEConfigurator.setup_vse_project()

### 3A.3 Weryfikacja MVP
- [ ] End-to-end test: utworzenie projektu z --animation-mode beat-switch
- [ ] Manual verification w Blenderze: czy keyframes są widoczne w timeline
- [ ] Basic demo: 2 video strips przełączające się w rytm beat events

**🎯 MVP Success Criteria:**
- Blender tworzy projekt z keyframes na timeline
- Video strips mają animowane blend_alpha właściwości
- Timing jest synchronizowany z beat events z analizy audio
- Można otworzyć projekt w Blenderze i zobaczyć animacje

## Faza 3B: Rozszerzenie (Po weryfikacji MVP)

### 3B.1 Energy Pulse Animation
- [ ] Test: animate_energy_pulse() - skalowanie transform.scale_x/y
- [ ] Implementacja: energy_pulse mode z energy_peaks events
- [ ] Integracja z istniejącym MVP system

### 3B.2 Pozostałe tryby animacji
- [ ] animate_section_transitions() - płynne przejścia na sections
- [ ] animate_multi_pip() - wszystkie PiP widoczne z różnymi efektami
- [ ] Advanced keyframe helpers i easing functions

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

### Tydzień 2 (Faza 2-3A)
- Poniedziałek: Integracja z systemem ✅ COMPLETE
- Wtorek: Phase 3A MVP - Beat Switch Animation (TDD + Implementation)
- Środa: Phase 3A MVP - Weryfikacja i manual testing w Blenderze
- Czwartek: Phase 3B (jeśli MVP sukces) lub pivot (jeśli problemy)
- Piątek: Bugfixing i optymalizacja

### Tydzień 3 (Faza 4)
- Poniedziałek-Wtorek: Skrypt demo
- Środa: Dokumentacja
- Czwartek-Piątek: Prezentacja i feedback

## Ryzyka i mitygacje

1. **Librosa compatibility**
   - Ryzyko: konflikt wersji z OBS Python
   - Mitygacja: opcjonalna analiza, fallback na prostsze metody

2. **Blender API zmiany** - 🎯 GŁÓWNE RYZYKO - MVP focus
   - Ryzyko: różne wersje Blendera, zmiany w VSE API, strip.keyframe_insert() może nie działać
   - Mitygacja: MVP approach - weryfikacja najpierw beat-switch, potem inne animacje
   - Aktualizacja: Znamy kluczowe API - bpy.context.scene.sequence_editor, strip.keyframe_insert()
   - MVP Strategy: Szybka weryfikacja czy keyframes w ogóle działają

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