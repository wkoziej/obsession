"""
Tests for blend_setup CLI.

This module contains unit tests for the blend_setup CLI module.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock

from src.cli.blend_setup import (
    parse_args,
    validate_recording_directory,
    main,
    setup_logging,
)
from src.core.audio_validator import MultipleAudioFilesError


class TestParseArgs:
    """Test cases for parse_args function."""

    def test_parse_args_basic(self):
        """Test parsing basic arguments."""
        with patch("sys.argv", ["blend_setup.py", "/path/to/recording"]):
            args = parse_args()
            assert args.recording_dir == Path("/path/to/recording")
            assert args.verbose is False
            assert args.force is False
            assert args.main_audio is None

    def test_parse_args_all_flags(self):
        """Test parsing all arguments."""
        with patch(
            "sys.argv",
            [
                "blend_setup.py",
                "/path/to/recording",
                "--verbose",
                "--force",
                "--main-audio",
                "audio.mp3",
            ],
        ):
            args = parse_args()
            assert args.recording_dir == Path("/path/to/recording")
            assert args.verbose is True
            assert args.force is True
            assert args.main_audio == "audio.mp3"

    def test_parse_args_short_flags(self):
        """Test parsing short flag versions."""
        with patch("sys.argv", ["blend_setup.py", "/path/to/recording", "-v", "-f"]):
            args = parse_args()
            assert args.verbose is True
            assert args.force is True


class TestValidateRecordingDirectory:
    """Test cases for validate_recording_directory function."""

    def test_validate_nonexistent_directory(self, tmp_path):
        """Test validation with nonexistent directory."""
        nonexistent = tmp_path / "nonexistent"

        with pytest.raises(ValueError, match="Katalog nagrania nie istnieje"):
            validate_recording_directory(nonexistent)

    def test_validate_not_directory(self, tmp_path):
        """Test validation with file instead of directory."""
        file_path = tmp_path / "file.txt"
        file_path.touch()

        with pytest.raises(ValueError, match="Ścieżka nie jest katalogiem"):
            validate_recording_directory(file_path)

    def test_validate_missing_metadata(self, tmp_path):
        """Test validation with missing metadata.json."""
        recording_dir = tmp_path / "recording"
        recording_dir.mkdir()

        with pytest.raises(ValueError, match="Brak pliku metadata.json"):
            validate_recording_directory(recording_dir)

    def test_validate_missing_extracted_directory(self, tmp_path):
        """Test validation with missing extracted directory."""
        recording_dir = tmp_path / "recording"
        recording_dir.mkdir()

        # Create metadata.json
        metadata_file = recording_dir / "metadata.json"
        metadata_file.touch()

        with pytest.raises(ValueError, match="Brak katalogu extracted/"):
            validate_recording_directory(recording_dir)

    def test_validate_extracted_not_directory(self, tmp_path):
        """Test validation with extracted as file instead of directory."""
        recording_dir = tmp_path / "recording"
        recording_dir.mkdir()

        # Create metadata.json
        metadata_file = recording_dir / "metadata.json"
        metadata_file.touch()

        # Create extracted as file
        extracted_file = recording_dir / "extracted"
        extracted_file.touch()

        with pytest.raises(ValueError, match="extracted/ nie jest katalogiem"):
            validate_recording_directory(recording_dir)

    def test_validate_empty_extracted_directory(self, tmp_path):
        """Test validation with empty extracted directory."""
        recording_dir = tmp_path / "recording"
        recording_dir.mkdir()

        # Create metadata.json
        metadata_file = recording_dir / "metadata.json"
        metadata_file.touch()

        # Create empty extracted directory
        extracted_dir = recording_dir / "extracted"
        extracted_dir.mkdir()

        with pytest.raises(ValueError, match="Katalog extracted/ jest pusty"):
            validate_recording_directory(recording_dir)

    def test_validate_valid_directory(self, tmp_path):
        """Test validation with valid directory structure."""
        recording_dir = tmp_path / "recording"
        recording_dir.mkdir()

        # Create metadata.json
        metadata_file = recording_dir / "metadata.json"
        metadata_file.touch()

        # Create extracted directory with files
        extracted_dir = recording_dir / "extracted"
        extracted_dir.mkdir()

        # Add some files
        (extracted_dir / "video.mp4").touch()
        (extracted_dir / "audio.mp3").touch()

        # Should not raise exception
        validate_recording_directory(recording_dir)


class TestSetupLogging:
    """Test cases for setup_logging function."""

    @patch("logging.basicConfig")
    def test_setup_logging_normal(self, mock_basicConfig):
        """Test setup_logging with normal verbosity."""
        setup_logging(verbose=False)

        mock_basicConfig.assert_called_once()
        args, kwargs = mock_basicConfig.call_args
        assert kwargs["level"] == 20  # logging.INFO

    @patch("logging.basicConfig")
    def test_setup_logging_verbose(self, mock_basicConfig):
        """Test setup_logging with verbose mode."""
        setup_logging(verbose=True)

        mock_basicConfig.assert_called_once()
        args, kwargs = mock_basicConfig.call_args
        assert kwargs["level"] == 10  # logging.DEBUG


class TestMain:
    """Test cases for main function."""

    @patch("src.cli.blend_setup.parse_args")
    @patch("src.cli.blend_setup.validate_recording_directory")
    @patch("src.cli.blend_setup.BlenderProjectManager")
    @patch("src.cli.blend_setup.setup_logging")
    @patch("builtins.print")
    def test_main_success(
        self,
        mock_print,
        mock_setup_logging,
        mock_manager_class,
        mock_validate,
        mock_parse_args,
    ):
        """Test successful main execution."""
        # Setup mocks
        mock_args = Mock()
        mock_args.recording_dir = Path("/test/recording")
        mock_args.verbose = False
        mock_args.main_audio = None
        mock_parse_args.return_value = mock_args

        mock_manager = Mock()
        mock_manager.create_vse_project.return_value = Path(
            "/test/recording/blender/project.blend"
        )
        mock_manager_class.return_value = mock_manager

        # Execute
        result = main()

        # Verify
        assert result == 0
        mock_setup_logging.assert_called_once_with(False)
        mock_validate.assert_called_once_with(mock_args.recording_dir)
        mock_manager.create_vse_project.assert_called_once_with(
            mock_args.recording_dir, None
        )
        mock_print.assert_called_once()

    @patch("src.cli.blend_setup.parse_args")
    @patch("src.cli.blend_setup.validate_recording_directory")
    @patch("builtins.print")
    def test_main_validation_error(self, mock_print, mock_validate, mock_parse_args):
        """Test main with validation error."""
        # Setup mocks
        mock_args = Mock()
        mock_args.recording_dir = Path("/test/recording")
        mock_args.verbose = False
        mock_parse_args.return_value = mock_args

        mock_validate.side_effect = ValueError("Validation error")

        # Execute
        result = main()

        # Verify
        assert result == 1
        mock_print.assert_called_once()

    @patch("src.cli.blend_setup.parse_args")
    @patch("src.cli.blend_setup.validate_recording_directory")
    @patch("src.cli.blend_setup.BlenderProjectManager")
    @patch("builtins.print")
    def test_main_audio_validation_error(
        self, mock_print, mock_manager_class, mock_validate, mock_parse_args
    ):
        """Test main with audio validation error."""
        # Setup mocks
        mock_args = Mock()
        mock_args.recording_dir = Path("/test/recording")
        mock_args.verbose = False
        mock_args.main_audio = None
        mock_parse_args.return_value = mock_args

        mock_manager = Mock()
        mock_manager.create_vse_project.side_effect = MultipleAudioFilesError(
            "Multiple audio files"
        )
        mock_manager_class.return_value = mock_manager

        # Execute
        result = main()

        # Verify
        assert result == 1
        mock_print.assert_called_once()

    @patch("src.cli.blend_setup.parse_args")
    @patch("src.cli.blend_setup.validate_recording_directory")
    @patch("src.cli.blend_setup.BlenderProjectManager")
    @patch("builtins.print")
    def test_main_unexpected_error(
        self, mock_print, mock_manager_class, mock_validate, mock_parse_args
    ):
        """Test main with unexpected error."""
        # Setup mocks
        mock_args = Mock()
        mock_args.recording_dir = Path("/test/recording")
        mock_args.verbose = False
        mock_args.main_audio = None
        mock_parse_args.return_value = mock_args

        mock_manager = Mock()
        mock_manager.create_vse_project.side_effect = RuntimeError("Unexpected error")
        mock_manager_class.return_value = mock_manager

        # Execute
        result = main()

        # Verify
        assert result == 1
        mock_print.assert_called_once()
