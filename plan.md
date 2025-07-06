# Plan implementacji: Centralizacja logiki struktury katalogów

## Cel
Stworzenie centralnego modułu `FileStructureManager` i refaktoring istniejącego kodu aby eliminować duplikację logiki struktury katalogów.

## Faza 1: Stworzenie FileStructureManager

### 1.1 Utworzenie `src/core/file_structure.py`
```python
@dataclass
class RecordingStructure:
    """Reprezentuje strukturę katalogów nagrania."""
    recording_dir: Path          # Katalog główny nagrania
    video_file: Path            # Plik wideo nagrania  
    metadata_file: Path         # Plik metadanych (zawsze metadata.json)
    extracted_dir: Path         # Katalog extracted/

class FileStructureManager:
    """Centralne zarządzanie strukturą katalogów nagrań."""
    
    @staticmethod
    def get_structure(video_path: Path) -> RecordingStructure:
        """Zwraca strukturę katalogów dla danego pliku wideo."""
        
    @staticmethod
    def create_structure(video_path: Path) -> RecordingStructure:
        """Tworzy nową strukturę katalogów."""
        
    @staticmethod
    def get_extracted_dir(video_path: Path) -> Path:
        """Zwraca katalog extracted/ dla danego nagrania."""
        
    @staticmethod
    def get_metadata_file(video_path: Path) -> Path:
        """Zwraca ścieżkę do pliku metadata.json."""
        
    @staticmethod
    def create_recording_directory_name(video_path: Path) -> str:
        """Tworzy nazwę katalogu nagrania na podstawie pliku wideo."""
```

### 1.2 Implementacja metod FileStructureManager
- `get_structure()` - zwraca strukturę katalogów dla pliku wideo
- `create_structure()` - tworzy nową strukturę katalogów
- `get_extracted_dir()` - zwraca katalog extracted/
- `get_metadata_file()` - zwraca ścieżkę do metadata.json
- `create_recording_directory_name()` - tworzy nazwę katalogu

### 1.3 Testy dla FileStructureManager
```python
class TestFileStructureManager:
    def test_get_structure()
    def test_create_structure()
    def test_get_extracted_dir()
    def test_get_metadata_file()
    def test_create_recording_directory_name()
    def test_structure_validation()
```

## Faza 2: Refaktoring obs_script.py

### 2.1 Zastąpienie logiki reorganizacji
```python
# Stary kod:
def reorganize_files_after_recording(recording_path, metadata_path):
    # Duplikacja logiki tworzenia katalogów
    
# Nowy kod:
def reorganize_files_after_recording(recording_path, metadata_path):
    structure = FileStructureManager.create_structure(Path(recording_path))
    # Użycie structure.recording_dir, structure.extracted_dir, etc.
```

### 2.2 Aktualizacja find_latest_recording_file()
- Użycie `FileStructureManager` do tworzenia nazw katalogów
- Eliminacja duplikacji logiki nazewnictwa

### 2.3 Testy aktualizacji obs_script.py
- Test integracji z FileStructureManager
- Test zachowania kompatybilności

## Faza 3: Refaktoring extract.py

### 3.1 Zastąpienie find_metadata_file()
```python
# Stary kod:
def find_metadata_file(video_path: Path) -> Optional[Path]:
    # Duplikacja logiki rozpoznawania struktury
    
# Nowy kod:
def find_metadata_file(video_path: Path) -> Path:
    return FileStructureManager.get_metadata_file(video_path)
```

### 3.2 Aktualizacja main()
```python
# Stary kod:
if output_dir:
    output_dir_path = Path(output_dir)
else:
    # Duplikacja logiki wyboru katalogu
    
# Nowy kod:
if output_dir:
    output_dir_path = Path(output_dir)
else:
    output_dir_path = FileStructureManager.get_extracted_dir(video_path)
```

### 3.3 Testy aktualizacji extract.py
- Test integracji z FileStructureManager
- Test zachowania kompatybilności

## Faza 4: Refaktoring extractor.py

