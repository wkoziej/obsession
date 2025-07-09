# Plan Realizacji: Generator Projektów Blender VSE

## 📅 Harmonogram Ogólny

**Metodologia**: TDD (Test-Driven Development)  
**Podejście**: Iteracyjne z testowaniem po każdej fazie

## 🏗️ Faza 1: Przygotowanie Infrastruktury (1 dzień)

### Zadanie 1.1: Konfiguracja Blender Python API

#### Kroki:
1. **Sprawdzenie dostępności bpy**
   ```bash
   # Test czy bpy jest dostępne w systemie
   python -c "import bpy; print('Blender API available')"
   ```

2. **Wybór strategii integracji**
   - **Opcja**: Wywołanie zewnętrzne Blender z skryptem
   
3. **Konfiguracja środowiska**
   ```bash
   # sprawdzenie dostępności blender w PATH
   which blender
   ```

#### Kryteria Akceptacji:
- [ ] Możliwość importu/wywołania Blender API
- [ ] Test tworzenia pustego projektu .blend
- [ ] Dokumentacja wybranej strategii

### Zadanie 1.2: Struktura Modułów

#### Kroki:
1. **Utworzenie struktury plików**
   ```
   src/
   ├── core/
   │   ├── blender_project.py    # Główna logika VSE
   │   └── audio_validator.py    # Walidacja i detekcja plików audio
   └── cli/
       └── blend_setup.py        # Interface CLI
   ```

2. **Podstawowe importy i szkielety klas**
   ```python
   # core/blender_project.py
   class BlenderProjectManager:
       def create_vse_project(self, recording_path: Path) -> Path:
           pass
   
   # core/audio_validator.py  
   class AudioValidator:
       def detect_main_audio(self, extracted_dir: Path, specified_audio: str = None) -> Path:
           pass
   ```

#### Kryteria Akceptacji:
- [ ] Struktura plików utworzona
- [ ] Podstawowe klasy zdefiniowane
- [ ] Importy działają bez błędów

### Zadanie 1.3: Konfiguracja Testów

#### Kroki:
1. **Utworzenie plików testowych**
   ```
   tests/
   ├── test_blender_project.py
   ├── test_audio_validator.py
   └── test_blend_setup_cli.py
   ```

2. **Konfiguracja fixtures**
   ```python
   # tests/conftest.py
   @pytest.fixture
   def sample_recording_structure():
       # Struktura testowa z plikami
       pass
   ```

#### Kryteria Akceptacji:
- [ ] Pliki testowe utworzone
- [ ] Fixtures skonfigurowane
- [ ] `pytest` uruchamia się bez błędów

## 🔧 Faza 2: Walidacja i Detekcja Plików Audio (1 dzień)

### Zadanie 2.1: Implementacja AudioValidator

#### Kroki:
1. **Test-driven development**
   ```python
   # tests/test_audio_validator.py
   def test_single_audio_file_detection():
       # Test gdy jest tylko jeden plik audio
       validator = AudioValidator()
       result = validator.detect_main_audio(extracted_dir)
       assert result is not None
   
   def test_multiple_audio_files_error():
       # Test gdy jest więcej niż jeden plik audio
       validator = AudioValidator()
       with pytest.raises(MultipleAudioFilesError):
           validator.detect_main_audio(extracted_dir)
   ```

2. **Implementacja walidatora**
   ```python
   # core/audio_validator.py
   class AudioValidator:
       def detect_main_audio(self, extracted_dir: Path, specified_audio: str = None) -> Path:
           """Wykrywa główny plik audio lub zgłasza błąd"""
           audio_files = self.find_audio_files(extracted_dir)
           
           if specified_audio:
               return self.validate_specified_audio(extracted_dir, specified_audio)
           
           if len(audio_files) == 0:
               raise NoAudioFileError("Brak plików audio w katalogu extracted/")
           elif len(audio_files) > 1:
               raise MultipleAudioFilesError(f"Znaleziono {len(audio_files)} plików audio. Użyj --main-audio aby wskazać właściwy.")
           
           return audio_files[0]
   ```

