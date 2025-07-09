# ABOUTME: Tests for Blender VSE animation functions
# ABOUTME: Mock Blender API testing for beat-switch animation MVP

"""
Tests for Blender VSE animation functions.

Phase 3A MVP: Beat Switch Animation
Focus on testing core animation functions with mocked Blender API.
"""

import pytest
import os
import json
from unittest.mock import Mock, patch


# Mock bpy module before importing blender_vse_script
class MockBPY:
    """Mock Blender Python API for testing."""

    def __init__(self):
        self.context = Mock()
        self.ops = Mock()
        self.types = Mock()

        # Mock scene and sequence editor
        self.context.scene = Mock()
        self.context.scene.sequence_editor = Mock()
        self.context.scene.sequence_editor.sequences = []

        # Mock render settings
        self.context.scene.render = Mock()
        self.context.scene.render.fps = 30

        # Mock frame settings
        self.context.scene.frame_start = 1
        self.context.scene.frame_end = 100


# Create a global mock bpy instance
_mock_bpy = MockBPY()

# Patch bpy before importing the module
with patch.dict("sys.modules", {"bpy": _mock_bpy}):
    from src.core.blender_vse_script import BlenderVSEConfigurator


@pytest.fixture
def mock_bpy():
    """Fixture providing mocked Blender API."""
    return MockBPY()


@pytest.fixture
def sample_beat_events():
    """Sample beat events for testing."""
    return {
        "animation_events": {
            "beats": [1.0, 2.0, 3.0, 4.0, 5.0],  # Beat times in seconds
        },
        "tempo": {"bpm": 120.0},
        "duration": 6.0,
    }


@pytest.fixture
def sample_animation_data():
    """Sample animation data focusing on beat events only."""
    return {
        "duration": 10.0,
        "tempo": {"bpm": 120.0},
        "animation_events": {"beats": [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]},
    }


class TestBlenderVSEAnimationsMVP:
    """Test class for Phase 3A MVP - Beat Switch Animation."""

    def test_mock_bpy_setup(self, mock_bpy):
        """Test that mock Blender API is properly set up."""
        # Verify basic mock structure
        assert mock_bpy.context is not None
        assert mock_bpy.context.scene is not None
        assert mock_bpy.context.scene.sequence_editor is not None
        assert mock_bpy.context.scene.render is not None

        # Verify default values
        assert mock_bpy.context.scene.render.fps == 30
        assert mock_bpy.context.scene.frame_start == 1
        assert mock_bpy.context.scene.frame_end == 100


class TestLoadAnimationData:
    """Tests for load_animation_data function - MVP version."""

    def test_load_animation_data_from_env_var(self, sample_beat_events):
        """Test loading animation data from environment variable."""
        # Set up environment variable
        animation_json = json.dumps(sample_beat_events)

        with patch.dict(os.environ, {"BLENDER_VSE_AUDIO_ANALYSIS": animation_json}):
            from src.core.blender_vse_script import load_animation_data

            result = load_animation_data()

            # Verify the result
            assert result == sample_beat_events
            assert "animation_events" in result
            assert "beats" in result["animation_events"]
            assert len(result["animation_events"]["beats"]) == 5

    def test_load_animation_data_empty_env_var(self):
        """Test loading animation data with empty environment variable."""
        with patch.dict(os.environ, {"BLENDER_VSE_AUDIO_ANALYSIS": ""}):
            from src.core.blender_vse_script import load_animation_data

            result = load_animation_data()

            assert result is None

    def test_load_animation_data_invalid_json(self):
        """Test loading animation data with invalid JSON."""
        with patch.dict(os.environ, {"BLENDER_VSE_AUDIO_ANALYSIS": "invalid_json"}):
            from src.core.blender_vse_script import load_animation_data

            result = load_animation_data()

            assert result is None

    def test_load_animation_data_only_beat_events(self, sample_animation_data):
        """Test that only beat events are loaded in MVP version."""
        animation_json = json.dumps(sample_animation_data)

        with patch.dict(os.environ, {"BLENDER_VSE_AUDIO_ANALYSIS": animation_json}):
            from src.core.blender_vse_script import load_animation_data

            result = load_animation_data()

            assert result == sample_animation_data
            assert "beats" in result["animation_events"]
            # MVP: other events should not be included in our filtered data
            assert "energy_peaks" not in result["animation_events"]
            assert "sections" not in result["animation_events"]
            assert "onsets" not in result["animation_events"]


