"""
Tests for BlenderProjectManager.

This module contains unit tests for the BlenderProjectManager class.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import subprocess

from src.core.blender_project import BlenderProjectManager


class TestBlenderProjectManager:
    """Test cases for BlenderProjectManager class."""

    def test_init_default_executable(self):
        """Test BlenderProjectManager initialization with default executable."""
        manager = BlenderProjectManager()
        assert manager.blender_executable == "blender"

    def test_init_custom_executable(self):
        """Test BlenderProjectManager initialization with custom executable."""
        custom_blender = "/usr/local/bin/blender"
        manager = BlenderProjectManager(custom_blender)
        assert manager.blender_executable == custom_blender

    def test_create_vse_project_invalid_structure(self):
        """Test that create_vse_project raises ValueError for invalid structure."""
        manager = BlenderProjectManager()
        recording_path = Path("/tmp/test_recording")

        with pytest.raises(ValueError, match="Invalid recording structure"):
            manager.create_vse_project(recording_path)

    def test_find_video_files_empty_directory(self, tmp_path):
        """Test find_video_files with empty directory."""
        manager = BlenderProjectManager()
        video_files = manager.find_video_files(tmp_path)
        assert video_files == []

    def test_find_video_files_with_videos(self, tmp_path):
        """Test find_video_files with video files."""
        # Create test video files
        video_files = [
            tmp_path / "camera1.mp4",
            tmp_path / "screen.mkv",
            tmp_path / "audio.mp3",  # Should be ignored
            tmp_path / "document.txt",  # Should be ignored
        ]

        for file_path in video_files:
            file_path.touch()

        manager = BlenderProjectManager()
        found_videos = manager.find_video_files(tmp_path)

        # Should find only video files, sorted by name
        expected = [tmp_path / "camera1.mp4", tmp_path / "screen.mkv"]
        assert found_videos == expected

    def test_find_video_files_sorting(self, tmp_path):
        """Test that find_video_files returns sorted results."""
        # Create video files in non-alphabetical order
        video_files = [
            tmp_path / "zebra.mp4",
            tmp_path / "alpha.mkv",
            tmp_path / "beta.avi",
        ]

        for file_path in video_files:
            file_path.touch()

        manager = BlenderProjectManager()
        found_videos = manager.find_video_files(tmp_path)

        # Should be sorted alphabetically
        expected = [
            tmp_path / "alpha.mkv",
            tmp_path / "beta.avi",
            tmp_path / "zebra.mp4",
        ]
        assert found_videos == expected

    def test_find_video_files_case_insensitive(self, tmp_path):
        """Test that find_video_files handles case insensitive extensions."""
        video_files = [
            tmp_path / "video1.MP4",
            tmp_path / "video2.MKV",
            tmp_path / "video3.AVI",
        ]

        for file_path in video_files:
            file_path.touch()

        manager = BlenderProjectManager()
        found_videos = manager.find_video_files(tmp_path)

        assert len(found_videos) == 3
        assert all(f.suffix.lower() in [".mp4", ".mkv", ".avi"] for f in found_videos)

    @patch("subprocess.run")
    def test_execute_blender_script_success(self, mock_run):
        """Test successful execution of Blender script."""
        mock_run.return_value = Mock(stdout="Success", stderr="")

        manager = BlenderProjectManager()
        script_path = Path("/tmp/test_script.py")
        output_blend = Path("/tmp/test.blend")

        # Should not raise exception
        manager._execute_blender_script(script_path, output_blend)

        # Check subprocess.run was called with correct arguments
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert args[0] == [
            "snap",
            "run",
            "blender",
            "--background",
            "--python",
            str(script_path),
        ]
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True
        assert kwargs["check"] is True

    @patch("subprocess.run")
    def test_execute_blender_script_custom_executable(self, mock_run):
        """Test execution with custom Blender executable."""
        mock_run.return_value = Mock(stdout="Success", stderr="")

        manager = BlenderProjectManager("/usr/local/bin/blender")
        script_path = Path("/tmp/test_script.py")
        output_blend = Path("/tmp/test.blend")

        # Should not raise exception
        manager._execute_blender_script(script_path, output_blend)

        # Check subprocess.run was called with custom executable
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert args[0] == [
            "/usr/local/bin/blender",
            "--background",
            "--python",
            str(script_path),
        ]

    @patch("subprocess.run")
    def test_execute_blender_script_failure(self, mock_run):
        """Test failed execution of Blender script."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "blender", stderr="Blender error"
        )

        manager = BlenderProjectManager()
        script_path = Path("/tmp/test_script.py")
        output_blend = Path("/tmp/test.blend")

        with pytest.raises(RuntimeError, match="Blender execution failed"):
            manager._execute_blender_script(script_path, output_blend)

    def test_create_vse_project_no_video_files(self, sample_recording_structure):
        """Test create_vse_project with no video files."""
        # Remove video files from extracted directory
        extracted_dir = sample_recording_structure / "extracted"
        for file_path in extracted_dir.glob("*.mp4"):
            file_path.unlink()

        manager = BlenderProjectManager()

        with pytest.raises(ValueError, match="No video files found"):
            manager.create_vse_project(sample_recording_structure)

    @patch("subprocess.run")
    def test_create_vse_project_success(self, mock_run, sample_recording_structure):
        """Test successful create_vse_project execution."""
        # Mock successful subprocess execution
        mock_run.return_value = Mock(stdout="Success", stderr="")

        manager = BlenderProjectManager()

        # Should not raise exception and return blend path
        result = manager.create_vse_project(sample_recording_structure)

        # Check result
        expected_blend = (
            sample_recording_structure
            / "blender"
            / f"{sample_recording_structure.name}.blend"
        )
        assert result == expected_blend

        # Check subprocess was called
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[:3] == ["snap", "run", "blender"]
        assert "--background" in args
        assert "--python" in args

    def test_generate_blender_script_content(self, tmp_path):
        """Test _generate_blender_script_content generates valid script."""
        manager = BlenderProjectManager()

        # Create test files
        video_files = [tmp_path / "video1.mp4", tmp_path / "video2.mp4"]
        main_audio = tmp_path / "audio.m4a"
        output_blend = tmp_path / "project.blend"
        render_output = tmp_path / "render.mp4"

        for file_path in video_files + [main_audio]:
            file_path.touch()

        # Generate script content
        script_content = manager._generate_blender_script_content(
            video_files, main_audio, output_blend, render_output, fps=30
        )

        # Verify script contains expected elements
        assert "import bpy" in script_content
        assert "setup_vse_project" in script_content
        assert "sequence_editor_create" in script_content
        assert "resolution_x = 1280" in script_content
        assert "resolution_y = 720" in script_content
        assert str(video_files[0].resolve()) in script_content
        assert str(main_audio.resolve()) in script_content
        assert str(output_blend.resolve()) in script_content

    def test_create_blender_script_creates_file(self, tmp_path):
        """Test that _create_blender_script creates a temporary file."""
        manager = BlenderProjectManager()

        # Create test files
        video_files = [tmp_path / "video1.mp4"]
        main_audio = tmp_path / "audio.m4a"
        output_blend = tmp_path / "project.blend"
        render_output = tmp_path / "render.mp4"

        for file_path in video_files + [main_audio]:
            file_path.touch()

        # Create script
        script_path = manager._create_blender_script(
            video_files, main_audio, output_blend, render_output, fps=30
        )

        # Verify file was created
        assert script_path.exists()
        assert script_path.suffix == ".py"
        assert script_path.name.startswith("blender_vse_")

        # Verify content
        content = script_path.read_text()
        assert "import bpy" in content

        # Clean up
        script_path.unlink()

    def test_read_fps_from_metadata(self, tmp_path):
        """Test reading FPS from metadata.json."""
        manager = BlenderProjectManager()

        # Create test metadata file
        metadata_file = tmp_path / "metadata.json"
        metadata_content = {"fps": 60, "canvas_size": [1920, 1080], "sources": {}}

        import json

        with open(metadata_file, "w") as f:
            json.dump(metadata_content, f)

        # Test reading FPS
        fps = manager._read_fps_from_metadata(metadata_file)
        assert fps == 60

    def test_read_fps_from_metadata_default(self, tmp_path):
        """Test reading FPS with default fallback."""
        manager = BlenderProjectManager()

        # Create test metadata file without fps
        metadata_file = tmp_path / "metadata.json"
        metadata_content = {"canvas_size": [1920, 1080], "sources": {}}

        import json

        with open(metadata_file, "w") as f:
            json.dump(metadata_content, f)

        # Test reading FPS (should default to 30)
        fps = manager._read_fps_from_metadata(metadata_file)
        assert fps == 30

    def test_read_fps_from_metadata_invalid_file(self, tmp_path):
        """Test reading FPS from non-existent file."""
        manager = BlenderProjectManager()

        # Test with non-existent file
        metadata_file = tmp_path / "non_existent.json"
        fps = manager._read_fps_from_metadata(metadata_file)
        assert fps == 30
