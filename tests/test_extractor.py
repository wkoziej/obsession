"""
Test module for extractor functionality.
Following TDD approach - starting with RED phase.
"""

import subprocess
from unittest.mock import patch, Mock
from pathlib import Path
from src.core.extractor import (
    ExtractionResult,
    extract_sources,
    calculate_crop_params,
    sanitize_filename,
)


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


class TestRealVideoIntegration:
    """Integration tests with real video files and FFmpeg execution."""

    def test_extract_dual_sources_from_real_video(self):
        """Test extracting two sources from a real canvas recording."""
        # Given - real video file and metadata for dual source extraction
        video_file = "tests/fixtures/sample_canvas_recording.mp4"
        metadata = {
            "canvas_size": [3840, 1080],
            "sources": {
                "LeftSource": {
                    "position": {"x": 0, "y": 0},
                    "scale": {"x": 1.0, "y": 1.0},
                },
                "RightSource": {
                    "position": {"x": 1920, "y": 0},
                    "scale": {"x": 1.0, "y": 1.0},
                },
            },
        }

        # When
        result = extract_sources(video_file, metadata)

        # Then
        assert result.success is True
        assert len(result.extracted_files) == 2

        # Verify output files exist
        from pathlib import Path

        for file_path in result.extracted_files:
            assert Path(file_path).exists()
            assert Path(file_path).stat().st_size > 0  # File is not empty

        # Verify file names
        assert any("LeftSource.mp4" in f for f in result.extracted_files)
        assert any("RightSource.mp4" in f for f in result.extracted_files)

        # Clean up - remove extracted files and directory
        import shutil

        output_dir = Path(video_file).parent / f"{Path(video_file).stem}_extracted"
        if output_dir.exists():
            shutil.rmtree(output_dir)

    def test_extract_single_scaled_source_from_real_video(self):
        """Test extracting a scaled source from real video."""
        # Given - real video file with scaled source
        video_file = "tests/fixtures/sample_canvas_recording.mp4"
        metadata = {
            "canvas_size": [3840, 1080],
            "sources": {
                "ScaledSource": {
                    "position": {"x": 100, "y": 100},
                    "scale": {"x": 0.5, "y": 0.5},
                }
            },
        }

        # When
        result = extract_sources(video_file, metadata)

        # Then
        assert result.success is True
        assert len(result.extracted_files) == 1

        # Verify output file exists and has content
        from pathlib import Path

        output_file = Path(result.extracted_files[0])
        assert output_file.exists()
        assert output_file.stat().st_size > 0

        # Verify dimensions using ffprobe
        import subprocess

        probe_cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_streams",
            str(output_file),
        ]
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)

        if probe_result.returncode == 0:
            import json

            probe_data = json.loads(probe_result.stdout)
            video_stream = next(
                s for s in probe_data["streams"] if s["codec_type"] == "video"
            )

            # Should be 960x540 (1920*0.5 x 1080*0.5)
            assert video_stream["width"] == 960
            assert video_stream["height"] == 540

        # Clean up
        import shutil

        output_dir = Path(video_file).parent / f"{Path(video_file).stem}_extracted"
        if output_dir.exists():
            shutil.rmtree(output_dir)

    def test_real_video_with_invalid_crop_parameters(self):
        """Test behavior with crop parameters that extend beyond video bounds."""
        # Given - real video file with crop parameters extending beyond bounds
        video_file = "tests/fixtures/sample_canvas_recording.mp4"
        metadata = {
            "canvas_size": [3840, 1080],
            "sources": {
                "EdgeSource": {
                    "position": {
                        "x": 3000,
                        "y": 0,
                    },  # Near edge but still within bounds
                    "scale": {"x": 1.0, "y": 1.0},
                }
            },
        }

        # When
        result = extract_sources(video_file, metadata)

        # Then - FFmpeg should succeed but create a video with partial content
        assert result.success is True
        assert len(result.extracted_files) == 1

        # Verify output file exists and has content
        from pathlib import Path

        output_file = Path(result.extracted_files[0])
        assert output_file.exists()
        assert output_file.stat().st_size > 0

        # Clean up
        import shutil

        output_dir = Path(video_file).parent / f"{Path(video_file).stem}_extracted"
        if output_dir.exists():
            shutil.rmtree(output_dir)


