# Audio Animation PoC - TODO Tracker

## Status: 🎉 Phase 3B.1: Energy Pulse Animation - COMPLETE SUCCESS! 🎆

Last updated: 2025-07-09

## Progress Overview

- [x] Specyfikacja (spec.md)
- [x] Plan implementacji (plan.md)  
- [x] TODO tracker (this file)
- [x] **Phase 1: Audio Analysis (TDD)** ✅
- [x] **Phase 2: System Integration** ✅ COMPLETE 
- [x] **Phase 3A: MVP Beat Switch Animation** ✅ END-TO-END SUCCESS
- [x] **Phase 3B.1: Energy Pulse Animation** ✅ COMPLETE SUCCESS
- [ ] Phase 3B.2: Pozostałe tryby animacji (section-transition, multi-pip)
- [ ] Phase 4: Demo & Documentation

---

## Phase 1: Audio Analysis Foundation

### 1.1 Test Setup ✅
- [x] Create tests/test_audio_analyzer.py
- [x] Prepare audio fixtures in tests/fixtures/audio/
- [x] Add pytest markers for audio tests
- [x] Setup conftest.py for audio test utilities (używamy istniejącego)

### 1.2 Unit Tests ✅
- [x] Test: AudioAnalyzer initialization
- [x] Test: Lazy loading of librosa
- [x] Test: Lazy loading of scipy
- [x] Test: Handle missing dependencies gracefully
- [x] Test: analyze_for_animation() with mock data
- [x] Test: _detect_boundaries() logic (via integration)
- [x] Test: _filter_onsets() with various intervals
- [x] Test: _analyze_frequency_bands() output format (via integration)
- [x] Test: _find_bass_peaks() threshold logic (via integration)
- [x] Test: save_analysis() JSON structure

### 1.3 Implementation ✅
- [x] AudioAnalyzer class already exists (kept existing implementation)
- [x] Lazy loading for dependencies implemented
- [x] analyze_for_animation() implemented
- [x] Helper methods implemented
- [x] Logging added
- [x] Error handling and validation in place

### 1.4 Integration Tests ✅
- [x] Test with real audio file (4 różne pliki testowe)
- [x] Test with various audio formats (WAV)
- [x] Test error cases (skip if file missing)
- [x] Performance test (10s audio analyzed < 3s)
- [x] Added test_audio_analyzer_integration.py
- [x] Created demo_audio_analysis.py script

---

## Phase 2: System Integration

### 2.1 FileStructure Integration ✅
- [x] Add analysis/ directory to structure
- [x] Test FileStructureManager with analysis data  
- [x] Added ANALYSIS_DIRNAME = "analysis"
- [x] Implemented ensure_analysis_dir(), get_analysis_file_path()
- [x] Added save_audio_analysis(), find_audio_analysis(), load_audio_analysis()
- [x] 10 new tests passing for FileStructure audio integration

### 2.2 BlenderProjectManager Updates ✅
- [x] Test new environment variables
- [x] Add BLENDER_VSE_AUDIO_ANALYSIS path
- [x] Add BLENDER_VSE_ANIMATION_MODE parameter
- [x] Add BLENDER_VSE_BEAT_DIVISION parameter
- [x] Extended create_vse_project() with animation_mode, beat_division params
- [x] Added _prepare_environment_variables_with_analysis()
- [x] Added _validate_animation_mode(), _validate_beat_division()
- [x] 8 new tests passing for BlenderProjectManager audio integration

### 2.3 CLI Commands ✅
- [x] Create cli/analyze_audio.py ✅
- [x] Add --analyze-audio flag to blend_setup ✅
- [x] Test CLI integration end-to-end ✅
- [x] CLI with analyze_audio_command() and main() functions
- [x] Support for --beat-division and --min-onset-interval flags
- [x] 10 tests passing for CLI analyze_audio
- [x] Extended blend_setup with --analyze-audio, --animation-mode, --beat-division
- [x] Added validate_animation_parameters(), find_main_audio_file(), perform_audio_analysis()
- [x] 6 new tests passing for blend_setup audio integration

