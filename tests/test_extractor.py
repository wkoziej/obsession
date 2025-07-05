"""
Tests for source extraction functionality.
"""

import tempfile
import os
from unittest.mock import patch
from src.core.extractor import (
    ExtractionResult,
    calculate_crop_params,
    sanitize_filename,
    SourceExtractor,
)


class TestExtractionResult:
    """Test cases for ExtractionResult class."""

    def test_extraction_result_creation_default(self):
        """Test creating ExtractionResult with default values."""
        # When
        result = ExtractionResult()

        # Then
        assert result.success is False
        assert result.extracted_files == []
        assert result.error_message is None

    def test_extraction_result_creation_with_success(self):
        """Test creating ExtractionResult with success."""
        # Given
        files = ["file1.mp4", "file2.mp4"]

        # When
        result = ExtractionResult(success=True, extracted_files=files)

        # Then
        assert result.success is True
        assert result.extracted_files == files
        assert result.error_message is None

    def test_extraction_result_creation_with_error(self):
        """Test creating ExtractionResult with error."""
        # Given
        error_msg = "FFmpeg failed"

        # When
        result = ExtractionResult(success=False, error_message=error_msg)

        # Then
        assert result.success is False
        assert result.extracted_files == []
        assert result.error_message == error_msg

    def test_extraction_result_str_representation(self):
        """Test string representation of ExtractionResult."""
        # Given
        result = ExtractionResult(
            success=True, extracted_files=["file1.mp4", "file2.mp4"]
        )

        # When
        str_repr = str(result)

        # Then
        assert "ExtractionResult(success=True" in str_repr
        assert "extracted_files=2" in str_repr


class TestCropParams:
    """Test cases for crop parameter calculation."""

    def test_calculate_crop_params_basic(self, basic_source_info, standard_canvas_size):
        """Test basic crop parameter calculation."""
        # When
        params = calculate_crop_params(basic_source_info, standard_canvas_size)

        # Then
        assert params["x"] == 0
        assert params["y"] == 0
        assert params["width"] == 1920
        assert params["height"] == 1080

    def test_calculate_crop_params_with_position(
        self, positioned_source_info, wide_canvas_size
    ):
        """Test crop parameters with non-zero position."""
        # When
        params = calculate_crop_params(positioned_source_info, wide_canvas_size)

        # Then
        assert params["x"] == 1920
        assert params["y"] == 0
        assert params["width"] == 1920
        assert params["height"] == 1080

    def test_calculate_crop_params_with_scale(
        self, scaled_source_info, standard_canvas_size
    ):
        """Test crop parameters with scaling."""
        # When
        params = calculate_crop_params(scaled_source_info, standard_canvas_size)

        # Then
        assert params["x"] == 0
        assert params["y"] == 0
        assert params["width"] == 960  # 1920 * 0.5
        assert params["height"] == 540  # 1080 * 0.5

    def test_calculate_crop_params_complex(
        self, complex_source_info, standard_canvas_size
    ):
        """Test crop parameters with both position and scale."""
        # When
        params = calculate_crop_params(complex_source_info, standard_canvas_size)

        # Then
        assert params["x"] == 100
        assert params["y"] == 50
        assert params["width"] == 1536  # 1920 * 0.8
        assert params["height"] == 648  # 1080 * 0.6


class TestSanitizeFilename:
    """Test cases for filename sanitization."""

    def test_sanitize_filename_basic(self):
        """Test basic filename sanitization."""
        # Given
        filename = "Camera1"

        # When
        result = sanitize_filename(filename)

        # Then
        assert result == "Camera1"

    def test_sanitize_filename_with_special_characters(self):
        """Test sanitization of filename with special characters."""
        # Given
        filename = 'Source/With\\Special:Characters*?<>|"'

        # When
        result = sanitize_filename(filename)

        # Then
        assert result == "Source_With_Special_Characters"
        assert "/" not in result
        assert "\\" not in result
        assert ":" not in result
        assert "*" not in result
        assert "?" not in result
        assert "<" not in result
        assert ">" not in result
        assert "|" not in result
        assert '"' not in result

    def test_sanitize_filename_multiple_underscores(self):
        """Test that multiple consecutive underscores are collapsed."""
        # Given
        filename = "Source///With\\\\\\Many:::Special"

        # When
        result = sanitize_filename(filename)

        # Then
        assert result == "Source_With_Many_Special"

    def test_sanitize_filename_leading_trailing_underscores(self):
        """Test removal of leading and trailing underscores."""
        # Given
        filename = "/Source_Name/"

        # When
        result = sanitize_filename(filename)

        # Then
        assert result == "Source_Name"

    def test_sanitize_filename_empty_after_sanitization(self):
        """Test handling of filename that becomes empty after sanitization."""
        # Given
        filename = "///**???"

        # When
        result = sanitize_filename(filename)

        # Then
        assert result == "source"

    def test_sanitize_filename_only_special_characters(self):
        """Test sanitization of filename with only special characters."""
        # Given
        filename = '<>|*?"'

        # When
        result = sanitize_filename(filename)

        # Then
        assert result == "source"


