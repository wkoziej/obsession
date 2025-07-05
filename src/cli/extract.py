"""
CLI interface for extracting sources from OBS canvas recordings.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from core.extractor import extract_sources


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command line arguments.

    Args:
        args: Optional list of arguments (for testing)

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Extract individual sources from OBS canvas recording",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s recording.mp4 recording.mp4.json
  %(prog)s recording.mp4 metadata.json --output-dir extracted/
  %(prog)s recording.mp4 metadata.json --verbose
        """,
    )

    parser.add_argument("video_file", help="Path to the input video file")

    parser.add_argument("metadata_file", help="Path to the metadata JSON file")

    parser.add_argument(
        "--output-dir",
        help="Custom output directory (default: <video_name>_extracted/)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    return parser.parse_args(args)


def main() -> int:
    """
    Main CLI entry point.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        args = parse_args()

        # Validate input files exist
        video_path = Path(args.video_file)
        metadata_path = Path(args.metadata_file)

        if not video_path.exists():
            print(f"Error: Video file not found: {video_path}", file=sys.stderr)
            return 1

        if not metadata_path.exists():
            print(f"Error: Metadata file not found: {metadata_path}", file=sys.stderr)
            return 1

        # Load metadata
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in metadata file: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error: Failed to read metadata file: {e}", file=sys.stderr)
            return 1

        # Print verbose info if requested
        if args.verbose:
            print(f"Input video: {video_path}")
            print(f"Metadata file: {metadata_path}")
            print(f"Canvas size: {metadata.get('canvas_size', 'Unknown')}")
            print(f"Number of sources: {len(metadata.get('sources', {}))}")
            print()

        # Extract sources
        if args.verbose:
            print("Starting extraction...")

        result = extract_sources(str(video_path), metadata, args.output_dir)

        if result.success:
            print(f"Successfully extracted {len(result.extracted_files)} sources:")
            for file_path in result.extracted_files:
                print(f"  - {file_path}")

            if args.verbose:
                print("\nExtraction completed successfully!")

            return 0
        else:
            print(f"Extraction failed: {result.error_message}", file=sys.stderr)
            return 1

    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
