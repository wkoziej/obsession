"""
Test module for extractor functionality.
Following TDD approach - starting with RED phase.
"""

from src.core.extractor import ExtractionResult, extract_sources


class TestExtractionResult:
    """Test cases for ExtractionResult class."""

    def test_extraction_result_creation_default(self):
        """Test creating ExtractionResult with default values."""
        # Given/When
        result = ExtractionResult()

        # Then
        assert result.success is False
        assert result.extracted_files == []
        assert result.error_message is None

    def test_extraction_result_creation_with_success(self):
        """Test creating ExtractionResult with success=True."""
        # Given
        extracted_files = ["camera1.mp4", "camera2.mp4"]

        # When
        result = ExtractionResult(success=True, extracted_files=extracted_files)

        # Then
        assert result.success is True
        assert result.extracted_files == extracted_files
        assert result.error_message is None

    def test_extraction_result_creation_with_error(self):
        """Test creating ExtractionResult with error."""
        # Given
        error_msg = "FFmpeg failed to process video"

        # When
        result = ExtractionResult(success=False, error_message=error_msg)

        # Then
        assert result.success is False
        assert result.extracted_files == []
        assert result.error_message == error_msg

    def test_extraction_result_str_representation(self):
        """Test string representation of ExtractionResult."""
        # Given
        result = ExtractionResult(success=True, extracted_files=["test.mp4"])

        # When
        str_repr = str(result)

        # Then
        assert "success=True" in str_repr
        assert "extracted_files=1" in str_repr


class TestExtractSources:
    """Test cases for extract_sources function."""

    def test_extract_single_source_success(self):
        """Test extracting single source from video."""
        # Given
        video_file = "tests/fixtures/test_recording.mp4"
        metadata = {
            "canvas_size": [1920, 1080],
            "sources": {
                "Camera1": {"position": {"x": 0, "y": 0}, "scale": {"x": 1.0, "y": 1.0}}
            },
        }

        # When
        result = extract_sources(video_file, metadata)

        # Then
        assert isinstance(result, ExtractionResult)
        assert result.success is True
        assert len(result.extracted_files) == 1
        assert "Camera1.mp4" in result.extracted_files[0]

    def test_extract_multiple_sources_success(self):
        """Test extracting multiple sources from video."""
        # Given
        video_file = "tests/fixtures/test_recording.mp4"
        metadata = {
            "canvas_size": [3840, 1080],
            "sources": {
                "Camera1": {
                    "position": {"x": 0, "y": 0},
                    "scale": {"x": 1.0, "y": 1.0},
                },
                "Camera2": {
                    "position": {"x": 1920, "y": 0},
                    "scale": {"x": 1.0, "y": 1.0},
                },
            },
        }

        # When
        result = extract_sources(video_file, metadata)

        # Then
        assert isinstance(result, ExtractionResult)
        assert result.success is True
        assert len(result.extracted_files) == 2
        assert any("Camera1.mp4" in f for f in result.extracted_files)
        assert any("Camera2.mp4" in f for f in result.extracted_files)

    def test_extract_sources_file_not_found(self):
        """Test extraction with non-existent video file."""
        # Given
        video_file = "non_existent_file.mp4"
        metadata = {
            "canvas_size": [1920, 1080],
            "sources": {
                "Camera1": {"position": {"x": 0, "y": 0}, "scale": {"x": 1.0, "y": 1.0}}
            },
        }

        # When
        result = extract_sources(video_file, metadata)

        # Then
        assert isinstance(result, ExtractionResult)
        assert result.success is False
        assert result.extracted_files == []
        assert "not found" in result.error_message.lower()

    def test_extract_sources_invalid_metadata(self):
        """Test extraction with invalid metadata."""
        # Given
        video_file = "tests/fixtures/test_recording.mp4"
        metadata = {
            "canvas_size": [1920, 1080],
            # Missing sources field
        }

        # When
        result = extract_sources(video_file, metadata)

        # Then
        assert isinstance(result, ExtractionResult)
        assert result.success is False
        assert result.extracted_files == []
        assert "metadata" in result.error_message.lower()

    def test_extract_sources_empty_sources(self):
        """Test extraction with empty sources list."""
        # Given
        video_file = "tests/fixtures/test_recording.mp4"
        metadata = {"canvas_size": [1920, 1080], "sources": {}}

        # When
        result = extract_sources(video_file, metadata)

        # Then
        assert isinstance(result, ExtractionResult)
        assert result.success is True
        assert result.extracted_files == []
