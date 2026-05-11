import argparse
import sys
from pathlib import Path
from .parser import vkx2gpx


def main():
    parser = argparse.ArgumentParser(
        prog="vkx2gpx",
        description="Convert Vakaros .vkx files to .gpx format.",
    )
    parser.add_argument("--input", type=Path, required=True, help="Input .vkx file")
    parser.add_argument("--output", type=Path, help="Output .gpx file (default: same name as input)")
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print details about parsed points and marks",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    if args.input.suffix.lower() != ".vkx":
        print(f"Warning: input file does not have a .vkx extension", file=sys.stderr)

    output = args.output or args.input.with_suffix(".gpx")
    vkx2gpx(args.input, output, verbose=args.verbose)


if __name__ == "__main__":
    main()
