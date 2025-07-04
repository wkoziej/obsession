# Canvas Recording MVP - OBS Multi-Source

## 1. Cel Projektu (MVP)

### Co chcemy osiągnąć
1. **Ręcznie** układamy źródła w OBS na dużym canvas (jak mozaika)
2. Plugin zapisuje metadata o pozycjach źródeł
3. Po nagraniu skrypt automatycznie wycina poszczególne źródła
4. Wynik: folder z osobnymi plikami video + audio

### Uproszczony workflow
```
Układam kamery → Start Recording → Stop → Auto Extract → Gotowe pliki
     (ręcznie)        (OBS)               (skrypt)        (output)
```

## 2. Open Source NLE i Standardy

### Darmowe/Open Source NLE

1. **DaVinci Resolve** (darmowa wersja)
   - Profesjonalne narzędzie, ograniczenia tylko w 4K+ export
   - Wspiera import XML/EDL
   - Windows/Mac/Linux

2. **Kdenlive** (Open Source)
   - Prawdziwie open source
   - Import/export MLT XML
   - Dobry dla Linux

3. **OpenShot** (Open Source)
   - Prostszy, dobry na początek
   - Python-based
   - Cross-platform

4. **Shotcut** (Open Source)
   - Bazuje na MLT framework
   - Wspiera wiele formatów projektu
   - Aktywnie rozwijany

### Standardy metadanych (zamiast NLE)

**Najlepsze rozwiązanie: JSON + FFmpeg concat**

```json
{
  "project": {
    "name": "Recording_2024_01_15",
    "canvas_size": [5760, 3240],
    "fps": 30,
    "duration": 3600.5,
    "sources": {
      "Camera_1": {
        "position": {"x": 0, "y": 0},
        "size": {"width": 1920, "height": 1080},
        "file": "Camera_1.mp4"
      },
      "Camera_2": {
        "position": {"x": 1920, "y": 0},
        "size": {"width": 1920, "height": 1080},
        "file": "Camera_2.mp4"
      }
    },
    "audio_tracks": [
      {"track": 1, "name": "Mic_1", "file": "audio_track_1.wav"},
      {"track": 2, "name": "Mic_2", "file": "audio_track_2.wav"}
    ]
  }
}
```

Ten JSON może być użyty przez:
- Własne skrypty do składania video
- Import do różnych NLE
- Web-based video editors
- FFmpeg do automatycznego złożenia

## 3. Implementacja MVP

### Opcje implementacji (od najprostszej)

#### Opcja 1: Python Script w OBS (REKOMENDOWANE dla MVP)
```python
# canvas_recorder.py - skrypt OBS Python
import obspython as obs
import json
import os
from datetime import datetime

# Globalne zmienne
recording_active = False
metadata_saved = False

def on_event(event):
    global recording_active, metadata_saved
    
    if event == obs.OBS_FRONTEND_EVENT_RECORDING_STARTED:
        recording_active = True
        metadata_saved = False
        print("Recording started - will save metadata on stop")
        
    elif event == obs.OBS_FRONTEND_EVENT_RECORDING_STOPPED:
        if recording_active and not metadata_saved:
            save_metadata()
            trigger_extraction()
            metadata_saved = True
            recording_active = False

def save_metadata():
    """Zapisz pozycje wszystkich źródeł do JSON"""
    # Pobierz aktualną scenę
    scene_source = obs.obs_frontend_get_current_scene()
    scene = obs.obs_scene_from_source(scene_source)
    
    metadata = {
        "canvas_size": [
            obs.obs_get_video_info().base_width,
            obs.obs_get_video_info().base_height
        ],
        "fps": obs.obs_get_video_info().fps_num,
        "sources": {}
    }
    
    # Iteruj przez źródła w scenie
    scene_items = obs.obs_scene_enum_items(scene)
    for item in scene_items:
        source = obs.obs_sceneitem_get_source(item)
        name = obs.obs_source_get_name(source)
        
        # Pobierz pozycję i rozmiar
        pos = obs.vec2()
        obs.obs_sceneitem_get_pos(item, pos)
        
        scale = obs.vec2()
        obs.obs_sceneitem_get_scale(item, scale)
        
        # Zapisz do metadata
        metadata["sources"][name] = {
            "position": {"x": pos.x, "y": pos.y},
            "scale": {"x": scale.x, "y": scale.y}
        }
    
    # Zapisz do pliku
    output_file = get_last_recording_path() + ".json"
    with open(output_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Metadata saved to: {output_file}")
    obs.obs_source_release(scene_source)

def script_load(settings):
    obs.obs_frontend_add_event_callback(on_event)

def script_description():
    return "Canvas Recorder - Saves source positions for extraction"
```

#### Opcja 2: Lua Script (również prosta)
```lua
-- canvas_recorder.lua
obs = obslua

function on_event(event)
    if event == obs.OBS_FRONTEND_EVENT_RECORDING_STOPPED then
        save_metadata()
        trigger_extraction()
    end
end

function script_load(settings)
    obs.obs_frontend_add_event_callback(on_event)
end
```

#### Opcja 3: C++ Plugin (tylko jeśli potrzeba więcej kontroli)
- Wymaga kompilacji OBS
- Więcej możliwości ale znacznie więcej pracy
- Dla MVP: NIEPOTRZEBNE

### Dlaczego Python Script jest najlepszy dla MVP:
1. **Nie wymaga kompilacji** - po prostu wgrywasz plik
2. **Łatwa edycja** - możesz modyfikować na żywo
3. **Pełny dostęp do OBS API**
4. **Może uruchamiać zewnętrzne procesy**