---

## Phase 3A: MVP Beat Switch Animation 🎯

### 3A.1 Fundamenty MVP (TDD) - Focus na core risk ✅ COMPLETE
- [x] Mock Blender API (bpy) for testing - focus na VSE sequence_editor
- [x] Test: load_animation_data() tylko dla beat events (nie wszystkie)
- [x] Test: calculate_pip_positions() - prosty hardcoded 2x2 grid
- [x] Test: animate_beat_switch() - przełączanie blend_alpha na beat timing
- [x] 16 new tests passing for animation functions

### 3A.2 Implementacja MVP - Minimal viable features ✅ COMPLETE
- [x] load_animation_data() - tylko beat events + basic validation
- [x] calculate_pip_positions() - hardcoded 2x2 grid layout (4 pozycje)
- [x] animate_beat_switch() - blend_alpha keyframes na beat events
- [x] Minimalna integracja z BlenderVSEConfigurator.setup_vse_project()
- [x] Fixed audio analysis file loading path resolution
- [x] Fixed environment variable size limit (file path vs JSON data)

### 3A.3 Weryfikacja MVP - Manual testing critical ✅ END-TO-END SUCCESS
- [x] End-to-end test: utworzenie projektu z --animation-mode beat-switch
- [x] Manual verification w Blenderze: czy keyframes są widoczne w timeline
- [x] Basic demo: 2 video strips przełączające się w rytm beat events
- [x] Problem z FPS parsing rozwiązany (int(float()) fix)
- [x] Dokumentacja beat-switch animation w CLAUDE.md

**🎯 MVP Success Criteria:**
- Blender tworzy projekt z keyframes na timeline ✅
- Video strips mają animowane blend_alpha właściwości ✅
- Timing jest synchronizowany z beat events z analizy audio ✅
- Można otworzyć projekt w Blenderze i zobaczyć animacje ✅

---

## Phase 3B: Rozszerzenie (Po weryfikacji MVP)

### 3B.1 Energy Pulse Animation - COMPLETE SUCCESS ✅
- [x] Test: animate_energy_pulse() - skalowanie transform.scale_x/y na energy_peaks
- [x] Implementacja: energy_pulse mode z energy_peaks events z analizy audio
- [x] Integracja z istniejącym MVP system (extend BlenderVSEConfigurator)
- [x] End-to-end test: --animation-mode energy-pulse
- [x] Manual verification: czy scale animation jest widoczny w Blenderze
- [x] 5 new tests passing for energy-pulse animation
- [x] Expanded _load_animation_data() to support beats + energy_peaks
- [x] Larger blend files (481440 bytes vs 380480 bytes) confirming scale keyframes

### 3B.2 Pozostałe tryby animacji - FUTURE
- [ ] animate_section_transitions() - płynne przejścia na sections
- [ ] animate_multi_pip() - wszystkie PiP widoczne z różnymi efektami
- [ ] Advanced keyframe helpers i easing functions
- [ ] Kombinacja animacji (beat-switch + energy-pulse)

---

## Phase 4: Demo & Documentation

### 4.1 Demo Script
- [ ] Create demo_audio_animation.py
- [ ] Find/create sample recording with music
- [ ] Generate all animation modes
- [ ] Create comparison video

### 4.2 Documentation
- [ ] Update main README
- [ ] Create audio_animation_guide.md
- [ ] Record screencast
- [ ] Create example outputs

---

## Notes & Decisions

### 2025-01-09
- Started with TDD approach as requested
- Created comprehensive spec and plan
- ✅ PHASE 1 COMPLETE:
  - AudioAnalyzer fully implemented and tested
  - 21 tests passing (14 unit + 7 integration)
  - Test audio fixtures generated
  - Demo script showing output format
  - Analysis generates proper animation events:
    * Beat switching events (for PiP)
    * Section boundaries (for transitions)
    * Filtered onsets (for accents)
    * Energy peaks (for pulsing effects)
    * Continuous frequency band data

