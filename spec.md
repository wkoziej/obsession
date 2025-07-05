# Specyfikacja Projektu: OBS Canvas Recording MVP

## 1. Cel i Wizja Projektu

### Problem
Nagrywanie wielu źródeł w OBS wymaga ręcznego wycinania każdego źródła po nagraniu, co jest czasochłonne i podatne na błędy.

### Rozwiązanie
System automatycznej ekstrakcji źródeł z nagrania canvas OBS na podstawie metadanych pozycji zapisanych podczas nagrywania.

### Wartość biznesowa
- Oszczędność czasu: 90% redukcja czasu post-processingu
- Eliminacja błędów: automatyczna precyzja wycinania
- Skalowalność: obsługa dowolnej liczby źródeł

## 2. Architektura Systemu (TDD Approach)

### 2.1 Struktura Projektu

```
obs-canvas-recorder/
├── docs/
│   ├── spec.md                    # Ta specyfikacja
│   ├── architecture.md            # Architektura systemu
│   └── user-guide.md             # Instrukcja użytkownika
│
├── src/
│   ├── core/                     # Logika biznesowa
│   │   ├── __init__.py
│   │   ├── metadata.py           # Zarządzanie metadanymi (JSON schema)
│   │   ├── extractor.py          # Ekstrakcja źródeł (FFmpeg wrapper)
│   │   ├── validator.py          # Walidacja danych
│   │   └── config.py             # Konfiguracja systemu
│   │
│   ├── obs_integration/          # Integracja z OBS
│   │   ├── __init__.py
│   │   ├── obs_script.py         # Główny skrypt OBS (Python)
│   │   ├── scene_analyzer.py     # Analiza sceny (obs_scene_enum_items)
│   │   └── event_handler.py      # Obsługa eventów (RECORDING_STOPPED)
│   │
│   ├── cli/                      # Interface linii komend
│   │   ├── __init__.py
│   │   ├── main.py               # Główny CLI
│   │   ├── extract.py            # Komenda ekstrakcji
│   │
│   └── utils/                    # Narzędzia pomocnicze
│       ├── __init__.py
│       ├── ffmpeg_wrapper.py     # Wrapper dla FFmpeg
│       ├── file_watcher.py       # Obserwator plików
│       └── logger.py             # System logowania
│
├── tests/                        # Testy (TDD)
│   ├── unit/                     # Testy jednostkowe
│   │   ├── test_metadata.py
│   │   ├── test_extractor.py
│   │   ├── test_validator.py
│   │   └── test_ffmpeg_wrapper.py
│   │
│   ├── integration/              # Testy integracyjne
│   │   ├── test_obs_integration.py
│   │   ├── test_cli_workflow.py
│   │   └── test_end_to_end.py
│   │
│   ├── fixtures/                 # Dane testowe
│   │   ├── sample_metadata.json
│   │   ├── sample_video.mp4
│   │   └── expected_outputs/
│   │
│   └── conftest.py              # Konfiguracja pytest
│
│
│
├── .github/                      # CI/CD
│   └── workflows/
│       ├── test.yml
│       ├── release.yml
│       └── docs.yml
│
│
├── pyproject.toml               # Konfiguracja projektu
├── pytest.ini                  # Konfiguracja pytest
├── .gitignore
└── README.md
```

## 3. Fazy Rozwoju (TDD Incremental)

### Faza 0: POC (Proof of Concept) - 1 tydzień
**Cel**: Sprawdzenie wykonalności podstawowej funkcjonalności

**Deliverables**:
- Minimalny skrypt OBS zapisujący metadane
- Prosty ekstraktor używający FFmpeg
- Podstawowe testy smoke

**Kryteria akceptacji**:
- [ ] Skrypt OBS zapisuje pozycje źródeł do JSON (używając `obs_scene_enum_items()`)
- [ ] Event callback reaguje na `OBS_FRONTEND_EVENT_RECORDING_STOPPED`
- [ ] Ekstraktor wycina jedno źródło z nagrania (FFmpeg crop filter)
- [ ] Proces działa end-to-end dla 2 źródeł

### Faza 1: MVP Core - 2 tygodnie
**Cel**: Funkcjonalna wersja dla podstawowych przypadków użycia

**TDD Cycle**:
1. **Red**: Napisz testy dla core functionality
2. **Green**: Implementuj minimum do przejścia testów
3. **Refactor**: Optymalizuj i popraw kod

**User Stories**:
```gherkin
Feature: Metadata Collection
  Scenario: Recording with multiple sources
    Given OBS scene with 3 video sources
    When user starts and stops recording
    Then metadata JSON is created with source positions
    And metadata contains canvas dimensions and FPS

Feature: Source Extraction
  Scenario: Extract individual sources
    Given recording file and metadata JSON
    When user runs extraction command
    Then individual MP4 files are created for each source
    And audio tracks are extracted separately
```

**Kryteria akceptacji**:
- [ ] Wszystkie testy jednostkowe przechodzą
- [ ] Obsługa 1-10 źródeł wideo
- [ ] Ekstrakcja audio tracks
- [ ] CLI interface
- [ ] Walidacja metadanych

### Faza 2: Production Ready - 2 tygodnie
**Cel**: Stabilna wersja gotowa do użytku produkcyjnego

**Dodatkowe funkcjonalności**:
- Error handling i recovery
- Logging i monitoring
- Performance optimization
- Dokumentacja użytkownika

