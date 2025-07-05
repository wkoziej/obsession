"""
Test module for metadata functionality.
Following TDD approach - starting with RED phase.
"""

import pytest
from src.core.metadata import create_metadata, determine_source_type, validate_metadata


class TestMetadata:
    """Test cases for metadata creation and handling."""

    def test_create_empty_metadata(self):
        """Test creating metadata with no sources."""
        # Given
        sources = []
        canvas_size = (1920, 1080)

        # When
        metadata = create_metadata(sources, canvas_size=canvas_size)

        # Then
        assert metadata["canvas_size"] == [1920, 1080]
        assert metadata["sources"] == {}
        assert "fps" in metadata
        assert "timestamp" in metadata

    def test_create_metadata_with_single_source(self):
        """Test creating metadata with one source."""
        # Given
        sources = [{"name": "Camera1", "x": 0, "y": 0, "width": 1920, "height": 1080}]
        canvas_size = (1920, 1080)

        # When
        metadata = create_metadata(sources, canvas_size=canvas_size)

        # Then
        assert len(metadata["sources"]) == 1
        assert "Camera1" in metadata["sources"]
        assert metadata["sources"]["Camera1"]["position"]["x"] == 0
        assert metadata["sources"]["Camera1"]["position"]["y"] == 0

    def test_create_metadata_with_multiple_sources(self):
        """Test creating metadata with multiple sources."""
        # Given
        sources = [
            {"name": "Camera1", "x": 0, "y": 0, "width": 1920, "height": 1080},
            {"name": "Camera2", "x": 1920, "y": 0, "width": 1920, "height": 1080},
        ]
        canvas_size = (3840, 1080)

        # When
        metadata = create_metadata(sources, canvas_size=canvas_size)

        # Then
        assert len(metadata["sources"]) == 2
        assert metadata["canvas_size"] == [3840, 1080]
        assert metadata["sources"]["Camera1"]["position"]["x"] == 0
        assert metadata["sources"]["Camera2"]["position"]["x"] == 1920

    def test_metadata_validation_invalid_canvas_size(self):
        """Test metadata validation with invalid canvas size."""
        # Given
        sources = []
        canvas_size = (0, 0)  # Invalid

        # When/Then
        with pytest.raises(ValueError, match="Canvas size must be positive"):
            create_metadata(sources, canvas_size=canvas_size)

    def test_metadata_validation_invalid_source_position(self):
        """Test metadata validation with invalid source position."""
        # Given
        sources = [
            {"name": "Camera1", "x": -100, "y": 0, "width": 1920, "height": 1080}
        ]
        canvas_size = (1920, 1080)

        # When/Then
        with pytest.raises(ValueError, match="Source position cannot be negative"):
            create_metadata(sources, canvas_size=canvas_size)


