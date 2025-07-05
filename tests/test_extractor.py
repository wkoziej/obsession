"""
Test module for extractor functionality.
Following TDD approach - starting with RED phase.
"""

from src.core.extractor import ExtractionResult, extract_sources, calculate_crop_params


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


class TestCropParams:
    """Test cases for crop parameter calculation."""

    def test_calculate_crop_params_basic(self, basic_source_info, standard_canvas_size):
        """Test basic crop parameter calculation."""
        # When
        crop_params = calculate_crop_params(basic_source_info, standard_canvas_size)

        # Then
        assert crop_params["width"] == 1920
        assert crop_params["height"] == 1080
        assert crop_params["x"] == 0
        assert crop_params["y"] == 0

    def test_calculate_crop_params_with_position(
        self, positioned_source_info, wide_canvas_size
    ):
        """Test crop parameters with non-zero position."""
        # When
        crop_params = calculate_crop_params(positioned_source_info, wide_canvas_size)

        # Then
        assert crop_params["width"] == 1920
        assert crop_params["height"] == 1080
        assert crop_params["x"] == 1920
        assert crop_params["y"] == 0

    def test_calculate_crop_params_with_scale(
        self, scaled_source_info, standard_canvas_size
    ):
        """Test crop parameters with scaling."""
        # When
        crop_params = calculate_crop_params(scaled_source_info, standard_canvas_size)

        # Then
        assert crop_params["width"] == 960  # 1920 * 0.5
        assert crop_params["height"] == 540  # 1080 * 0.5
        assert crop_params["x"] == 0
        assert crop_params["y"] == 0

    def test_calculate_crop_params_complex(
        self, complex_source_info, standard_canvas_size
    ):
        """Test crop parameters with position and scale."""
        # When
        crop_params = calculate_crop_params(complex_source_info, standard_canvas_size)

        # Then
        assert crop_params["width"] == 1536  # 1920 * 0.8
        assert crop_params["height"] == 648  # 1080 * 0.6
        assert crop_params["x"] == 100
        assert crop_params["y"] == 50


class TestExtractSources:
    """Test cases for extract_sources function."""

    def test_extract_single_source_success(
        self, test_video_file, single_source_metadata
    ):
        """Test extracting single source from video."""
        # When
        result = extract_sources(test_video_file, single_source_metadata)

        # Then
        assert isinstance(result, ExtractionResult)
        assert result.success is True
        assert len(result.extracted_files) == 1
        assert "Camera1.mp4" in result.extracted_files[0]

    def test_extract_multiple_sources_success(
        self, test_video_file, dual_source_metadata
    ):
        """Test extracting multiple sources from video."""
        # When
        result = extract_sources(test_video_file, dual_source_metadata)

        # Then
        assert isinstance(result, ExtractionResult)
        assert result.success is True
        assert len(result.extracted_files) == 2
        assert any("Camera1.mp4" in f for f in result.extracted_files)
        assert any("Camera2.mp4" in f for f in result.extracted_files)

    def test_extract_sources_file_not_found(self, single_source_metadata):
        """Test extraction with non-existent video file."""
        # Given
        video_file = "non_existent_file.mp4"

        # When
        result = extract_sources(video_file, single_source_metadata)

        # Then
        assert isinstance(result, ExtractionResult)
        assert result.success is False
        assert result.extracted_files == []
        assert "not found" in result.error_message.lower()

    def test_extract_sources_invalid_metadata(self, test_video_file, invalid_metadata):
        """Test extraction with invalid metadata."""
        # When
        result = extract_sources(test_video_file, invalid_metadata)

        # Then
        assert isinstance(result, ExtractionResult)
        assert result.success is False
        assert result.extracted_files == []
        assert "metadata" in result.error_message.lower()

    def test_extract_sources_empty_sources(
        self, test_video_file, empty_sources_metadata
    ):
        """Test extraction with empty sources list."""
        # When
        result = extract_sources(test_video_file, empty_sources_metadata)

        # Then
        assert isinstance(result, ExtractionResult)
        assert result.success is True
        assert result.extracted_files == []
