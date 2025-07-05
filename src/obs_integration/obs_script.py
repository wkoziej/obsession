"""
OBS Studio script for Canvas Recording metadata collection.
This script integrates with OBS Studio to automatically collect scene metadata
when recording stops.
"""

import os
import json
import time
from typing import Dict, Any

try:
    import obspython as obs
except ImportError:
    # For testing purposes when OBS is not available
    obs = None

# Import capabilities detection from metadata module
try:
    from src.core.metadata import determine_source_capabilities
except ImportError:
    # Fallback for when running in OBS without proper Python path
    def determine_source_capabilities(obs_source) -> Dict[str, bool]:
        """Fallback implementation for OBS environment."""
        if obs_source is None or obs is None:
            return {"has_audio": False, "has_video": False}

        flags = obs.obs_source_get_output_flags(obs_source)

        # OBS source flags constants
        OBS_SOURCE_VIDEO = 0x001
        OBS_SOURCE_AUDIO = 0x002

        return {
            "has_audio": bool(flags & OBS_SOURCE_AUDIO),
            "has_video": bool(flags & OBS_SOURCE_VIDEO),
        }


# Global variables for script state
script_enabled = False
metadata_output_path = ""
current_scene_data = {}


def script_description():
    """Return script description for OBS Studio."""
    return """
    <h2>Canvas Recording Metadata Collector</h2>
    <p>Automatically collects scene metadata when recording stops.</p>
    <p>This data is used for automatic source extraction from recordings.</p>
    """


def script_properties():
    """Define script properties for OBS Studio UI."""
    if obs is None:
        return None

    props = obs.obs_properties_create()

    # Enable/disable script
    obs.obs_properties_add_bool(props, "enabled", "Enable metadata collection")

    # Output path for metadata
    obs.obs_properties_add_path(
        props,
        "output_path",
        "Metadata output directory",
        obs.OBS_PATH_DIRECTORY,
        "",
        "",
    )

    # Add info text
    obs.obs_properties_add_text(props, "info", "Info", obs.OBS_TEXT_INFO)

    return props


def script_defaults(settings):
    """Set default values for script properties."""
    if obs is None:
        return

    obs.obs_data_set_default_bool(settings, "enabled", True)
    obs.obs_data_set_default_string(settings, "output_path", "")
    obs.obs_data_set_default_string(
        settings, "info", "Metadata will be saved when recording stops."
    )


def script_update(settings):
    """Called when script properties are updated."""
    global script_enabled, metadata_output_path

    if obs is None:
        return

    script_enabled = obs.obs_data_get_bool(settings, "enabled")
    metadata_output_path = obs.obs_data_get_string(settings, "output_path")

    print(f"[Canvas Recorder] Script enabled: {script_enabled}")
    print(f"[Canvas Recorder] Output path: {metadata_output_path}")


def script_load(settings):
    """Called when script is loaded."""
    global script_enabled

    if obs is None:
        print("[Canvas Recorder] OBS Python API not available")
        return

    print("[Canvas Recorder] Script loaded")

    # Register frontend event callback
    obs.obs_frontend_add_event_callback(on_event)

    # Initialize settings
    script_update(settings)


def script_unload():
    """Called when script is unloaded."""
    if obs is None:
        return

    print("[Canvas Recorder] Script unloaded")

    # Remove frontend event callback
    obs.obs_frontend_remove_event_callback(on_event)


def on_event(event):
    """Handle OBS frontend events."""
    if obs is None or not script_enabled:
        return

    if event == obs.OBS_FRONTEND_EVENT_RECORDING_STARTED:
        print("[Canvas Recorder] Recording started - preparing metadata collection")
        prepare_metadata_collection()

    elif event == obs.OBS_FRONTEND_EVENT_RECORDING_STOPPED:
        print("[Canvas Recorder] Recording stopped - collecting metadata")
        collect_and_save_metadata()


def prepare_metadata_collection():
    """Prepare for metadata collection when recording starts."""
    global current_scene_data

    if obs is None:
        return

    # Get current scene
    current_scene = obs.obs_frontend_get_current_scene()
    if current_scene is None:
        print("[Canvas Recorder] No current scene found")
        return

    # Get video info
    video_info = obs.obs_video_info()
    obs.obs_get_video_info(video_info)

    # Store basic info
    current_scene_data = {
        "canvas_size": [video_info.base_width, video_info.base_height],
        "fps": video_info.fps_num / video_info.fps_den
        if video_info.fps_den > 0
        else 30.0,
        "recording_start_time": time.time(),
        "scene_name": obs.obs_source_get_name(current_scene),
    }

    print(
        f"[Canvas Recorder] Prepared metadata for scene: {current_scene_data['scene_name']}"
    )
    print(f"[Canvas Recorder] Canvas size: {current_scene_data['canvas_size']}")
    print(f"[Canvas Recorder] FPS: {current_scene_data['fps']}")

    # Release source reference
    obs.obs_source_release(current_scene)


