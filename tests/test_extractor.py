"""
Test module for extractor functionality.
Following TDD approach - starting with RED phase.
"""

from src.core.extractor import ExtractionResult


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
