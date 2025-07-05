"""
Scene analyzer for OBS Studio integration.
This module provides functionality to analyze OBS scenes and extract metadata.
"""

import time
from typing import Dict, List, Any, Optional, Tuple

try:
    import obspython as obs
except ImportError:
    # For testing purposes when OBS is not available
    obs = None


class SceneAnalyzer:
    """Analyzes OBS scenes and extracts source metadata."""
    
    def __init__(self):
        self.current_scene_data = {}
        self.video_info = None
    
    def get_video_info(self) -> Optional[Dict[str, Any]]:
        """Get video information from OBS."""
        if obs is None:
            return None
        
        video_info = obs.obs_video_info()
        obs.obs_get_video_info(video_info)
        
        return {
            "canvas_size": [video_info.base_width, video_info.base_height],
            "output_size": [video_info.output_width, video_info.output_height],
            "fps": video_info.fps_num / video_info.fps_den if video_info.fps_den > 0 else 30.0,
            "format": video_info.output_format,
            "adapter": video_info.adapter,
            "gpu_conversion": video_info.gpu_conversion
        }
    
    def get_current_scene_name(self) -> Optional[str]:
        """Get the name of the current scene."""
        if obs is None:
            return None
        
        current_scene = obs.obs_frontend_get_current_scene()
        if current_scene is None:
            return None
        
        try:
            scene_name = obs.obs_source_get_name(current_scene)
            return scene_name
        finally:
            obs.obs_source_release(current_scene)
    
    def analyze_scene_sources(self, scene_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze scene sources and extract metadata.
        
        Args:
            scene_name: Optional scene name. If None, uses current scene.
            
        Returns:
            Dictionary containing scene metadata
        """
        if obs is None:
            return {}
        
        # Get scene
        if scene_name:
            scene_source = obs.obs_get_source_by_name(scene_name)
            if scene_source is None:
                return {}
            scene = obs.obs_scene_from_source(scene_source)
        else:
            scene_source = obs.obs_frontend_get_current_scene()
            if scene_source is None:
                return {}
            scene = obs.obs_scene_from_source(scene_source)
        
        if scene is None:
            if scene_source:
                obs.obs_source_release(scene_source)
            return {}
        
        try:
            # Get video info
            video_info = self.get_video_info()
            if not video_info:
                return {}
            
            # Get scene name
            actual_scene_name = obs.obs_source_get_name(scene_source)
            
            # Collect sources
            sources = {}
            
            def enum_scene_items(scene_obj, scene_item, data):
                """Callback for enumerating scene items."""
                source = obs.obs_sceneitem_get_source(scene_item)
                if source is None:
                    return True
                
                # Skip if source is not visible
                if not obs.obs_sceneitem_visible(scene_item):
                    return True
                
                # Get source info
                source_name = obs.obs_source_get_name(source)
                source_id = obs.obs_source_get_id(source)
                source_type = obs.obs_source_get_type(source)
                
                # Get position and scale
                pos = obs.vec2()
                scale = obs.vec2()
                bounds = obs.vec2()
                
                obs.obs_sceneitem_get_pos(scene_item, pos)
                obs.obs_sceneitem_get_scale(scene_item, scale)
                obs.obs_sceneitem_get_bounds(scene_item, bounds)
                
                # Get source dimensions
                source_width = obs.obs_source_get_width(source)
                source_height = obs.obs_source_get_height(source)
                
                # Calculate final dimensions
                final_width = int(source_width * scale.x) if source_width > 0 else int(bounds.x)
                final_height = int(source_height * scale.y) if source_height > 0 else int(bounds.y)
                
                # Get transformation info
                transform_info = obs.obs_sceneitem_get_info(scene_item)
                
                # Store source data
                sources[source_name] = {
                    "name": source_name,
                    "id": source_id,
                    "type": source_type,
                    "position": {
                        "x": int(pos.x),
                        "y": int(pos.y)
                    },
                    "scale": {
                        "x": float(scale.x),
                        "y": float(scale.y)
                    },
                    "bounds": {
                        "x": float(bounds.x),
                        "y": float(bounds.y)
                    },
                    "dimensions": {
                        "source_width": source_width,
                        "source_height": source_height,
                        "final_width": final_width,
                        "final_height": final_height
                    },
                    "transform": {
                        "rotation": getattr(transform_info, 'rot', 0.0),
                        "alignment": getattr(transform_info, 'alignment', 0),
                        "bounds_type": getattr(transform_info, 'bounds_type', 0),
                        "bounds_alignment": getattr(transform_info, 'bounds_alignment', 0)
                    },
                    "visible": True,
                    "locked": obs.obs_sceneitem_locked(scene_item)
                }
                
                return True  # Continue enumeration
            
            # Enumerate scene items
            obs.obs_scene_enum_items(scene, enum_scene_items, None)
            
            # Build complete metadata
            metadata = {
                "scene_name": actual_scene_name,
                "timestamp": time.time(),
                "video_info": video_info,
                "sources": sources,
                "total_sources": len(sources),
                "visible_sources": len([s for s in sources.values() if s["visible"]])
            }
            
            return metadata
            
        finally:
            if scene_source:
                obs.obs_source_release(scene_source)
    
    def get_scene_list(self) -> List[str]:
        """Get list of all available scenes."""
        if obs is None:
            return []
        
        scenes = []
        
        def enum_scenes(scene_source, data):
            """Callback for enumerating scenes."""
            scene_name = obs.obs_source_get_name(scene_source)
            scenes.append(scene_name)
            return True
        
        obs.obs_frontend_enum_scenes(enum_scenes, None)
        return scenes
    
    def save_scene_metadata(self, output_path: str, scene_name: Optional[str] = None) -> bool:
        """
        Save scene metadata to file.
        
        Args:
            output_path: Path to save metadata file
            scene_name: Optional scene name. If None, uses current scene.
            
        Returns:
            True if successful, False otherwise
        """
        import json
        import os
        
        try:
            # Analyze scene
            metadata = self.analyze_scene_sources(scene_name)
            if not metadata:
                return False
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving scene metadata: {e}")
            return False
    
    def validate_scene_metadata(self, metadata: Dict[str, Any]) -> bool:
        """
        Validate scene metadata structure.
        
        Args:
            metadata: Metadata dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["scene_name", "timestamp", "video_info", "sources"]
        
        # Check required fields
        for field in required_fields:
            if field not in metadata:
                return False
        
        # Validate video_info
        video_info = metadata["video_info"]
        if not isinstance(video_info, dict):
            return False
        
        required_video_fields = ["canvas_size", "fps"]
        for field in required_video_fields:
            if field not in video_info:
                return False
        
        # Validate canvas_size
        canvas_size = video_info["canvas_size"]
        if not isinstance(canvas_size, list) or len(canvas_size) != 2:
            return False
        
        if not all(isinstance(x, int) and x > 0 for x in canvas_size):
            return False
        
        # Validate sources
        sources = metadata["sources"]
        if not isinstance(sources, dict):
            return False
        
        # Validate each source
        for source_name, source_data in sources.items():
            if not isinstance(source_data, dict):
                return False
            
            required_source_fields = ["name", "position", "dimensions"]
            for field in required_source_fields:
                if field not in source_data:
                    return False
            
            # Validate position
            position = source_data["position"]
            if not isinstance(position, dict):
                return False
            
            if "x" not in position or "y" not in position:
                return False
            
            if not all(isinstance(position[k], int) for k in ["x", "y"]):
                return False
        
        return True


# Convenience functions for backward compatibility
def get_current_scene_metadata() -> Dict[str, Any]:
    """Get metadata for current scene."""
    analyzer = SceneAnalyzer()
    return analyzer.analyze_scene_sources()


def save_current_scene_metadata(output_path: str) -> bool:
    """Save current scene metadata to file."""
    analyzer = SceneAnalyzer()
    return analyzer.save_scene_metadata(output_path) 