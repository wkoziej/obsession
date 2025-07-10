"""
Parametryczny skrypt Blender do konfiguracji VSE.

Ten skrypt może być uruchomiony w Blenderze i konfiguruje VSE project
na podstawie parametrów przekazanych przez zmienne środowiskowe.

Zmienne środowiskowe:
- BLENDER_VSE_VIDEO_FILES: Lista plików wideo (oddzielone przecinkami)
- BLENDER_VSE_MAIN_AUDIO: Ścieżka do głównego pliku audio
- BLENDER_VSE_OUTPUT_BLEND: Ścieżka do pliku .blend
- BLENDER_VSE_RENDER_OUTPUT: Ścieżka do pliku wyjściowego renderowania
- BLENDER_VSE_FPS: Liczba klatek na sekundę (domyślnie 30)
- BLENDER_VSE_RESOLUTION_X: Szerokość rozdzielczości (domyślnie 1280)
- BLENDER_VSE_RESOLUTION_Y: Wysokość rozdzielczości (domyślnie 720)

Użycie w Blenderze:
1. Otwórz Blender
2. Przejdź do workspace Scripting
3. Wklej ten skrypt
4. Ustaw zmienne środowiskowe lub zmodyfikuj parametry w skrypcie
5. Uruchom skrypt (Alt+P)

Użycie z CLI:
blender --background --python blender_vse_script.py
"""

import bpy
import os
import sys
import json
from pathlib import Path
from typing import List, Optional, Tuple, Dict

# Import refactored modules
try:
    from .blender_vse.config import BlenderVSEConfig
    from .blender_vse.constants import AnimationConstants
except ImportError:
    # Fallback for when script is run standalone in Blender
    sys.path.append(str(Path(__file__).parent))
    from blender_vse.config import BlenderVSEConfig
    from blender_vse.constants import AnimationConstants