class TestCalculatePipPositions:
    """Tests for calculate_pip_positions function - MVP hardcoded 2x2 grid."""

    def test_calculate_pip_positions_2x2_grid(self):
        """Test hardcoded 2x2 grid positioning for MVP."""
        from src.core.blender_vse_script import calculate_pip_positions

        result = calculate_pip_positions()

        # Expected 2x2 grid positions for 1280x720 resolution
        expected_positions = [
            {"x": 0, "y": 360, "width": 640, "height": 360},  # Top-left
            {"x": 640, "y": 360, "width": 640, "height": 360},  # Top-right
            {"x": 0, "y": 0, "width": 640, "height": 360},  # Bottom-left
            {"x": 640, "y": 0, "width": 640, "height": 360},  # Bottom-right
        ]

        assert result == expected_positions
        assert len(result) == 4  # 2x2 grid = 4 positions

        # Verify all positions are within bounds
        for pos in result:
            assert pos["x"] >= 0
            assert pos["y"] >= 0
            assert pos["width"] > 0
            assert pos["height"] > 0

    def test_calculate_pip_positions_different_resolution(self):
        """Test PiP positions with different resolution."""
        from src.core.blender_vse_script import calculate_pip_positions

        result = calculate_pip_positions(resolution_x=1920, resolution_y=1080)

        # For 1920x1080 resolution
        expected_positions = [
            {"x": 0, "y": 540, "width": 960, "height": 540},
            {"x": 960, "y": 540, "width": 960, "height": 540},
            {"x": 0, "y": 0, "width": 960, "height": 540},
            {"x": 960, "y": 0, "width": 960, "height": 540},
        ]

        assert result == expected_positions
        assert len(result) == 4

    def test_calculate_pip_positions_max_4_videos(self):
        """Test that MVP supports maximum 4 video sources."""
        from src.core.blender_vse_script import calculate_pip_positions

        result = calculate_pip_positions()

        # MVP limitation: maximum 4 positions
        assert len(result) <= 4
        assert len(result) == 4


class TestAnimateBeatSwitch:
    """Tests for animate_beat_switch function - MVP core functionality."""

    def test_animate_beat_switch_basic(self, mock_bpy, sample_beat_events):
        """Test basic beat switch animation with blend_alpha keyframes."""
        # Create mock video strips
        strip1 = Mock()
        strip1.name = "Video_1"
        strip1.blend_alpha = 1.0
        strip1.keyframe_insert = Mock()

        strip2 = Mock()
        strip2.name = "Video_2"
        strip2.blend_alpha = 0.0
        strip2.keyframe_insert = Mock()

        video_strips = [strip1, strip2]

        # Mock bpy.context.scene.render.fps for the function
        with patch("src.core.blender_vse_script.bpy", mock_bpy):
            from src.core.blender_vse_script import animate_beat_switch

            result = animate_beat_switch(video_strips, sample_beat_events)

            assert result is True

    def test_animate_beat_switch_keyframe_insertion(self, mock_bpy):
        """Test that keyframes are inserted at correct beat times."""
        # Mock video strip
        strip = Mock()
        strip.name = "Video_1"
        strip.blend_alpha = 1.0
        strip.keyframe_insert = Mock()

        beat_events = {
            "animation_events": {
                "beats": [1.0, 2.0, 3.0]  # Beat times in seconds
            }
        }

        with patch("src.core.blender_vse_script.bpy", mock_bpy):
            from src.core.blender_vse_script import animate_beat_switch

            result = animate_beat_switch([strip], beat_events)

            assert result is True
            # Verify keyframe_insert was called for each beat + initial frame
            expected_calls = (
                len(beat_events["animation_events"]["beats"]) + 1
            )  # +1 for initial frame
            assert strip.keyframe_insert.call_count == expected_calls

    def test_animate_beat_switch_alternating_alpha(self, mock_bpy):
        """Test that strips alternate visibility on beat events."""
        strip1 = Mock()
        strip1.name = "Video_1"
        strip1.blend_alpha = 1.0
        strip1.keyframe_insert = Mock()

        strip2 = Mock()
        strip2.name = "Video_2"
        strip2.blend_alpha = 0.0
        strip2.keyframe_insert = Mock()

        video_strips = [strip1, strip2]
        beat_events = {"animation_events": {"beats": [1.0, 2.0, 3.0, 4.0]}}

        with patch("src.core.blender_vse_script.bpy", mock_bpy):
            from src.core.blender_vse_script import animate_beat_switch

            result = animate_beat_switch(video_strips, beat_events)

            assert result is True
            # Each strip should have keyframes for initial + each beat
            assert strip1.keyframe_insert.call_count == 5  # 1 initial + 4 beats
            assert strip2.keyframe_insert.call_count == 5  # 1 initial + 4 beats

    def test_animate_beat_switch_no_beats(self, mock_bpy):
        """Test beat switch animation with no beat events."""
        strip = Mock()
        strip.keyframe_insert = Mock()

        empty_events = {"animation_events": {"beats": []}}

        with patch("src.core.blender_vse_script.bpy", mock_bpy):
            from src.core.blender_vse_script import animate_beat_switch

            result = animate_beat_switch([strip], empty_events)

            assert result is True
            # No keyframes should be inserted for beats, but initial frame should be
            assert strip.keyframe_insert.call_count == 0  # No beats = no keyframes

    def test_animate_beat_switch_fps_conversion(self, mock_bpy):
        """Test that beat times are correctly converted to frames."""
        strip = Mock()
        strip.keyframe_insert = Mock()

        beat_events = {
            "animation_events": {
                "beats": [0.5, 1.0, 1.5, 2.0]  # Times in seconds
            }
        }

        with patch("src.core.blender_vse_script.bpy", mock_bpy):
            from src.core.blender_vse_script import animate_beat_switch

            result = animate_beat_switch([strip], beat_events)

            assert result is True
            # Should have keyframes for initial + 4 beats
            assert strip.keyframe_insert.call_count == 5


