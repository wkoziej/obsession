"""
Blender Project Manager for OBS Canvas Recording VSE projects.

This module handles the creation and configuration of Blender VSE projects
from extracted OBS recordings.
"""

import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class BlenderProjectManager:
    """
    Manager for creating and configuring Blender VSE projects.

    This class handles the creation of Blender projects with Video Sequence Editor
    configured for extracted OBS Canvas recordings.
    """

    def __init__(self, blender_executable: str = "blender"):
        """
        Initialize BlenderProjectManager.

        Args:
            blender_executable: Path or command to Blender executable
        """
        self.blender_executable = blender_executable

    def create_vse_project(
        self, recording_path: Path, main_audio_name: Optional[str] = None
    ) -> Path:
        """
        Create a Blender VSE project from extracted OBS recording.

        Args:
            recording_path: Path to the recording directory
            main_audio_name: Optional name of main audio file

        Returns:
            Path: Path to the created .blend file

        Raises:
            ValueError: If recording structure is invalid
            RuntimeError: If Blender execution fails
        """
        from .file_structure import FileStructureManager
        from .audio_validator import AudioValidator

        logger.info(f"Creating Blender VSE project for: {recording_path}")

        # 1. Validate recording structure
        structure = FileStructureManager.find_recording_structure(recording_path)
        if not structure:
            raise ValueError(f"Invalid recording structure in: {recording_path}")

        # 2. Detect main audio file
        audio_validator = AudioValidator()
        main_audio = audio_validator.detect_main_audio(
            structure.extracted_dir, main_audio_name
        )
        logger.info(f"Main audio file: {main_audio.name}")

        # 3. Find video files
        video_files = self.find_video_files(structure.extracted_dir)
        if not video_files:
            raise ValueError(f"No video files found in: {structure.extracted_dir}")
        logger.info(f"Found {len(video_files)} video files")

        # 4. Ensure blender directory exists
        blender_dir = FileStructureManager.ensure_blender_dir(recording_path)

        # 5. Create output paths
        project_name = recording_path.name
        output_blend = blender_dir / f"{project_name}.blend"
        render_output = blender_dir / "render" / f"{project_name}_final.mp4"

        # 6. Read FPS from metadata
        fps = self._read_fps_from_metadata(structure.metadata_file)

        # 7. Create and execute Blender script
        script_path = self._create_blender_script(
            video_files, main_audio, output_blend, render_output, fps
        )

        try:
            self._execute_blender_script(script_path, output_blend)
            logger.info(f"Blender project created successfully: {output_blend}")
            return output_blend
        finally:
            # Clean up temporary script
            if script_path.exists():
                script_path.unlink()
                logger.debug(f"Cleaned up temporary script: {script_path}")

    def _execute_blender_script(self, script_path: Path, output_blend: Path) -> None:
        """
        Execute Blender script in background mode.

        Args:
            script_path: Path to Python script for Blender
            output_blend: Path where to save .blend file

        Raises:
            RuntimeError: If Blender execution fails
        """
        # Use snap run blender if blender_executable is default
        if self.blender_executable == "blender":
            cmd = [
                "snap",
                "run",
                "blender",
                "--background",
                "--python",
                str(script_path),
            ]
        else:
            cmd = [
                self.blender_executable,
                "--background",
                "--python",
                str(script_path),
            ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Blender script executed successfully: {script_path}")
            logger.debug(f"Blender output: {result.stdout}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Blender execution failed: {e}")
            logger.error(f"Blender stderr: {e.stderr}")
            raise RuntimeError(f"Blender execution failed: {e.stderr}")

    def _read_fps_from_metadata(self, metadata_file: Path) -> int:
        """
        Read FPS value from metadata.json file.

        Args:
            metadata_file: Path to metadata.json file

        Returns:
            int: FPS value from metadata, defaults to 30 if not found
        """
        import json

        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            fps = metadata.get("fps", 30)
            # Ensure fps is a valid integer
            fps = int(fps) if fps > 0 else 30
            logger.debug(f"Read FPS from metadata: {fps}")
            return fps

        except (json.JSONDecodeError, IOError, OSError, ValueError) as e:
            logger.warning(f"Failed to read FPS from metadata: {e}, using default 30")
            return 30

    def _create_blender_script(
        self,
        video_files: List[Path],
        main_audio: Path,
        output_blend: Path,
        render_output: Path,
        fps: int = 30,
    ) -> Path:
        """
        Create Python script for Blender VSE configuration.

        Args:
            video_files: List of video files to add to VSE
            main_audio: Main audio file path
            output_blend: Output .blend file path
            render_output: Render output directory

        Returns:
            Path: Path to created script file
        """

        # Create temporary script file
        script_fd, script_path = tempfile.mkstemp(suffix=".py", prefix="blender_vse_")
        script_path = Path(script_path)

        # Generate script content
        script_content = self._generate_blender_script_content(
            video_files, main_audio, output_blend, render_output, fps
        )

        # Write script to file
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        logger.debug(f"Created Blender script: {script_path}")
        return script_path

    def _generate_blender_script_content(
        self,
        video_files: List[Path],
        main_audio: Path,
        output_blend: Path,
        render_output: Path,
        fps: int = 30,
    ) -> str:
        """
        Generate the actual Python script content for Blender.

        Args:
            video_files: List of video files to add to VSE
            main_audio: Main audio file path
            output_blend: Output .blend file path
            render_output: Render output directory

        Returns:
            str: Python script content for Blender
        """
        import textwrap

        # Convert paths to strings for script
        video_paths = [str(vf.resolve()) for vf in video_files]
        main_audio_path = str(main_audio.resolve())
        output_blend_path = str(output_blend.resolve())
        render_output_path = str(render_output.resolve())

        script = f'''
#!/usr/bin/env python3
"""
Blender VSE setup script generated by OBS Canvas Recorder.
This script creates a VSE project with video and audio strips.
"""

import bpy
import sys
import os
from pathlib import Path

def setup_vse_project():
    """Setup Blender VSE project with video and audio strips."""
    print("=== Setting up Blender VSE project ===")

    # 1. Clear default scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    print("✓ Cleared default scene")

    # 2. Create sequence editor
    if not bpy.context.scene.sequence_editor:
        bpy.context.scene.sequence_editor_create()
    print("✓ Created sequence editor")

    # 3. Configure basic scene settings
    scene = bpy.context.scene
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.fps = {fps}
    scene.frame_start = 1
    print("✓ Set basic scene settings (720p, {{fps}}fps)")

    # 4. Add video strips to channels
    video_files = {video_paths}
    sequencer = scene.sequence_editor

    for i, video_path in enumerate(video_files):
        if not os.path.exists(video_path):
            print(f"⚠ Warning: Video file not found: {{video_path}}")
            continue

        try:
            # Add video strip to channel (i + 1)
            channel = i + 1
            strip = sequencer.sequences.new_movie(
                name=f"Video_{{i+1}}",
                filepath=video_path,
                channel=channel,
                frame_start=1
            )
            print(f"✓ Added video strip {{i+1}}: {{Path(video_path).name}} (channel {{channel}})")
        except Exception as e:
            print(f"✗ Error adding video {{video_path}}: {{e}}")

    # 5. Add main audio strip
    main_audio_path = "{main_audio_path}"
    if os.path.exists(main_audio_path):
        try:
            audio_strip = sequencer.sequences.new_sound(
                name="Main_Audio",
                filepath=main_audio_path,
                channel=1,  # Audio channel 1
                frame_start=1
            )
            print(f"✓ Added main audio: {{Path(main_audio_path).name}} (audio channel 1)")
        except Exception as e:
            print(f"✗ Error adding main audio: {{e}}")
    else:
        print(f"⚠ Warning: Main audio file not found: {{main_audio_path}}")

    # 6. Configure render settings
    render = scene.render
    render.image_settings.file_format = 'FFMPEG'
    render.ffmpeg.format = 'MPEG4'
    render.ffmpeg.codec = 'H264'
    render.ffmpeg.constant_rate_factor = 'HIGH'
    render.filepath = "{render_output_path}"
    print("✓ Configured render settings (MP4, H.264)")

    # 7. Set timeline to show all content
    if sequencer.sequences:
        # Find the longest sequence
        max_frame_end = max(seq.frame_final_end for seq in sequencer.sequences)
        scene.frame_end = max_frame_end
        print(f"✓ Set timeline end to frame {{max_frame_end}}")

    # 8. Save .blend file
    output_path = "{output_blend_path}"
    try:
        bpy.ops.wm.save_as_mainfile(filepath=output_path)
        print(f"✓ Saved project: {{output_path}}")
    except Exception as e:
        print(f"✗ Error saving project: {{e}}")
        return False

    print("=== VSE project setup completed successfully ===")
    return True

if __name__ == "__main__":
    try:
        success = setup_vse_project()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"✗ Fatal error: {{e}}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
'''

        return textwrap.dedent(script).strip()

    def find_video_files(self, extracted_dir: Path) -> List[Path]:
        """
        Find all video files in extracted directory.

        Args:
            extracted_dir: Path to extracted files directory

        Returns:
            List[Path]: List of video file paths
        """
        video_extensions = [".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".webm"]
        video_files = []

        for file_path in extracted_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in video_extensions:
                video_files.append(file_path)

        # Sort for consistent ordering
        video_files.sort(key=lambda x: x.name)
        return video_files