### 4.1 Zastąpienie logiki wyboru katalogu wyjściowego
```python
# Stary kod:
# Check if we're in new file structure (metadata.json in same directory)
metadata_json_path = video_path.parent / "metadata.json"
if metadata_json_path.exists():
    # New structure: use extracted/ subdirectory
    output_dir_path = video_path.parent / "extracted"
else:
    # Old structure: use {video_name}_extracted/
    output_dir_path = video_path.parent / f"{video_path.stem}_extracted"

# Nowy kod:
output_dir_path = FileStructureManager.get_extracted_dir(video_path)
```

### 4.2 Aktualizacja testów extractor.py
- Zastąpienie testów struktury katalogów przez testy FileStructureManager
- Uproszczenie testów extract_sources()

## Faza 5: Refaktoring advanced_scene_switcher_extractor.py

### 5.1 Uproszczenie find_latest_recording()
```python
# Stary kod:
# Duplikacja logiki rozpoznawania struktury
for video_file in video_files:
    metadata_json_path = video_file.parent / "metadata.json"
    if metadata_json_path.exists():
        # Nowa struktura
    else:
        # Stara struktura
        
# Nowy kod:
for video_file in video_files:
    structure = FileStructureManager.get_structure(video_file)
    # Zawsze nowa struktura - uproszczenie logiki
```

### 5.2 Aktualizacja testów advanced_scene_switcher_extractor.py
- Test integracji z FileStructureManager
- Usunięcie testów legacy struktury

## Faza 6: Cleanup i optymalizacja

### 6.1 Usunięcie duplikacji kodu
- Usunięcie starych funkcji struktury katalogów
- Usunięcie wszystkich testów legacy struktury

### 6.2 Aktualizacja dokumentacji
- Aktualizacja docstringów
- Aktualizacja komentarzy w kodzie

### 6.3 Optymalizacja wydajności
- Optymalizacja operacji na plikach
- Walidacja struktury katalogów

## Harmonogram implementacji

### Tydzień 1: Stworzenie FileStructureManager
- [x] Analiza istniejącego kodu
- [x] Specyfikacja i plan
- [ ] Implementacja RecordingStructure
- [ ] Implementacja FileStructureManager
- [ ] Testy FileStructureManager

### Tydzień 2: Refaktoring modułów
- [ ] Refaktoring obs_script.py
- [ ] Refaktoring extract.py
- [ ] Refaktoring extractor.py
- [ ] Testy integracyjne

### Tydzień 3: Finalizacja
- [ ] Refaktoring advanced_scene_switcher_extractor.py
- [ ] Cleanup i usunięcie duplikacji
- [ ] Testy regresji
- [ ] Dokumentacja

## Pliki do modyfikacji

1. **src/core/file_structure.py** (nowy)
   - RecordingStructure dataclass
   - FileStructureManager class
   - Testy file_structure.py

2. **src/obs_integration/obs_script.py**
   - Refaktoring reorganize_files_after_recording()
   - Użycie FileStructureManager

3. **src/cli/extract.py**
   - Refaktoring find_metadata_file()
   - Użycie FileStructureManager.get_extracted_dir()

4. **src/core/extractor.py**
   - Refaktoring logiki wyboru katalogu wyjściowego
   - Użycie FileStructureManager.get_extracted_dir()

5. **src/obs_integration/advanced_scene_switcher_extractor.py**
   - Refaktoring find_latest_recording()
   - Użycie FileStructureManager.get_structure()

6. **tests/** (aktualizacja testów)
   - Nowe testy dla FileStructureManager
   - Aktualizacja istniejących testów

## Metryki sukcesu

### Przed refaktoringiem
- Duplikacja logiki w 4 modułach
- ~150 linii duplikowanego kodu
- Mieszanie logiki legacy i nowej struktury

### Po refaktoringu
- Centralna logika w 1 module
- Eliminacja duplikacji kodu
- Tylko nowa struktura katalogów
- Uproszczenie kodu

## Kryteria sukcesu

1. ✅ Cała logika struktury katalogów w FileStructureManager
2. ✅ Eliminacja duplikacji kodu (>90%)
3. ✅ Obsługa tylko nowej struktury katalogów
4. ✅ Wszystkie testy przechodzą (100%)
5. ✅ Kod jest czytelniejszy i łatwiejszy w utrzymaniu
6. ✅ Uproszczenie kodu przez eliminację legacy support
7. ✅ Brak regresji funkcjonalności