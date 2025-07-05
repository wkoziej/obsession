"""
Test module for extractor functionality.
Following TDD approach - starting with RED phase.
"""

import subprocess
from unittest.mock import patch, Mock
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

    @patch("subprocess.run")
    def test_extract_single_source_success(
        self, mock_subprocess, test_video_file, single_source_metadata
    ):
        """Test extracting single source from video."""
        # Given
        mock_subprocess.return_value = Mock(returncode=0)

        # When
        result = extract_sources(test_video_file, single_source_metadata)

        # Then
        assert isinstance(result, ExtractionResult)
        assert result.success is True
        assert len(result.extracted_files) == 1
        assert "Camera1.mp4" in result.extracted_files[0]

    @patch("subprocess.run")
    def test_extract_multiple_sources_success(
        self, mock_subprocess, test_video_file, dual_source_metadata
    ):
        """Test extracting multiple sources from video."""
        # Given
        mock_subprocess.return_value = Mock(returncode=0)

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
        assert result.error_message is not None
        assert "not found" in result.error_message.lower()

    def test_extract_sources_invalid_metadata(self, test_video_file, invalid_metadata):
        """Test extraction with invalid metadata."""
        # When
        result = extract_sources(test_video_file, invalid_metadata)

        # Then
        assert isinstance(result, ExtractionResult)
        assert result.success is False
        assert result.extracted_files == []
        assert result.error_message is not None
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


class TestFFmpegIntegration:
    """Test cases for FFmpeg subprocess integration."""

    @patch("subprocess.run")
    def test_ffmpeg_command_construction(
        self, mock_subprocess, test_video_file, single_source_metadata
    ):
        """Test that FFmpeg command is constructed correctly."""
        # Given
        mock_subprocess.return_value = Mock(returncode=0)

        # When
        result = extract_sources(test_video_file, single_source_metadata)

        # Then
        assert result.success is True
        mock_subprocess.assert_called_once()

        # Verify FFmpeg command structure
        call_args = mock_subprocess.call_args[0][
            0
        ]  # First positional argument (command list)
        assert call_args[0] == "ffmpeg"
        assert "-i" in call_args
        assert test_video_file in call_args
        assert "-filter:v" in call_args
        assert "crop=" in " ".join(call_args)

    @patch("subprocess.run")
    def test_ffmpeg_success_creates_output_files(
        self, mock_subprocess, test_video_file, single_source_metadata
    ):
        """Test successful FFmpeg execution creates output files."""
        # Given
        mock_subprocess.return_value = Mock(returncode=0)

        # When
        result = extract_sources(test_video_file, single_source_metadata)

        # Then
        assert result.success is True
        assert len(result.extracted_files) == 1
        assert result.extracted_files[0].endswith("Camera1.mp4")

    @patch("subprocess.run")
    def test_ffmpeg_failure_returns_error(
        self, mock_subprocess, test_video_file, single_source_metadata
    ):
        """Test FFmpeg failure is handled properly."""
        # Given
        mock_subprocess.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=["ffmpeg"], stderr=b"FFmpeg error occurred"
        )

        # When
        result = extract_sources(test_video_file, single_source_metadata)

        # Then
        assert result.success is False
        assert result.extracted_files == []
        assert result.error_message is not None
        assert "ffmpeg" in result.error_message.lower()

    @patch("subprocess.run")
    def test_ffmpeg_multiple_sources_multiple_calls(
        self, mock_subprocess, test_video_file, dual_source_metadata
    ):
        """Test that multiple sources result in multiple FFmpeg calls."""
        # Given
        mock_subprocess.return_value = Mock(returncode=0)

        # When
        result = extract_sources(test_video_file, dual_source_metadata)

        # Then
        assert result.success is True
        assert len(result.extracted_files) == 2
        assert mock_subprocess.call_count == 2

    @patch("subprocess.run")
    @patch("pathlib.Path.mkdir")
    def test_output_directory_creation(
        self, mock_mkdir, mock_subprocess, test_video_file, single_source_metadata
    ):
        """Test that output directory is created."""
        # Given
        mock_subprocess.return_value = Mock(returncode=0)

        # When
        result = extract_sources(test_video_file, single_source_metadata)

        # Then
        assert result.success is True
        mock_mkdir.assert_called_once_with(exist_ok=True)

    @patch("subprocess.run")
    def test_ffmpeg_crop_parameters_correct(
        self,
        mock_subprocess,
        test_video_file,
        complex_source_info,
        standard_canvas_size,
    ):
        """Test that crop parameters are passed correctly to FFmpeg."""
        # Given
        mock_subprocess.return_value = Mock(returncode=0)
        metadata = {
            "canvas_size": standard_canvas_size,
            "sources": {"TestSource": complex_source_info},
        }

        # When
        result = extract_sources(test_video_file, metadata)

        # Then
        assert result.success is True
        call_args = mock_subprocess.call_args[0][0]
        crop_filter = None
        for i, arg in enumerate(call_args):
            if arg == "-filter:v":
                crop_filter = call_args[i + 1]
                break

        assert crop_filter is not None
        assert "crop=1536:648:100:50" in crop_filter  # width:height:x:y
