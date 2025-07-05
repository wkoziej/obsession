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
import pytest


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


class TestCropParamsEdgeCases:
    """Test edge cases for crop parameter calculation."""

    def test_upscaled_source_exceeds_original_dimensions(self):
        """Test source scaled up beyond original dimensions."""
        # Given - source upscaled beyond original size (like our real case)
        source_info = {
            "position": {"x": 0, "y": 0},
            "scale": {"x": 1.053125, "y": 1.0527777},  # >1.0 scale
            "dimensions": {
                "source_width": 640,
                "source_height": 360,
                "final_width": 674,  # Bigger than source!
                "final_height": 378,
            },
        }
        canvas_size = [1280, 720]

        # When
        params = calculate_crop_params(source_info, canvas_size)

        # Then - crop should be limited to source dimensions
        assert params["width"] == 640  # Limited to source_width
        assert params["height"] == 360  # Limited to source_height
        assert params["x"] == 0
        assert params["y"] == 0

    def test_source_with_zero_dimensions(self):
        """Test source with 0x0 dimensions (audio-only)."""
        # Given - audio-only source
        source_info = {
            "position": {"x": 0, "y": 0},
            "scale": {"x": 1.0, "y": 1.0},
            "dimensions": {
                "source_width": 0,
                "source_height": 0,
                "final_width": 0,
                "final_height": 0,
            },
        }
        canvas_size = [1280, 720]

        # When/Then - should raise ValueError
        with pytest.raises(ValueError, match="Source has invalid dimensions: 0x0"):
            calculate_crop_params(source_info, canvas_size)

    def test_source_positioned_outside_canvas(self):
        """Test source positioned outside canvas bounds."""
        # Given - source positioned beyond canvas
        source_info = {
            "position": {"x": 1500, "y": 800},  # Outside 1280x720 canvas
            "scale": {"x": 1.0, "y": 1.0},
            "dimensions": {
                "source_width": 640,
                "source_height": 360,
                "final_width": 640,
                "final_height": 360,
            },
        }
        canvas_size = [1280, 720]

        # When
        params = calculate_crop_params(source_info, canvas_size)

        # Then - position remains but crop is minimal (canvas bounds exceeded)
        assert params["x"] == 1500  # Position unchanged
        assert params["y"] == 800  # Position unchanged
        assert params["width"] == 1  # Minimal crop (canvas exceeded)
        assert params["height"] == 1  # Minimal crop (canvas exceeded)

    def test_source_partially_outside_canvas(self):
        """Test source partially outside canvas bounds."""
        # Given - source extends beyond canvas
        source_info = {
            "position": {"x": 900, "y": 400},  # Partially outside 1280x720
            "scale": {"x": 1.0, "y": 1.0},
            "dimensions": {
                "source_width": 640,
                "source_height": 360,
                "final_width": 640,
                "final_height": 360,
            },
        }
        canvas_size = [1280, 720]

        # When
        params = calculate_crop_params(source_info, canvas_size)

        # Then - should be cropped to fit canvas
        assert params["x"] == 900
        assert params["y"] == 400
        # 900 + 640 > 1280, so width = 1280 - 900 = 380
        # 400 + 360 > 720, so height = 720 - 400 = 320
        # But then limited by source bounds: min(380, 640) and min(320, 360)
        assert params["width"] == 380  # 1280 - 900
        assert params["height"] == 320  # 720 - 400

    def test_downscaled_source(self):
        """Test source scaled down (scale < 1.0)."""
        # Given - source scaled down
        source_info = {
            "position": {"x": 606, "y": 330},
            "scale": {"x": 0.503125, "y": 0.5027777},  # <1.0 scale
            "dimensions": {
                "source_width": 1920,
                "source_height": 1080,
                "final_width": 966,  # 1920 * 0.503125
                "final_height": 543,  # 1080 * 0.5027777
            },
        }
        canvas_size = [1280, 720]

        # When
        params = calculate_crop_params(source_info, canvas_size)

        # Then
        assert params["x"] == 606
        assert params["y"] == 330
        # Desired: 1920 * 0.503125 = 966, but limited by canvas: 1280 - 606 = 674
        assert params["width"] == 674  # Limited by canvas bounds
        assert params["height"] == 390  # Limited by canvas bounds (720 - 330)

    def test_negative_position(self):
        """Test source with negative position."""
        # Given - source with negative position
        source_info = {
            "position": {"x": -100, "y": -50},
            "scale": {"x": 1.0, "y": 1.0},
            "dimensions": {
                "source_width": 640,
                "source_height": 360,
                "final_width": 640,
                "final_height": 360,
            },
        }
        canvas_size = [1280, 720]

        # When
        params = calculate_crop_params(source_info, canvas_size)

        # Then - negative positions should be clamped to 0
        assert params["x"] == 0
        assert params["y"] == 0
        assert params["width"] == 640
        assert params["height"] == 360

    def test_source_with_missing_dimensions(self):
        """Test source with missing dimensions data."""
        # Given - source without dimensions (fallback scenario)
        source_info = {
            "position": {"x": 0, "y": 0},
            "scale": {"x": 1.0, "y": 1.0},
            # Missing dimensions field
        }
        canvas_size = [1280, 720]

        # When
        params = calculate_crop_params(source_info, canvas_size)

        # Then - should use fallback dimensions
        assert params["width"] == 1280  # Limited by canvas
        assert params["height"] == 720  # Limited by canvas
        assert params["x"] == 0
        assert params["y"] == 0
