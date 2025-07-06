# Specyfikacja: Generator Projektów Blender VSE

## 📋 Przegląd

System automatycznego generowania projektów Blender VSE (Video Sequence Editor) z wyekstraktowanych nagrań OBS Canvas Recorder. Narzędzie tworzy gotowy do renderingu projekt Blender z uporządkowanymi ścieżkami wideo i audio.

## 🎯 Cel

Automatyczne przygotowanie pliku `.blend` zawierającego:
- Wyekstraktowane pliki wideo na osobnych ścieżkach VSE
- Główną ścieżkę audio z oryginalnego nagrania canvas na ścieżce VSE
- Skonfigurowane parametry renderingu (720p, MP4)
- Ustawioną ścieżkę wyjściową renderingu

## 📁 Struktura Wejściowa

```
nazwa_nagrania/
├── nazwa_nagrania.mkv          # Oryginalne nagranie canvas
├── metadata.json               # Metadane sceny
└── extracted/                  # Wyekstraktowane pliki
    ├── Camera1.mp4             # Video z Camera1
    ├── Main audio.m4a          # Audio wekstrachowane z Canvas
    ├── ScreenCapture.mp4       # Video z ScreenCapture
    └── ...
```

## 📁 Struktura Wyjściowa

```
nazwa_nagrania/
├── nazwa_nagrania.mkv          # Oryginalne nagranie
├── metadata.json               # Metadane
├── extracted/                  # Wyekstraktowane pliki
└── blender/                    # ← Nowy katalog
    ├── nazwa_nagrania.blend    # Projekt Blender
    └── render/                 # Katalog docelowy renderingu
```

## 🎬 Konfiguracja VSE

### Ścieżki Video (Channels)
- **Channel 1**: Pierwszy plik wideo (.mp4)
- **Channel 2**: Drugi plik wideo (.mp4)
- **Channel N**: N-ty plik wideo (.mp4)

### Ścieżki Audio (Channels)
- **Channel 1**: Główna ścieżka audio z canvas (`audio_main.m4a`)

### Timing
- **Start Frame**: Wszystkie ścieżki zaczynają się od frame 1
- **Długość**: Bazowana na długości głównej ścieżki audio
- **FPS**: Z metadata.json lub domyślnie 30fps

## ⚙️ Parametry Renderingu

### Rozdzielczość
- **Preset**: HD 720p (1280x720)
- **Aspect Ratio**: 16:9

### Format Wyjściowy
- **Container**: MP4
- **Video Codec**: H.264
- **Audio Codec**: AAC
- **Quality**: High (CRF 18)

### Ścieżka Wyjściowa
- **Katalog**: `{nazwa_nagrania}/blender/render/`
- **Nazwa pliku**: `{nazwa_nagrania}_final.mp4`

## 🔧 Interface CLI

### Komenda
```bash
python -m cli.blend_setup <katalog_nagrania>
```

### Przykład użycia
```bash
# Podstawowe użycie
python -m cli.blend_setup ./recording_20250105_143022

# Z verbose output
python -m cli.blend_setup ./recording_20250105_143022 --verbose

# Pomoc
python -m cli.blend_setup --help

# Ścieżka do głóœnego audio
python -m cli.blend_setup --main-audio main_audio.m4a

```

### Argumenty
- `recording_dir`: Ścieżka do katalogu nagrania (wymagane)
- `--verbose, -v`: Szczegółowe logowanie (opcjonalne)
- `--force, -f`: Nadpisz istniejący plik .blend (opcjonalne)

## 📊 Wymagania Funkcjonalne

### RF-001: Walidacja Struktury
- System musi sprawdzić czy katalog zawiera wymaganą strukturę
- Musi istnieć plik `metadata.json` i katalog `extracted/`
- Musi istnieć co najmniej jeden plik wideo lub audio w `extracted/`

### RF-002: Główne Audio z Canvas
- System zna główną ścieżkę audio z oryginalnego nagrania - jeżeli plików audio w katalogu extracted jest więcej niż jeden - zgłasza błąd i wymaga podania parametru z nazwą pliku audio 

### RF-003: Tworzenie Projektu Blender
- System musi utworzyć nowy projekt Blender z czystą sceną
- Musi skonfigurować VSE z odpowiednimi ścieżkami
- Musi ustawić parametry renderingu zgodnie ze specyfikacją