## 4. Struktura MVP

### Minimalna struktura projektu
```
obs-canvas-recorder-mvp/
├── obs-scripts/
│   └── canvas_recorder.py      # Script OBS do zapisywania metadata
│
├── extractor/
│   ├── extract.py              # Główny skrypt ekstrakcji
│   └── requirements.txt        # Tylko: ffmpeg-python
│
├── watch_folder.py             # Opcjonalny watcher
│
└── README.md
```

### extract.py - Skrypt ekstrakcji
```python
#!/usr/bin/env python3
import json
import sys
import subprocess
from pathlib import Path

def extract_sources(video_file, metadata_file):
    """Ekstraktuj źródła na podstawie metadata"""
    
    # Wczytaj metadata
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    # Utwórz folder output
    output_dir = Path(video_file).stem + "_extracted"
    Path(output_dir).mkdir(exist_ok=True)
    
    # Ekstraktuj każde źródło
    for source_name, info in metadata['sources'].items():
        output_file = f"{output_dir}/{source_name}.mp4"
        
        # Buduj komendę FFmpeg
        cmd = [
            'ffmpeg',
            '-i', video_file,
            '-filter:v', f"crop={info['width']}:{info['height']}:{info['position']['x']}:{info['position']['y']}",
            '-c:v', 'libx264',
            '-crf', '18',
            '-preset', 'fast',
            output_file
        ]
        
        print(f"Extracting {source_name}...")
        subprocess.run(cmd)
    
    # Ekstraktuj audio
    # ... (podobnie jak wyżej)
    
    print(f"Done! Files in: {output_dir}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: extract.py <video_file> <metadata_file>")
        sys.exit(1)
    
    extract_sources(sys.argv[1], sys.argv[2])
```

## 5. Konfiguracja w OBS (Profile)

### Używamy OBS Profile zamiast własnej konfiguracji

**Profile OBS zawiera wszystko czego potrzebujemy:**
- Rozdzielczość canvas
- Ustawienia encodera
- Ścieżki zapisu

### Setup profilu dla Canvas Recording:

1. **Utwórz nowy profil OBS:**
   - Profile → New → "Canvas Recording 6K"

2. **Ustawienia profilu:**
   ```
   Video:
   - Base Resolution: 5760x3240
   - Output Resolution: 5760x3240
   - FPS: 30
   
   Output:
   - Recording Path: D:\CanvasRecordings
   - Recording Format: mkv
   - Encoder: NVENC H.264
   - Rate Control: CQP
   - CQ Level: 18
   ```

3. **Scena z układem:**
   - Ręcznie układasz źródła jak mozaikę
   - Zapisujesz scenę jako "Canvas Layout"

### Workflow w praktyce:

1. **Przygotowanie (jednorazowo):**
   ```bash
   # Zainstaluj skrypt w OBS
   Tools → Scripts → Add → canvas_recorder.py
   ```

2. **Nagrywanie:**
   - Wybierz profil "Canvas Recording 6K"
   - Ułóż źródła na scenie
   - Start Recording
   - Stop Recording → automatycznie zapisze metadata

3. **Po nagraniu:**
   ```bash
   # Ręcznie lub przez watcher
   python extract.py recording.mkv recording.mkv.json
   ```

## 6. Przykład kompletnego workflow

### 1. Setup źródeł w OBS:
```
Scene: Canvas Layout
├── Camera 1 [Position: 0,0]
├── Camera 2 [Position: 1920,0]
├── Camera 3 [Position: 3840,0]
└── Desktop [Position: 0,1080, Size: 3840x2160]
```

### 2. Po nagraniu powstaje:
```
recording_2024_01_15_143022.mkv
recording_2024_01_15_143022.mkv.json
```

### 3. JSON z metadata:
```json
{
  "canvas_size": [5760, 3240],
  "fps": 30,
  "sources": {
    "Camera 1": {
      "position": {"x": 0, "y": 0},
      "size": {"width": 1920, "height": 1080}
    },
    "Camera 2": {
      "position": {"x": 1920, "y": 0},
      "size": {"width": 1920, "height": 1080}
    },
    "Desktop": {
      "position": {"x": 0, "y": 1080},
      "size": {"width": 3840, "height": 2160}
    }
  }
}
```

### 4. Po ekstrakcji:
```
recording_2024_01_15_143022_extracted/
├── Camera_1.mp4
├── Camera_2.mp4
├── Desktop.mp4
├── audio_track_1.wav
└── project_metadata.json
```

## 7. Instalacja MVP (5 minut)

```bash
# 1. Pobierz skrypty
git clone https://github.com/yourusername/obs-canvas-recorder-mvp
cd obs-canvas-recorder-mvp

# 2. Zainstaluj Python dependencies
pip install ffmpeg-python

# 3. Dodaj skrypt do OBS
# OBS → Tools → Scripts → Add → wybierz canvas_recorder.py

# 4. Opcjonalnie: uruchom watcher
python watch_folder.py D:\CanvasRecordings

# Gotowe!
```

## 8. Rozwój po MVP

**Faza 1 (MVP) ✓**
- Script Python w OBS
- Metadata JSON
- Ekstrakcja FFmpeg

**Faza 2 (Automatyzacja)**
- Auto-watcher service
- GUI do podglądu
- Batch processing

**Faza 3 (Integracja)**
- Export do Kdenlive/OpenShot
- Web preview
- Cloud sync

**Faza 4 (Advanced)**
- AI scene detection
- Smart cropping
- Real-time preview