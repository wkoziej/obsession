# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OBSession is a system for automatic extraction of sources from OBS canvas recordings using metadata collected during recording. The system integrates with OBS Studio to capture scene layout and uses FFmpeg for precise video/audio extraction.

## Key Architecture

### Core Components
- **`src/core/metadata.py`**: Handles metadata creation and OBS API integration for source capabilities detection
- **`src/core/extractor.py`**: FFmpeg-based video/audio extraction with crop parameter calculation
- **`src/obs_integration/obs_script.py`**: OBS Studio script that collects scene metadata during recording
- **`src/cli/extract.py`**: Command-line interface for manual extraction

### Data Flow
1. OBS script collects scene metadata on recording start/stop
2. Metadata includes source positions, dimensions, and capabilities (audio/video flags)
3. CLI tool uses metadata to extract individual sources via FFmpeg
4. Extracted files are organized by source type (video .mp4, audio .m4a)

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

# With verbose output
uv run python -m cli.extract recording.mkv metadata.json --verbose
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

### Error Handling
- `ExtractionResult` class wraps success/failure states
- Graceful fallbacks when OBS API unavailable (testing)
- File sanitization for cross-platform compatibility

## Testing Standards

- **TDD workflow**: Write failing tests first, implement minimal code to pass
- **Coverage target**: 80% minimum (configured in pyproject.toml)
- **Test markers**: `unit`, `integration`, `slow` for selective test execution
- **Fixture files**: Located in `tests/fixtures/` for sample recordings

## OBS Integration

The `obs_script.py` must be loaded in OBS Studio (Tools → Scripts → Add). It requires:
- Python 3.9+ environment accessible to OBS
- Metadata output path configuration
- Scene analysis capabilities for source enumeration

## Dependencies

- **Runtime**: `ffmpeg-python`, `pathlib-extensions`
- **Development**: `pytest`, `pytest-cov`, `black`, `mypy`, `flake8`
- **External**: FFmpeg 4.4+ must be available in PATH