def collect_and_save_metadata():
    """Collect scene metadata and save to file."""
    global current_scene_data, metadata_output_path

    if obs is None:
        return

    if not current_scene_data:
        print("[Canvas Recorder] No scene data prepared")
        return

    # Get current scene
    current_scene = obs.obs_frontend_get_current_scene()
    if current_scene is None:
        print("[Canvas Recorder] No current scene found")
        return

    try:
        # Convert source to scene
        scene = obs.obs_scene_from_source(current_scene)
        if scene is None:
            print("[Canvas Recorder] Failed to get scene from source")
            return

        # Collect scene items - in Python API, this returns a list
        scene_items = obs.obs_scene_enum_items(scene)
        if scene_items is None:
            print("[Canvas Recorder] No scene items found")
            return

        sources = {}

        # Process each scene item
        for scene_item in scene_items:
            if scene_item is None:
                continue

            # Get source from scene item
            source = obs.obs_sceneitem_get_source(scene_item)
            if source is None:
                continue

            # Get source info
            source_name = obs.obs_source_get_name(source)
            source_id = obs.obs_source_get_id(source)

            # Get position, scale and bounds
            pos = obs.vec2()
            scale = obs.vec2()
            bounds = obs.vec2()
            obs.obs_sceneitem_get_pos(scene_item, pos)
            obs.obs_sceneitem_get_scale(scene_item, scale)
            obs.obs_sceneitem_get_bounds(scene_item, bounds)
            bounds_type = obs.obs_sceneitem_get_bounds_type(scene_item)

            # Get source dimensions
            source_width = obs.obs_source_get_width(source)
            source_height = obs.obs_source_get_height(source)

            # Calculate final dimensions - priorytet dla bounds
            if (
                bounds.x > 0 and bounds.y > 0 and bounds_type != 0
            ):  # 0 = OBS_BOUNDS_NONE
                final_width = int(bounds.x)
                final_height = int(bounds.y)
            else:
                final_width = int(source_width * scale.x)
                final_height = int(source_height * scale.y)

            # Determine source capabilities (has_audio/has_video)
            capabilities = determine_source_capabilities(source)

            # Store source data
            sources[source_name] = {
                "name": source_name,
                "id": source_id,
                "position": {"x": int(pos.x), "y": int(pos.y)},
                "scale": {"x": scale.x, "y": scale.y},
                "bounds": {"x": bounds.x, "y": bounds.y, "type": bounds_type},
                "dimensions": {
                    "source_width": source_width,
                    "source_height": source_height,
                    "final_width": final_width,
                    "final_height": final_height,
                },
                "visible": obs.obs_sceneitem_visible(scene_item),
                # Add capabilities for new extractor
                "has_audio": capabilities["has_audio"],
                "has_video": capabilities["has_video"],
            }

        # Release scene items list
        obs.sceneitem_list_release(scene_items)

        # Complete metadata
        metadata = {
            **current_scene_data,
            "sources": sources,
            "recording_stop_time": time.time(),
            "total_sources": len(sources),
        }

        # Save metadata to file
        save_metadata_to_file(metadata)

        print(f"[Canvas Recorder] Collected metadata for {len(sources)} sources")

    except Exception as e:
        print(f"[Canvas Recorder] Error collecting metadata: {e}")

    finally:
        # Release source reference
        obs.obs_source_release(current_scene)


def save_metadata_to_file(metadata: Dict[str, Any]):
    """Save metadata to JSON file."""
    global metadata_output_path

    if not metadata_output_path:
        # Use default path relative to OBS
        metadata_output_path = os.path.expanduser("~/obs-canvas-metadata")

    # Ensure directory exists
    os.makedirs(metadata_output_path, exist_ok=True)

    # Generate filename with timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    scene_name = metadata.get("scene_name", "unknown").replace(" ", "_")
    filename = f"metadata_{scene_name}_{timestamp}.json"
    filepath = os.path.join(metadata_output_path, filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"[Canvas Recorder] Metadata saved to: {filepath}")

    except Exception as e:
        print(f"[Canvas Recorder] Error saving metadata: {e}")


# For testing purposes when running outside OBS
if __name__ == "__main__":
    print("Canvas Recording Metadata Collector")
    print("This script should be loaded in OBS Studio")
    print("Testing mode - OBS API not available")