3. **Obsługa błędów**
   - Walidacja istnienia pliku audio
   - Obsługa przypadku wielu plików audio
   - Walidacja parametru --main-audio

#### Kryteria Akceptacji:
- [ ] Testy przechodzą (TDD)
- [ ] Detekcja pojedynczego pliku audio działa
- [ ] Błąd przy wielu plikach audio
- [ ] Obsługa parametru --main-audio
- [ ] Dokumentacja metod

### Zadanie 2.2: Integracja z FileStructureManager

#### Kroki:
1. **Rozszerzenie FileStructureManager**
   ```python
   # core/file_structure.py
   @staticmethod
   def ensure_blender_dir(video_path: Path) -> Path:
       """Tworzy katalog blender/ w strukturze nagrania"""
       pass
   
   @staticmethod
   def find_audio_files(extracted_dir: Path) -> List[Path]:
       """Znajduje wszystkie pliki audio w katalogu extracted"""
       pass
   ```

2. **Testy integracji**
   ```python
   def test_blender_directory_creation():
       # Test tworzenia katalogu blender/
       pass
   
   def test_audio_files_detection():
       # Test znajdowania plików audio
       pass
   ```

#### Kryteria Akceptacji:
- [ ] Katalog `blender/` jest tworzony automatycznie
- [ ] Funkcja znajdowania plików audio
- [ ] Integracja z istniejącą strukturą
- [ ] Testy przechodzą

## 🎬 Faza 3: Tworzenie Projektu Blender VSE (2 dni)

### Zadanie 3.1: Podstawowa Konfiguracja Blender

#### Kroki:
1. **Szkielet BlenderProjectManager**
   ```python
   # core/blender_project.py
   class BlenderProjectManager:
       def __init__(self, blender_executable: str = "blender"):
           self.blender_executable = blender_executable
       
       def create_vse_project(self, recording_path: Path) -> Path:
           # 1. Przygotuj skrypt Blender
           # 2. Wywołaj blender --background --python script.py
           # 3. Zwróć ścieżkę do .blend
           pass
   ```

2. **Skrypt Blender (template)**
   ```python
   # templates/vse_setup_template.py
   import bpy
   
   # Czyszczenie sceny
   bpy.ops.wm.read_factory_settings(use_empty=True)
   
   # Konfiguracja VSE
   bpy.context.scene.sequence_editor_create()
   
   # Parametry renderingu
   bpy.context.scene.render.resolution_x = 1280
   bpy.context.scene.render.resolution_y = 720
   bpy.context.scene.render.fps = 30
   ```

3. **Testy podstawowe**
   ```python
   def test_create_empty_blend_project():
       manager = BlenderProjectManager()
       project_path = manager.create_vse_project(sample_recording_path)
       assert project_path.exists()
       assert project_path.suffix == '.blend'
   ```

#### Kryteria Akceptacji:
- [ ] Tworzenie pustego projektu .blend
- [ ] Konfiguracja VSE
- [ ] Podstawowe parametry renderingu
- [ ] Testy przechodzą

### Zadanie 3.2: Dodawanie Ścieżek VSE

#### Kroki:
1. **Implementacja dodawania ścieżek**
   ```python
   def add_video_strips(self, video_files: List[Path], start_frame: int = 1):
       """Dodaje ścieżki wideo do VSE"""
       for i, video_file in enumerate(video_files):
           channel = i + 1
           # bpy.ops.sequencer.movie_strip_add(...)
   
   def add_main_audio_strip(self, audio_file: Path, start_frame: int = 1):
       """Dodaje główną ścieżkę audio do VSE na kanale 1"""
       # bpy.ops.sequencer.sound_strip_add(...)
   ```

2. **Logika organizacji kanałów**
   - Video: kanały 1, 2, 3...
   - Audio: tylko główny audio na kanale 1

