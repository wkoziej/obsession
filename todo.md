# TODO Lista - Faza 0: POC Implementation

## 📋 Status Overview
- **Faza**: POC (Proof of Concept)
- **Okres**: 7 dni
- **Postęp**: 25/29 zadań ukończonych (86%)
- **Ostatnia aktualizacja**: 2024-01-15

## 🗓️ Dzień 1: Setup projektu (4/4 ukończone) ✅

### Środowisko i struktura
- [x] **ENV-001**: Stworzenie struktury folderów projektu
  - `src/core/`, `src/obs_integration/`, `src/cli/`, `tests/`, `docs/`
- [x] **ENV-002**: Konfiguracja `pyproject.toml`
  - Zależności: pytest, ffmpeg-python, pathlib
- [x] **ENV-003**: Konfiguracja `pytest.ini`
  - Test discovery, coverage settings
- [x] **ENV-004**: Pierwszy test smoke dla metadata
  - `test_create_empty_metadata()` - RED phase

## 🗓️ Dzień 2: Metadata podstawy (4/4 ukończone) ✅

### Core metadata functionality
- [x] **META-001**: Implementacja `create_metadata()` - GREEN phase <!-- 2024-01-15 -->
  - Podstawowa struktura JSON metadata
- [x] **META-002**: Test z prawdziwymi źródłami <!-- 2024-01-15 -->
  - `test_create_metadata_with_sources()` - RED phase
- [x] **META-003**: Rozszerzenie `create_metadata()` o źródła <!-- 2024-01-15 -->
  - Obsługa pozycji i skal źródeł - GREEN phase
- [x] **META-004**: Testy walidacji danych <!-- 2024-01-15 -->
  - Edge cases, błędne dane wejściowe

## 🗓️ Dzień 3: OBS Script struktura (4/4 ukończone) ✅

### Podstawowy skrypt OBS
- [x] **OBS-001**: Stworzenie `obs_script.py` <!-- 2024-01-15 -->
  - Podstawowa struktura z lifecycle functions
- [x] **OBS-002**: Implementacja `script_load()` i event callback <!-- 2024-01-15 -->
  - Rejestracja `obs_frontend_add_event_callback()`
- [x] **OBS-003**: Handler dla `RECORDING_STOPPED` event <!-- 2024-01-15 -->
  - Funkcja `on_event()` z rozpoznawaniem eventów
- [x] **OBS-004**: Test integracji z OBS <!-- 2024-01-15 -->
  - Manual test w OBS Studio (testy automatyczne z mock)

## 🗓️ Dzień 4: OBS Metadata collection (5/5 ukończone) ✅

### Zbieranie danych z OBS
- [x] **OBS-005**: Implementacja `save_scene_metadata()` <!-- 2024-01-15 -->
  - Pobieranie current scene z `obs_frontend_get_current_scene()`
- [x] **OBS-006**: Pobieranie video info <!-- 2024-01-15 -->
  - Canvas size i FPS z `obs_get_video_info()`
- [x] **OBS-007**: Enumeracja scene items <!-- 2024-01-15 -->
  - Implementacja callback dla `obs_scene_enum_items()`
- [x] **OBS-008**: Pobieranie pozycji i skal źródeł <!-- 2024-01-15 -->
  - `obs_sceneitem_get_pos()`, `obs_sceneitem_get_scale()`
- [x] **OBS-009**: Zapisywanie JSON do pliku <!-- 2024-01-15 -->
  - Path resolution i file I/O

## 🗓️ Dzień 5: Extractor struktura (4/4 ukończone) ✅

### Podstawowy ekstraktor
- [x] **EXT-001**: Stworzenie `ExtractionResult` class <!-- 2024-01-15 -->
  - Data structure dla wyników ekstrakcji
- [x] **EXT-002**: Test `extract_single_source()` - RED phase <!-- 2024-01-15 -->
  - Podstawowy test case z mock danymi
- [x] **EXT-003**: Implementacja `extract_sources()` - GREEN phase <!-- 2024-01-15 -->
  - Szkielet funkcji z walidacją parametrów
- [x] **EXT-004**: Testy walidacji input <!-- 2024-01-15 -->
  - File existence, metadata validation

## 🗓️ Dzień 6: FFmpeg integration (4/4 ukończone) ✅

### Prawdziwa ekstrakcja wideo
- [x] **EXT-005**: Implementacja FFmpeg crop logic <!-- 2024-01-15 -->
  - Obliczanie parametrów crop z metadata