class TestSourceTypeDetection:
    """Test cases for source type detection functionality."""

    def test_determine_video_source_type(self):
        """Test identifying video source by name patterns."""
        # Given
        video_sources = [
            "Urządzenie przechwytujące obraz (V4L2)",
            "Webcam",
            "Camera",
            "Video Capture Device",
            "Kamera",
            "Przechwytywanie wideo",
            "Display Capture",
            "Window Capture",
            "Browser Source",
            "Media Source",
            "Image Source",
            "Color Source",
            "Text (GDI+)",
            "VLC Video Source",
        ]

        # When/Then
        for source_name in video_sources:
            source_type = determine_source_type(source_name)
            assert source_type == "video", (
                f"Expected 'video' for {source_name}, got {source_type}"
            )

    def test_determine_audio_source_type(self):
        """Test identifying audio source by name patterns."""
        # Given
        audio_sources = [
            "Przechwytywanie wejścia dźwięku (PulseAudio)",
            "Audio Input Capture",
            "Microphone",
            "Mikrofon",
            "Audio Output Capture",
            "Desktop Audio",
            "Dźwięk pulpitu",
            "Audio Input",
            "Audio Output",
            "Pulse Audio",
            "ALSA Input",
            "ALSA Output",
        ]

        # When/Then
        for source_name in audio_sources:
            source_type = determine_source_type(source_name)
            assert source_type == "audio", (
                f"Expected 'audio' for {source_name}, got {source_type}"
            )

    def test_determine_unknown_source_type(self):
        """Test handling unknown source types."""
        # Given
        unknown_sources = [
            "Unknown Source",
            "Custom Plugin",
            "Mysterious Device",
            "",
            "Special Effect",
        ]

        # When/Then
        for source_name in unknown_sources:
            source_type = determine_source_type(source_name)
            assert source_type == "unknown", (
                f"Expected 'unknown' for {source_name}, got {source_type}"
            )

    def test_create_metadata_includes_source_types(self):
        """Test that created metadata includes source types."""
        # Given
        sources = [
            {
                "name": "Urządzenie przechwytujące obraz (V4L2)",
                "x": 0,
                "y": 0,
                "width": 640,
                "height": 360,
            },
            {
                "name": "Przechwytywanie wejścia dźwięku (PulseAudio)",
                "x": 0,
                "y": 0,
                "width": 0,
                "height": 0,
            },
        ]
        canvas_size = (1280, 720)

        # When
        metadata = create_metadata(sources, canvas_size=canvas_size)

        # Then
        video_source = metadata["sources"]["Urządzenie przechwytujące obraz (V4L2)"]
        audio_source = metadata["sources"][
            "Przechwytywanie wejścia dźwięku (PulseAudio)"
        ]

        assert "type" in video_source
        assert video_source["type"] == "video"
        assert "type" in audio_source
        assert audio_source["type"] == "audio"

    def test_source_type_case_insensitive(self):
        """Test that source type detection is case insensitive."""
        # Given
        test_cases = [
            ("CAMERA", "video"),
            ("camera", "video"),
            ("Camera", "video"),
            ("MICROPHONE", "audio"),
            ("microphone", "audio"),
            ("Microphone", "audio"),
        ]

        # When/Then
        for source_name, expected_type in test_cases:
            source_type = determine_source_type(source_name)
            assert source_type == expected_type, (
                f"Expected '{expected_type}' for {source_name}, got {source_type}"
            )

    def test_source_type_with_special_characters(self):
        """Test source type detection with special characters and numbers."""
        # Given
        test_cases = [
            ("Camera #1", "video"),
            ("Mikrofon (USB)", "audio"),
            ("Video-Capture_Device", "video"),
            ("Audio.Input.Source", "audio"),
            ("Webcam 2.0", "video"),
        ]

        # When/Then
        for source_name, expected_type in test_cases:
            source_type = determine_source_type(source_name)
            assert source_type == expected_type, (
                f"Expected '{expected_type}' for {source_name}, got {source_type}"
            )


class TestMetadataIntegration:
    """Test cases for metadata integration with other components."""

    def test_metadata_with_types_validates_correctly(self):
        """Test that metadata with source types passes validation."""
        # Given
        sources = [
            {
                "name": "Urządzenie przechwytujące obraz (V4L2)",
                "x": 0,
                "y": 0,
                "width": 640,
                "height": 360,
            },
            {
                "name": "Przechwytywanie wejścia dźwięku (PulseAudio)",
                "x": 0,
                "y": 0,
                "width": 0,
                "height": 0,
            },
        ]
        canvas_size = (1280, 720)

        # When
        metadata = create_metadata(sources, canvas_size=canvas_size)

        # Then
        assert validate_metadata(metadata) is True

        # Verify types are included
        for source_name, source_data in metadata["sources"].items():
            assert "type" in source_data
            assert source_data["type"] in ["video", "audio", "unknown"]

    def test_metadata_roundtrip_preserves_types(self):
        """Test that metadata types are preserved through JSON serialization."""
        # Given
        import json

        sources = [
            {"name": "Camera", "x": 0, "y": 0, "width": 1920, "height": 1080},
            {"name": "Microphone", "x": 0, "y": 0, "width": 0, "height": 0},
        ]
        canvas_size = (1920, 1080)

        # When
        original_metadata = create_metadata(sources, canvas_size=canvas_size)
        json_str = json.dumps(original_metadata)
        restored_metadata = json.loads(json_str)

        # Then
        assert restored_metadata["sources"]["Camera"]["type"] == "video"
        assert restored_metadata["sources"]["Microphone"]["type"] == "audio"
        assert validate_metadata(restored_metadata) is True
