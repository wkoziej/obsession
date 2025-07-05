# Plan Implementacji - Faza 0: POC (Proof of Concept)

## Cel Fazy POC
Sprawdzenie wykonalności podstawowej funkcjonalności systemu automatycznej ekstrakcji źródeł z nagrań OBS canvas.

**Czas realizacji**: 7 dni
**Podejście**: TDD (Test-Driven Development)

## Architektura POC

### Minimalna struktura projektu
```
obs-canvas-recorder/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── metadata.py
│   │   └── extractor.py
│   ├── obs_integration/
│   │   ├── __init__.py
│   │   └── obs_script.py
│   └── cli/
│       ├── __init__.py
│       └── extract.py
├── tests/
│   ├── __init__.py
│   ├── test_metadata.py
│   ├── test_extractor.py
│   └── fixtures/
│       ├── sample_metadata.json
│       └── sample_video.mp4
├── pyproject.toml
├── pytest.ini
└── README.md
```

## Harmonogram Implementacji

### Dzień 1-2: Setup projektu i podstawowe testy

#### Dzień 1: Inicjalizacja projektu
**Cele**:
- Setup środowiska Python
- Konfiguracja pytest
- Pierwszy test smoke
- Podstawowa struktura folderów

**Deliverables**:
- `pyproject.toml` z zależnościami
- `pytest.ini` z konfiguracją testów
- Pierwsza implementacja `src/core/metadata.py`
- Test smoke: `tests/test_metadata.py`

**TDD Cycle**:
```python
# test_metadata.py - RED
def test_create_empty_metadata():
    metadata = create_metadata([], canvas_size=(1920, 1080))
    assert metadata["canvas_size"] == [1920, 1080]
    assert metadata["sources"] == {}

# metadata.py - GREEN
def create_metadata(sources, canvas_size):
    return {
        "canvas_size": list(canvas_size),
        "sources": {}
    }
```

#### Dzień 2: Rozszerzenie metadata handling
**Cele**:
- Obsługa źródeł w metadanych
- Walidacja podstawowych danych
- Testy dla różnych scenariuszy

**TDD Cycle**:
```python
# RED - test z prawdziwymi źródłami
def test_create_metadata_with_sources():
    sources = [
        {"name": "Camera1", "x": 0, "y": 0, "width": 1920, "height": 1080},
        {"name": "Camera2", "x": 1920, "y": 0, "width": 1920, "height": 1080}
    ]
    metadata = create_metadata(sources, canvas_size=(3840, 1080))
    assert len(metadata["sources"]) == 2
    assert metadata["sources"]["Camera1"]["position"]["x"] == 0
```

### Dzień 3-4: Podstawowy skrypt OBS

#### Dzień 3: Struktura skryptu OBS
**Cele**:
- Stworzenie podstawowego skryptu Python dla OBS
- Implementacja event handlera
- Test integracji z OBS API

**Implementacja**:
```python
# obs_script.py
import obspython as obs
import json
import os

def script_description():
    return "Canvas Recorder - POC"

def script_load(settings):
    obs.obs_frontend_add_event_callback(on_event)

def on_event(event):
    if event == obs.OBS_FRONTEND_EVENT_RECORDING_STOPPED:
        save_scene_metadata()

def save_scene_metadata():
    # Implementacja w następnym kroku
    pass
```

#### Dzień 4: Implementacja zbierania metadanych
**Cele**:
- Pobieranie informacji o scenie z OBS
- Zapisywanie metadanych do JSON
- Test na prawdziwej scenie OBS

**Implementacja**:
```python
def save_scene_metadata():
    scene_source = obs.obs_frontend_get_current_scene()
    if not scene_source:
        return
    
    scene = obs.obs_scene_from_source(scene_source)
    video_info = obs.obs_get_video_info()
    
    metadata = {
        "canvas_size": [video_info.base_width, video_info.base_height],
        "fps": video_info.fps_num,
        "sources": {}
    }
    
    # Enumeracja źródeł
    def enum_item(scene, item, param):
        source = obs.obs_sceneitem_get_source(item)
        name = obs.obs_source_get_name(source)
        
        pos = obs.vec2()
        obs.obs_sceneitem_get_pos(item, pos)
        
        scale = obs.vec2()
        obs.obs_sceneitem_get_scale(item, scale)
        
        metadata["sources"][name] = {
            "position": {"x": pos.x, "y": pos.y},
            "scale": {"x": scale.x, "y": scale.y}
        }
        return True
    
    obs.obs_scene_enum_items(scene, enum_item, None)
    
    # Zapisz do pliku
    output_path = get_last_recording_path() + ".json"
    with open(output_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    obs.obs_source_release(scene_source)
```

### Dzień 5-6: Minimalny ekstraktor

#### Dzień 5: Struktura ekstraktora
**Cele**:
- Implementacja podstawowego ekstraktora
- Testy z mock FFmpeg
- Walidacja parametrów wejściowych

**TDD Cycle**:
```python
# test_extractor.py - RED
def test_extract_single_source():
    metadata = {
        "canvas_size": [1920, 1080],
        "sources": {
            "Camera1": {
                "position": {"x": 0, "y": 0},
                "scale": {"x": 1.0, "y": 1.0}
            }
        }
    }
    
    result = extract_sources("input.mp4", metadata)
    assert result.success
    assert len(result.extracted_files) == 1
    assert "Camera1.mp4" in result.extracted_files

# extractor.py - GREEN
class ExtractionResult:
    def __init__(self, success=False, extracted_files=None):
        self.success = success
        self.extracted_files = extracted_files or []

def extract_sources(video_file, metadata):
    # Implementacja z FFmpeg
    pass
```

#### Dzień 6: Implementacja FFmpeg integration
**Cele**:
- Prawdziwa implementacja z FFmpeg
- Obsługa crop filter
- Test na prawdziwym pliku wideo