class TestExtractorWithCapabilities:
    """Test extractor with new has_audio/has_video logic."""

    def test_extractor_processes_video_sources(self):
        """Test that extractor processes sources with has_video=True."""
        metadata = {
            "canvas_size": [1920, 1080],
            "sources": {
                "Camera": {
                    "has_audio": True,
                    "has_video": True,
                    "position": {"x": 0, "y": 0},
                },
                "Microphone": {"has_audio": True, "has_video": False},
                "TextSource": {
                    "has_audio": False,
                    "has_video": True,
                    "position": {"x": 100, "y": 100},
                },
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = os.path.join(temp_dir, "input.mkv")
            output_dir = os.path.join(temp_dir, "output")
            os.makedirs(output_dir)

            # Create dummy input file
            with open(input_file, "w") as f:
                f.write("dummy")

            extractor = SourceExtractor(input_file, metadata, output_dir)

            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                result = extractor.extract_sources()

                # Should call FFmpeg for:
                # Camera: video + audio = 2 calls
                # Microphone: audio only = 1 call
                # TextSource: video only = 1 call
                # Total: 4 calls
                assert mock_run.call_count == 4
                assert result.success is True
                assert len(result.extracted_files) == 4

                # Check that video sources were processed
                calls = [call.args[0] for call in mock_run.call_args_list]
                video_outputs = [
                    call for call in calls if any(".mp4" in arg for arg in call)
                ]
                audio_outputs = [
                    call for call in calls if any(".m4a" in arg for arg in call)
                ]
                assert len(video_outputs) == 2  # Camera, TextSource
                assert len(audio_outputs) == 2  # Camera, Microphone

    def test_extractor_extracts_audio_tracks(self):
        """Test that extractor extracts audio tracks from audio sources."""
        metadata = {
            "canvas_size": [1920, 1080],
            "sources": {
                "Camera": {
                    "has_audio": True,
                    "has_video": True,
                    "position": {"x": 0, "y": 0},
                },
                "Microphone": {"has_audio": True, "has_video": False},
                "ImageSource": {
                    "has_audio": False,
                    "has_video": True,
                    "position": {"x": 100, "y": 100},
                },
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = os.path.join(temp_dir, "input.mkv")
            output_dir = os.path.join(temp_dir, "output")
            os.makedirs(output_dir)

            with open(input_file, "w") as f:
                f.write("dummy")

            extractor = SourceExtractor(input_file, metadata, output_dir)

            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                result = extractor.extract_sources()

                # Check that audio tracks were extracted
                calls = [call.args[0] for call in mock_run.call_args_list]
                audio_outputs = [
                    call
                    for call in calls
                    if any((".wav" in arg or ".m4a" in arg) for arg in call)
                ]
                assert len(audio_outputs) == 2  # Camera and Microphone have audio
                assert result.success is True

    def test_extractor_skips_sources_without_capabilities(self):
        """Test that sources without audio/video are skipped."""
        metadata = {
            "canvas_size": [1920, 1080],
            "sources": {
                "ValidCamera": {
                    "has_audio": True,
                    "has_video": True,
                    "position": {"x": 0, "y": 0},
                },
                "EmptySource": {"has_audio": False, "has_video": False},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = os.path.join(temp_dir, "input.mkv")
            output_dir = os.path.join(temp_dir, "output")
            os.makedirs(output_dir)

            with open(input_file, "w") as f:
                f.write("dummy")

            extractor = SourceExtractor(input_file, metadata, output_dir)

            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                result = extractor.extract_sources()

                # Should only process ValidCamera (both video and audio)
                assert mock_run.call_count == 2  # 1 video + 1 audio
                assert result.success is True
                assert len(result.extracted_files) == 2

    def test_extractor_handles_video_only_sources(self):
        """Test that video-only sources generate only video files."""
        metadata = {
            "canvas_size": [1920, 1080],
            "sources": {
                "ImageSource": {
                    "has_audio": False,
                    "has_video": True,
                    "position": {"x": 0, "y": 0},
                }
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = os.path.join(temp_dir, "input.mkv")
            output_dir = os.path.join(temp_dir, "output")
            os.makedirs(output_dir)

            with open(input_file, "w") as f:
                f.write("dummy")

            extractor = SourceExtractor(input_file, metadata, output_dir)

            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                result = extractor.extract_sources()

                # Should only call FFmpeg once for video
                assert mock_run.call_count == 1
                assert result.success is True
                assert len(result.extracted_files) == 1
                assert result.extracted_files[0].endswith(".mp4")

    def test_extractor_handles_audio_only_sources(self):
        """Test that audio-only sources generate only audio files."""
        metadata = {
            "canvas_size": [1920, 1080],
            "sources": {"Microphone": {"has_audio": True, "has_video": False}},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = os.path.join(temp_dir, "input.mkv")
            output_dir = os.path.join(temp_dir, "output")
            os.makedirs(output_dir)

            with open(input_file, "w") as f:
                f.write("dummy")

            extractor = SourceExtractor(input_file, metadata, output_dir)

            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                result = extractor.extract_sources()

                # Should only call FFmpeg once for audio
                assert mock_run.call_count == 1
                assert result.success is True
                assert len(result.extracted_files) == 1
                assert result.extracted_files[0].endswith(".m4a")