### RF-004: Organizacja Ścieżek VSE
- Pliki wideo na osobnych kanałach (1, 2, 3...)
- Główna ścieżka audio na kanale 1 (audio)
- Wszystkie ścieżki synchronizowane od frame 1

### RF-005: Konfiguracja Renderingu
- Rozdzielczość: 1280x720 (HD)
- Format: MP4 (H.264 + AAC)
- Ścieżka wyjściowa: `{katalog}/blender/render/`
- Nazwa pliku: `{nazwa_nagrania}_final.mp4`

## 🚨 Wymagania Niefunkcjonalne


### RNF-002: Kompatybilność
- Blender 4.0+ (Python API)
- FFmpeg 4.4+ (ekstrakcja audio)
- Python 3.9+ (zgodność z istniejącym systemem)

### RNF-003: Niezawodność
- Walidacja wszystkich plików wejściowych
- Obsługa błędów FFmpeg i Blender API
- Rollback przy niepowodzeniu

### RNF-004: Użyteczność
- Jasne komunikaty o błędach
- Progress bar dla długich operacji
- Verbose mode dla debugowania

## 🔍 Przypadki Użycia

### UC-001: Podstawowe Tworzenie Projektu
1. Użytkownik uruchamia `python -m cli.blend_setup ./recording_dir`
2. System waliduje strukturę katalogu
3. System tworzy projekt Blender VSE
4. System konfiguruje ścieżki i parametry renderingu
5. System zapisuje plik `.blend`

### UC-002: Nadpisanie Istniejącego Projektu
1. Użytkownik uruchamia z flagą `--force`
2. System pyta o potwierdzenie nadpisania
3. System usuwa stary plik `.blend`
4. System tworzy nowy projekt

### UC-003: Obsługa Błędów
1. System wykrywa nieprawidłową strukturę
2. System wyświetla szczegółowy komunikat błędu
3. System kończy działanie z kodem błędu

## 📋 Kryteria Akceptacji

### AC-001: Struktura Wyjściowa
- [x] Utworzony katalog `blender/`
- [x] Plik `nazwa_nagrania.blend` istnieje
- [x] Katalog `render/` istnieje

### AC-002: Konfiguracja VSE
- [x] Wszystkie pliki wideo na osobnych kanałach
- [x] Główna ścieżka audio na kanale 1
- [x] Wszystkie ścieżki zaczynają się od frame 1

### AC-003: Parametry Renderingu
- [x] Rozdzielczość: 1280x720
- [x] Format: MP4
- [x] Ścieżka wyjściowa: `{katalog}/blender/render/`
- [x] Nazwa pliku: `{nazwa_nagrania}_final.mp4`

### AC-004: Interface CLI
- [x] Komenda `python -m cli.blend_setup` działa
- [x] Argumenty są poprawnie parsowane
- [x] Pomoc (`--help`) jest dostępna
- [x] Verbose mode (`--verbose`) działa

## 🧪 Strategia Testowa

### Testy Jednostkowe
- Walidacja struktury katalogów
- Parsowanie argumentów CLI
- Konfiguracja parametrów Blender

### Testy Integracyjne
- Ekstrakcja audio przez FFmpeg
- Tworzenie projektu Blender
- Zapis pliku `.blend`

### Testy E2E
- Pełny workflow od katalogu do projektu
- Różne scenariusze plików wejściowych
- Obsługa błędów i edge cases

## 📚 Zależności

### Nowe Zależności
- `bpy` (Blender Python API) - do tworzenia projektów
- Opcjonalnie: `bpy` jako moduł lub wywołanie zewnętrzne

### Istniejące Zależności
- `ffmpeg` - ekstrakcja audio
- `pathlib` - operacje na plikach
- `argparse` - parsowanie argumentów
- `json` - czytanie metadanych

## 🔄 Integracja z Istniejącym Systemem

### Współdzielone Komponenty
- `FileStructureManager` - zarządzanie strukturą plików
- `metadata.py` - czytanie metadanych
- `cli/` - struktura CLI

### Nowe Komponenty
- `cli/blend_setup.py` - główny interface CLI
- `core/blender_project.py` - logika tworzenia projektów