**Implementacja**:
```python
import subprocess
from pathlib import Path

def extract_sources(video_file, metadata):
    if not Path(video_file).exists():
        return ExtractionResult(success=False)
    
    output_dir = Path(video_file).stem + "_extracted"
    output_dir.mkdir(exist_ok=True)
    
    extracted_files = []
    
    for source_name, info in metadata['sources'].items():
        output_file = output_dir / f"{source_name}.mp4"
        
        # Oblicz wymiary crop
        canvas_width, canvas_height = metadata['canvas_size']
        x = int(info['position']['x'])
        y = int(info['position']['y'])
        
        # Dla POC: założenie 1920x1080 dla każdego źródła
        width = 1920
        height = 1080
        
        cmd = [
            'ffmpeg',
            '-i', str(video_file),
            '-filter:v', f'crop={width}:{height}:{x}:{y}',
            '-c:v', 'libx264',
            '-crf', '23',
            '-preset', 'fast',
            '-y',  # Overwrite output
            str(output_file)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            extracted_files.append(str(output_file))
        except subprocess.CalledProcessError as e:
            return ExtractionResult(success=False)
    
    return ExtractionResult(success=True, extracted_files=extracted_files)
```

### Dzień 7: Integracja i demo

#### Cele finalne:
- CLI interface do ekstraktora
- Test end-to-end z prawdziwym nagraniem OBS
- Demo workflow
- Dokumentacja POC

**CLI Implementation**:
```python
# cli/extract.py
import argparse
import json
from pathlib import Path
from ..core.extractor import extract_sources

def main():
    parser = argparse.ArgumentParser(description='Extract sources from OBS canvas recording')
    parser.add_argument('video_file', help='Path to video file')
    parser.add_argument('metadata_file', help='Path to metadata JSON file')
    
    args = parser.parse_args()
    
    with open(args.metadata_file, 'r') as f:
        metadata = json.load(f)
    
    result = extract_sources(args.video_file, metadata)
    
    if result.success:
        print(f"Successfully extracted {len(result.extracted_files)} sources:")
        for file in result.extracted_files:
            print(f"  - {file}")
    else:
        print("Extraction failed")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
```

## Kryteria Sukcesu POC

### Funkcjonalne:
- [ ] Skrypt OBS zapisuje metadane przy zatrzymaniu nagrania
- [ ] Metadane zawierają pozycje i rozmiary źródeł
- [ ] Ekstraktor poprawnie wycina 2 źródła z nagrania
- [ ] CLI pozwala na ręczne uruchomienie ekstrakcji
- [ ] Proces działa end-to-end

### Techniczne:
- [ ] Wszystkie testy jednostkowe przechodzą
- [ ] Kod jest zgodny z PEP 8
- [ ] Dokumentacja podstawowa jest kompletna
- [ ] Projekt można zainstalować i uruchomić

### Jakościowe:
- [ ] Wyniki ekstrakcji są wizualnie poprawne
- [ ] Czas ekstrakcji < 2x długość nagrania
- [ ] Brak błędów w konsoli OBS
- [ ] Pliki wyjściowe mają właściwe nazwy

## Setup Development Environment

### Wymagania:
```bash
# Python 3.9+
python --version

# FFmpeg
ffmpeg -version

# OBS Studio 28+
# (manual installation)
```

### Instalacja projektu:
```bash
# Clone/create project
mkdir obs-canvas-recorder
cd obs-canvas-recorder

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -e .

# Run tests
pytest
```

### Konfiguracja OBS:
1. Otwórz OBS Studio
2. Tools → Scripts
3. Add → wybierz `src/obs_integration/obs_script.py`
4. Skrypt powinien być załadowany i aktywny

## Testowanie POC

### Scenariusz testowy:
1. **Setup sceny OBS**:
   - Dodaj 2 źródła wideo (kamery/obrazy)
   - Ułóż je obok siebie (np. 1920x1080 każde)
   - Canvas: 3840x1080

2. **Nagranie**:
   - Start Recording
   - Nagraj 10-15 sekund
   - Stop Recording

3. **Weryfikacja**:
   - Sprawdź czy powstał plik `.json` z metadanymi
   - Uruchom CLI ekstraktor
   - Sprawdź czy powstały 2 pliki wideo
   - Odtwórz pliki i zweryfikuj zawartość

### Oczekiwane wyniki:
```
recording_2024_01_15_143022.mkv
recording_2024_01_15_143022.mkv.json
recording_2024_01_15_143022_extracted/
├── Camera_1.mp4
└── Camera_2.mp4
```

## Następne kroki po POC

Jeśli POC się powiedzie:
1. **Faza 1**: Rozszerzenie na więcej źródeł
2. **Faza 2**: Automatyczny watcher plików
3. **Faza 3**: GUI interface
4. **Faza 4**: Integracja z NLE

Jeśli POC napotka problemy:
1. Analiza przyczyn
2. Pivot w architekturze
3. Alternatywne podejścia (np. Lua zamiast Python)
4. Uproszczenie scope'u

## Metryki POC

### Czas implementacji:
- Setup: 0.5 dnia
- Metadata: 1.5 dnia  
- OBS Integration: 2 dni
- Extractor: 2 dni
- CLI + Demo: 1 dzień
- **Total: 7 dni**

### Jakość kodu:
- Test coverage: > 80%
- Linting: 0 błędów
- Documentation: Podstawowa kompletna

### Performance:
- Extraction speed: Akceptowalna dla POC
- Memory usage: < 200MB
- File size overhead: < 10%

Ten plan zapewni solidną podstawę dla dalszego rozwoju projektu i pozwoli na wczesną weryfikację kluczowych założeń technicznych. 