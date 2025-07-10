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

        # Mock keyframe_insert for scene-level keyframes
        self.context.scene.keyframe_insert = Mock()


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


@pytest.fixture
def sample_multi_pip_data():
    """Sample animation data for multi-pip mode with sections, beats, and energy."""
    return {
        "duration": 60.0,
        "tempo": {"bpm": 120.0},
        "animation_events": {
            "beats": [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
            "energy_peaks": [1.2, 2.8, 4.1, 5.5],
            "sections": [
                {"start": 0.0, "end": 15.0, "label": "intro"},
                {"start": 15.0, "end": 30.0, "label": "verse"},
                {"start": 30.0, "end": 45.0, "label": "chorus"},
                {"start": 45.0, "end": 60.0, "label": "outro"},
            ],
        },
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


class TestAnimateEnergyPulse:
    """Tests for animate_energy_pulse function - Phase 3B.1."""

    def test_animate_energy_pulse_basic(self, mock_bpy):
        """Test basic energy pulse animation with transform.scale keyframes."""
        # Create mock video strip with transform property
        strip = Mock()
        strip.name = "Video_1"
        strip.transform = Mock()
        strip.transform.scale_x = 1.0
        strip.transform.scale_y = 1.0
        strip.keyframe_insert = Mock()

        energy_events = {
            "animation_events": {
                "energy_peaks": [1.0, 2.0, 3.0]  # Energy peak times in seconds
            }
        }

        with patch("src.core.blender_vse_script.bpy", mock_bpy):
            from src.core.blender_vse_script import BlenderVSEConfigurator

            configurator = BlenderVSEConfigurator()

            result = configurator._animate_energy_pulse([strip], energy_events)

            assert result is True

    def test_animate_energy_pulse_scale_keyframes(self, mock_bpy):
        """Test that energy pulse creates scale keyframes at energy peaks."""
        strip = Mock()
        strip.name = "Video_1"
        strip.transform = Mock()
        strip.transform.scale_x = 1.0
        strip.transform.scale_y = 1.0

        energy_events = {
            "animation_events": {
                "energy_peaks": [1.0, 2.0]  # Two energy peaks
            }
        }

        with patch("src.core.blender_vse_script.bpy", mock_bpy):
            from src.core.blender_vse_script import BlenderVSEConfigurator

            configurator = BlenderVSEConfigurator()

            result = configurator._animate_energy_pulse([strip], energy_events)

            assert result is True
            # Should have scene-level keyframes for: initial (2) + 2 energy peaks * (scale up + scale down) * 2 axes
            # = 2 + 2 * 2 * 2 = 10 keyframes minimum
            assert mock_bpy.context.scene.keyframe_insert.call_count >= 10

    def test_animate_energy_pulse_no_energy_peaks(self, mock_bpy):
        """Test energy pulse animation with no energy peaks."""
        strip = Mock()
        strip.keyframe_insert = Mock()

        empty_events = {"animation_events": {"energy_peaks": []}}

        with patch("src.core.blender_vse_script.bpy", mock_bpy):
            from src.core.blender_vse_script import BlenderVSEConfigurator

            configurator = BlenderVSEConfigurator()

            result = configurator._animate_energy_pulse([strip], empty_events)

            assert result is True
            # No energy peaks = no keyframes
            assert strip.keyframe_insert.call_count == 0

    def test_animate_energy_pulse_multiple_strips(self, mock_bpy):
        """Test energy pulse animation with multiple video strips."""
        strip1 = Mock()
        strip1.name = "Video_1"
        strip1.transform = Mock()
        strip1.transform.scale_x = 1.0
        strip1.transform.scale_y = 1.0

        strip2 = Mock()
        strip2.name = "Video_2"
        strip2.transform = Mock()
        strip2.transform.scale_x = 1.0
        strip2.transform.scale_y = 1.0

        energy_events = {"animation_events": {"energy_peaks": [1.0, 2.0, 3.0]}}

        with patch("src.core.blender_vse_script.bpy", mock_bpy):
            from src.core.blender_vse_script import BlenderVSEConfigurator

            configurator = BlenderVSEConfigurator()

            result = configurator._animate_energy_pulse([strip1, strip2], energy_events)

            assert result is True
            # 2 strips * (2 initial + 3 energy peaks * 2 keyframes * 2 axes) = 2 * (2 + 12) = 28 keyframes
            assert mock_bpy.context.scene.keyframe_insert.call_count >= 28

    def test_animate_energy_pulse_fps_conversion(self, mock_bpy):
        """Test that energy peak times are correctly converted to frames."""
        strip = Mock()
        strip.name = "Video_1"
        strip.transform = Mock()
        strip.transform.scale_x = 1.0
        strip.transform.scale_y = 1.0

        energy_events = {
            "animation_events": {
                "energy_peaks": [0.5, 1.0, 1.5]  # Times in seconds
            }
        }

        with patch("src.core.blender_vse_script.bpy", mock_bpy):
            from src.core.blender_vse_script import BlenderVSEConfigurator

            configurator = BlenderVSEConfigurator()

            result = configurator._animate_energy_pulse([strip], energy_events)

            assert result is True
            # Should have scene-level keyframes for energy peaks converted to frames (30 FPS)
            # 0.5s = frame 15, 1.0s = frame 30, 1.5s = frame 45
            # 2 initial + 3 peaks * 2 keyframes * 2 axes = 2 + 12 = 14 keyframes
            assert mock_bpy.context.scene.keyframe_insert.call_count >= 14


class TestMultiPipMode:
    """Tests for Multi-PiP Mode animation - Phase 3B.2."""

    def test_animate_multi_pip_function_exists(self, mock_bpy):
        """Test that animate_multi_pip function can be called."""
        with patch("src.core.blender_vse_script.bpy", mock_bpy):
            from src.core.blender_vse_script import BlenderVSEConfigurator

            configurator = BlenderVSEConfigurator()

            # Function should exist (will fail until implemented)
            assert hasattr(configurator, "_animate_multi_pip")

    def test_animate_multi_pip_basic_call(self, mock_bpy, sample_multi_pip_data):
        """Test basic multi-pip animation call with sample data."""
        # Create mock strips (as list, like other animation functions)
        strips = []
        for i in range(1, 5):  # video1, video2, video3, video4
            strip = Mock()
            strip.name = f"Video_{i}"
            strip.blend_alpha = 1.0
            strip.transform = Mock()
            strip.transform.offset_x = 0
            strip.transform.offset_y = 0
            strip.transform.scale_x = 1.0
            strip.transform.scale_y = 1.0
            strips.append(strip)

        with patch("src.core.blender_vse_script.bpy", mock_bpy):
            from src.core.blender_vse_script import BlenderVSEConfigurator

            configurator = BlenderVSEConfigurator()

            result = configurator._animate_multi_pip(strips, sample_multi_pip_data)

            assert result is True

    def test_setup_main_camera_sections_function_exists(self, mock_bpy):
        """Test that _setup_main_camera_sections helper function exists."""
        with patch("src.core.blender_vse_script.bpy", mock_bpy):
            from src.core.blender_vse_script import BlenderVSEConfigurator

            configurator = BlenderVSEConfigurator()

            assert hasattr(configurator, "_setup_main_camera_sections")

    def test_setup_main_camera_sections_basic_logic(
        self, mock_bpy, sample_multi_pip_data
    ):
        """Test main camera section switching logic."""
        # Create mock main camera strips (video1, video2)
        video1 = Mock()
        video1.name = "Video_1"
        video1.blend_alpha = 1.0

        video2 = Mock()
        video2.name = "Video_2"
        video2.blend_alpha = 1.0

        main_cameras = {"Video_1": video1, "Video_2": video2}

        with patch("src.core.blender_vse_script.bpy", mock_bpy):
            from src.core.blender_vse_script import BlenderVSEConfigurator

            configurator = BlenderVSEConfigurator()

            result = configurator._setup_main_camera_sections(
                main_cameras, sample_multi_pip_data
            )

            assert result is True
            # Should have keyframes for section transitions
            assert mock_bpy.context.scene.keyframe_insert.call_count > 0

    def test_setup_corner_pip_effects_function_exists(self, mock_bpy):
        """Test that _setup_corner_pip_effects helper function exists."""
        with patch("src.core.blender_vse_script.bpy", mock_bpy):
            from src.core.blender_vse_script import BlenderVSEConfigurator

            configurator = BlenderVSEConfigurator()

            assert hasattr(configurator, "_setup_corner_pip_effects")

    def test_setup_corner_pip_effects_basic_logic(
        self, mock_bpy, sample_multi_pip_data
    ):
        """Test corner PiP effects (scale + position animations)."""
        # Create mock corner PiP strips (video3, video4, and non-active main cameras)
        video3 = Mock()
        video3.name = "Video_3"
        video3.transform = Mock()
        video3.transform.offset_x = 1680  # Top-right corner
        video3.transform.offset_y = 200
        video3.transform.scale_x = 0.25
        video3.transform.scale_y = 0.25

        video4 = Mock()
        video4.name = "Video_4"
        video4.transform = Mock()
        video4.transform.offset_x = 240  # Top-left corner
        video4.transform.offset_y = 200
        video4.transform.scale_x = 0.25
        video4.transform.scale_y = 0.25

        corner_pips = {"Video_3": video3, "Video_4": video4}

        with patch("src.core.blender_vse_script.bpy", mock_bpy):
            from src.core.blender_vse_script import BlenderVSEConfigurator

            configurator = BlenderVSEConfigurator()

            result = configurator._setup_corner_pip_effects(
                corner_pips, sample_multi_pip_data
            )

            assert result is True
            # Should have keyframes for beat/energy effects on corner PiPs
            assert mock_bpy.context.scene.keyframe_insert.call_count > 0

    def test_multi_pip_layout_calculation(self, mock_bpy):
        """Test multi-pip layout positioning calculation."""
        with patch("src.core.blender_vse_script.bpy", mock_bpy):
            from src.core.blender_vse_script import BlenderVSEConfigurator

            configurator = BlenderVSEConfigurator()

            # Should have method to calculate multi-pip positions
            assert hasattr(configurator, "_calculate_multi_pip_layout")

            layout = configurator._calculate_multi_pip_layout(4)

            # Should return 4 positions for 4 strips
            assert len(layout) == 4

            # Position 0,1: Main cameras (fullscreen)
            assert layout[0] == (960, 540, 1.0)  # video1 - center, full scale
            assert layout[1] == (960, 540, 1.0)  # video2 - center, full scale

            # Position 2,3: Corner PiPs
            assert layout[2][2] == 0.25  # video3 - corner scale
            assert layout[3][2] == 0.25  # video4 - corner scale

    def test_multi_pip_integration_with_vse_configurator(
        self, mock_bpy, sample_multi_pip_data
    ):
        """Test multi-pip mode integration with main VSE configurator."""
        # Create mock sequencer with video strips
        mock_sequencer = Mock()

        # Create mock video strips
        strips = []
        for i in range(1, 5):
            strip = Mock()
            strip.name = f"Video_{i}"
            strip.blend_alpha = 1.0
            strip.transform = Mock()
            strip.transform.offset_x = 0
            strip.transform.offset_y = 0
            strip.transform.scale_x = 1.0
            strip.transform.scale_y = 1.0
            strips.append(strip)

        mock_sequencer.sequences = strips

        with patch("src.core.blender_vse_script.bpy", mock_bpy):
            from src.core.blender_vse_script import BlenderVSEConfigurator

            configurator = BlenderVSEConfigurator()
            configurator.animation_mode = "multi-pip"

            # Mock the audio analysis data loading
            with patch.object(
                configurator, "_load_animation_data", return_value=sample_multi_pip_data
            ):
                result = configurator._apply_animations(mock_sequencer)

            assert result is True
