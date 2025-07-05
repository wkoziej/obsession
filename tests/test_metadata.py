"""
Test module for metadata functionality.
Following TDD approach - starting with RED phase.
"""
import pytest
from src.core.metadata import create_metadata


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
        sources = [
            {"name": "Camera1", "x": 0, "y": 0, "width": 1920, "height": 1080}
        ]
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
            {"name": "Camera2", "x": 1920, "y": 0, "width": 1920, "height": 1080}
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