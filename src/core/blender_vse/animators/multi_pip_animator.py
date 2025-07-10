"""
ABOUTME: MultiPipAnimator class - handles main camera switching with PiP corner effects.
ABOUTME: Extracts multi-pip logic from BlenderVSEConfigurator for better modularity and testability.
"""

from typing import List, Dict

from ..keyframe_helper import KeyframeHelper
from ..layout_manager import BlenderLayoutManager


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

        # First: Apply layout positions to ALL strips (like original implementation)
        layout = self.layout_manager.calculate_multi_pip_layout(len(video_strips))
        for i, strip in enumerate(video_strips):
            if i < len(layout):
                pos_x, pos_y, base_scale = layout[i]
                if hasattr(strip, "transform"):
                    strip.transform.offset_x = pos_x
                    strip.transform.offset_y = pos_y
                    strip.transform.scale_x = base_scale
                    strip.transform.scale_y = base_scale
                    print(
                        f"  {strip.name}: position ({pos_x}, {pos_y}), scale {base_scale}"
                    )

        # Apply main camera switching based on sections
        if sections:
            self._animate_main_camera_switching(video_strips, sections, fps)

        # Apply PiP corner effects based on energy peaks (like original)
        energy_peaks = animation_data["animation_events"].get("energy_peaks", [])
        if energy_peaks and len(video_strips) > 2:  # Need corner PiPs (index 2+)
            self._animate_pip_corner_effects(video_strips, energy_peaks, fps)

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
        self, video_strips: List, energy_peaks: List[float], fps: int
    ):
        """
        Animate PiP corner effects on energy peaks (like original implementation).

        Args:
            video_strips: List of video strips
            energy_peaks: List of energy peak times in seconds
            fps: Frames per second
        """
        print(f"  PiP corner effects on {len(energy_peaks)} energy peaks")

        # Set up PiP strips (non-main cameras) - positions already set above
        pip_strips = video_strips[2:]  # Corner PiPs start from index 2 (like original)

        # Make all corner PiPs visible and set initial keyframes
        for strip in pip_strips:
            if hasattr(strip, "transform"):
                strip.blend_alpha = 1.0
                # Set initial scale keyframes at frame 1
                self.keyframe_helper.insert_transform_scale_keyframes(strip.name, 1)
                print(f"    PiP strip {strip.name}: visible with initial keyframes")

        # Apply energy peak effects to all PiP strips (like original)
        for peak_index, peak_time in enumerate(energy_peaks):
            frame = int(peak_time * fps)

            for strip in pip_strips:
                if not hasattr(strip, "transform"):
                    continue

                # Get current base scale and apply 10% pulse (like original)
                current_scale = strip.transform.scale_x
                pulse_scale = current_scale * 1.1  # 10% pulse for corner PiPs

                # Scale up on energy peak
                strip.transform.scale_x = pulse_scale
                strip.transform.scale_y = pulse_scale
                self.keyframe_helper.insert_transform_scale_keyframes(
                    strip.name, frame, pulse_scale
                )

                # Scale back down (1 frame later)
                return_frame = frame + 1
                strip.transform.scale_x = current_scale
                strip.transform.scale_y = current_scale
                self.keyframe_helper.insert_transform_scale_keyframes(
                    strip.name, return_frame, current_scale
                )
