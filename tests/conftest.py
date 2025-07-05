"""
Shared fixtures for tests.
"""

import pytest


@pytest.fixture
def test_video_file():
    """Fixture for test video file path."""
    return "tests/fixtures/test_recording.mp4"


@pytest.fixture
def basic_source_info():
    """Fixture for basic source information."""
    return {"position": {"x": 0, "y": 0}, "scale": {"x": 1.0, "y": 1.0}}


@pytest.fixture
def positioned_source_info():
    """Fixture for source with non-zero position."""
    return {"position": {"x": 1920, "y": 0}, "scale": {"x": 1.0, "y": 1.0}}


@pytest.fixture
def scaled_source_info():
    """Fixture for source with scaling."""
    return {"position": {"x": 0, "y": 0}, "scale": {"x": 0.5, "y": 0.5}}


@pytest.fixture
def complex_source_info():
    """Fixture for source with position and scale."""
    return {"position": {"x": 100, "y": 50}, "scale": {"x": 0.8, "y": 0.6}}


@pytest.fixture
def single_source_metadata():
    """Fixture for metadata with single source."""
    return {
        "canvas_size": [1920, 1080],
        "sources": {
            "Camera1": {"position": {"x": 0, "y": 0}, "scale": {"x": 1.0, "y": 1.0}}
        },
    }


@pytest.fixture
def dual_source_metadata():
    """Fixture for metadata with two sources."""
    return {
        "canvas_size": [3840, 1080],
        "sources": {
            "Camera1": {"position": {"x": 0, "y": 0}, "scale": {"x": 1.0, "y": 1.0}},
            "Camera2": {"position": {"x": 1920, "y": 0}, "scale": {"x": 1.0, "y": 1.0}},
        },
    }


@pytest.fixture
def empty_sources_metadata():
    """Fixture for metadata with empty sources."""
    return {"canvas_size": [1920, 1080], "sources": {}}


@pytest.fixture
def invalid_metadata():
    """Fixture for invalid metadata (missing sources field)."""
    return {
        "canvas_size": [1920, 1080],
        # Missing sources field
    }


@pytest.fixture
def standard_canvas_size():
    """Fixture for standard canvas size."""
    return [1920, 1080]


@pytest.fixture
def wide_canvas_size():
    """Fixture for wide canvas size."""
    return [3840, 1080]
