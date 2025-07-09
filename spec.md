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

### 3.3 Ograniczenia PoC
- Maksymalnie 4 źródła PiP
- Tylko podstawowe efekty (pozycja, skala, przezroczystość)
- Brak złożonych przejść czy efektów cząsteczkowych

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

### UC2: Podcast z reakcjami
- Wejście: 2 źródła (host + gość) + audio
- Proces: detekcja mowy → podświetlanie aktywnego mówcy
- Wyjście: automatyczne focus na mówiącego

### UC3: Gameplay z komentarzem
- Wejście: gameplay + kamera gracza + audio
- Proces: analiza energii → PiP reaguje na emocje
- Wyjście: dynamiczne pojawianie się gracza w momentach akcji

## 6. Interfejs użytkownika

### 6.1 CLI
```bash
# Analiza audio
python -m cli.analyze_audio recording_20250105_143022/main_audio.m4a

# Tworzenie projektu z animacjami
python -m cli.blend_setup recording_20250105_143022 --with-audio-animation

# Wybór trybu animacji
python -m cli.blend_setup recording_20250105_143022 --animation-mode beat-switch
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