**Kryteria akceptacji**:
- [ ] Test coverage > 90%
- [ ] Obsługa błędów FFmpeg
- [ ] Batch processing
- [ ] File watcher service
- [ ] Performance benchmarks

## 4. Strategia Testowania (TDD)

### 4.1 Piramida Testów

```
    /\
   /  \      E2E Tests (5%)
  /____\     - Full workflow tests
 /      \    - OBS integration tests
/________\   Integration Tests (15%)
          \  - Component interaction
           \ - FFmpeg integration
            \Unit Tests (80%)
             - Pure functions
             - Business logic
             - Data validation
```

### 4.2 Test Categories

**Unit Tests** (Szybkie, izolowane):
```python
# test_metadata.py
def test_metadata_creation():
    # Given
    sources = [{"name": "Camera1", "x": 0, "y": 0}]
    
    # When
    metadata = create_metadata(sources, canvas_size=(1920, 1080))
    
    # Then
    assert metadata["canvas_size"] == [1920, 1080]
    assert len(metadata["sources"]) == 1
```

**Integration Tests** (Komponenty razem):
```python
# test_extraction_workflow.py
def test_full_extraction_workflow():
    # Given
    video_file = "fixtures/sample_recording.mp4"
    metadata_file = "fixtures/sample_metadata.json"
    
    # When
    result = extract_sources(video_file, metadata_file)
    
    # Then
    assert result.success
    assert len(result.extracted_files) == 3
    assert all(file.exists() for file in result.extracted_files)
```

**E2E Tests** (Cały system):
```python
# test_obs_workflow.py
def test_obs_recording_to_extraction():
    # Given OBS is running with test scene
    # When recording is started and stopped
    # Then metadata is saved and extraction works
    pass
```

### 4.3 Test Data Management

**Fixtures Strategy**:
- Małe pliki testowe (< 1MB)
- Syntetyczne dane dla różnych scenariuszy
- Mockowanie FFmpeg dla szybkich testów
- Prawdziwe pliki dla testów integracyjnych

## 5. Definicja Gotowości (Definition of Done)

### Dla każdej funkcjonalności:
- [ ] Testy jednostkowe napisane i przechodzą
- [ ] Testy integracyjne przechodzą
- [ ] Code review zakończony
- [ ] Dokumentacja zaktualizowana
- [ ] Performance nie pogorszyło się
- [ ] Backwards compatibility zachowane

### Dla release:
- [ ] Wszystkie testy przechodzą (CI/CD)
- [ ] Manual testing wykonany
- [ ] Dokumentacja użytkownika kompletna
- [ ] Performance benchmarks w normie
- [ ] Security review przeprowadzone

## 6. Metryki Sukcesu

### Techniczne:
- Test coverage: > 90%
- Build time: < 2 minuty
- Test execution time: < 30 sekund
- Memory usage: < 100MB podczas ekstrakcji

### Funkcjonalne:
- Extraction accuracy: 100% (pixel-perfect)
- Supported sources: 1-20 per recording
- Max canvas size: 8K (7680x4320)
- Processing speed: > 1x realtime

### Użytkowość:
- Setup time: < 5 minut
- CLI commands: < 3 kroki dla podstawowego workflow
- Error messages: Clear and actionable
- Documentation: Complete examples for all use cases

## 7. Ryzyka i Mitigation

### Techniczne Ryzyka:
1. **FFmpeg compatibility issues**
   - Mitigation: Extensive testing on different systems
   - Fallback: Multiple FFmpeg command strategies

2. **OBS API changes**
   - Mitigation: Version pinning and compatibility layer
   - Monitoring: OBS release notifications

3. **Performance with large files**
   - Mitigation: Streaming processing, chunking
   - Testing: Performance benchmarks in CI

### Biznesowe Ryzyka:
1. **User adoption**
   - Mitigation: Excellent documentation, examples
   - Strategy: Community engagement, tutorials

2. **Maintenance burden**
   - Mitigation: High test coverage, clean architecture
   - Strategy: Automated releases, community contributions

## 8. Timeline i Milestones

### Sprint 1 (POC): Dni 1-7
- Day 1-2: Setup projektu, testy smoke
- Day 3-4: Podstawowy skrypt OBS
- Day 5-6: Minimalny ekstraktor
- Day 7: POC demo i ewaluacja

### Sprint 2 (MVP Core): Dni 8-21
- Week 2: Core metadata handling + tests
- Week 3: Robust extraction + CLI

### Sprint 3 (Production): Dni 22-35
- Week 4: Error handling, logging
- Week 5: Performance, documentation

### Sprint 4 (Advanced): Dni 36-56
- Week 6-7: GUI, NLE export
- Week 8: Polish, release prep

## 9. Środowisko Deweloperskie

### Setup Requirements:
```bash
# Python 3.9+
# FFmpeg 4.4+
# OBS Studio 28+
# Git
```

### Development Workflow:
1. **Feature Branch**: `git checkout -b feature/metadata-validation`
2. **TDD Cycle**: Red → Green → Refactor
3. **Commit**: Atomic commits z tests
4. **PR**: Code review + CI checks
5. **Merge**: Squash merge do main

### Quality Gates:
- All tests pass
- Code coverage maintained
- No linting errors
- Performance benchmarks pass
- Documentation updated

Ten approach zapewni wysoką jakość kodu, szybki development i łatwą maintenance w długim terminie. 