3. **Testy z rzeczywistymi plikami**
   ```python
   def test_add_multiple_video_strips():
       # Test dodawania wielu ścieżek wideo
       pass
   
   def test_add_main_audio_strip():
       # Test dodawania głównej ścieżki audio
       pass
   ```

#### Kryteria Akceptacji:
- [ ] Dodawanie ścieżek wideo działa
- [ ] Dodawanie głównej ścieżki audio działa
- [ ] Prawidłowa organizacja kanałów
- [ ] Synchronizacja od frame 1
- [ ] Testy przechodzą

### Zadanie 3.3: Konfiguracja Renderingu

#### Kroki:
1. **Implementacja ustawień renderingu**
   ```python
   def configure_render_settings(self, output_path: Path, fps: int = 30):
       """Konfiguruje parametry renderingu"""
       # Rozdzielczość 720p
       bpy.context.scene.render.resolution_x = 1280
       bpy.context.scene.render.resolution_y = 720
       
       # Format MP4
       bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
       bpy.context.scene.render.ffmpeg.format = 'MPEG4'
       bpy.context.scene.render.ffmpeg.codec = 'H264'
       
       # Ścieżka wyjściowa
       bpy.context.scene.render.filepath = str(output_path)
   ```

2. **Testy konfiguracji**
   ```python
   def test_render_settings_configuration():
       # Test ustawień renderingu
       pass
   ```

#### Kryteria Akceptacji:
- [ ] Rozdzielczość 1280x720
- [ ] Format MP4 (H.264)
- [ ] Ścieżka wyjściowa ustawiona
- [ ] FPS z metadanych
- [ ] Testy przechodzą

## 🖥️ Faza 4: Interface CLI (1 dzień)

### Zadanie 4.1: Implementacja CLI

#### Kroki:
1. **Parsowanie argumentów**
   ```python
   # cli/blend_setup.py
   import argparse
   
   def parse_args():
       parser = argparse.ArgumentParser(
           description='Tworzy projekt Blender VSE z nagrania OBS'
       )
       parser.add_argument('recording_dir', help='Katalog nagrania')
       parser.add_argument('--verbose', '-v', action='store_true')
       parser.add_argument('--force', '-f', action='store_true')
       parser.add_argument('--main-audio', help='Nazwa głównego pliku audio')
       return parser.parse_args()
   ```

2. **Główna logika CLI**
   ```python
   def main():
       args = parse_args()
       
       # Walidacja katalogu
       recording_path = Path(args.recording_dir)
       if not recording_path.exists():
           print(f"Błąd: Katalog {recording_path} nie istnieje")
           return 1
       
       # Tworzenie projektu
       manager = BlenderProjectManager()
       project_path = manager.create_vse_project(recording_path)
       
       print(f"Projekt utworzony: {project_path}")
       return 0
   ```

3. **Testy CLI**
   ```python
   def test_cli_basic_usage():
       # Test podstawowego użycia CLI
       pass
   
   def test_cli_invalid_directory():
       # Test obsługi błędów
       pass
   ```

#### Kryteria Akceptacji:
- [ ] Parsowanie argumentów działa
- [ ] Walidacja katalogów
- [ ] Obsługa błędów
- [ ] Verbose mode
- [ ] Testy przechodzą

### Zadanie 4.2: Integracja Wszystkich Komponentów

#### Kroki:
1. **Workflow integracji**
   ```python
   def create_vse_project(self, recording_path: Path, main_audio_name: str = None) -> Path:
       # 1. Walidacja struktury
       structure = FileStructureManager.find_recording_structure(recording_path)
       
       # 2. Detekcja głównego audio
       audio_validator = AudioValidator()
       main_audio = audio_validator.detect_main_audio(structure.extracted_dir, main_audio_name)
       
       # 3. Znajdź wyekstraktowane pliki wideo
       video_files = self.find_video_files(structure.extracted_dir)
       
       # 4. Utwórz projekt Blender
       blend_path = self.create_blend_file(video_files, main_audio, ...)
       
       return blend_path
   ```

2. **Testy end-to-end**
   ```python
   def test_full_workflow():
       # Test pełnego workflow od katalogu do projektu
       pass
   ```

