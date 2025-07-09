# Specyfikacja PoC: Animacje w Blender VSE oparte na analizie audio

## 1. Cel PoC

Zademonstrowanie możliwości automatycznego tworzenia animacji PiP (Picture-in-Picture) w Blender VSE, które są zsynchronizowane z muzyką na podstawie analizy audio.

## 2. Zakres funkcjonalny

### 2.1 Analiza audio
- Wykrywanie bitów i tempa (BPM)
- Identyfikacja granic sekcji muzycznych
- Analiza energii w pasmach częstotliwości (bass, mid, high)
- Detekcja onsetów (początków dźwięków)
- Generowanie eventów animacji na podstawie analizy

### 2.2 Integracja z Blender VSE
- Rozszerzenie istniejącego skryptu `blender_vse_script.py`
- Dodanie animacji PiP dla źródeł wideo
- Synchronizacja przełączeń/efektów z eventami audio

### 2.3 Tryby animacji PiP
1. **Beat Switch Mode** - przełączanie aktywnego PiP co N bitów
2. **Energy Pulse Mode** - pulsowanie rozmiaru PiP w rytm basu
3. **Section Transition Mode** - płynne przejścia na granicach sekcji
4. **Multi-PiP Mode** - wszystkie PiP widoczne, różne efekty dla każdego

## 3. Wymagania techniczne

### 3.1 Zależności
- Python 3.9+ (kompatybilny z OBS)
- librosa (analiza audio)
- numpy, scipy (obliczenia)
- Blender 3.0+ (VSE z Python API)

### 3.2 Format danych
- Wejście: plik audio (z extracted/ lub main recording)
- Analiza: JSON z eventami i danymi czasowymi
- Wyjście: projekt .blend z animacjami

### 3.3 Blender VSE API - kluczowe komponenty
- `bpy.context.scene.sequence_editor` - główny interfejs VSE
- `sequencer.sequences` - lista wszystkich strip'ów
- `strip.blend_alpha` - kontrola przezroczystości (0.0-1.0)
- `strip.transform.offset_x/y` - pozycja PiP w pikselach
- `strip.transform.scale_x/y` - skala PiP (1.0 = 100%)
- `strip.keyframe_insert(data_path, frame)` - dodawanie keyframe'ów
- `strip.frame_start/frame_final_end` - pozycja na timeline

### 3.4 Ograniczenia PoC
- Maksymalnie 4 źródła PiP
- Tylko podstawowe efekty (pozycja, skala, przezroczystość)
- Brak złożonych przejść czy efektów cząsteczkowych
- Animacje oparte na keyframe'ach z linear interpolation

## 4. Kryteria sukcesu

1. **Funkcjonalność**
   - ✓ Analiza audio generuje prawidłowe eventy
   - ✓ Blender tworzy animacje na podstawie eventów
   - ✓ Animacje są zsynchronizowane z muzyką

2. **Widoczność dla operatora**
   - ✓ Operator widzi wszystkie źródła w Blenderze
   - ✓ Może podglądać animacje w czasie rzeczywistym
   - ✓ Może modyfikować parametry animacji

3. **Integracja**
   - ✓ Działa z istniejącą strukturą projektu
   - ✓ Nie wymaga zmian w OBS script
   - ✓ Wykorzystuje istniejące extracted sources

## 5. Przypadki użycia

### UC1: Automatyczna animacja koncertu
- Wejście: nagranie z 3 kamer + główny audio
- Proces: analiza audio → generowanie eventów → animacje PiP
- Wyjście: dynamiczny montaż z przełączaniem kamer w rytm


## 6. Interfejs użytkownika

### 6.1 CLI
```bash
# Analiza audio
python -m cli.analyze_audio recording_20250105_143022/extracted/main_audio.m4a ./analysis

# Tworzenie projektu z animacjami
python -m cli.blend_setup recording_20250105_143022 --analyze-audio --animation-mode beat-switch

# Wybór trybu animacji i beat division
python -m cli.blend_setup recording_20250105_143022 --animation-mode energy-pulse --beat-division 4
```

### 6.2 Parametry w Blenderze
- Slider: Beat Division (co ile bitów przełączać)
- Slider: Energy Threshold (próg reakcji na bas)
- Checkbox: Enable/Disable dla każdego trybu
- Preview button: podgląd 10s animacji

## 7. Przykładowe eventy animacji

```json
{
  "animation_events": {
    "beats": [0.5, 1.0, 1.5, 2.0],  // co 8 bitów
    "sections": [0.0, 32.5, 64.2],   // granice części
    "energy_peaks": [2.3, 8.7, 15.2], // szczyty basu
    "onsets": [0.1, 2.1, 4.2]        // filtrowane onsety
  }
}
```

## 8. Metryki wydajności

- Czas analizy: < 10s dla 5-minutowego audio
- Generowanie keyframes: < 5s
- Render preview: czasu rzeczywistego
- Pamięć: < 500MB dla całego procesu