class BlenderVSEConfigurator:
    """Konfigurator Blender VSE z parametrami."""

    def __init__(self):
        """Inicjalizuj konfigurator z parametrami z zmiennych środowiskowych."""
        # Use new config module for parameter parsing
        config = BlenderVSEConfig()

        # Set attributes from config (maintaining compatibility)
        self.video_files = config.video_files
        self.main_audio = config.main_audio
        self.output_blend = config.output_blend
        self.render_output = config.render_output
        self.fps = config.fps
        self.resolution_x = config.resolution_x
        self.resolution_y = config.resolution_y
        self.animation_mode = config.animation_mode
        self.beat_division = config.beat_division

    def validate_parameters(self) -> Tuple[bool, List[str]]:
        """
        Waliduj parametry konfiguracji.

        Returns:
            Tuple[bool, List[str]]: (czy_valid, lista_błędów)
        """
        # Use config module for validation (maintaining compatibility)
        config = BlenderVSEConfig()
        return config.validate()

    def setup_vse_project(self) -> bool:
        """
        Skonfiguruj projekt Blender VSE.

        Returns:
            bool: True jeśli sukces
        """
        print("=== Konfiguracja projektu Blender VSE ===")

        # Walidacja parametrów
        is_valid, errors = self.validate_parameters()
        if not is_valid:
            print("✗ Błędy walidacji parametrów:")
            for error in errors:
                print(f"  - {error}")
            return False

        try:
            # 1. Wyczyść domyślną scenę
            bpy.ops.wm.read_factory_settings(use_empty=True)
            print("✓ Wyczyszczono domyślną scenę")

            # 2. Utwórz sequence editor
            if not bpy.context.scene.sequence_editor:
                bpy.context.scene.sequence_editor_create()
            print("✓ Utworzono sequence editor")

            # 3. Skonfiguruj podstawowe ustawienia sceny
            scene = bpy.context.scene
            scene.render.resolution_x = self.resolution_x
            scene.render.resolution_y = self.resolution_y
            scene.render.fps = self.fps
            scene.frame_start = 1
            print(
                f"✓ Ustawiono podstawowe parametry sceny ({self.resolution_x}x{self.resolution_y}, {self.fps}fps)"
            )

            # 4. Dodaj główny pasek audio (kanał 1)
            sequencer = scene.sequence_editor

            if self.main_audio:
                try:
                    sequencer.sequences.new_sound(
                        name="Main_Audio",
                        filepath=str(self.main_audio),
                        channel=1,  # Kanał audio 1
                        frame_start=1,
                    )
                    print(
                        f"✓ Dodano główne audio: {self.main_audio.name} (kanał audio 1)"
                    )
                except Exception as e:
                    print(f"✗ Błąd dodawania głównego audio: {e}")
                    return False

            # 5. Dodaj paski wideo do kanałów (zaczynając od kanału 2)
            for i, video_file in enumerate(self.video_files):
                try:
                    # Dodaj pasek wideo do kanału (i + 2) - zaczynamy od kanału 2
                    channel = i + 2
                    sequencer.sequences.new_movie(
                        name=f"Video_{i + 1}",
                        filepath=str(video_file),
                        channel=channel,
                        frame_start=1,
                    )
                    print(
                        f"✓ Dodano pasek wideo {i + 1}: {video_file.name} (kanał {channel})"
                    )
                except Exception as e:
                    print(f"✗ Błąd dodawania wideo {video_file}: {e}")
                    return False

            # 6. Skonfiguruj ustawienia renderowania
            render = scene.render
            render.image_settings.file_format = "FFMPEG"
            render.ffmpeg.format = "MPEG4"
            render.ffmpeg.codec = "H264"
            render.ffmpeg.constant_rate_factor = "HIGH"
            render.filepath = str(self.render_output)
            print("✓ Skonfigurowano ustawienia renderowania (MP4, H.264)")

            # 7. Ustaw timeline aby pokazać całą zawartość
            if sequencer.sequences:
                # Znajdź najdłuższą sekwencję
                max_frame_end = max(seq.frame_final_end for seq in sequencer.sequences)
                scene.frame_end = max_frame_end
                print(f"✓ Ustawiono koniec timeline na klatkę {max_frame_end}")

            # 8. Zapisz plik .blend
            if self.output_blend:
                try:
                    # Upewnij się, że katalog istnieje
                    self.output_blend.parent.mkdir(parents=True, exist_ok=True)
                    print(f"DEBUG: Attempting to save to: {self.output_blend}")
                    print(
                        f"DEBUG: Directory exists: {self.output_blend.parent.exists()}"
                    )

                    result = bpy.ops.wm.save_as_mainfile(
                        filepath=str(self.output_blend)
                    )
                    print(f"DEBUG: Save operation result: {result}")

                    # Check if file was actually created
                    if self.output_blend.exists():
                        print(f"✓ Zapisano projekt: {self.output_blend}")
                        print(
                            f"DEBUG: File size: {self.output_blend.stat().st_size} bytes"
                        )
                    else:
                        print(
                            f"✗ Plik nie został utworzony mimo braku błędów: {self.output_blend}"
                        )
                        return False

                except Exception as e:
                    print(f"✗ Błąd zapisywania projektu: {e}")
                    import traceback

                    traceback.print_exc()
                    return False

            # 9. Apply animations if requested
            if self.animation_mode != "none":
                success = self._apply_animations(sequencer)
                if not success:
                    print(
                        "⚠ Animacje nie zostały zastosowane, ale projekt został utworzony"
                    )
                else:
                    # 10. Save file again after adding animations
                    if self.output_blend:
                        try:
                            bpy.ops.wm.save_as_mainfile(filepath=str(self.output_blend))
                            print(
                                f"✓ Zapisano projekt z animacjami: {self.output_blend}"
                            )
                        except Exception as e:
                            print(f"✗ Błąd zapisywania projektu z animacjami: {e}")
                            return False

            print("=== Konfiguracja projektu VSE zakończona sukcesem ===")
            return True

        except Exception as e:
            print(f"✗ Błąd krytyczny: {e}")
            import traceback

            traceback.print_exc()
            return False

    def _apply_animations(self, sequencer) -> bool:
        """
        Apply audio-driven animations to video strips.

        Args:
            sequencer: Blender sequence editor

        Returns:
            bool: True if animations were applied successfully
        """
        print(f"=== Applying {self.animation_mode} animations ===")

        # Load animation data
        animation_data = self._load_animation_data()
        if not animation_data:
            print("✗ No animation data available")
            return False

        # Get video strips (exclude audio strips)
        video_strips = [
            seq
            for seq in sequencer.sequences
            if hasattr(seq, "blend_alpha") and hasattr(seq, "transform")
        ]
        if not video_strips:
            print("✗ No video strips found for animation")
            return False

        print(f"✓ Found {len(video_strips)} video strips for animation")

        # Apply animation based on mode
        if self.animation_mode == "beat-switch":
            success = self._animate_beat_switch(video_strips, animation_data)
            if success:
                print("✓ Beat switch animation applied successfully")
            else:
                print("✗ Beat switch animation failed")
            return success
        elif self.animation_mode == "energy-pulse":
            success = self._animate_energy_pulse(video_strips, animation_data)
            if success:
                print("✓ Energy pulse animation applied successfully")
            else:
                print("✗ Energy pulse animation failed")
            return success
        elif self.animation_mode == "multi-pip":
            success = self._animate_multi_pip(video_strips, animation_data)
            if success:
                print("✓ Multi-PiP animation applied successfully")
            else:
                print("✗ Multi-PiP animation failed")
            return success
        else:
            print(f"✗ Animation mode '{self.animation_mode}' not implemented yet")
            return False

    def _load_animation_data(self) -> Optional[Dict]:
        """
        Load animation data from BLENDER_VSE_AUDIO_ANALYSIS environment variable.

        MVP version: Only loads beat events, ignores other animation data.

        Returns:
            Optional[Dict]: Animation data with beat events or None if not available
        """
        # Try loading from file first (new approach)
        analysis_file = os.getenv("BLENDER_VSE_AUDIO_ANALYSIS_FILE", "")

        if analysis_file and Path(analysis_file).exists():
            try:
                with open(analysis_file, "r") as f:
                    full_data = json.load(f)
            except Exception as e:
                print(f"Error loading analysis file {analysis_file}: {e}")
                return None
        else:
            # Fallback to environment variable (old approach)
            analysis_json = os.getenv("BLENDER_VSE_AUDIO_ANALYSIS", "")

            if not analysis_json:
                print("No audio analysis data found in file or environment variable")
                return None

            try:
                full_data = json.loads(analysis_json)
            except json.JSONDecodeError as e:
                print(f"Error parsing animation data JSON: {e}")
                return None

        # Common processing for both file and env var approaches
        try:
            # Phase 3B: Extract beat events and energy peaks
            if "animation_events" not in full_data:
                print("No animation_events found in analysis data")
                return None

            animation_events = full_data["animation_events"]

            # Phase 3B: Support both beats and energy_peaks
            events_data = {}
            if "beats" in animation_events:
                events_data["beats"] = animation_events["beats"]
                print(f"✓ Loaded {len(events_data['beats'])} beat events")

            if "energy_peaks" in animation_events:
                events_data["energy_peaks"] = animation_events["energy_peaks"]
                print(f"✓ Loaded {len(events_data['energy_peaks'])} energy peak events")

            # Phase 3B.2: Support sections for multi-pip mode
            if "sections" in animation_events:
                events_data["sections"] = animation_events["sections"]
                print(
                    f"✓ Loaded {len(events_data['sections'])} section boundary events"
                )

            if not events_data:
                print(
                    "No supported animation events found (beats, energy_peaks, or sections)"
                )
                return None

            # Phase 3B: Return expanded data
            expanded_data = {
                "duration": full_data.get("duration", 0.0),
                "tempo": full_data.get("tempo", {"bpm": 120.0}),
                "animation_events": events_data,
            }

            return expanded_data

        except Exception as e:
            print(f"Error processing animation data: {e}")
            return None

    def _calculate_pip_positions(
        self, resolution_x: int = 1280, resolution_y: int = 720
    ) -> List[Dict]:
        """
        Calculate PiP positions for 2x2 grid layout.

        MVP version: Hardcoded 2x2 grid for maximum 4 video sources.

        Args:
            resolution_x: Canvas width in pixels
            resolution_y: Canvas height in pixels

        Returns:
            List[Dict]: List of position dictionaries with x, y, width, height
        """
        # MVP: Hardcoded 2x2 grid
        pip_width = resolution_x // 2
        pip_height = resolution_y // 2

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

        print(
            f"✓ Calculated 2x2 PiP positions for {resolution_x}x{resolution_y} canvas"
        )
        return positions

    def _animate_beat_switch(self, video_strips: List, animation_data: Dict) -> bool:
        """
        Animate beat switch by alternating strip visibility using blend_alpha.

        MVP version: Simple alternating visibility on beat events.

        Args:
            video_strips: List of video strips from Blender VSE
            animation_data: Animation data containing beat events

        Returns:
            bool: True if animation was applied successfully
        """
        if not animation_data or "animation_events" not in animation_data:
            print("No animation data available")
            return True

        beats = animation_data["animation_events"].get("beats", [])
        if not beats:
            print("No beat events found - skipping animation")
            return True

        if not video_strips:
            print("No video strips found - skipping animation")
            return True

        # Get FPS from scene
        fps = bpy.context.scene.render.fps
        print(
            f"✓ Animating {len(video_strips)} strips on {len(beats)} beats at {fps} FPS"
        )

        # Set initial visibility - first strip visible, others hidden
        for i, strip in enumerate(video_strips):
            strip.blend_alpha = 1.0 if i == 0 else 0.0
            # Insert keyframe at frame 1 using scene keyframe_insert
            data_path = f'sequence_editor.sequences_all["{strip.name}"].blend_alpha'
            bpy.context.scene.keyframe_insert(data_path=data_path, frame=1)

        # Animate on beat events
        for beat_index, beat_time in enumerate(beats):
            frame = int(beat_time * fps)
            active_strip_index = beat_index % len(video_strips)

            print(
                f"  Beat {beat_index + 1}: frame {frame}, active strip {active_strip_index}"
            )

            # Set visibility for all strips
            for strip_index, strip in enumerate(video_strips):
                if strip_index == active_strip_index:
                    strip.blend_alpha = 1.0  # Visible
                else:
                    strip.blend_alpha = 0.0  # Hidden

                # Insert keyframe using scene keyframe_insert
                data_path = f'sequence_editor.sequences_all["{strip.name}"].blend_alpha'
                bpy.context.scene.keyframe_insert(data_path=data_path, frame=frame)

        print("✓ Beat switch animation applied successfully")
        return True

    def _animate_energy_pulse(self, video_strips: List, animation_data: Dict) -> bool:
        """
        Animate energy pulse by scaling strips on energy peaks.

        Args:
            video_strips: List of video strips from Blender VSE
            animation_data: Animation data containing energy_peaks events

        Returns:
            bool: True if animation was applied successfully
        """
        if not animation_data or "animation_events" not in animation_data:
            print("No animation data available")
            return True

        energy_peaks = animation_data["animation_events"].get("energy_peaks", [])
        if not energy_peaks:
            print("No energy peaks found - skipping animation")
            return True

        if not video_strips:
            print("No video strips found - skipping animation")
            return True

        # Get FPS from scene
        fps = bpy.context.scene.render.fps
        print(
            f"✓ Animating {len(video_strips)} strips on {len(energy_peaks)} energy peaks at {fps} FPS"
        )

        # Set initial scale to normal
        for strip in video_strips:
            if hasattr(strip, "transform"):
                strip.transform.scale_x = 1.0
                strip.transform.scale_y = 1.0
                # Insert keyframe at frame 1 using scene keyframe_insert
                data_path_x = (
                    f'sequence_editor.sequences_all["{strip.name}"].transform.scale_x'
                )
                data_path_y = (
                    f'sequence_editor.sequences_all["{strip.name}"].transform.scale_y'
                )
                bpy.context.scene.keyframe_insert(data_path=data_path_x, frame=1)
                bpy.context.scene.keyframe_insert(data_path=data_path_y, frame=1)

        # Animate on energy peak events
        for peak_index, peak_time in enumerate(energy_peaks):
            frame = int(peak_time * fps)

            print(f"  Energy peak {peak_index + 1}: frame {frame}")

            # Scale up on energy peak
            for strip in video_strips:
                if hasattr(strip, "transform"):
                    strip.transform.scale_x = (
                        AnimationConstants.ENERGY_SCALE_FACTOR
                    )  # Scale up by 20%
                    strip.transform.scale_y = AnimationConstants.ENERGY_SCALE_FACTOR

                    # Insert keyframe at peak frame using scene keyframe_insert
                    data_path_x = f'sequence_editor.sequences_all["{strip.name}"].transform.scale_x'
                    data_path_y = f'sequence_editor.sequences_all["{strip.name}"].transform.scale_y'
                    bpy.context.scene.keyframe_insert(
                        data_path=data_path_x, frame=frame
                    )
                    bpy.context.scene.keyframe_insert(
                        data_path=data_path_y, frame=frame
                    )

            # Scale back down after peak (1 frame later)
            return_frame = frame + 1
            for strip in video_strips:
                if hasattr(strip, "transform"):
                    strip.transform.scale_x = 1.0  # Back to normal
                    strip.transform.scale_y = 1.0

                    # Insert keyframe at return frame
                    data_path_x = f'sequence_editor.sequences_all["{strip.name}"].transform.scale_x'
                    data_path_y = f'sequence_editor.sequences_all["{strip.name}"].transform.scale_y'
                    bpy.context.scene.keyframe_insert(
                        data_path=data_path_x, frame=return_frame
                    )
                    bpy.context.scene.keyframe_insert(
                        data_path=data_path_y, frame=return_frame
                    )

        print("✓ Energy pulse animation applied successfully")
        return True

    def _animate_multi_pip(self, video_strips: List, animation_data: Dict) -> bool:
        """
        Apply Multi-PiP animation mode.

        Layout: Main cameras (video1/video2) switch on section boundaries,
               Corner PiPs (video3/video4+) always visible with beat/energy effects.

        Args:
            video_strips: List of video strips
            animation_data: Animation data with sections, beats, and energy_peaks

        Returns:
            bool: True if animation applied successfully
        """
        print("=== Applying Multi-PiP animation mode ===")

        # Get required data
        # Get sections from animation data (already converted to objects)
        sections = animation_data.get("animation_events", {}).get("sections", [])
        beats = animation_data.get("animation_events", {}).get("beats", [])
        energy_peaks = animation_data.get("animation_events", {}).get(
            "energy_peaks", []
        )

        print(
            f"Found {len(sections)} sections, {len(beats)} beats, {len(energy_peaks)} energy peaks"
        )

        if not sections:
            print("✗ No sections found for Multi-PiP mode")
            return False

        # Setup multi-pip layout positions
        layout = self._calculate_multi_pip_layout(len(video_strips))

        # Apply layout positions to all strips
        for i, strip in enumerate(video_strips):
            if i < len(layout):
                pos_x, pos_y, base_scale = layout[i]
                strip.transform.offset_x = pos_x
                strip.transform.offset_y = pos_y
                strip.transform.scale_x = base_scale
                strip.transform.scale_y = base_scale
                print(
                    f"  {strip.name}: position ({pos_x}, {pos_y}), scale {base_scale}"
                )

        # Separate main cameras from corner PiPs
        main_cameras = {}
        corner_pips = {}

        for i, strip in enumerate(video_strips):
            if i < 2:  # First two strips are main cameras
                main_cameras[strip.name] = strip
            else:  # Rest are corner PiPs
                corner_pips[strip.name] = strip

        print(f"Main cameras: {list(main_cameras.keys())}")
        print(f"Corner PiPs: {list(corner_pips.keys())}")

        # Setup main camera section switching (pass converted sections)
        success1 = self._setup_main_camera_sections(
            main_cameras, {"sections": sections}
        )

        # Setup corner PiP effects
        success2 = self._setup_corner_pip_effects(corner_pips, animation_data)

        return success1 and success2

    def _calculate_multi_pip_layout(
        self, strip_count: int
    ) -> List[Tuple[int, int, float]]:
        """
        Calculate Multi-PiP layout positions based on scene resolution.

        In Blender VSE, (0,0) is the center of the screen.
        Positive X is right, negative X is left.
        Positive Y is up, negative Y is down.

        Args:
            strip_count: Number of video strips

        Returns:
            List of (pos_x, pos_y, scale) tuples for each strip
        """
        # Get scene resolution for calculating offsets
        width = bpy.context.scene.render.resolution_x
        height = bpy.context.scene.render.resolution_y

        # PiP settings
        pip_scale = 0.25
        pip_margin = AnimationConstants.PIP_MARGIN  # Distance from edge

        # Calculate corner positions relative to center (0,0)
        # For 1280x720: half_width=640, half_height=360
        half_width = width // 2
        half_height = height // 2

        # Corner positions (offset from center)
        top_left_x = -(half_width - pip_margin)  # Left side
        top_left_y = half_height - pip_margin  # Top side
        top_right_x = half_width - pip_margin  # Right side
        top_right_y = half_height - pip_margin  # Top side
        bottom_left_x = -(half_width - pip_margin)  # Left side
        bottom_left_y = -(half_height - pip_margin)  # Bottom side
        bottom_right_x = half_width - pip_margin  # Right side
        bottom_right_y = -(half_height - pip_margin)  # Bottom side

        layout = []

        if strip_count >= 1:
            # video1: Main camera (fullscreen, center)
            layout.append((0, 0, 1.0))
        if strip_count >= 2:
            # video2: Main camera (fullscreen, center)
            layout.append((0, 0, 1.0))
        if strip_count >= 3:
            # video3: Top-right corner PiP
            layout.append((top_right_x, top_right_y, pip_scale))
        if strip_count >= 4:
            # video4: Top-left corner PiP
            layout.append((top_left_x, top_left_y, pip_scale))
        if strip_count >= 5:
            # video5: Bottom-right corner PiP
            layout.append((bottom_right_x, bottom_right_y, pip_scale))
        if strip_count >= 6:
            # video6: Bottom-left corner PiP (fallback)
            layout.append((bottom_left_x, bottom_left_y, pip_scale))

        return layout

    def _setup_main_camera_sections(
        self, main_cameras: Dict, animation_data: Dict
    ) -> bool:
        """
        Setup main camera section switching.

        Main cameras (video1/video2) alternate on section boundaries.

        Args:
            main_cameras: Dictionary of main camera strips
            animation_data: Animation data with sections

        Returns:
            bool: True if setup successful
        """
        sections = animation_data.get("sections", [])
        fps = bpy.context.scene.render.fps

        print("=== Setting up main camera section switching ===")

        strip_names = list(main_cameras.keys())
        if len(strip_names) < 2:
            print("✗ Need at least 2 main cameras for section switching")
            return False

        # Initially hide all main cameras
        for strip in main_cameras.values():
            strip.blend_alpha = 0.0

        # Setup section switching (alternating between video1 and video2)
        for section_index, section in enumerate(sections):
            start_frame = int(section["start"] * fps)
            end_frame = int(section["end"] * fps)

            # Determine which camera should be active
            active_index = section_index % len(strip_names)
            active_strip_name = strip_names[active_index]
            active_strip = main_cameras[active_strip_name]

            print(
                f"  Section {section_index + 1} ({section['label']}): frames {start_frame}-{end_frame}, camera {active_strip_name}"
            )

            # Hide all cameras at section start
            for strip in main_cameras.values():
                strip.blend_alpha = 0.0
                data_path = f'sequence_editor.sequences_all["{strip.name}"].blend_alpha'
                bpy.context.scene.keyframe_insert(
                    data_path=data_path, frame=start_frame
                )

            # Show active camera
            active_strip.blend_alpha = 1.0
            data_path = (
                f'sequence_editor.sequences_all["{active_strip.name}"].blend_alpha'
            )
            bpy.context.scene.keyframe_insert(data_path=data_path, frame=start_frame)

        return True

    def _setup_corner_pip_effects(
        self, corner_pips: Dict, animation_data: Dict
    ) -> bool:
        """
        Setup corner PiP effects (beat/energy animations).

        Corner PiPs are always visible and react to beats/energy.

        Args:
            corner_pips: Dictionary of corner PiP strips
            animation_data: Animation data with beats and energy_peaks

        Returns:
            bool: True if setup successful
        """
        energy_peaks = animation_data.get("animation_events", {}).get(
            "energy_peaks", []
        )
        fps = bpy.context.scene.render.fps

        print("=== Setting up corner PiP effects ===")

        if not corner_pips:
            print("✓ No corner PiPs to animate")
            return True

        # Make all corner PiPs visible
        for strip in corner_pips.values():
            strip.blend_alpha = 1.0

        # Add beat-based scale pulsing (like energy-pulse mode)
        for strip in corner_pips.values():
            # Set initial scale keyframes at frame 1
            data_path_x = (
                f'sequence_editor.sequences_all["{strip.name}"].transform.scale_x'
            )
            data_path_y = (
                f'sequence_editor.sequences_all["{strip.name}"].transform.scale_y'
            )
            bpy.context.scene.keyframe_insert(data_path=data_path_x, frame=1)
            bpy.context.scene.keyframe_insert(data_path=data_path_y, frame=1)

        # Animate on energy peaks (bass response)
        for peak_index, peak_time in enumerate(energy_peaks):
            frame = int(peak_time * fps)

            for strip in corner_pips.values():
                # Get current base scale from layout
                current_scale = strip.transform.scale_x
                pulse_scale = (
                    current_scale * AnimationConstants.PIP_SCALE_FACTOR
                )  # 10% pulse for corner PiPs

                # Scale up on energy peak
                strip.transform.scale_x = pulse_scale
                strip.transform.scale_y = pulse_scale

                data_path_x = (
                    f'sequence_editor.sequences_all["{strip.name}"].transform.scale_x'
                )
                data_path_y = (
                    f'sequence_editor.sequences_all["{strip.name}"].transform.scale_y'
                )
                bpy.context.scene.keyframe_insert(data_path=data_path_x, frame=frame)
                bpy.context.scene.keyframe_insert(data_path=data_path_y, frame=frame)

                # Scale back down (1 frame later)
                return_frame = frame + 1
                strip.transform.scale_x = current_scale
                strip.transform.scale_y = current_scale
                bpy.context.scene.keyframe_insert(
                    data_path=data_path_x, frame=return_frame
                )
                bpy.context.scene.keyframe_insert(
                    data_path=data_path_y, frame=return_frame
                )

        print(f"✓ Corner PiP effects applied to {len(corner_pips)} strips")
        return True