- ✅ PHASE 2: COMPLETE:
  - FileStructureManager: Added analysis/ directory support (10 tests ✅)
  - BlenderProjectManager: Added audio analysis env vars (8 tests ✅) 
  - CLI analyze_audio.py: Full implementation (10 tests ✅)
  - CLI blend_setup: Added audio integration (6 tests ✅)
  - Total new tests: 34 tests passing
  - Ready for Phase 3: Blender Animations

### 2025-07-09
- ✅ PHASE 3A: MVP BEAT SWITCH ANIMATION - END-TO-END SUCCESS:
  - Phase 3A.1: TDD implementation - 16 animation tests passing
  - Phase 3A.2: Core animation functions implemented (load_animation_data, calculate_pip_positions, animate_beat_switch)
  - Phase 3A.3: End-to-end integration SUCCESS - full CLI workflow working
  - Fixed audio analysis file loading (extracted/ → analysis/ path resolution)
  - Fixed environment variable size limit (1.7MB JSON → file path approach)
  - Successfully created Blender VSE project with beat-switch animation mode
  - Total tests: 250+ passing (21 + 34 + 16 + integration tests)

- ✅ PHASE 3B.1: ENERGY PULSE ANIMATION - COMPLETE SUCCESS:
  - 5 new tests passing for energy-pulse animation (TDD approach)
  - _animate_energy_pulse() implemented with transform.scale_x/y keyframes
  - Integration with BlenderVSEConfigurator - energy-pulse mode working
  - End-to-end CLI success: --animation-mode energy-pulse creates .blend files
  - Expanded _load_animation_data() to support both beats and energy_peaks
  - Larger blend files (481440 vs 380480 bytes) confirming scale animation keyframes
  - Total tests: 255+ passing (21 + 34 + 16 + 5 + integration tests)

### Design Decisions
- Using lazy loading for optional dependencies
- JSON format for data exchange with Blender
- Keeping animations simple for PoC (position, scale, opacity)
- Focus on PiP switching as main demo feature
- Blender VSE API: strip.keyframe_insert() for animation
- Grid 2x2 layout for PiP positioning
- Linear interpolation between keyframes
- Environment variables for Blender script communication

### 🎯 MVP Strategy (Phase 3A)
- Risk-first approach: weryfikacja Blender API integration najpierw
- Beat-switch animation = najważniejsze ryzyko (keyframes + timing)
- Hardcoded 2x2 grid dla szybkości (optymalizacja później)
- Manual testing w Blenderze critical dla weryfikacji
- Sukces MVP → dalsze animacje, failure → pivot/alternatywne podejście

### Technical Debt
- [ ] Consider caching analysis results
- [ ] Optimize for large audio files
- [ ] Add more animation easing options
- [ ] Support for more complex effects
- [ ] OBS Extraction Issue: Metadane w nowych nagraniach mają has_audio=false, has_video=false mimo że źródła są widoczne/słyszalne

### Known Issues
- **OBS Extraction Script**: Nowa wersja skryptu ekstrakcji ma problem z wykrywaniem audio/video capabilities w metadanych.
  - **Problem**: W metadata.json wszystkie źródła mają `has_audio: false, has_video: false`
  - **Impact**: Automatyczna ekstrakcja nie znajduje źródeł do wyekstraktowania
  - **Workaround**: Używać starszych nagrań z poprawnie wykrytymi capabilities lub naprawić OBS script
  - **Recording affected**: `/home/wojtas/Wideo/obs/2025-07-09 21-34-46/` (wszystkie źródła has_audio/video=false)
  - **Working recordings**: `/home/wojtas/Wideo/obs/2025-07-08 19-38-18/` (poprawne capabilities)

---

