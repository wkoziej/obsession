"""
Extractor functionality for OBS Canvas Recording.
This module handles video source extraction from canvas recordings.
"""

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

    # For now, mock the extraction process
    # In real implementation, this would use FFmpeg
    extracted_files = []

    # Create output directory
    video_path = Path(video_file)
    output_dir = video_path.parent / f"{video_path.stem}_extracted"

    # Mock extraction for each source
    for source_name in sources.keys():
        output_file = output_dir / f"{source_name}.mp4"
        extracted_files.append(str(output_file))

    return ExtractionResult(success=True, extracted_files=extracted_files)
