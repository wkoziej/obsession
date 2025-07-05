"""
Metadata management for OBS Canvas Recording.
This module handles creation and manipulation of recording metadata.
"""
import time
from typing import Dict, List, Tuple, Any


def create_metadata(sources: List[Dict[str, Any]], 
                   canvas_size: Tuple[int, int] = (1920, 1080),
                   fps: float = 30.0) -> Dict[str, Any]:
    """
    Create metadata for OBS canvas recording.
    
    Args:
        sources: List of source information dictionaries
        canvas_size: Canvas dimensions as (width, height)
        fps: Frames per second for recording
        
    Returns:
        Dictionary containing recording metadata
        
    Raises:
        ValueError: If canvas size is invalid or source positions are negative
    """
    # Validate canvas size
    if canvas_size[0] <= 0 or canvas_size[1] <= 0:
        raise ValueError("Canvas size must be positive")
    
    # Convert sources list to dictionary format
    sources_dict = {}
    for i, source in enumerate(sources):
        # Validate source position
        if source.get('x', 0) < 0 or source.get('y', 0) < 0:
            raise ValueError("Source position cannot be negative")
        
        # Use name as key, fallback to source_id
        source_id = source.get('name', source.get('id', f'source_{i}'))
        
        # Transform source data to match expected format
        source_data = source.copy()
        if 'x' in source and 'y' in source:
            source_data['position'] = {
                'x': source['x'],
                'y': source['y']
            }
        
        sources_dict[source_id] = source_data
    
    return {
        "canvas_size": list(canvas_size),
        "sources": sources_dict,
        "fps": fps,
        "timestamp": time.time()
    }


def validate_metadata(metadata: Dict[str, Any]) -> bool:
    """
    Validate metadata structure.
    
    Args:
        metadata: Metadata dictionary to validate
        
    Returns:
        True if metadata is valid, False otherwise
    """
    required_fields = ["canvas_size", "sources", "fps", "timestamp"]
    
    # Check all required fields exist
    for field in required_fields:
        if field not in metadata:
            return False
    
    # Validate canvas_size format
    canvas_size = metadata["canvas_size"]
    if not isinstance(canvas_size, list) or len(canvas_size) != 2:
        return False
    
    if not all(isinstance(x, int) and x > 0 for x in canvas_size):
        return False
    
    # Validate sources format
    if not isinstance(metadata["sources"], dict):
        return False
    
    # Validate fps
    if not isinstance(metadata["fps"], (int, float)) or metadata["fps"] <= 0:
        return False
    
    # Validate timestamp
    if not isinstance(metadata["timestamp"], (int, float)):
        return False
    
    return True 