"""
ABOUTME: Layout manager module for Blender VSE - handles PiP positioning and layout calculations.
ABOUTME: Centralizes layout logic for different video arrangement patterns and multi-camera setups.
"""

from typing import List, Dict, Tuple

from .constants import BlenderConstants, AnimationConstants


class BlenderLayoutManager:
    """Manager class for Blender VSE layout calculations and positioning."""

    def __init__(self, resolution_x: int = None, resolution_y: int = None):
        """
        Initialize layout manager with resolution parameters.

        Args:
            resolution_x: Canvas width in pixels. Defaults to BlenderConstants.DEFAULT_RESOLUTION_X
            resolution_y: Canvas height in pixels. Defaults to BlenderConstants.DEFAULT_RESOLUTION_Y
        """
        self.resolution_x = resolution_x or BlenderConstants.DEFAULT_RESOLUTION_X
        self.resolution_y = resolution_y or BlenderConstants.DEFAULT_RESOLUTION_Y

    def calculate_pip_positions(self) -> List[Dict]:
        """
        Calculate PiP positions for 2x2 grid layout.

        Returns:
            List[Dict]: List of position dictionaries with x, y, width, height
        """
        # Calculate quadrant dimensions
        pip_width = self.resolution_x // 2
        pip_height = self.resolution_y // 2

        positions = [
            # Top-left
            {"x": 0, "y": pip_height, "width": pip_width, "height": pip_height},
            # Top-right
            {"x": pip_width, "y": pip_height, "width": pip_width, "height": pip_height},
            # Bottom-left
            {"x": 0, "y": 0, "width": pip_width, "height": pip_height},
            # Bottom-right
            {"x": pip_width, "y": 0, "width": pip_width, "height": pip_height},
        ]

        return positions

    def calculate_multi_pip_layout(
        self, strip_count: int
    ) -> List[Tuple[int, int, float]]:
        """
        Calculate Multi-PiP layout positions based on scene resolution.

        In Blender VSE, (0,0) is the center of the screen.
        First two strips are main cameras (fullscreen, center).
        Remaining strips are corner PiPs with reduced scale.

        Args:
            strip_count: Number of video strips

        Returns:
            List of (pos_x, pos_y, scale) tuples for each strip
        """
        if strip_count <= 0:
            return []

        layout = []

        # PiP settings
        pip_scale = AnimationConstants.PIP_SCALE_FACTOR
        corner_positions = self.get_corner_positions()

        for i in range(strip_count):
            if i < 2:
                # First two strips: Main cameras (fullscreen, center)
                layout.append((0, 0, 1.0))
            else:
                # Remaining strips: Corner PiPs
                corner_index = (i - 2) % len(corner_positions)
                pos_x, pos_y = corner_positions[corner_index]
                layout.append((pos_x, pos_y, pip_scale))

        return layout

    def get_corner_positions(self, margin: int = None) -> List[Tuple[int, int]]:
        """
        Get corner positions with margin from edges.

        Args:
            margin: Distance from edge. Defaults to AnimationConstants.PIP_MARGIN

        Returns:
            List of (x, y) tuples for corner positions
        """
        if margin is None:
            margin = AnimationConstants.PIP_MARGIN

        # Calculate half dimensions for center-based coordinates
        half_width = self.resolution_x // 2
        half_height = self.resolution_y // 2

        # Corner positions relative to center (0,0)
        corners = [
            (half_width - margin, half_height - margin),  # Top-right
            (-(half_width - margin), half_height - margin),  # Top-left
            (-(half_width - margin), -(half_height - margin)),  # Bottom-left
            (half_width - margin, -(half_height - margin)),  # Bottom-right
        ]

        return corners

    def get_center_position(self) -> Tuple[int, int]:
        """
        Get center position coordinates.

        Returns:
            Tuple[int, int]: Center position (0, 0)
        """
        return (0, 0)
