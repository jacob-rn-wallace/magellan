# Magellan

A personal-reference project for producing an accurate, original rendering
of the HP-41C/CV/CX's 14-segment alphanumeric display.

It's built in two parts:

- **`hp41-display/`** — a Python CLI that renders HP-41 FOCAL-charset
  strings as clean vector/raster 14-segment display images. This is the
  actual deliverable and is complete.
- Longer-term, the same geometry/character-table data is meant to become
  the source of truth for a new piece of hardware: a quad-register 400x240
  Sharp Memory LCD add-on for [soynut](https://github.com/jacob-rn-wallace/soynut),
  an HP-41 emulator running on a Raspberry Pi Pico 2. Magellan doesn't
  touch soynut's code directly — it's geometry data that soynut's own
  build tooling consumes.

The display is a "sunburst" 14-segment layout (an unsplit hexagonal outer
ring plus an 8-arm inner asterisk, all meeting at one center point) — the
classic look of HP's "Nut" calculator series, not the generic split-bar
14-segment font most references describe. The geometry is original,
parametrically-generated vector art informed by locally measuring a
reference image, not a bitmap trace.

## Usage

```
cd hp41-display
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python render.py "12,345.67" --out display.png --scale 4x
```

```
./render.py "HELLO" --out hello.svg
./render.py "-3.14159" --out pi.png --scale 8x --background none
```

Run `render.py --help` for the full set of options (colors, ghosting,
spacing, italic slant).

## Repo layout

```
hp41-display/
  data/segments.py        - segment geometry (the visual style)
  data/charset_41.py      - character -> segment mapping
  hp41display/renderer.py - SVG builder + PNG export
  render.py                - CLI entry point
  tools/                    - one-off analysis scripts used to derive segments.py
nonpareil/                  - gitignored research reference, not committed
```

## Provenance

No copyrighted asset files (images, ROMs, KML) from any reference project
are copied into this repo. Segment geometry was measured/analyzed locally
from a reference image and redrawn as original vector art. The character
table is transcribed as data from Nonpareil's `41cv.ncd.tmpl`
(CC-BY-SA 2.5, Copyright 2006/2008 Eric Smith) with full provenance kept
in the module docstring. See `CLAUDE.md` for the full technical writeup,
including how the geometry was derived and cross-checked.
