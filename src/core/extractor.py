"""
Extractor functionality for OBS Canvas Recording.
This module handles video source extraction from canvas recordings.
"""

import re
import subprocess
from typing import List, Optional, Dict, Any
from pathlib import Path


class ExtractionResult:
    """
    Result object for video extraction operations.

    Attributes:
        success: Boolean indicating if extraction was successful
        extracted_files: List of paths to extracted video files
        error_message: Optional error message if extraction failed
    """

    def __init__(
        self,
        success: bool = False,
        extracted_files: Optional[List[str]] = None,
        error_message: Optional[str] = None,
    ):
        """
        Initialize ExtractionResult.

        Args:
            success: Whether extraction was successful
            extracted_files: List of extracted file paths
            error_message: Error message if extraction failed
        """
        self.success = success
        self.extracted_files = extracted_files or []
        self.error_message = error_message

    def __str__(self) -> str:
        """String representation of ExtractionResult."""
        return (
            f"ExtractionResult(success={self.success}, "
            f"extracted_files={len(self.extracted_files)}, "
            f"error_message={self.error_message})"
        )


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing or replacing problematic characters.

    Args:
        filename: Original filename that may contain special characters

    Returns:
        Sanitized filename safe for filesystem use
    """
    # Replace problematic characters with underscores
    # Characters: / \ : * ? " < > |
    sanitized = re.sub(r'[/\\:*?"<>|]', "_", filename)

    # Remove multiple consecutive underscores
    sanitized = re.sub(r"_+", "_", sanitized)

    # Remove leading/trailing underscores
    sanitized = sanitized.strip("_")

    # Ensure filename is not empty after sanitization
    if not sanitized:
        sanitized = "source"

    return sanitized


def calculate_crop_params(
    source_info: Dict[str, Any], canvas_size: List[int]
) -> Dict[str, int]:
    """
    Calculate crop parameters for FFmpeg based on source info.

    Args:
        source_info: Source information with position and scale
        canvas_size: Canvas dimensions [width, height]

    Returns:
        Dictionary with crop parameters (x, y, width, height)

    Raises:
        ValueError: If source has invalid dimensions (0x0)
    """
    # Extract position and scale from source info
    position = source_info.get("position", {"x": 0, "y": 0})
    scale = source_info.get("scale", {"x": 1.0, "y": 1.0})

    # Get actual source dimensions from metadata
    dimensions = source_info.get("dimensions", {})

    # Use source dimensions (original video size) for crop calculation
    # The final dimensions are after scaling in OBS, but we need to crop from the original video
    source_width = dimensions.get("source_width", 1920)  # Default fallback
    source_height = dimensions.get("source_height", 1080)  # Default fallback

    # Check if source has valid dimensions
    if source_width <= 0 or source_height <= 0:
        raise ValueError(
            f"Source has invalid dimensions: {source_width}x{source_height}"
        )

    # Calculate crop dimensions based on source dimensions and scale
    # But ensure we don't exceed the actual source dimensions
    desired_crop_width = int(source_width * scale["x"])
    desired_crop_height = int(source_height * scale["y"])

    # Limit crop dimensions to actual source dimensions
    crop_width = min(desired_crop_width, source_width)
    crop_height = min(desired_crop_height, source_height)

    # Position is where to crop from
    crop_x = int(position["x"])
    crop_y = int(position["y"])

    # Ensure crop region doesn't exceed canvas bounds
    # If the crop region would go beyond the canvas, adjust it
    if crop_x + crop_width > canvas_size[0]:
        crop_width = canvas_size[0] - crop_x
    if crop_y + crop_height > canvas_size[1]:
        crop_height = canvas_size[1] - crop_y

    # Ensure minimum crop size and that position is not negative
    crop_x = max(crop_x, 0)
    crop_y = max(crop_y, 0)
    crop_width = max(crop_width, 1)
    crop_height = max(crop_height, 1)

    return {"x": crop_x, "y": crop_y, "width": crop_width, "height": crop_height}


def _get_ffmpeg_base_cmd(input_file: str) -> List[str]:
    """
    Get base FFmpeg command.

    Args:
        input_file: Path to input video file

    Returns:
        Base FFmpeg command as list of strings
    """
    return ["ffmpeg", "-i", str(input_file)]


def _extract_video_source(
    input_file: str,
    output_file: Path,
    source_info: Dict[str, Any],
    canvas_size: List[int],
) -> None:
    """
    Extract video from source using FFmpeg.

    Args:
        input_file: Path to input video file
        output_file: Path to output video file
        source_info: Source information with position data
        canvas_size: Canvas dimensions

    Raises:
        subprocess.CalledProcessError: If FFmpeg command fails
        FileNotFoundError: If FFmpeg is not found
        ValueError: If source has invalid dimensions
    """
    # Calculate crop parameters
    crop_params = calculate_crop_params(source_info, canvas_size)
    crop_filter = f"crop={crop_params['width']}:{crop_params['height']}:{crop_params['x']}:{crop_params['y']}"

    # Build FFmpeg command for video extraction
    cmd = _get_ffmpeg_base_cmd(input_file) + [
        "-filter:v",
        crop_filter,
        "-c:v",
        "libx264",
        "-crf",
        "23",
        "-preset",
        "fast",
        "-an",  # No audio in video files
        "-y",
        str(output_file),
    ]

    subprocess.run(cmd, check=True, capture_output=True, text=True)


def _extract_audio_source(input_file: str, output_file: Path) -> None:
    """
    Extract audio from source using FFmpeg.

    Args:
        input_file: Path to input video file
        output_file: Path to output audio file

    Raises:
        subprocess.CalledProcessError: If FFmpeg command fails
        FileNotFoundError: If FFmpeg is not found
    """
    # Build FFmpeg command for audio extraction
    cmd = _get_ffmpeg_base_cmd(input_file) + [
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-vn",  # No video in audio files
        "-y",
        str(output_file),
    ]

    subprocess.run(cmd, check=True, capture_output=True, text=True)


def extract_sources(
    video_file: str, metadata: Dict[str, Any], output_dir: Optional[str] = None
) -> ExtractionResult:
    """
    Extract individual sources from canvas recording.

    Args:
        video_file: Path to the input video file
        metadata: Recording metadata containing source positions
        output_dir: Optional custom output directory path

    Returns:
        ExtractionResult with success status and extracted files
    """
    # Validate input file exists
    if not Path(video_file).exists():
        return ExtractionResult(
            success=False, error_message=f"Video file not found: {video_file}"
        )

    # Validate metadata structure
    if not isinstance(metadata, dict):
        return ExtractionResult(
            success=False, error_message="Invalid metadata: must be a dictionary"
        )

    if "sources" not in metadata:
        return ExtractionResult(
            success=False, error_message="Invalid metadata: missing 'sources' field"
        )

    sources = metadata["sources"]

    # Handle empty sources - this is valid (no extraction needed)
    if not sources:
        return ExtractionResult(success=True, extracted_files=[])

    # Create output directory
    video_path = Path(video_file)
    if output_dir:
        output_dir_path = Path(output_dir)
    else:
        output_dir_path = video_path.parent / f"{video_path.stem}_extracted"

    try:
        output_dir_path.mkdir(exist_ok=True, parents=True)
    except PermissionError:
        return ExtractionResult(
            success=False,
            error_message=f"Permission denied: Cannot create output directory {output_dir_path}",
        )
    except OSError as e:
        return ExtractionResult(
            success=False,
            error_message=f"Failed to create output directory {output_dir_path}: {e}",
        )

    # Get canvas size for crop calculations
    canvas_size = metadata.get("canvas_size", [1920, 1080])
    extracted_files = []

    # Process each source based on its capabilities
    for source_name, source_info in sources.items():
        has_audio = source_info.get("has_audio", False)
        has_video = source_info.get("has_video", False)

        # Skip sources without audio or video
        if not has_audio and not has_video:
            continue

        safe_source_name = sanitize_filename(source_name)

        # Extract video if source has video
        if has_video:
            # Check if source has valid dimensions before creating output file
            try:
                dimensions = source_info.get("dimensions", {})
                source_width = dimensions.get("source_width", 1920)
                source_height = dimensions.get("source_height", 1080)

                if source_width <= 0 or source_height <= 0:
                    print(
                        f"Warning: Skipping video extraction for {source_name}: Source has invalid dimensions: {source_width}x{source_height}"
                    )
                    continue

                video_output_file = output_dir_path / f"{safe_source_name}.mp4"

                _extract_video_source(
                    video_file, video_output_file, source_info, canvas_size
                )
                extracted_files.append(str(video_output_file))
            except ValueError as e:
                # Skip sources with invalid dimensions (e.g., 0x0)
                print(f"Warning: Skipping video extraction for {source_name}: {e}")
                continue
            except subprocess.CalledProcessError as e:
                return ExtractionResult(
                    success=False,
                    error_message=f"FFmpeg failed to extract video from {source_name}: {e.stderr}",
                )
            except FileNotFoundError:
                return ExtractionResult(
                    success=False,
                    error_message="FFmpeg not found. Please install FFmpeg and ensure it's in your PATH.",
                )

        # Extract audio if source has audio
        if has_audio:
            audio_output_file = output_dir_path / f"{safe_source_name}.m4a"

            try:
                _extract_audio_source(video_file, audio_output_file)
                extracted_files.append(str(audio_output_file))
            except subprocess.CalledProcessError as e:
                return ExtractionResult(
                    success=False,
                    error_message=f"FFmpeg failed to extract audio from {source_name}: {e.stderr}",
                )
            except FileNotFoundError:
                return ExtractionResult(
                    success=False,
                    error_message="FFmpeg not found. Please install FFmpeg and ensure it's in your PATH.",
                )

    return ExtractionResult(success=True, extracted_files=extracted_files)


class SourceExtractor:
    """
    Extractor for individual sources from canvas recording.
    """

    def __init__(self, input_file: str, metadata: Dict[str, Any], output_dir: str):
        """
        Initialize SourceExtractor.

        Args:
            input_file: Path to the input video file
            metadata: Recording metadata containing source information
            output_dir: Directory to save extracted files
        """
        self.input_file = input_file
        self.metadata = metadata
        self.output_dir = output_dir

    def extract_sources(self) -> ExtractionResult:
        """
        Extract sources using the standalone function.

        Returns:
            ExtractionResult with success status and extracted files
        """
        return extract_sources(self.input_file, self.metadata, self.output_dir)
