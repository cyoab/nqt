import argparse
import sys
from pathlib import Path

from nqt.core import SUPPORTED_EXTENSIONS, build_output_path, change_speed


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="nqt",
        description="Speed up or slow down audio files with pitch preservation.",
    )
    parser.add_argument(
        "file",
        type=Path,
        help="Input audio file (.wav or .mp3)",
    )

    speed_group = parser.add_mutually_exclusive_group(required=True)
    speed_group.add_argument(
        "--up",
        type=float,
        metavar="FACTOR",
        help="Speed up by factor (e.g. 1.5)",
    )
    speed_group.add_argument(
        "--down",
        type=float,
        metavar="FACTOR",
        help="Slow down by factor (e.g. 2 means half speed)",
    )

    parser.add_argument(
        "--out",
        type=str,
        metavar="PATH",
        help="Output file path or directory",
    )

    args = parser.parse_args()

    input_path: Path = args.file
    if not input_path.exists():
        print(f"Error: File '{input_path}' not found", file=sys.stderr)
        sys.exit(1)

    ext = input_path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        print(
            f"Error: Unsupported format '{ext}'. Supported: .wav, .mp3",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.up is not None:
        speed_factor = args.up
    else:
        speed_factor = 1.0 / args.down

    if not (0.1 <= speed_factor <= 100.0):
        print(
            "Error: Speed factor must be between 0.1 and 100.0",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        output_path = build_output_path(input_path, speed_factor, args.out)
        change_speed(input_path, speed_factor, output_path)
        print(output_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
