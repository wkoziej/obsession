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
    """
    # Extract position and scale from source info
    position = source_info.get("position", {"x": 0, "y": 0})
    scale = source_info.get("scale", {"x": 1.0, "y": 1.0})

    # For POC: assume standard source size (1920x1080) scaled by scale factor
    # In real implementation, this would come from source metadata
    standard_source_width = 1920
    standard_source_height = 1080

    # Calculate crop dimensions based on standard source size and scale
    crop_width = int(standard_source_width * scale["x"])
    crop_height = int(standard_source_height * scale["y"])

    # Position is where to crop from
    crop_x = int(position["x"])
    crop_y = int(position["y"])

    return {"x": crop_x, "y": crop_y, "width": crop_width, "height": crop_height}


def extract_sources(video_file: str, metadata: Dict[str, Any]) -> ExtractionResult:
    """
    Extract individual sources from canvas recording.

    Args:
        video_file: Path to the input video file
        metadata: Recording metadata containing source positions

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
    output_dir = video_path.parent / f"{video_path.stem}_extracted"

    try:
        output_dir.mkdir(exist_ok=True)
    except PermissionError:
        return ExtractionResult(
            success=False,
            error_message=f"Permission denied: Cannot create output directory {output_dir}",
        )
    except OSError as e:
        return ExtractionResult(
            success=False,
            error_message=f"Failed to create output directory {output_dir}: {e}",
        )

    # Get canvas size for crop calculations
    canvas_size = metadata.get("canvas_size", [1920, 1080])

    extracted_files = []

    # Extract each source using FFmpeg
    for source_name, source_info in sources.items():
        # Sanitize source name for safe filename
        safe_source_name = sanitize_filename(source_name)
        output_file = output_dir / f"{safe_source_name}.mp4"

        # Calculate crop parameters
        crop_params = calculate_crop_params(source_info, canvas_size)

        # Build FFmpeg command
        crop_filter = f"crop={crop_params['width']}:{crop_params['height']}:{crop_params['x']}:{crop_params['y']}"

        cmd = [
            "ffmpeg",
            "-i",
            str(video_file),
            "-filter:v",
            crop_filter,
            "-c:v",
            "libx264",
            "-crf",
            "23",
            "-preset",
            "fast",
            "-y",  # Overwrite output files
            str(output_file),
        ]

        try:
            # Execute FFmpeg command
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            extracted_files.append(str(output_file))
        except subprocess.CalledProcessError as e:
            return ExtractionResult(
                success=False,
                error_message=f"FFmpeg failed to extract {source_name}: {e.stderr}",
            )
        except FileNotFoundError:
            return ExtractionResult(
                success=False,
                error_message="FFmpeg not found. Please install FFmpeg and ensure it's in your PATH.",
            )

    return ExtractionResult(success=True, extracted_files=extracted_files)