def main() -> int:
    """
    Główna funkcja skryptu.

    Returns:
        int: Kod wyjścia (0 dla sukcesu, 1 dla błędu)
    """
    configurator = BlenderVSEConfigurator()

    print("=== Parametryczny skrypt Blender VSE ===")
    print(f"Pliki wideo: {len(configurator.video_files)}")
    print(f"Główne audio: {configurator.main_audio}")
    print(f"Plik wyjściowy: {configurator.output_blend}")
    print(f"Renderowanie: {configurator.render_output}")
    print(f"Rozdzielczość: {configurator.resolution_x}x{configurator.resolution_y}")
    print(f"FPS: {configurator.fps}")
    print()

    success = configurator.setup_vse_project()

    if success:
        print("✅ Projekt VSE skonfigurowany pomyślnie!")
        return 0
    else:
        print("❌ Błąd konfiguracji projektu VSE")
        return 1


# Sprawdź czy jesteśmy w Blenderze czy uruchamiamy z linii poleceń
def is_running_in_blender() -> bool:
    """Sprawdź czy skrypt jest uruchamiany w Blenderze."""
    try:
        import importlib.util

        spec = importlib.util.find_spec("bpy")
        return spec is not None
    except ImportError:
        return False


# Uruchom główną funkcję tylko gdy skrypt jest wykonywany bezpośrednio
if __name__ == "__main__":
    exit_code = main()

    # Jeśli uruchamiamy z linii poleceń (nie w Blenderze), użyj sys.exit()
    if not is_running_in_blender():
        sys.exit(exit_code)
