"""
Metadata management for OBS Canvas Recording.
This module handles creation and manipulation of recording metadata.
"""

import re
import time
from typing import Dict, List, Tuple, Any


def determine_source_type(source_name: str) -> str:
    """
    Determine the type of OBS source based on its name.

    Args:
        source_name: Name of the OBS source

    Returns:
        Source type: "video", "audio", or "unknown"
    """
    if not source_name:
        return "unknown"

    # Convert to lowercase for case-insensitive matching
    name_lower = source_name.lower()

    # Audio source patterns - check these first as they're more specific
    audio_patterns = [
        # Audio input/output with specific keywords
        r"(audio|dźwięk|dzwiek)",
        r"(microphone|mikrofon|mic)",
        r"(pulse|pulseaudio)",
        r"(alsa)",
        r"(speaker|głośnik|glosnik)",
        r"(headphone|słuchawki|sluchawki)",
        r"(sound|dźwięk|dzwiek)",
        r"(wejścia.*dźwięku|wejscia.*dzwieku)",
        r"(desktop.*audio|pulpit.*dźwięk)",
        # More specific patterns to avoid conflicts
        r"(.*audio.*input|.*audio.*output)",
        r"(.*dźwięk.*input|.*dźwięk.*output)",
        r"(.*wejścia.*dźwięku|.*wejscia.*dzwieku)",
    ]

    # Video source patterns
    video_patterns = [
        # Camera/Video capture - more specific patterns
        r"(camera|kamera|webcam|cam)",
        r"(video|wideo)",
        r"(v4l2|video4linux)",
        r"(display|desktop|pulpit|ekran)",
        r"(window|okno)",
        r"(browser|przeglądarka)",
        r"(media|multimedia)",
        r"(image|zdjęcie)",
        r"(color|kolor|colour)",
        r"(text|tekst|gdi)",
        r"(vlc|video.*source)",
        r"(screen|monitor)",
        r"(game|gra)",
        r"(source.*video)",
        # More specific video capture patterns
        r"(urządzenie.*obraz)",
        r"(przechwytuj.*obraz)",
        r"(capture.*video)",
        r"(video.*capture)",
    ]

    # Check audio patterns first (more specific)
    for pattern in audio_patterns:
        if re.search(pattern, name_lower):
            return "audio"

    # Check video patterns second
    for pattern in video_patterns:
        if re.search(pattern, name_lower):
            return "video"

    # Special case: if contains "input" or "output" but not matched above, likely audio
    if re.search(r"(input|output|wejście|wyjście|wejscie|wyjscie)", name_lower):
        return "audio"

    # If no pattern matches, return unknown
    return "unknown"


def create_metadata(
    sources: List[Dict[str, Any]],
    canvas_size: Tuple[int, int] = (1920, 1080),
    fps: float = 30.0,
) -> Dict[str, Any]:
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
        if source.get("x", 0) < 0 or source.get("y", 0) < 0:
            raise ValueError("Source position cannot be negative")

        # Use name as key, fallback to source_id
        source_id = source.get("name", source.get("id", f"source_{i}"))

        # Transform source data to match expected format
        source_data = source.copy()
        if "x" in source and "y" in source:
            source_data["position"] = {"x": source["x"], "y": source["y"]}

        # Add source type detection
        source_data["type"] = determine_source_type(source_id)

        sources_dict[source_id] = source_data

    return {
        "canvas_size": list(canvas_size),
        "sources": sources_dict,
        "fps": fps,
        "timestamp": time.time(),
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
