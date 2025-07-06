"""
Moduł zarządzający strukturą plików nagrań OBS Canvas Recorder.

Centralizuje logikę tworzenia i rozpoznawania struktury katalogów nagrań.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class RecordingStructure:
    """Struktura reprezentująca organizację plików nagrania."""

    recording_dir: Path
    video_file: Path
    metadata_file: Path
    extracted_dir: Path

    def exists(self) -> bool:
        """Sprawdza czy struktura istnieje w systemie plików."""
        return (
            self.recording_dir.exists()
            and self.video_file.exists()
            and self.metadata_file.exists()
            and self.extracted_dir.exists()
        )

    def is_valid(self) -> bool:
        """Sprawdza czy struktura jest poprawna (katalogi istnieją, plik metadata jest poprawny)."""
        try:
            # Sprawdź czy katalogi istnieją
            if not self.recording_dir.exists():
                return False

            # Sprawdź czy plik wideo istnieje
            if not self.video_file.exists():
                return False

            # Sprawdź czy plik metadata istnieje i jest poprawny JSON
            if not self.metadata_file.exists():
                return False

            with open(self.metadata_file, "r", encoding="utf-8") as f:
                json.load(f)  # Sprawdź czy to poprawny JSON

            return True
        except (json.JSONDecodeError, IOError, OSError):
            return False


class FileStructureManager:
    """Zarządca struktury plików nagrań."""

    METADATA_FILENAME = "metadata.json"
    EXTRACTED_DIRNAME = "extracted"

    @staticmethod
    def get_structure(video_path: Path) -> RecordingStructure:
        """
        Zwraca strukturę nagrania na podstawie ścieżki do pliku wideo.

        Args:
            video_path: Ścieżka do pliku wideo nagrania

        Returns:
            RecordingStructure: Struktura nagrania
        """
        video_path = Path(video_path)

        # Katalog nagrania to katalog zawierający plik wideo
        recording_dir = video_path.parent

        # Ścieżki do plików
        metadata_file = recording_dir / FileStructureManager.METADATA_FILENAME
        extracted_dir = recording_dir / FileStructureManager.EXTRACTED_DIRNAME

        return RecordingStructure(
            recording_dir=recording_dir,
            video_file=video_path,
            metadata_file=metadata_file,
            extracted_dir=extracted_dir,
        )

    @staticmethod
    def create_structure(video_path: Path) -> RecordingStructure:
        """
        Tworzy strukturę nagrania w systemie plików.

        Args:
            video_path: Ścieżka do pliku wideo nagrania

        Returns:
            RecordingStructure: Utworzona struktura nagrania
        """
        structure = FileStructureManager.get_structure(video_path)

        # Utwórz katalog extracted jeśli nie istnieje
        structure.extracted_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Utworzono strukturę nagrania: {structure.recording_dir}")

        return structure

    @staticmethod
    def get_extracted_dir(video_path: Path) -> Path:
        """
        Zwraca ścieżkę do katalogu extracted dla danego nagrania.

        Args:
            video_path: Ścieżka do pliku wideo nagrania

        Returns:
            Path: Ścieżka do katalogu extracted
        """
        structure = FileStructureManager.get_structure(video_path)
        return structure.extracted_dir

    @staticmethod
    def get_metadata_file(video_path: Path) -> Path:
        """
        Zwraca ścieżkę do pliku metadata.json dla danego nagrania.

        Args:
            video_path: Ścieżka do pliku wideo nagrania

        Returns:
            Path: Ścieżka do pliku metadata.json
        """
        structure = FileStructureManager.get_structure(video_path)
        return structure.metadata_file

    @staticmethod
    def create_recording_directory_name(video_path: Path) -> str:
        """
        Tworzy nazwę katalogu nagrania na podstawie ścieżki do pliku wideo.

        Args:
            video_path: Ścieżka do pliku wideo nagrania

        Returns:
            str: Nazwa katalogu nagrania
        """
        video_path = Path(video_path)
        return video_path.stem  # Nazwa pliku bez rozszerzenia

    @staticmethod
    def find_recording_structure(base_path: Path) -> Optional[RecordingStructure]:
        """
        Szuka struktury nagrania w danym katalogu.

        Args:
            base_path: Ścieżka do katalogu do przeszukania

        Returns:
            Optional[RecordingStructure]: Znaleziona struktura lub None
        """
        base_path = Path(base_path)

        if not base_path.exists() or not base_path.is_dir():
            return None

        # Szukaj pliku metadata.json
        metadata_file = base_path / FileStructureManager.METADATA_FILENAME
        if not metadata_file.exists():
            return None

        # Szukaj pliku wideo w tym samym katalogu
        video_extensions = [".mkv", ".mp4", ".avi", ".mov", ".flv", ".wmv", ".webm"]
        video_file = None

        for file_path in base_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in video_extensions:
                video_file = file_path
                break

        if not video_file:
            return None

        # Utwórz strukturę
        structure = FileStructureManager.get_structure(video_file)

        # Sprawdź czy struktura jest poprawna
        if structure.is_valid():
            return structure

        return None

    @staticmethod
    def ensure_extracted_dir(video_path: Path) -> Path:
        """
        Zapewnia istnienie katalogu extracted dla danego nagrania.

        Args:
            video_path: Ścieżka do pliku wideo nagrania

        Returns:
            Path: Ścieżka do katalogu extracted
        """
        extracted_dir = FileStructureManager.get_extracted_dir(video_path)
        extracted_dir.mkdir(parents=True, exist_ok=True)
        return extracted_dir

    @staticmethod
    def ensure_blender_dir(recording_dir: Path) -> Path:
        """
        Tworzy katalog blender/ w strukturze nagrania.

        Args:
            recording_dir: Ścieżka do katalogu nagrania

        Returns:
            Path: Ścieżka do katalogu blender/
        """
        blender_dir = recording_dir / "blender"
        blender_dir.mkdir(parents=True, exist_ok=True)

        # Utwórz także katalog render/
        render_dir = blender_dir / "render"
        render_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Utworzono katalog blender: {blender_dir}")
        return blender_dir

    @staticmethod
    def find_audio_files(extracted_dir: Path) -> list[Path]:
        """
        Znajduje wszystkie pliki audio w katalogu extracted.

        Args:
            extracted_dir: Ścieżka do katalogu extracted

        Returns:
            list[Path]: Lista plików audio
        """
        audio_extensions = [".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg", ".wma"]
        audio_files = []

        if not extracted_dir.exists():
            logger.warning(f"Katalog extracted nie istnieje: {extracted_dir}")
            return audio_files

        for file_path in extracted_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in audio_extensions:
                audio_files.append(file_path)

        # Sortuj dla spójności
        audio_files.sort(key=lambda x: x.name)
        logger.debug(f"Znaleziono {len(audio_files)} plików audio w {extracted_dir}")
        return audio_files

    @staticmethod
    def find_video_files(extracted_dir: Path) -> list[Path]:
        """
        Znajduje wszystkie pliki wideo w katalogu extracted.

        Args:
            extracted_dir: Ścieżka do katalogu extracted

        Returns:
            list[Path]: Lista plików wideo
        """
        video_extensions = [".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".webm"]
        video_files = []

        if not extracted_dir.exists():
            logger.warning(f"Katalog extracted nie istnieje: {extracted_dir}")
            return video_files

        for file_path in extracted_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in video_extensions:
                video_files.append(file_path)

        # Sortuj dla spójności
        video_files.sort(key=lambda x: x.name)
        logger.debug(f"Znaleziono {len(video_files)} plików wideo w {extracted_dir}")
        return video_files
