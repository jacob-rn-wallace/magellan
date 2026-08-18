"""
Renders a text string as a row of HP-41-style 14-segment display cells.

Two layers of "data" this module consumes, kept deliberately separate so
the visual style and the character mapping can be iterated independently:

  - data/segments.py    geometry: where the 14 segments (+ punctuation
                         marks) are, in one reference-size cell
  - data/charset_41.py  which segments are lit for a given character

This module only knows how to lay cells out in a row and turn the chosen
segments into SVG/PNG. It has no calculator-specific knowledge itself.
"""

import io
import sys
from dataclasses import dataclass, field
from typing import Optional

from data.segments import (
    SEGMENTS,
    SEGMENT_ORDER,
    CELL_WIDTH,
    CELL_HEIGHT,
    DECIMAL_POINT,
    COMMA,
    COLON,
)
from data.charset_41 import CHAR_SEGMENTS, GAP_PUNCTUATION

_GAP_MARKS = {".": DECIMAL_POINT, ",": COMMA, ":": COLON}

# Default rendering knobs. All colors are CSS color strings.
LIT_COLOR = "#1a1a1a"
UNLIT_COLOR = "#1a1a1a"
UNLIT_OPACITY = 0.08
BACKGROUND_COLOR = "#c9d6b8"  # a muted LCD-glass green; None for transparent
CELL_GAP_FRAC = 0.28          # inter-cell gap, as a fraction of CELL_WIDTH
MARGIN_FRAC = 0.18            # outer margin, as a fraction of CELL_WIDTH
DEFAULT_PX_PER_UNIT = 0.22    # "1x" pixel scale of the CELL_WIDTH/HEIGHT units


@dataclass
class RenderOptions:
    lit_color: str = LIT_COLOR
    unlit_color: str = UNLIT_COLOR
    show_ghost: bool = True
    unlit_opacity: float = UNLIT_OPACITY
    background_color: Optional[str] = BACKGROUND_COLOR
    cell_gap_frac: float = CELL_GAP_FRAC
    margin_frac: float = MARGIN_FRAC
    italic: bool = True  # segments.py already bakes in the slant; False un-shears


@dataclass
class _Cell:
    lit: frozenset
    marks: list = field(default_factory=list)  # list of polygon-lists (already positioned)


def layout(text: str) -> list:
    """Turn a string into a list of _Cell objects. Decimal point / comma /
    colon attach to the previous cell instead of creating a new one, matching
    how the real hardware's punctuation dots work (see charset_41.py)."""
    cells: list = []
    for ch in text:
        if ch in GAP_PUNCTUATION:
            if not cells:
                cells.append(_Cell(lit=frozenset()))  # leading punctuation: blank cell first
            cells[-1].marks.append(_GAP_MARKS[ch])
            continue
        segs = CHAR_SEGMENTS.get(ch)
        if segs is None:
            print(f"warning: no glyph for {ch!r}, rendering blank cell", file=sys.stderr)
            segs = frozenset()
        cells.append(_Cell(lit=segs))
    return cells


def _polygon_svg(points, fill, opacity=1.0):
    pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    op = "" if opacity >= 1.0 else f' fill-opacity="{opacity:.3f}"'
    return f'<polygon points="{pts}" fill="{fill}"{op}/>'


def _unshear(points):
    """Undo the italic shear baked into segments.py, for italic=False."""
    from data.segments import ITALIC_SLANT_DEG
    import math
    slant = math.tan(math.radians(ITALIC_SLANT_DEG))
    return [(x - slant * (CELL_HEIGHT - y), y) for x, y in points]


def render_svg(text: str, options: RenderOptions = None) -> str:
    options = options or RenderOptions()
    cells = layout(text)
    if not cells:
        cells = [_Cell(lit=frozenset())]

    gap = options.cell_gap_frac * CELL_WIDTH
    margin = options.margin_frac * CELL_WIDTH
    pitch = CELL_WIDTH + gap

    total_w = margin * 2 + len(cells) * CELL_WIDTH + (len(cells) - 1) * gap
    total_h = margin * 2 + CELL_HEIGHT

    px_w = round(total_w * DEFAULT_PX_PER_UNIT)
    px_h = round(total_h * DEFAULT_PX_PER_UNIT)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{px_w}" height="{px_h}" viewBox="0 0 {total_w:.2f} {total_h:.2f}">'
    ]

    if options.background_color:
        parts.append(f'<rect x="0" y="0" width="{total_w:.2f}" height="{total_h:.2f}" '
                      f'fill="{options.background_color}"/>')

    xform = (lambda pts: pts) if options.italic else _unshear

    for idx, cell in enumerate(cells):
        ox = margin + idx * pitch
        oy = margin
        group = [f'<g transform="translate({ox:.2f},{oy:.2f})">']

        if options.show_ghost:
            for seg_id in SEGMENT_ORDER:
                pts = xform(SEGMENTS[seg_id])
                group.append(_polygon_svg(pts, options.unlit_color, options.unlit_opacity))

        for seg_id in SEGMENT_ORDER:
            if seg_id in cell.lit:
                pts = xform(SEGMENTS[seg_id])
                group.append(_polygon_svg(pts, options.lit_color))

        for mark in cell.marks:
            # marks are authored upright in segments.py and never sheared,
            # regardless of options.italic (dots have no strong slant cue)
            for poly in mark:
                group.append(_polygon_svg(poly, options.lit_color))

        group.append("</g>")
        parts.append("".join(group))

    parts.append("</svg>")
    return "".join(parts)


def render_png(text: str, out_path: str, options: RenderOptions = None, scale: float = 1.0) -> None:
    """Render to a PNG file at `out_path`. `scale` multiplies the default
    raster resolution (vector geometry stays exact, so this is true
    high-resolution output, not upscaled pixels)."""
    import os
    os.environ.setdefault("DYLD_LIBRARY_PATH", "/opt/homebrew/lib:/usr/local/lib")
    import cairosvg  # imported lazily so `--out foo.svg` never needs cairo installed

    svg_str = render_svg(text, options)
    cairosvg.svg2png(bytestring=svg_str.encode("utf-8"), write_to=out_path, scale=scale)


def render_to_file(text: str, out_path: str, options: RenderOptions = None, scale: float = 1.0) -> None:
    """Dispatch on the output file extension: .svg writes vector markup
    directly, anything else is rasterized to PNG via cairosvg."""
    if out_path.lower().endswith(".svg"):
        with open(out_path, "w") as f:
            f.write(render_svg(text, options))
    else:
        render_png(text, out_path, options, scale=scale)
