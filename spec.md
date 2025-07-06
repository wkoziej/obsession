# Specyfikacja: Centralizacja logiki struktury katalogów

## Cel
Centralizacja rozproszonej logiki struktury katalogów w jednym module, eliminując duplikację kodu i ułatwiając zarządzanie różnymi strukturami plików nagrań.

## Problem
Obecnie logika struktury katalogów jest rozproszona w wielu miejscach:
- `obs_script.py` - tworzy strukturę `nagranie_YYYY-MM-DD_HH-MM-SS/`
- `extract.py` - rozpoznaje strukturę przez obecność `metadata.json`
- `advanced_scene_switcher_extractor.py` - szuka plików w różnych strukturach
- `extractor.py` - wybiera katalog wyjściowy na podstawie struktury

## Rozwiązanie: FileStructureManager

### Nowy moduł `src/core/file_structure.py`

#### Klasa RecordingStructure
```python
@dataclass
class RecordingStructure:
    """Reprezentuje strukturę katalogów nagrania."""
    recording_dir: Path          # Katalog główny nagrania
    video_file: Path            # Plik wideo nagrania
    metadata_file: Path         # Plik metadanych (zawsze metadata.json)
    extracted_dir: Path         # Katalog extracted/
```

#### Klasa FileStructureManager
```python
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

## Struktura katalogów

### Jedyna obsługiwana struktura
```
/ścieżka/do/nagrań/
├── nagranie_2025-01-06_15-30-00/
│   ├── nagranie_2025-01-06_15-30-00.mkv
│   ├── metadata.json
│   └── extracted/
│       ├── source1.mp4
│       └── source2.m4a
```

## Refaktoring istniejących modułów

### obs_script.py
- Użycie `FileStructureManager.create_structure()`
- Eliminacja duplikacji logiki tworzenia katalogów

### extract.py
- Zastąpienie `find_metadata_file()` przez `FileStructureManager.get_metadata_file()`
- Użycie `FileStructureManager.get_extracted_dir()`

### extractor.py
- Zastąpienie logiki wyboru katalogu wyjściowego
- Użycie `FileStructureManager.get_extracted_dir()`

### advanced_scene_switcher_extractor.py
- Uproszczenie logiki wyszukiwania plików
- Użycie `FileStructureManager.get_structure()`

## Korzyści

### Techniczne
- **DRY**: Eliminacja duplikacji kodu
- **Single Responsibility**: Jedna klasa odpowiedzialna za strukturę
- **Łatwość testowania**: Centralne testy logiki struktury
- **Rozszerzalność**: Łatwe dodanie nowych struktur

### Utrzymaniowe
- **Łatwość zmian**: Modyfikacje w jednym miejscu
- **Czytelność**: Jasne API do pracy ze strukturą
- **Debugowanie**: Centralne logowanie operacji

## Wymagania techniczne

### Zależności
- Python `pathlib` dla manipulacji ścieżkami
- `dataclasses` dla RecordingStructure
- `typing` dla type hints

### Obsługa błędów
- Graceful handling błędów przy tworzeniu katalogów
- Walidacja struktury katalogów
- Logowanie operacji

### Testy
- Testy jednostkowe dla każdej metody
- Testy integracyjne z istniejącymi modułami
- Testy tworzenia i walidacji struktury

## Kryteria sukcesu

1. ✅ Cała logika struktury katalogów w jednym module
2. ✅ Eliminacja duplikacji kodu
3. ✅ Obsługa tylko nowej struktury katalogów
4. ✅ Wszystkie testy przechodzą
5. ✅ Kod jest czytelniejszy i łatwiejszy w utrzymaniu
6. ✅ Uproszczenie kodu przez eliminację legacy support