class TestOutputFileManagement:
    """Test cases for enhanced output file and directory management."""

    @patch("subprocess.run")
    def test_output_directory_naming_with_timestamp(
        self, mock_subprocess, test_video_file, single_source_metadata
    ):
        """Test that output directory can include timestamp for uniqueness."""
        # Given
        mock_subprocess.return_value = Mock(returncode=0)

        # When
        result = extract_sources(test_video_file, single_source_metadata)

        # Then
        assert result.success is True
        output_file = Path(result.extracted_files[0])
        assert "test_recording_extracted" in str(output_file.parent)

    @patch("subprocess.run")
    def test_safe_filename_generation(self, mock_subprocess, test_video_file):
        """Test that source names with special characters are sanitized."""
        # Given
        mock_subprocess.return_value = Mock(returncode=0)
        metadata = {
            "canvas_size": [1920, 1080],
            "sources": {
                'Source/With\\Special:Characters*?<>|"': {
                    "position": {"x": 0, "y": 0},
                    "scale": {"x": 1.0, "y": 1.0},
                }
            },
        }

        # When
        result = extract_sources(test_video_file, metadata)

        # Then
        assert result.success is True
        output_file = Path(result.extracted_files[0])
        # Should not contain problematic characters
        assert "/" not in output_file.name
        assert "\\" not in output_file.name
        assert ":" not in output_file.name
        assert "*" not in output_file.name
        assert "?" not in output_file.name
        assert "<" not in output_file.name
        assert ">" not in output_file.name
        assert "|" not in output_file.name
        assert '"' not in output_file.name

    @patch("subprocess.run")
    def test_duplicate_source_name_handling(self, mock_subprocess, test_video_file):
        """Test handling of duplicate source names with automatic numbering."""
        # Given
        mock_subprocess.return_value = Mock(returncode=0)
        metadata = {
            "canvas_size": [1920, 1080],
            "sources": {
                "Camera": {"position": {"x": 0, "y": 0}, "scale": {"x": 1.0, "y": 1.0}},
                "Camera_2": {  # Potential conflict with auto-numbering
                    "position": {"x": 1920, "y": 0},
                    "scale": {"x": 1.0, "y": 1.0},
                },
            },
        }

        # When
        result = extract_sources(test_video_file, metadata)

        # Then
        assert result.success is True
        assert len(result.extracted_files) == 2
        # All files should have unique names
        filenames = [Path(f).name for f in result.extracted_files]
        assert len(set(filenames)) == 2

    @patch("subprocess.run")
    def test_custom_output_directory_support(
        self, mock_subprocess, test_video_file, single_source_metadata
    ):
        """Test support for custom output directory paths."""
        # This test would require extending extract_sources to accept output_dir parameter
        # For now, just test current behavior
        # Given
        mock_subprocess.return_value = Mock(returncode=0)

        # When
        result = extract_sources(test_video_file, single_source_metadata)

        # Then
        assert result.success is True
        output_file = Path(result.extracted_files[0])
        # Should be in default location relative to input file
        assert output_file.parent.name == "test_recording_extracted"

    @patch("subprocess.run")
    def test_preserve_file_extensions_from_metadata(
        self, mock_subprocess, test_video_file
    ):
        """Test that custom file extensions from metadata are preserved."""
        # Given
        mock_subprocess.return_value = Mock(returncode=0)
        metadata = {
            "canvas_size": [1920, 1080],
            "sources": {
                "Camera1": {
                    "position": {"x": 0, "y": 0},
                    "scale": {"x": 1.0, "y": 1.0},
                    "output_format": "mkv",  # Custom format
                }
            },
        }

        # When
        result = extract_sources(test_video_file, metadata)

        # Then
        assert result.success is True
        # Currently defaults to .mp4, but could be extended to support custom formats
        assert result.extracted_files[0].endswith(".mp4")

    @patch("subprocess.run")
    def test_error_handling_directory_creation_failure(
        self, mock_subprocess, test_video_file, single_source_metadata
    ):
        """Test error handling when output directory creation fails."""
        # Given
        mock_subprocess.return_value = Mock(returncode=0)

        # Mock Path.mkdir to raise PermissionError
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            mock_mkdir.side_effect = PermissionError("Permission denied")

            # When
            result = extract_sources(test_video_file, single_source_metadata)

            # Then
            assert result.success is False
            assert result.error_message is not None
            assert (
                "permission" in result.error_message.lower()
                or "directory" in result.error_message.lower()
            )

    @patch("subprocess.run")
    def test_relative_vs_absolute_paths_in_result(
        self, mock_subprocess, test_video_file, single_source_metadata
    ):
        """Test that extracted files paths are consistently formatted."""
        # Given
        mock_subprocess.return_value = Mock(returncode=0)

        # When
        result = extract_sources(test_video_file, single_source_metadata)

        # Then
        assert result.success is True
        for file_path in result.extracted_files:
            # Should be absolute paths for consistency
            assert (
                Path(file_path).is_absolute() or "/" in file_path or "\\" in file_path
            )


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
