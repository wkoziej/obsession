"""
CLI interface for Blender VSE project setup.

This module provides command-line interface for creating Blender VSE projects
from extracted OBS Canvas recordings.
"""

import argparse
import logging
import sys
from pathlib import Path

from ..core.blender_project import BlenderProjectManager
from ..core.audio_validator import AudioValidationError


def setup_logging(verbose: bool = False) -> None:
    """
    Setup logging configuration.

    Args:
        verbose: Enable verbose logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Tworzy projekt Blender VSE z nagrania OBS Canvas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  %(prog)s ./recording_20250105_143022
  %(prog)s ./recording_20250105_143022 --verbose
  %(prog)s ./recording_20250105_143022 --main-audio "main_audio.m4a"
  %(prog)s ./recording_20250105_143022 --force
        """,
    )

    parser.add_argument("recording_dir", type=Path, help="Katalog nagrania OBS Canvas")

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Szczegółowe logowanie"
    )

    parser.add_argument(
        "--force", "-f", action="store_true", help="Nadpisz istniejący plik .blend"
    )

    parser.add_argument(
        "--main-audio",
        type=str,
        help="Nazwa głównego pliku audio (wymagane gdy jest więcej niż jeden plik audio)",
    )

    return parser.parse_args()


def validate_recording_directory(recording_dir: Path) -> None:
    """
    Validate recording directory structure.

    Args:
        recording_dir: Path to recording directory

    Raises:
        ValueError: If directory structure is invalid
    """
    if not recording_dir.exists():
        raise ValueError(f"Katalog nagrania nie istnieje: {recording_dir}")

    if not recording_dir.is_dir():
        raise ValueError(f"Ścieżka nie jest katalogiem: {recording_dir}")

    # Check for metadata.json
    metadata_path = recording_dir / "metadata.json"
    if not metadata_path.exists():
        raise ValueError(f"Brak pliku metadata.json w katalogu: {recording_dir}")

    # Check for extracted directory
    extracted_dir = recording_dir / "extracted"
    if not extracted_dir.exists():
        raise ValueError(f"Brak katalogu extracted/ w katalogu: {recording_dir}")

    if not extracted_dir.is_dir():
        raise ValueError(f"extracted/ nie jest katalogiem w: {recording_dir}")

    # Check if extracted directory has any files
    if not any(extracted_dir.iterdir()):
        raise ValueError(f"Katalog extracted/ jest pusty w: {recording_dir}")


def main() -> int:
    """
    Main CLI entry point.

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    args = parse_args()
    setup_logging(args.verbose)

    logger = logging.getLogger(__name__)

    try:
        # Validate recording directory
        logger.info(f"Validating recording directory: {args.recording_dir}")
        validate_recording_directory(args.recording_dir)

        # Create Blender project manager
        manager = BlenderProjectManager()

        # Create VSE project
        logger.info("Creating Blender VSE project...")
        project_path = manager.create_vse_project(args.recording_dir, args.main_audio)

        print(f"✅ Projekt Blender VSE utworzony: {project_path}")
        return 0

    except AudioValidationError as e:
        logger.error(f"Audio validation error: {e}")
        print(f"❌ Błąd audio: {e}", file=sys.stderr)
        return 1

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        print(f"❌ Błąd walidacji: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Nieoczekiwany błąd: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