class TestBlenderVSEConfiguratorIntegration:
    """Tests for BlenderVSEConfigurator integration with animations."""

    def test_apply_animations_beat_switch(self, mock_bpy):
        """Test _apply_animations method with beat-switch mode."""
        # Create mock sequencer with video strips
        mock_sequencer = Mock()

        # Create mock video strips
        strip1 = Mock()
        strip1.blend_alpha = 1.0
        strip1.keyframe_insert = Mock()

        strip2 = Mock()
        strip2.blend_alpha = 0.0
        strip2.keyframe_insert = Mock()

        mock_sequencer.sequences = [strip1, strip2]

        # Mock animation data
        animation_data = {
            "animation_events": {"beats": [1.0, 2.0, 3.0]},
            "duration": 4.0,
            "tempo": {"bpm": 120.0},
        }

        # Test with beat-switch mode
        with patch.dict(
            os.environ,
            {
                "BLENDER_VSE_ANIMATION_MODE": "beat-switch",
                "BLENDER_VSE_BEAT_DIVISION": "8",
                "BLENDER_VSE_AUDIO_ANALYSIS": json.dumps(animation_data),
            },
        ):
            configurator = BlenderVSEConfigurator()

            # Mock bpy.context.scene.render.fps
            mock_bpy.context.scene.render.fps = 30

            result = configurator._apply_animations(mock_sequencer)

            assert result is True
            assert configurator.animation_mode == "beat-switch"
            assert configurator.beat_division == 8

            # Verify keyframes were inserted
            assert strip1.keyframe_insert.call_count >= 3  # At least one per beat
            assert strip2.keyframe_insert.call_count >= 3

    def test_apply_animations_no_data(self, mock_bpy):
        """Test _apply_animations with no animation data."""
        mock_sequencer = Mock()
        mock_sequencer.sequences = []

        with patch.dict(
            os.environ,
            {
                "BLENDER_VSE_ANIMATION_MODE": "beat-switch",
                "BLENDER_VSE_AUDIO_ANALYSIS": "",
            },
        ):
            configurator = BlenderVSEConfigurator()
            result = configurator._apply_animations(mock_sequencer)

            assert result is False

    def test_apply_animations_unsupported_mode(self, mock_bpy):
        """Test _apply_animations with unsupported animation mode."""
        mock_sequencer = Mock()
        mock_sequencer.sequences = []

        animation_data = {"animation_events": {"beats": [1.0, 2.0]}, "duration": 3.0}

        with patch.dict(
            os.environ,
            {
                "BLENDER_VSE_ANIMATION_MODE": "unsupported-mode",
                "BLENDER_VSE_AUDIO_ANALYSIS": json.dumps(animation_data),
            },
        ):
            configurator = BlenderVSEConfigurator()
            result = configurator._apply_animations(mock_sequencer)

            assert result is False
