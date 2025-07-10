"""
ABOUTME: MultiPipAnimator class - handles main camera switching with PiP corner effects.
ABOUTME: Extracts multi-pip logic from BlenderVSEConfigurator for better modularity and testability.
"""

from typing import List, Dict

from ..keyframe_helper import KeyframeHelper
from ..layout_manager import BlenderLayoutManager
from ..constants import AnimationConstants


class MultiPipAnimator:
    """Animator for main camera switching with PiP corner effects."""

    def __init__(self):
        """Initialize MultiPipAnimator with required components."""
        self.keyframe_helper = KeyframeHelper()
        self.layout_manager = BlenderLayoutManager()

    def get_animation_mode(self) -> str:
        """
        Get the animation mode this animator handles.

        Returns:
            str: Animation mode identifier
        """
        return "multi-pip"

    def can_handle(self, animation_mode: str) -> bool:
        """
        Check if this animator can handle the specified animation mode.

        Args:
            animation_mode: Animation mode to check

        Returns:
            bool: True if this animator can handle the mode
        """
        return animation_mode == "multi-pip"

    def animate(self, video_strips: List, animation_data: Dict, fps: int) -> bool:
        """
        Apply multi-pip animation with main camera switching and corner PiPs.

        Args:
            video_strips: List of video strips from Blender VSE
            animation_data: Animation data containing sections and beats events
            fps: Frames per second for frame calculation

        Returns:
            bool: True if animation was applied successfully
        """
        # Validate inputs
        if fps <= 0:
            return False

        if not video_strips:
            return True  # Nothing to animate

        if not animation_data or "animation_events" not in animation_data:
            return True  # No animation data

        sections = animation_data["animation_events"].get("sections", [])
        beats = animation_data["animation_events"].get("beats", [])

        if not sections and not beats:
            return True  # No animation events

        print(
            f"✓ Multi-PiP animation: {len(video_strips)} strips, {len(sections)} sections, {len(beats)} beats at {fps} FPS"
        )

        # Apply main camera switching based on sections
        if sections:
            self._animate_main_camera_switching(video_strips, sections, fps)

        # Apply PiP corner effects based on beats
        if beats and len(video_strips) > 1:
            self._animate_pip_corner_effects(video_strips, beats, fps)

        print("✓ Multi-PiP animation applied successfully")
        return True

    def _animate_main_camera_switching(
        self, video_strips: List, sections: List[Dict], fps: int
    ):
        """
        Animate main camera switching on section boundaries.

        Args:
            video_strips: List of video strips
            sections: List of section dictionaries with start/end times
            fps: Frames per second
        """
        print(f"  Main camera switching on {len(sections)} sections")

        # Set initial main camera (first strip visible)
        for i, strip in enumerate(video_strips):
            alpha_value = 1.0 if i == 0 else 0.0
            strip.blend_alpha = alpha_value
            self.keyframe_helper.insert_blend_alpha_keyframe(strip.name, 1, alpha_value)

        # Switch main camera on section boundaries
        for section_index, section in enumerate(sections):
            if section_index == 0:
                continue  # Skip first section (already set initial state)

            frame = int(section["start"] * fps)
            active_strip_index = section_index % len(video_strips)

            print(
                f"    Section {section_index}: frame {frame}, main camera {active_strip_index}"
            )

            # Set main camera visibility
            for strip_index, strip in enumerate(video_strips):
                if strip_index == active_strip_index:
                    # Main camera: full visibility
                    strip.blend_alpha = 1.0
                    self.keyframe_helper.insert_blend_alpha_keyframe(
                        strip.name, frame, 1.0
                    )
                else:
                    # Other cameras: check if they should be PiP
                    if strip_index < 4:  # Up to 4 strips total (1 main + 3 PiPs)
                        strip.blend_alpha = 0.3  # PiP visibility
                        self.keyframe_helper.insert_blend_alpha_keyframe(
                            strip.name, frame, 0.3
                        )
                    else:
                        strip.blend_alpha = 0.0  # Hidden
                        self.keyframe_helper.insert_blend_alpha_keyframe(
                            strip.name, frame, 0.0
                        )

    def _animate_pip_corner_effects(
        self, video_strips: List, beats: List[float], fps: int
    ):
        """
        Animate PiP corner effects on beats.

        Args:
            video_strips: List of video strips
            beats: List of beat times in seconds
            fps: Frames per second
        """
        print(f"  PiP corner effects on {len(beats)} beats")

        # Get corner positions from layout manager
        corner_positions = self.layout_manager.get_corner_positions(
            AnimationConstants.PIP_MARGIN
        )

        # Set up PiP strips (non-main cameras)
        pip_strips = video_strips[1:4]  # Up to 3 PiP strips

        # Position PiP strips in corners
        for i, strip in enumerate(pip_strips):
            if i < len(corner_positions):
                # Set PiP scale
                if hasattr(strip, "transform"):
                    strip.transform.scale_x = AnimationConstants.PIP_SCALE_FACTOR
                    strip.transform.scale_y = AnimationConstants.PIP_SCALE_FACTOR
                    self.keyframe_helper.insert_transform_scale_keyframes(
                        strip.name, 1, AnimationConstants.PIP_SCALE_FACTOR
                    )

        # Apply beat effects to PiP strips
        for beat_index, beat_time in enumerate(beats):
            frame = int(beat_time * fps)

            # Cycle through PiP strips for beat effects
            for i, strip in enumerate(pip_strips):
                if not hasattr(strip, "transform"):
                    continue

                # Apply slight scale pulse effect on beats
                if beat_index % len(pip_strips) == i:
                    # This PiP gets a slight scale boost
                    enhanced_scale = AnimationConstants.PIP_SCALE_FACTOR * 1.1
                    strip.transform.scale_x = enhanced_scale
                    strip.transform.scale_y = enhanced_scale
                    self.keyframe_helper.insert_transform_scale_keyframes(
                        strip.name, frame, enhanced_scale
                    )

                    # Return to normal scale after 1 frame
                    return_frame = frame + 1
                    strip.transform.scale_x = AnimationConstants.PIP_SCALE_FACTOR
                    strip.transform.scale_y = AnimationConstants.PIP_SCALE_FACTOR
                    self.keyframe_helper.insert_transform_scale_keyframes(
                        strip.name, return_frame, AnimationConstants.PIP_SCALE_FACTOR
                    )