## Quick Commands

```bash
# Run audio tests only
uv run pytest tests/test_audio_analyzer.py -v

# Run with coverage
uv run pytest tests/test_audio_analyzer.py --cov=src.core.audio_analyzer

# Test audio analysis CLI
uv run python -m cli.analyze_audio audio_file.wav ./output --beat-division 4

# Test specific animation modes (WORKING!)
uv run python -m src.cli.blend_setup "/home/wojtas/Wideo/obs/2025-07-08 19-38-18" --animation-mode beat-switch --beat-division 8 --main-audio "Przechwytywanie wejścia dźwięku (PulseAudio).m4a" --verbose

uv run python -m src.cli.blend_setup "/home/wojtas/Wideo/obs/2025-07-08 19-38-18" --animation-mode energy-pulse --beat-division 8 --main-audio "Przechwytywanie wejścia dźwięku (PulseAudio).m4a" --verbose

# Quick demo
uv run python demo_audio_animation.py
```

## Animation Data Sources 🎵

### Audio Analysis Output Format

Animacje bazują na danych z `AudioAnalyzer.analyze_for_animation()` zapisanych w `analysis/[audio_file]_analysis.json`:

```json
{
  "duration": 180.36,
  "tempo": {
    "bpm": 120.0,
    "confidence": 0.85
  },
  "animation_events": {
    "beats": [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, ...],
    "energy_peaks": [2.1, 5.8, 12.3, 18.7, 24.2, ...],
    "sections": [
      {"start": 0.0, "end": 32.1, "label": "intro"},
      {"start": 32.1, "end": 96.4, "label": "verse"},
      {"start": 96.4, "end": 128.5, "label": "chorus"}
    ],
    "onsets": [0.12, 0.54, 1.02, 1.48, 2.01, ...]
  },
  "frequency_bands": {
    "bass": [0.8, 1.2, 0.6, 1.5, 0.9, ...],
    "mid": [0.5, 0.7, 0.9, 0.6, 0.8, ...],
    "treble": [0.3, 0.6, 0.4, 0.7, 0.5, ...]
  }
}
```

### Animation Modes & Data Usage

**1. Beat-Switch Animation** (`--animation-mode beat-switch`)
- **Data source**: `animation_events.beats` (array of timestamps in seconds)
- **How it works**: Przełącza widoczność video strips (blend_alpha) na każdy beat
- **Keyframes**: `sequence_editor.sequences_all[strip_name].blend_alpha`
- **Pattern**: Strip 1→2→3→4→1→2→3→4 (round-robin)
- **Timing**: Beat times * FPS = frame numbers for keyframes

**2. Energy Pulse Animation** (`--animation-mode energy-pulse`)
- **Data source**: `animation_events.energy_peaks` (array of timestamps in seconds)
- **How it works**: Skaluje wszystkie video strips o 20% na energy peaks
- **Keyframes**: `sequence_editor.sequences_all[strip_name].transform.scale_x/y`
- **Pattern**: Normal scale (1.0) → Peak scale (1.2) → Normal scale (1.0)
- **Timing**: Energy peak times * FPS = frame numbers, +1 frame for return

**3. Section Transitions** (future - `--animation-mode section-transition`)
- **Data source**: `animation_events.sections` (array of objects with start/end/label)
- **How it works**: Smooth transitions between strips on section boundaries
- **Keyframes**: Multiple properties (blend_alpha, transform, effects)

**4. Multi-PiP** (future - `--animation-mode multi-pip`)
- **Data source**: `animation_events.onsets` + `frequency_bands`
- **How it works**: All strips visible simultaneously with different effects
- **Keyframes**: Position, scale, rotation based on frequency analysis

### Beat Division Impact

Parameter `--beat-division` wpływa na `animation_events.beats`:
- `1`: Every beat (quarter notes) - fewer animation events
- `2`: Every half beat (eighth notes) 
- `4`: Every quarter beat (sixteenth notes)
- `8`: Every eighth beat (thirty-second notes) - default, more animation events
- `16`: Every sixteenth beat (sixty-fourth notes) - most animation events

