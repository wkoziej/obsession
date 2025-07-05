#!/usr/bin/env python3
"""
Advanced Scene Switcher integration script for OBSession auto-extraction.
Automatically finds the latest recording and triggers extraction.
"""

import sys
import os
import glob
import datetime
import subprocess
import time
from pathlib import Path


def log_message(message):
    """Log message with timestamp"""
    log_file = Path("/tmp/obsession_auto_extract.log")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

    print(f"[{timestamp}] {message}")


def find_latest_recording():
    """
    Find the most recent OBS recording file.
    Checks common OBS recording locations and formats.
    """
    # Common OBS recording directories
    possible_dirs = [
        Path.home() / "Wideo" / "obs",  # Polish Videos/obs subdirectory
        Path.home() / "Videos" / "obs",  # Videos/obs subdirectory
    ]

    # Common OBS recording formats
    extensions = ["*.mkv", "*.mp4", "*.flv", "*.mov"]

    all_files = []

    for directory in possible_dirs:
        if directory.exists():
            log_message(f"Checking directory: {directory}")
            for ext in extensions:
                # Check both direct files and files in subdirectories
                pattern = str(directory / ext)
                files = glob.glob(pattern)
                log_message(f"  Pattern {pattern}: found {len(files)} files")
                if files:
                    log_message(f"    Files: {files}")
                all_files.extend(files)

                # Also check subdirectories recursively
                pattern_recursive = str(directory / "**" / ext)
                files_recursive = glob.glob(pattern_recursive, recursive=True)
                log_message(
                    f"  Recursive pattern {pattern_recursive}: found {len(files_recursive)} files"
                )
                if files_recursive:
                    log_message(f"    Files: {files_recursive}")
                all_files.extend(files_recursive)
        else:
            log_message(f"Directory does not exist: {directory}")

    log_message(f"Total files found: {len(all_files)}")

    if not all_files:
        log_message("No recording files found")
        return None

    # Find the newest file
    latest_file = max(all_files, key=os.path.getmtime)

    # Check if file was created in the last 2 minutes (fresh recording)
    # Extended from 30 seconds to 2 minutes to account for file writing time
    file_age = time.time() - os.path.getmtime(latest_file)

    log_message(f"Latest file: {latest_file}")
    log_message(f"File age: {file_age:.1f} seconds")

    if file_age > 30:
        log_message("File too old, probably not the recording we want")
        return None

    return latest_file


def run_extraction(recording_file):
    """
    Run OBSession extraction on the recording file.
    """
    log_message(f"Starting extraction for: {recording_file}")

    # Path to OBSession CLI
    cli_path = Path("/home/wojtas/dev/obsession/src/cli/extract.py")

    if not cli_path.exists():
        log_message(f"ERROR: CLI not found at {cli_path}")
        return False

    # Build command with uv run
    cmd = [
        "uv",
        "run",
        "python",
        str(cli_path),
        recording_file,
        "--auto",
        "--verbose",
        "--delay",
        "0",
    ]

    log_message(f"Running command: {' '.join(cmd)}")

    try:
        # Run extraction
        result = subprocess.run(
            cmd,
            cwd="/home/wojtas/dev/obsession",
            capture_output=True,
            text=True,
            timeout=1800,  # 30 minutes max
        )

        # Log output
        if result.stdout:
            log_message(f"STDOUT: {result.stdout}")

        if result.stderr:
            log_message(f"STDERR: {result.stderr}")

        if result.returncode == 0:
            log_message("✅ Extraction completed successfully")
            return True
        else:
            log_message(f"❌ Extraction failed with code: {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        log_message("❌ Extraction timeout (30 minutes)")
        return False
    except Exception as e:
        log_message(f"❌ Extraction error: {e}")
        return False


def main():
    """Main function"""
    log_message("=== OBSession Auto-Extraction Started ===")
    log_message(f"Arguments: {sys.argv}")
    log_message(f"Working directory: {os.getcwd()}")

    # Find latest recording
    recording_file = find_latest_recording()

    if not recording_file:
        log_message("❌ No recent recording file found")
        return 1

    # Run extraction
    success = run_extraction(recording_file)

    if success:
        log_message("🎉 Auto-extraction completed successfully!")
        return 0
    else:
        log_message("💥 Auto-extraction failed!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