#### Kryteria Akceptacji:
- [ ] Pełny workflow działa
- [ ] Wszystkie komponenty zintegrowane
- [ ] Testy E2E przechodzą
- [ ] Obsługa błędów na każdym etapie

## 🧪 Faza 5: Testowanie i Optymalizacja (1 dzień)

### Zadanie 5.1: Testy Kompleksowe

#### Kroki:
1. **Testy z różnymi scenariuszami**
   ```python
   def test_scenario_only_video_files():
       # Test gdy są tylko pliki wideo
       pass
   
   def test_scenario_single_audio_file():
       # Test gdy jest tylko jeden plik audio
       pass
   
   def test_scenario_mixed_files():
       # Test mieszanych plików
       pass
   ```


3. **Testy edge cases**
   - Pusty katalog extracted/
   - Wiele plików audio bez parametru --main-audio
   - Uszkodzone pliki wideo/audio
   - Brakujące metadane

#### Kryteria Akceptacji:
- [ ] Wszystkie scenariusze testowe przechodzą
- [ ] Wydajność w akceptowalnych granicach
- [ ] Edge cases obsłużone
- [ ] Pokrycie testów > 90%

### Zadanie 5.2: Dokumentacja i Finalizacja
**Czas**: 2 godziny  
**Priorytet**: Średni

#### Kroki:
1. **Aktualizacja README.md**
   - Dodanie sekcji o Blender VSE
   - Przykłady użycia
   - Wymagania systemowe

2. **Dokumentacja API**
   - Docstrings dla wszystkich metod
   - Przykłady kodu
   - Diagramy workflow

3. **Finalne testy**
   ```bash
   # Uruchomienie pełnego zestawu testów
   uv run pytest --cov=src --cov-report=html
   
   # Test CLI
   uv run python -m cli.blend_setup ./test_recording --verbose
   ```

#### Kryteria Akceptacji:
- [ ] Dokumentacja zaktualizowana
- [ ] API udokumentowane
- [ ] Wszystkie testy przechodzą
- [ ] Gotowe do produkcji

## 📋 Harmonogram Szczegółowy


### Ryzyko 1: Złożoność obsługi wielu plików audio
**Prawdopodobieństwo**: Średnie  
**Wpływ**: Średni  
**Mitigacja**: Jasne komunikaty błędów, dokumentacja parametru --main-audio

## ✅ Definicja Ukończenia (DoD)

Projekt jest ukończony gdy:
- [ ] Wszystkie testy przechodzą (100%)
- [ ] Pokrycie testów > 90%
- [ ] CLI działa zgodnie ze specyfikacją
- [ ] Dokumentacja jest kompletna
- [ ] Kod przeszedł review
- [ ] Wydajność w akceptowalnych granicach
- [ ] Brak znanych bugów krytycznych

## 🔄 Proces Iteracyjny

Po każdej fazie:
1. **Uruchomienie testów** - sprawdzenie czy nic się nie zepsuło
2. **Code review** - sprawdzenie jakości kodu
3. **Dokumentacja** - aktualizacja dokumentacji
4. **Commit** - atomic commit z opisem zmian
5. **Demo** - prezentacja postępu

## 🛠️ Narzędzia i Środowisko

### Wymagane Narzędzia:
- **Python 3.9+** z uv
- **Blender 4.0+** w PATH
- **FFmpeg 4.4+** w PATH
- **pytest** do testów
- **Git** do kontroli wersji

### Środowisko Deweloperskie:
```bash
# Przygotowanie środowiska
uv sync
uv run pytest  # sprawdzenie testów
which blender  # sprawdzenie Blender
which ffmpeg   # sprawdzenie FFmpeg
```

### Komendy Deweloperskie:
```bash
# Uruchomienie testów
uv run pytest tests/test_blender_project.py -v

# Test CLI
uv run python -m cli.blend_setup ./test_recording --verbose

# Sprawdzenie pokrycia testów
uv run pytest --cov=src --cov-report=html
``` 