### Data Generation Process

1. **Audio Analysis**: `AudioAnalyzer.analyze_for_animation(audio_file)`
2. **Beat Detection**: `librosa.beat.beat_track()` → timestamps
3. **Energy Detection**: `librosa.feature.rms()` + peak finding → timestamps  
4. **Section Detection**: `librosa.segment.agglomerative()` → boundaries
5. **Onset Detection**: `librosa.onset.onset_detect()` → timestamps
6. **Frequency Analysis**: `librosa.feature.spectral_centroid()` → continuous data
7. **File Save**: JSON format w `analysis/[audio_file]_analysis.json`

### Debug Animation Data

```bash
# View raw analysis data
cat "/home/wojtas/Wideo/obs/2025-07-08 19-38-18/analysis/Przechwytywanie wejścia dźwięku (PulseAudio)_analysis.json" | jq '.animation_events.beats | length'

# Count energy peaks
cat "/home/wojtas/Wideo/obs/2025-07-08 19-38-18/analysis/Przechwytywanie wejścia dźwięku (PulseAudio)_analysis.json" | jq '.animation_events.energy_peaks | length'

# Check tempo
cat "/home/wojtas/Wideo/obs/2025-07-08 19-38-18/analysis/Przechwytywanie wejścia dźwięku (PulseAudio)_analysis.json" | jq '.tempo.bpm'
```

## Manual Verification Guide

### How to verify beat-switch animation in Blender:

1. **Open the created project:**
   ```bash
   # The blend file should be created at:
   /home/wojtas/Wideo/obs/2025-07-08 19-38-18/blender/2025-07-08 19-38-18.blend
   
   # Open in Blender:
   blender "/home/wojtas/Wideo/obs/2025-07-08 19-38-18/blender/2025-07-08 19-38-18.blend"
   # OR via snap:
   snap run blender "/home/wojtas/Wideo/obs/2025-07-08 19-38-18/blender/2025-07-08 19-38-18.blend"
   ```

2. **Switch to Video Sequence Editor workspace:**
   - W górnej części Blender kliknij na zakładkę "Video Editing"
   - Zobaczysz timeline z paskami video i audio

3. **Verify animation setup:**
   - **Timeline**: Sprawdź czy widzisz 5 video strips + 1 audio strip
   - **Keyframes**: Szukaj żółtych diamentów na timeline - to są keyframes dla blend_alpha
   - **Beat timing**: Keyframes powinny być w czasach: 3.9s, 8.2s, 12.3s, 16.4s, 20.6s, etc. (zgodnie z beat events)

4. **Test animation playback:**
   - Naciśnij SPACEBAR aby odtworzyć animację
   - Powinny być widoczne przełączające się video strips w rytm muzyki
   - Tylko jeden strip jest widoczny w danym momencie (blend_alpha = 1.0), pozostałe ukryte (blend_alpha = 0.0)

5. **Check animation properties:**
   - Kliknij na video strip
   - W Properties panel (po prawej stronie) → Strip → Blend
   - Powinieneś zobaczyć animowane "Opacity" property z keyframes

6. **Debug if project doesn't exist:**
   ```bash
   # Check if Blender created any output files:
   ls -la "/home/wojtas/Wideo/obs/2025-07-08 19-38-18/blender/"
   
   # Check render directory:
   ls -la "/home/wojtas/Wideo/obs/2025-07-08 19-38-18/blender/render/"
   
   # If no blend file, try running with more debug output:
   RUST_LOG=debug uv run python -m src.cli.blend_setup "/home/wojtas/Wideo/obs/2025-07-08 19-38-18" --animation-mode beat-switch --beat-division 8 --main-audio "Przechwytywanie wejścia dźwięku (PulseAudio).m4a" --verbose
   ```