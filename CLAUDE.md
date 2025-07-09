# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OBS Canvas Recorder is a comprehensive system for automatic extraction of sources from OBS canvas recordings and creation of Blender VSE projects. The system integrates with OBS Studio to capture scene layout, uses FFmpeg for precise video/audio extraction, and provides automated Blender Video Sequence Editor project generation.

## Key Architecture

### Core Components
- **`src/core/metadata.py`**: Handles metadata creation and OBS API integration for source capabilities detection
- **`src/core/extractor.py`**: FFmpeg-based video/audio extraction with crop parameter calculation
- **`src/core/file_structure.py`**: Manages organized file structure for recordings (metadata.json, extracted/, blender/)
- **`src/core/blender_project.py`**: Creates Blender VSE projects from extracted recordings using parametric scripts
- **`src/core/audio_validator.py`**: Validates and selects main audio files for projects
- **`src/core/blender_vse_script.py`**: Parametric Blender script for VSE project creation
- **`src/obs_integration/obs_script.py`**: OBS Studio script that collects scene metadata and auto-organizes files
- **`src/cli/extract.py`**: Command-line interface for source extraction
- **`src/cli/blend_setup.py`**: CLI for creating Blender VSE projects from recordings
- **`src/cli/cameras.py`**: CLI for managing multiple camera setup with RPi cameras

### Data Flow
1. OBS script collects scene metadata on recording start/stop
2. Files are automatically organized into structured directories using FileStructureManager
3. Metadata includes source positions, dimensions, and capabilities (audio/video flags)
4. CLI tool uses metadata to extract individual sources via FFmpeg to extracted/ directory
5. Blender VSE projects can be created from extracted files with automatic main audio detection
6. Final structure: recording_name/[video_file, metadata.json, extracted/, blender/]

## Development Commands

### Setup
```bash
# Install dependencies
uv sync

# Install development dependencies
uv sync --group dev
```

### Testing (TDD Approach)
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test categories
uv run pytest -m unit          # Unit tests only
uv run pytest -m integration   # Integration tests only
uv run pytest -m "not slow"    # Skip slow tests

# Run single test file
uv run pytest tests/test_extractor.py -v
```

### Code Quality
```bash
# Format code
uv run black src/ tests/

# Type checking
uv run mypy src/

# Linting (via flake8 in dev dependencies)
uv run flake8 src/ tests/
```

### CLI Usage
```bash
# Extract sources from recording
uv run python -m cli.extract recording.mkv metadata.json

# With output directory
uv run python -m cli.extract recording.mkv metadata.json --output-dir ./extracted/

# With verbose output and auto-detection
uv run python -m cli.extract recording.mkv --auto --verbose

# Create Blender VSE project from extracted recording
uv run python -m cli.blend_setup ./recording_20250105_143022

# With specific main audio file
uv run python -m cli.blend_setup ./recording_20250105_143022 --main-audio "main_audio.m4a"

# Manage camera setup (RPi cameras)
uv run python -m cli.cameras --help
```

## Key Design Patterns

### Metadata Format (v2.0)
The system uses a structured metadata format with source capabilities:
- `has_audio`/`has_video` flags determined via OBS API
- Source positioning and dimensions for crop calculations
- Recording timestamps and canvas size

### FFmpeg Integration
- Video extraction uses crop filter: `crop=width:height:x:y`
- Audio extraction strips video: `-vn` flag
- Separate files for video (.mp4) and audio (.m4a) based on capabilities

### File Structure Management
- **FileStructureManager**: Centralized file organization system
- **Auto-reorganization**: OBS script automatically creates proper directory structure
- **Standardized paths**: `metadata.json`, `extracted/`, `blender/` directories
- **Cross-platform compatibility**: File sanitization and path handling

### Error Handling
- `ExtractionResult` class wraps success/failure states
- Graceful fallbacks when OBS API unavailable (testing)
- File sanitization for cross-platform compatibility
- `AudioValidationError` for audio file validation issues
- Comprehensive logging throughout the system

## Testing Standards

- **TDD workflow**: Write failing tests first, implement minimal code to pass
- **Coverage target**: 80% minimum (configured in pyproject.toml)
- **Test markers**: `unit`, `integration`, `slow` for selective test execution
- **Fixture files**: Located in `tests/fixtures/` for sample recordings

## OBS Integration

The `obs_script.py` must be loaded in OBS Studio (Tools → Scripts → Add). It requires:
- Python 3.9+ environment accessible to OBS
- Automatic file reorganization after recording stops
- Scene analysis capabilities for source enumeration
- Integration with FileStructureManager for consistent organization
- Support for both fallback metadata saving and structured organization

## Blender Integration

The system includes comprehensive Blender VSE project generation:
- **Parametric script approach**: Environment variables control project creation
- **Automatic main audio detection**: Uses AudioValidator to select primary audio track
- **FPS detection**: Reads frame rate from recording metadata
- **Snap support**: Works with snap-installed Blender
- **Render configuration**: Sets up output paths and resolution
- **VSE timeline setup**: Automatically arranges video and audio tracks

## Dependencies

- **Runtime**: `ffmpeg-python`, `pathlib-extensions`
- **Development**: `pytest`, `pytest-cov`, `black`, `mypy`, `flake8`, `pre-commit`
- **External**: 
  - FFmpeg 4.4+ must be available in PATH
  - Blender 3.0+ for VSE project generation (can be snap-installed)
  - OBS Studio with Python scripting support

## Project Structure

```
recording_name/
├── recording_name.mkv       # Main recording file
├── metadata.json           # Scene metadata from OBS
├── extracted/              # Extracted individual sources
│   ├── source1.mp4
│   ├── source2.m4a
│   └── ...
└── blender/               # Blender VSE projects
    ├── recording_name.blend
    └── render/
        └── recording_name_final.mp4
```

## Advanced Features

### Multi-Camera Setup
- RPi camera management via `cli.cameras`
- Deployment scripts for camera networks
- Integration with OBS for multi-angle recording

### Audio Processing
- Automatic main audio detection based on file size and duration
- Support for multiple audio sources in VSE projects
- Audio validation and error handling

### Advanced Scene Switcher Integration
- Support for OBS Advanced Scene Switcher plugin
- Automatic source extraction based on scene switching metadata
- Enhanced metadata collection for complex setups