"""
Test module for scene analyzer functionality.
Since obspython is not available in test environment, we mock it.
"""
import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock obspython module (reuse from previous test)
mock_obs = Mock()

# Mock vec2 class
class MockVec2:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0

mock_obs.vec2 = MockVec2

# Mock video info class
class MockVideoInfo:
    def __init__(self):
        self.base_width = 1920
        self.base_height = 1080
        self.output_width = 1920
        self.output_height = 1080
        self.fps_num = 30
        self.fps_den = 1
        self.output_format = 0
        self.adapter = 0
        self.gpu_conversion = True

mock_obs.obs_video_info = MockVideoInfo

# Mock transform info
class MockTransformInfo:
    def __init__(self):
        self.rot = 0.0
        self.alignment = 0
        self.bounds_type = 0
        self.bounds_alignment = 0

# Add mock to sys.modules before importing our module
sys.modules['obspython'] = mock_obs

# Now import our module
from src.obs_integration.scene_analyzer import (
    SceneAnalyzer, get_current_scene_metadata, save_current_scene_metadata
)


class TestSceneAnalyzer:
    """Test cases for scene analyzer functionality."""
    
    def test_scene_analyzer_init(self):
        """Test scene analyzer initialization."""
        analyzer = SceneAnalyzer()
        assert analyzer.current_scene_data == {}
        assert analyzer.video_info is None
    
    def test_get_video_info(self):
        """Test getting video info from OBS."""
        analyzer = SceneAnalyzer()
        
        # Mock OBS functions
        mock_obs.obs_get_video_info = Mock()
        
        # Call get_video_info
        video_info = analyzer.get_video_info()
        
        # Verify structure
        assert video_info is not None
        assert "canvas_size" in video_info
        assert "fps" in video_info
        assert "output_size" in video_info
        assert video_info["canvas_size"] == [1920, 1080]
        assert video_info["fps"] == 30.0
    
    def test_get_current_scene_name(self):
        """Test getting current scene name."""
        analyzer = SceneAnalyzer()
        
        # Mock OBS functions
        mock_scene = Mock()
        mock_obs.obs_frontend_get_current_scene = Mock(return_value=mock_scene)
        mock_obs.obs_source_get_name = Mock(return_value="Test Scene")
        mock_obs.obs_source_release = Mock()
        
        # Call get_current_scene_name
        scene_name = analyzer.get_current_scene_name()
        
        # Verify
        assert scene_name == "Test Scene"
        mock_obs.obs_frontend_get_current_scene.assert_called_once()
        mock_obs.obs_source_get_name.assert_called_once_with(mock_scene)
        mock_obs.obs_source_release.assert_called_once_with(mock_scene)
    
    def test_get_current_scene_name_no_scene(self):
        """Test getting current scene name when no scene exists."""
        analyzer = SceneAnalyzer()
        
        # Mock OBS functions
        mock_obs.obs_frontend_get_current_scene = Mock(return_value=None)
        
        # Call get_current_scene_name
        scene_name = analyzer.get_current_scene_name()
        
        # Verify
        assert scene_name is None
    
    def test_analyze_scene_sources_empty(self):
        """Test analyzing scene with no sources."""
        analyzer = SceneAnalyzer()
        
        # Mock OBS functions
        mock_scene_source = Mock()
        mock_scene = Mock()
        mock_obs.obs_frontend_get_current_scene = Mock(return_value=mock_scene_source)
        mock_obs.obs_scene_from_source = Mock(return_value=mock_scene)
        mock_obs.obs_source_get_name = Mock(return_value="Empty Scene")
        mock_obs.obs_source_release = Mock()
        mock_obs.obs_scene_enum_items = Mock()
        mock_obs.obs_get_video_info = Mock()
        
        # Call analyze_scene_sources
        metadata = analyzer.analyze_scene_sources()
        
        # Verify structure
        assert isinstance(metadata, dict)
        assert "scene_name" in metadata
        assert "timestamp" in metadata
        assert "video_info" in metadata
        assert "sources" in metadata
        assert "total_sources" in metadata
        assert metadata["scene_name"] == "Empty Scene"
        assert metadata["total_sources"] == 0
    
    def test_analyze_scene_sources_with_sources(self):
        """Test analyzing scene with sources."""
        analyzer = SceneAnalyzer()
        
        # Mock scene and sources
        mock_scene_source = Mock()
        mock_scene = Mock()
        mock_source = Mock()
        
        mock_obs.obs_frontend_get_current_scene = Mock(return_value=mock_scene_source)
        mock_obs.obs_scene_from_source = Mock(return_value=mock_scene)
        mock_obs.obs_source_get_name = Mock(return_value="Test Scene")
        mock_obs.obs_source_release = Mock()
        mock_obs.obs_get_video_info = Mock()
        
        # Mock source enumeration
        def mock_enum_items(scene, callback, data):
            # Create mock scene item
            mock_scene_item = Mock()
            
            # Mock source functions
            mock_obs.obs_sceneitem_get_source = Mock(return_value=mock_source)
            mock_obs.obs_sceneitem_visible = Mock(return_value=True)
            mock_obs.obs_source_get_name = Mock(return_value="Camera1")
            mock_obs.obs_source_get_id = Mock(return_value="camera_source")
            mock_obs.obs_source_get_type = Mock(return_value=1)
            mock_obs.obs_source_get_width = Mock(return_value=1920)
            mock_obs.obs_source_get_height = Mock(return_value=1080)
            mock_obs.obs_sceneitem_locked = Mock(return_value=False)
            
            # Mock position and scale
            mock_obs.obs_sceneitem_get_pos = Mock()
            mock_obs.obs_sceneitem_get_scale = Mock()
            mock_obs.obs_sceneitem_get_bounds = Mock()
            mock_obs.obs_sceneitem_get_info = Mock(return_value=MockTransformInfo())
            
            # Call the callback
            callback(scene, mock_scene_item, data)
        
        mock_obs.obs_scene_enum_items = Mock(side_effect=mock_enum_items)
        
        # Call analyze_scene_sources
        metadata = analyzer.analyze_scene_sources()
        
        # Verify structure
        assert isinstance(metadata, dict)
        assert "sources" in metadata
        assert metadata["total_sources"] == 1
        assert "Camera1" in metadata["sources"]
        
        # Verify source data
        camera_source = metadata["sources"]["Camera1"]
        assert camera_source["name"] == "Camera1"
        assert camera_source["id"] == "camera_source"
        assert "position" in camera_source
        assert "dimensions" in camera_source
        assert camera_source["visible"] is True
    
    def test_get_scene_list(self):
        """Test getting list of scenes."""
        analyzer = SceneAnalyzer()
        
        # Mock scene enumeration
        def mock_enum_scenes(callback, data):
            # Create mock scenes
            mock_scene1 = Mock()
            mock_scene2 = Mock()
            
            mock_obs.obs_source_get_name = Mock(side_effect=["Scene 1", "Scene 2"])
            
            # Call callback for each scene
            callback(mock_scene1, data)
            callback(mock_scene2, data)
        
        mock_obs.obs_frontend_enum_scenes = Mock(side_effect=mock_enum_scenes)
        
        # Call get_scene_list
        scenes = analyzer.get_scene_list()
        
        # Verify
        assert len(scenes) == 2
        assert "Scene 1" in scenes
        assert "Scene 2" in scenes
    
    def test_save_scene_metadata(self):
        """Test saving scene metadata to file."""
        analyzer = SceneAnalyzer()
        
        # Mock analyze_scene_sources
        mock_metadata = {
            "scene_name": "Test Scene",
            "timestamp": 1234567890.0,
            "video_info": {"canvas_size": [1920, 1080], "fps": 30.0},
            "sources": {},
            "total_sources": 0
        }
        
        with patch.object(analyzer, 'analyze_scene_sources', return_value=mock_metadata):
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                temp_path = f.name
            
            try:
                # Call save_scene_metadata
                result = analyzer.save_scene_metadata(temp_path)
                
                # Verify
                assert result is True
                assert os.path.exists(temp_path)
                
                # Verify file content
                with open(temp_path, 'r') as f:
                    saved_data = json.load(f)
                
                assert saved_data["scene_name"] == "Test Scene"
                assert saved_data["total_sources"] == 0
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
    
    def test_save_scene_metadata_no_metadata(self):
        """Test saving scene metadata when no metadata available."""
        analyzer = SceneAnalyzer()
        
        # Mock analyze_scene_sources to return empty
        with patch.object(analyzer, 'analyze_scene_sources', return_value={}):
            # Call save_scene_metadata
            result = analyzer.save_scene_metadata("/tmp/test.json")
            
            # Verify
            assert result is False
    
    def test_validate_scene_metadata_valid(self):
        """Test validating valid scene metadata."""
        analyzer = SceneAnalyzer()
        
        valid_metadata = {
            "scene_name": "Test Scene",
            "timestamp": 1234567890.0,
            "video_info": {
                "canvas_size": [1920, 1080],
                "fps": 30.0
            },
            "sources": {
                "Camera1": {
                    "name": "Camera1",
                    "position": {"x": 0, "y": 0},
                    "dimensions": {"source_width": 1920, "source_height": 1080}
                }
            }
        }
        
        # Call validate_scene_metadata
        result = analyzer.validate_scene_metadata(valid_metadata)
        
        # Verify
        assert result is True
    
    def test_validate_scene_metadata_invalid_missing_field(self):
        """Test validating invalid scene metadata with missing field."""
        analyzer = SceneAnalyzer()
        
        invalid_metadata = {
            "scene_name": "Test Scene",
            # Missing timestamp, video_info, sources
        }
        
        # Call validate_scene_metadata
        result = analyzer.validate_scene_metadata(invalid_metadata)
        
        # Verify
        assert result is False
    
    def test_validate_scene_metadata_invalid_canvas_size(self):
        """Test validating invalid scene metadata with bad canvas size."""
        analyzer = SceneAnalyzer()
        
        invalid_metadata = {
            "scene_name": "Test Scene",
            "timestamp": 1234567890.0,
            "video_info": {
                "canvas_size": [0, 0],  # Invalid
                "fps": 30.0
            },
            "sources": {}
        }
        
        # Call validate_scene_metadata
        result = analyzer.validate_scene_metadata(invalid_metadata)
        
        # Verify
        assert result is False
    
    def test_convenience_functions(self):
        """Test convenience functions."""
        # Mock SceneAnalyzer
        with patch('src.obs_integration.scene_analyzer.SceneAnalyzer') as mock_analyzer_class:
            mock_analyzer = Mock()
            mock_analyzer_class.return_value = mock_analyzer
            mock_analyzer.analyze_scene_sources.return_value = {"test": "data"}
            mock_analyzer.save_scene_metadata.return_value = True
            
            # Test get_current_scene_metadata
            result = get_current_scene_metadata()
            assert result == {"test": "data"}
            mock_analyzer.analyze_scene_sources.assert_called_once()
            
            # Test save_current_scene_metadata
            result = save_current_scene_metadata("/tmp/test.json")
            assert result is True
            mock_analyzer.save_scene_metadata.assert_called_once_with("/tmp/test.json") 