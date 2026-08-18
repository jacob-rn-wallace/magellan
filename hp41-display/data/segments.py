"""
14-segment character-cell geometry for the HP-41C/CV/CX-style FOCAL display.

This is ORIGINAL vector artwork generated parametrically (not a traced copy
of any single copyrighted asset). The segment *layout* -- which is a real,
physical fact about the 1979 HP-41 LCD glass, not a creative expression --
was cross-checked by locally analyzing (bounding boxes / centroids / rough
polygon shape only, never redistributed) the color-coded segment template
shipped in Eric Smith's Nonpareil project:

    https://github.com/brouhaha/nonpareil
    nui/nut/41c/lcd_segments_template.png  (CC-BY-SA 2.5, (c) Eric Smith)

That analysis established two facts this module encodes:

  1. The HP-41 cell is a "sunburst" 14-segment layout, NOT the generic
     rectangular 14-segment font (split top/bottom bars) described in the
     Wikipedia "Fourteen-segment display" overview. It is an UNSPLIT
     hexagonal outer ring (6 bars: top, upper-right, lower-right, bottom,
     lower-left, upper-left) plus an 8-arm inner asterisk (split middle
     horizontal, split middle vertical, and 4 diagonals) that all meet at
     one shared center point. This is the classic HP "Nut" calculator
     display style used across the 41C/CV/CX and related Voyager/Coconut
     series.

  2. The font is measurably italic. Comparing the centroid of the top bar
     (segment 'a') to the centroid of the bottom bar (segment 'd') in the
     reference template gives a horizontal offset of ~7.2px over a ~100px
     cell height, i.e. an italic slant of ~4 degrees, leaning top-right.
     See ITALIC_SLANT_DEG below.

Segment naming follows Nonpareil's own letter scheme (a..n) since it maps
directly onto the *.ncd chargen tables used for the FOCAL character set
(see data/charset_41.py). This is NOT the same as the generic 14-segment
A/B/C/.../G1/G2 naming sometimes shown on Wikipedia; a translation isn't
needed here since we only ever key by these same letters end to end.

Segment id -> rough description:
    a  top horizontal bar (full width, unsplit)
    b  upper-right side bar
    c  lower-right side bar
    d  bottom horizontal bar (full width, unsplit)
    e  lower-left side bar
    f  upper-left side bar
    g  inner arm: center -> middle-left
    h  inner arm: center -> middle-right
    i  inner arm: center -> top-middle
    j  inner arm: center -> bottom-middle
    k  inner arm: center -> upper-right diagonal
    l  inner arm: center -> upper-left diagonal
    m  inner arm: center -> lower-right diagonal
    n  inner arm: center -> lower-left diagonal
"""

import math

# ---------------------------------------------------------------------------
# Tunable design parameters -- change these to restyle the glyph without
# touching the construction code below.
# ---------------------------------------------------------------------------

# Reference cell size. Everything is defined in this coordinate space and
# scaled at render time, so these can be any convenient round numbers.
CELL_WIDTH = 1000
CELL_HEIGHT = 1350

# Margin between the cell's bounding box and the outer ring, as a fraction
# of CELL_WIDTH / CELL_HEIGHT.
MARGIN_X_FRAC = 0.10
MARGIN_Y_FRAC = 0.03

# Half-thickness of the outer ring bars and the inner asterisk arms, as a
# fraction of CELL_WIDTH.
OUTER_HALF_THICK_FRAC = 0.075
INNER_HALF_THICK_FRAC = 0.060

# Gap left at each joint so adjacent segments don't visually fuse into one
# blob when both are lit, as a fraction of CELL_WIDTH.
OUTER_GAP_FRAC = 0.010

# How far each diagonal inner arm's outer tip sits along the line from the
# center to the corresponding outer corner (1.0 = touches the corner).
DIAGONAL_REACH = 0.86

# How far short of its outer target point each inner arm's flat tip is cut,
# as a fraction of that arm's own length (keeps a visible gap from the ring).
INNER_GAP_FRAC = 0.10

# Italic slant, leaning top-right, measured from the reference template
# (see module docstring). Positive = top shifts right of bottom.
ITALIC_SLANT_DEG = 4.0


# ---------------------------------------------------------------------------
# Construction helpers
# ---------------------------------------------------------------------------

def _straight_bar(p1, p2, half_width, gap):
    """Flat-ended rectangular bar along the segment p1->p2, inset by `gap`
    at each end and offset by `half_width` on each side of the centerline."""
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    s = (p1[0] + ux * gap, p1[1] + uy * gap)
    e = (p2[0] - ux * gap, p2[1] - uy * gap)
    return [
        (s[0] + px * half_width, s[1] + py * half_width),
        (e[0] + px * half_width, e[1] + py * half_width),
        (e[0] - px * half_width, e[1] - py * half_width),
        (s[0] - px * half_width, s[1] - py * half_width),
    ]


def _tapered_arm(center, tip, half_width, gap_frac):
    """Wedge from a point at `center` widening to a flat cut short of `tip`.
    Used for the 8 inner asterisk arms so they all meet cleanly at the
    center point with no seam."""
    dx, dy = tip[0] - center[0], tip[1] - center[1]
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    end = (tip[0] - ux * gap_frac * length, tip[1] - uy * gap_frac * length)
    p1 = (end[0] + px * half_width, end[1] + py * half_width)
    p2 = (end[0] - px * half_width, end[1] - py * half_width)
    return [center, p1, p2]


def _shear(points, height):
    """Apply the italic shear, anchored at the bottom of the cell (y=height)
    so the baseline stays put and the top leans right."""
    slant = math.tan(math.radians(ITALIC_SLANT_DEG))
    return [(x + slant * (height - y), y) for x, y in points]


