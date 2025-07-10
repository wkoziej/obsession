# Plan Refaktoryzacji Architektury Blender VSE - Postępy

## Cel
Zrefaktoryzować monolityczną klasę `BlenderVSEConfigurator` (892 linie) na mniejsze, bardziej skupione komponenty przy zachowaniu pełnej kompatybilności wstecznej.
Implentuj tylko niezbędne rzeczy w tworzonych klasach.


## Postęp Ogólny
- [x] Utworzenie brancha `refactor/blender-vse-architecture`
- [x] Analiza zależności i wzorców użycia
- [x] Projekt nowej architektury
- [ ] Implementacja refaktoryzacji
- [ ] Walidacja i testy

## Nowa Architektura

### 1. Struktura Klas
- [ ] `src/core/blender_vse/constants.py` - Wyciągnięcie magicznych liczb
  - [ ] `BlenderConstants` (DEFAULT_FPS, DEFAULT_RESOLUTION_X/Y)
  - [ ] `AnimationConstants` (ENERGY_SCALE_FACTOR, PIP_SCALE_FACTOR, PIP_MARGIN)
  
- [ ] `src/core/blender_vse/config.py` - Konfiguracja z walidacją
  - [ ] `BlenderVSEConfig` - Parsowanie i walidacja parametrów
  
- [ ] `src/core/blender_vse/project_setup.py` - Podstawowa konfiguracja VSE
  - [ ] `BlenderProjectSetup` - Setup sceny, audio, wideo, render
  
- [ ] `src/core/blender_vse/keyframe_helper.py` - Eliminacja duplikacji
  - [ ] `KeyframeHelper` - Wspólne metody keyframe'ów
  
- [ ] `src/core/blender_vse/layout_manager.py` - Pozycjonowanie PiP
  - [ ] `BlenderLayoutManager` - Kalkulacje pozycji, layout 2x2, multi-pip
  
- [ ] `src/core/blender_vse/animation_engine.py` - Główna logika animacji
  - [ ] `BlenderAnimationEngine` - Delegowanie do animatorów
  
- [ ] `src/core/blender_vse/animators/` - Specyficzne animatory
  - [ ] `BeatSwitchAnimator` - Animacje przełączania na beat
  - [ ] `EnergyPulseAnimator` - Animacje pulsowania na energy peaks
  - [ ] `MultiPipAnimator` - Złożone animacje multi-pip
  
- [ ] `src/core/blender_vse_script.py` - Zrefaktoryzowana facade
  - [ ] `BlenderVSEConfigurator` - Facade pattern zachowujący kompatybilność

### 2. Zachowanie Kompatybilności ✅
- [x] Główna klasa `BlenderVSEConfigurator` pozostaje jako facade
- [x] Wszystkie publiczne metody zachowują identyczne sygnatury
- [x] Zmienne środowiskowe pozostają bez zmian
- [x] Testy działają bez modyfikacji

### 3. Kolejność Implementacji

#### Faza 1: Utworzenie modułu constants i config
- [ ] Utworzenie struktury katalogów
- [ ] Implementacja `constants.py`
- [ ] Implementacja `config.py`
- [ ] Aktualizacja głównej klasy do używania nowych modułów
- [ ] Testy fazy 1

#### Faza 2: Wyciągnięcie KeyframeHelper i LayoutManager
- [ ] Implementacja `keyframe_helper.py`
- [ ] Implementacja `layout_manager.py`
- [ ] Refaktoryzacja głównej klasy
- [ ] Testy fazy 2

#### Faza 3: Rozdzielenie animatorów na osobne klasy
- [ ] Implementacja `animators/beat_switch_animator.py`
- [ ] Implementacja `animators/energy_pulse_animator.py`
- [ ] Implementacja `animators/multi_pip_animator.py`
- [ ] Implementacja `animation_engine.py`
- [ ] Testy fazy 3

#### Faza 4: Refaktoryzacja głównej klasy jako facade
- [ ] Implementacja `project_setup.py`
- [ ] Przekształcenie głównej klasy w facade
- [ ] Testy fazy 4

#### Faza 5: Walidacja i testy
- [ ] Uruchomienie wszystkich testów
- [ ] Walidacja kompatybilności wstecznej
- [ ] Testy integracyjne
- [ ] Dokumentacja zmian

## Metryki Przed/Po
### Przed:
- `BlenderVSEConfigurator`: 892 linie, 1 klasa
- Metoda `setup_vse_project()`: ~150 linii
- Duplikacja kodu keyframe'ów: 6+ wystąpień
- Magiczne liczby: 10+ wartości

### Po (cel):
- `BlenderVSEConfigurator`: ~100 linii (facade)
- Komponenty: 8 klas o 50-100 liniach każda
- Duplikacja kodu: 0 (KeyframeHelper)
- Magiczne liczby: 0 (constants.py)

## Ryzyka i Mitygacja
- ✅ **Ryzyko**: Złamanie kompatybilności wstecznej
  - **Mitygacja**: Zachowanie wszystkich publicznych interfejsów
- ✅ **Ryzyko**: Nieprzechodzące testy
  - **Mitygacja**: Testy po każdej fazie, bez zmian w testach
- ✅ **Ryzyko**: Złamanie subprocess execution
  - **Mitygacja**: Zachowanie wzorca wykonywania