- [x] **EXT-006**: Subprocess integration <!-- 2024-01-15 -->
  - Wywołanie FFmpeg z proper error handling
- [x] **EXT-007**: Test z prawdziwym plikiem wideo <!-- 2024-01-15 -->
  - End-to-end test z sample video
- [x] **EXT-008**: Output file management <!-- 2024-01-15 -->
  - Directory creation, file naming, safe filename generation

## 🗓️ Dzień 7: CLI i demo (0/4 ukończone)

### Interface i integracja
- [ ] **CLI-001**: Implementacja `cli/extract.py`
  - Argument parsing, main function
- [ ] **CLI-002**: End-to-end test workflow
  - OBS recording → metadata → extraction
- [ ] **CLI-003**: Demo scenariusz
  - 2 sources, manual verification
- [ ] **CLI-004**: Dokumentacja użycia
  - README z przykładami

## 🔄 Kryteria akceptacji (0/5 ukończone)

### Funkcjonalne wymagania
- [ ] **ACC-001**: OBS script zapisuje metadata przy recording stop
- [ ] **ACC-002**: Metadata zawiera pozycje i rozmiary źródeł
- [ ] **ACC-003**: Ekstraktor wycina 2 źródła poprawnie
- [ ] **ACC-004**: CLI pozwala na ręczną ekstrakcję
- [ ] **ACC-005**: End-to-end workflow działa

## 🧪 Testy i jakość (0/4 ukończone)

### Quality assurance
- [ ] **QA-001**: Test coverage > 80%
- [ ] **QA-002**: Wszystkie testy jednostkowe przechodzą
- [ ] **QA-003**: Kod zgodny z PEP 8
- [ ] **QA-004**: Podstawowa dokumentacja kompletna

## 📊 Metryki i monitoring

### Postęp według dni:
- **Dzień 1**: 4/4 (100%) ✅
- **Dzień 2**: 4/4 (100%) ✅
- **Dzień 3**: 4/4 (100%) ✅
- **Dzień 4**: 5/5 (100%) ✅
- **Dzień 5**: 4/4 (100%) ✅
- **Dzień 6**: 4/4 (100%) ✅
- **Dzień 7**: 0/4 (0%)

### Postęp według kategorii:
- **Środowisko**: 4/4 (100%) ✅
- **Metadata**: 4/4 (100%) ✅
- **OBS Integration**: 9/9 (100%) ✅
- **Extractor**: 8/8 (100%) ✅
- **CLI**: 0/4 (0%)

## 🚨 Ryzyka i blokery

### Aktualnie zidentyfikowane:
- [ ] **RISK-001**: Brak dostępu do OBS Studio dla testów
- [ ] **RISK-002**: FFmpeg nie zainstalowany w systemie
- [ ] **RISK-003**: Python OBS API compatibility issues
- [ ] **RISK-004**: File path resolution na różnych OS

### Mitigation actions:
- [ ] **MIT-001**: Zainstaluj OBS Studio 28+
- [ ] **MIT-002**: Zainstaluj FFmpeg 4.4+
- [ ] **MIT-003**: Test Python OBS integration
- [ ] **MIT-004**: Cross-platform path handling

## 📝 Notatki i uwagi

### Decyzje techniczne:
- Python 3.9+ jako baseline
- pytest jako test framework
- FFmpeg jako video processing engine
- JSON jako metadata format

### Założenia POC:
- Maksymalnie 2 źródła dla POC
- Stałe rozmiary źródeł (1920x1080)
- Prosty layout (obok siebie)
- Brak audio processing w POC

### Następne kroki po POC:
1. Jeśli sukces → Faza 1 (MVP Core)
2. Jeśli problemy → Analiza i pivot
3. Dokumentacja lessons learned
4. Plan kolejnej iteracji

---

## 🔄 Instrukcje aktualizacji

### Jak oznaczać ukończone zadania:
1. Zmień `[ ]` na `[x]` po ukończeniu
2. Dodaj datę ukończenia w komentarzu
3. Zaktualizuj procenty postępu
4. Dodaj notatki o problemach/rozwiązaniach

### Przykład:
```markdown
- [x] **ENV-001**: Stworzenie struktury folderów projektu <!-- 2024-01-15 -->
  - `src/core/`, `src/obs_integration/`, `src/cli/`, `tests/`, `docs/`
  - Notatka: Użyto standardowej struktury Python package
```

### Aktualizacja postępu:
- Przelicz procenty po każdym ukończonym zadaniu
- Zaktualizuj sekcję "Status Overview"
- Dodaj entry do "Notatki i uwagi" jeśli potrzebne 