def build_segments():
    """Return {segment_id: [(x, y), ...]} for all 14 segments, in the
    CELL_WIDTH x CELL_HEIGHT reference space, with italic slant applied."""
    w, h = CELL_WIDTH, CELL_HEIGHT
    mx, my = MARGIN_X_FRAC * w, MARGIN_Y_FRAC * h
    outer_half = OUTER_HALF_THICK_FRAC * w
    inner_half = INNER_HALF_THICK_FRAC * w
    outer_gap = OUTER_GAP_FRAC * w

    tl, tr = (mx, my), (w - mx, my)
    bl, br = (mx, h - my), (w - mx, h - my)
    ml, mr = (mx, h / 2), (w - mx, h / 2)
    tm, bm = (w / 2, my), (w / 2, h - my)
    c = (w / 2, h / 2)

    segments = {
        # outer hexagonal ring
        "a": _straight_bar(tl, tr, outer_half, outer_gap),
        "b": _straight_bar(tr, mr, outer_half, outer_gap),
        "c": _straight_bar(mr, br, outer_half, outer_gap),
        "d": _straight_bar(bl, br, outer_half, outer_gap),
        "e": _straight_bar(bl, ml, outer_half, outer_gap),
        "f": _straight_bar(tl, ml, outer_half, outer_gap),
        # inner asterisk, horizontal + vertical arms
        "g": _tapered_arm(c, ml, inner_half, INNER_GAP_FRAC),
        "h": _tapered_arm(c, mr, inner_half, INNER_GAP_FRAC),
        "i": _tapered_arm(c, tm, inner_half, INNER_GAP_FRAC),
        "j": _tapered_arm(c, bm, inner_half, INNER_GAP_FRAC),
        # inner asterisk, diagonal arms (tips pulled in from the true
        # corners so they don't collide with the a/b/c/d/e/f ring)
        "k": _tapered_arm(c, (c[0] + DIAGONAL_REACH * (tr[0] - c[0]),
                               c[1] + DIAGONAL_REACH * (tr[1] - c[1])), inner_half, INNER_GAP_FRAC),
        "l": _tapered_arm(c, (c[0] + DIAGONAL_REACH * (tl[0] - c[0]),
                               c[1] + DIAGONAL_REACH * (tl[1] - c[1])), inner_half, INNER_GAP_FRAC),
        "m": _tapered_arm(c, (c[0] + DIAGONAL_REACH * (br[0] - c[0]),
                               c[1] + DIAGONAL_REACH * (br[1] - c[1])), inner_half, INNER_GAP_FRAC),
        "n": _tapered_arm(c, (c[0] + DIAGONAL_REACH * (bl[0] - c[0]),
                               c[1] + DIAGONAL_REACH * (bl[1] - c[1])), inner_half, INNER_GAP_FRAC),
    }

    return {seg_id: _shear(pts, h) for seg_id, pts in segments.items()}


# Precomputed once at import time; this is what renderer.py consumes.
SEGMENTS = build_segments()

# Order segments are drawn in (outer ring first, then inner asterisk, so
# joints look clean regardless of anti-aliasing order).
SEGMENT_ORDER = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n"]


# ---------------------------------------------------------------------------
# Auxiliary punctuation marks (decimal point / comma / colon).
#
# On the real HP-41 display these are NOT part of the 14-segment glyph --
# they're small dedicated dots living in the gap between character cells,
# and a "12,345.67"-style string does not consume an extra cell per mark
# (see charset_41.py / renderer.py, which attach these to the *previous*
# cell rather than advancing the cursor). Shapes here are simple original
# glyphs, not derived from any reference asset.
#
# Each mark is a list of one or more polygons, defined in the SAME local
# coordinate frame as this cell's own 14 segments (0..CELL_WIDTH), just
# centered on x=CELL_WIDTH -- i.e. straddling the boundary with the next
# cell's gap, not on top of this cell's own glyph. renderer.py draws these
# with the identical per-cell transform it uses for SEGMENTS, no extra
# offset needed.
# ---------------------------------------------------------------------------

_DOT_SIZE = 0.11 * CELL_WIDTH
_GAP_DOT_X = CELL_WIDTH  # centered on the cell boundary / inter-cell gap
_BASELINE_Y = CELL_HEIGHT - 0.10 * CELL_HEIGHT

def _square_at(cx, cy, half):
    return [(cx - half, cy - half), (cx + half, cy - half),
            (cx + half, cy + half), (cx - half, cy + half)]

# Decimal point: a single square dot on the baseline, straddling the gap.
DECIMAL_POINT = [_square_at(_GAP_DOT_X, _BASELINE_Y, _DOT_SIZE / 2)]

# Comma: the same dot, plus a short tail curling down and to the left.
_tail_dx, _tail_dy = -0.06 * CELL_WIDTH, 0.16 * CELL_HEIGHT
_half = _DOT_SIZE / 2
COMMA = [_square_at(_GAP_DOT_X, _BASELINE_Y, _half) + [
    (_GAP_DOT_X + _half, _BASELINE_Y + _half),
    (_GAP_DOT_X + _half + _tail_dx, _BASELINE_Y + _half + _tail_dy),
]]

# Colon: two stacked dots, straddling the gap, centered vertically in the cell.
_colon_gap = 0.22 * CELL_HEIGHT
COLON = [
    _square_at(_GAP_DOT_X, CELL_HEIGHT / 2 - _colon_gap / 2, _DOT_SIZE / 2),
    _square_at(_GAP_DOT_X, CELL_HEIGHT / 2 + _colon_gap / 2, _DOT_SIZE / 2),
]
