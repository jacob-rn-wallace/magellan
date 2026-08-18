#!/usr/bin/env python3
"""
CLI for rendering HP-41-style 14-segment alphanumeric display strings.

Examples:
    ./render.py "12,345.67" --out display.png --scale 4x
    ./render.py "HELLO" --out hello.svg
    ./render.py "-3.14159" --out pi.png --scale 8x --background none
    ./render.py "8.8.8.8.8.8." --out ghost-test.png --unlit-opacity 0.15
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hp41display.renderer import RenderOptions, render_to_file


def _parse_scale(value: str) -> float:
    m = re.fullmatch(r"\s*([0-9]*\.?[0-9]+)\s*x?\s*", value, re.IGNORECASE)
    if not m:
        raise argparse.ArgumentTypeError(f"invalid --scale value: {value!r} (expected e.g. '4' or '4x')")
    return float(m.group(1))


def _parse_color(value: str):
    if value.lower() in ("none", "transparent"):
        return None
    return value


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("text", help="string to render")
    p.add_argument("--out", required=True, help="output path; .svg for vector, anything else rasterizes to PNG")
    p.add_argument("--scale", type=_parse_scale, default=1.0,
                   help="raster resolution multiplier for PNG output, e.g. 4x (default: 1x)")
    p.add_argument("--lit-color", default=RenderOptions.lit_color, help="color of lit segments")
    p.add_argument("--unlit-color", default=RenderOptions.unlit_color, help="color of unlit/ghost segments")
    p.add_argument("--unlit-opacity", type=float, default=RenderOptions.unlit_opacity,
                   help="opacity of unlit segment ghosting, 0-1 (default: %(default)s)")
    p.add_argument("--no-ghost", action="store_true", help="omit faint unlit-segment outlines entirely")
    p.add_argument("--background", type=_parse_color, default=RenderOptions.background_color,
                   help="background color, or 'none' for transparent")
    p.add_argument("--gap", type=float, default=RenderOptions.cell_gap_frac,
                   help="inter-cell gap, as a fraction of cell width (default: %(default)s)")
    p.add_argument("--margin", type=float, default=RenderOptions.margin_frac,
                   help="outer margin, as a fraction of cell width (default: %(default)s)")
    p.add_argument("--no-italic", action="store_true", help="render upright instead of the default italic slant")

    args = p.parse_args()

    options = RenderOptions(
        lit_color=args.lit_color,
        unlit_color=args.unlit_color,
        show_ghost=not args.no_ghost,
        unlit_opacity=args.unlit_opacity,
        background_color=args.background,
        cell_gap_frac=args.gap,
        margin_frac=args.margin,
        italic=not args.no_italic,
    )

    render_to_file(args.text, args.out, options, scale=args.scale)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
