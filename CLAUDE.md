# CLAUDE.md — Magellan

## What this is

Magellan is a personal-reference project for producing an accurate,
original rendering of the HP-41C/CV/CX's 14-segment alphanumeric display —
both as high-resolution offline mockups (the `hp41-display/` Python tool,
built first) and, longer-term, as the actual visual design driving a new
piece of hardware: a quad-register 400x240 Sharp Memory LCD add-on for
**soynut** (`/Users/jake/soynut`, a separate repo — an HP-41 emulator
running on a Raspberry Pi Pico 2). Magellan is not an emulator and does not
touch soynut's code directly; it's the geometry/character-table source of
truth that soynut's own build tooling will eventually consume (see "The
bigger picture" below).

Everything here is for personal reference use, not redistribution. No
copyrighted asset files (images, ROMs, KML) from any reference project have
been copied into this repo — geometry was measured/analyzed locally from a
reference image and redrawn as original vector art; the character table was
transcribed as data (see licensing note below) with full provenance kept in
code comments.

## Repo layout

- `hp41-display/` — the actual deliverable: a Python CLI that renders HP-41
  FOCAL-charset strings as clean vector/raster 14-segment display images.
- `nonpareil/` — a shallow clone of Eric Smith's
  [brouhaha/nonpareil](https://github.com/brouhaha/nonpareil) (GPLv2 code /
  CC-BY-SA 2.5 `ncd/` tree), kept around locally purely as a research
  reference (see below for what was actually found in it). Gitignored, not
  committed to this repo — per the same convention soynut follows (treat
  other repos' code as a black box, don't host/maintain a second copy of
  it), re-clone it yourself if you need to re-derive geometry/charset data:
  `git clone --depth 1 https://github.com/brouhaha/nonpareil.git`. Not a
  dependency of anything here; safe to delete if disk space matters, nothing
  in `hp41-display/`
  reads from it at runtime.

## `hp41-display/` — the rendering tool

### What it does

`render.py "12,345.67" --out display.png --scale 4x` renders a string as a
row of 14-segment cells, SVG natively (`--out foo.svg`) or rasterized to PNG
via `cairosvg`. Options: `--lit-color`, `--unlit-color`, `--unlit-opacity`,
`--no-ghost`, `--background none` (transparent), `--gap`, `--margin`,
`--no-italic`.

```
hp41-display/
  data/segments.py       - segment geometry (the visual style)
  data/charset_41.py     - character -> segment mapping (which segments light up)
  hp41display/renderer.py - SVG builder + PNG export
  render.py              - CLI entry point
  tools/                 - one-off analysis scripts used to derive segments.py (see below)
  .venv/                 - cairosvg + pillow already installed
```

Geometry and character data are deliberately separate files so the visual
style (`segments.py`) can be restyled without touching what each character
looks like (`charset_41.py`), and vice versa.

### Segment geometry (`data/segments.py`)

**Key finding, worth remembering**: the HP-41's actual display is a
"sunburst" 14-segment layout, *not* the generic rectangular 14-segment font
(split top/bottom bars) that Wikipedia's "Fourteen-segment display" article
describes as the general case. It's an **unsplit hexagonal outer ring** (6
bars: top, upper-right, lower-right, bottom, lower-left, upper-left) plus an
**8-arm inner asterisk** (split middle-horizontal, split middle-vertical,
and 4 diagonals) that all meet at one shared center point — the classic look
of HP's "Nut" calculator series displays. This was confirmed by locally
analyzing (bounding boxes, centroids, simplified polygon contours — see
`tools/extract_polygons.py`) the color-coded segment template shipped in
Nonpareil (`nui/nut/41c/lcd_segments_template.png`, 123x133px, one segment
per flat RGB color per the project's own KML-based rendering technique). The
analysis script only ever read that local image to measure proportions —
nothing from it was copied into this repo.

The geometry in `segments.py` is **original, parametrically-generated
vector art** informed by those measurements, not a bitmap trace: each of the
6 outer bars is a flat-cut trapezoid between two corner points, each of the
8 inner arms is a wedge tapering to a point at dead center (all 14 meeting
cleanly with no seam), all tunable via constants at the top of the file
(`CELL_WIDTH`/`CELL_HEIGHT` = 1000/1350 reference units,
`OUTER_HALF_THICK_FRAC`, `INNER_HALF_THICK_FRAC`, `OUTER_GAP_FRAC`,
`DIAGONAL_REACH`, etc.).

**Italic slant**: also measured from the reference, not assumed — comparing
the centroid of the top bar to the bottom bar in the reference template
gives a horizontal offset of ~7.2px over a ~100px cell height, i.e. `atan`
≈ 4 degrees, leaning top-right. Baked in as `ITALIC_SLANT_DEG = 4.0`, applied
as a shear anchored at the cell's bottom (baseline stays put, top leans
right) — confirmed against real photos to be the correct lean direction.

**Decimal point / comma / colon** (`DECIMAL_POINT`, `COMMA`, `COLON`) are
small original shapes, *not* part of the 14-segment glyph — on the real
hardware these are dedicated marks living in the gap between character
cells (confirmed: no dedicated glyph for `.`/`,`/`:` exists anywhere in
Nonpareil's 128-entry FOCAL chargen table). They're defined centered on
`x = CELL_WIDTH` (the cell's right edge / the inter-cell gap), so the
renderer can draw them with the exact same per-cell transform it uses for
the 14 real segments — no separate offset math needed.

### Character table (`data/charset_41.py`)

Transcribed from Nonpareil's `ncd/41c/41cv.ncd.tmpl` (an XML `<chargen>`
table, CC-BY-SA 2.5, Copyright 2006/2008 Eric Smith), 128 entries covering
`@`, A-Z, digits, punctuation, a-z, and some Greek/math symbols. Full
provenance and exceptions are documented in the module docstring; the
short version of what's worth remembering:

- **The table is keyed by the literal displayed character, not any numeric
  code.** This was a deliberate, load-bearing decision: Nonpareil's XML
  `id="0x.."` attribute is the LCD driver chip's internal chargen-ROM
  address, a hardware indexing scheme — it is **not** the same as the
  7-bit FOCAL character code used in ALPHA strings that Wikipedia's "FOCAL
  character set" article documents (confirmed empirically: Wikipedia's
  table has `0x41` = uppercase `A`; Nonpareil's chargen ROM has `0x41` =
  lowercase `a`). Comparing the two tables by numeric id is invalid; only
  comparing by the actual glyph identity is safe, hence keying by character.
- Wikipedia's FOCAL character set page does **not** document segment-level
  on/off patterns at all (confirmed by direct fetch) — it was only useful
  for cross-checking character *identities* (e.g. confirming the 41-series
  table vs. the revised 42S table on the same page are genuinely different
  tables), not segment shapes.
- A handful of source entries had no usable ASCII text (Nonpareil's own
  author left them as a bare `"?"` placeholder, explained only in an XML
  comment — mostly the calculator's animated "hangman" BUSY-indicator
  frames, which are intentionally omitted here as not real display
  characters). Where the comment clearly identified a real symbol (Greek
  letters, angle, not-equal), it's included here keyed by its natural
  Unicode character instead — a curatorial choice made in this repo, not
  something Nonpareil itself specifies a text form for. `μ ≠ Σ ∠ π α β γ σ
  λ δ` — see the module docstring for exactly which source id each came
  from.
- Two small corrections made against the source: `0x7d}` is labeled
  `text=")"` in Nonpareil's XML but its comment says "right brace" and its
  segment pattern doesn't match the *other* `)` entry at `0x29` — corrected
  to `}` here to pair with `{` at `0x7b`. A second unlabeled `"?"` (at
  `0x3f`, pattern `abfhj`) was dropped as an unresolved duplicate of the
  real question mark (kept at `0x1e`, pattern `abkn`).
- `ALL_SEGMENTS_ON` (all 14 lit — the "starburst" LCD test pattern) and
  `GAP_PUNCTUATION = {".", ",", ":"}` are exported separately from the main
  character dict.

### Renderer (`hp41display/renderer.py`)

Lays cells out left-to-right (`CELL_GAP_FRAC`/`MARGIN_FRAC` control
spacing), draws all 14 segments faintly first as "ghosting" (the real LCD's
visible-but-unlit segment outlines) if `show_ghost`, then the actually-lit
segments on top, then any attached gap-marks. `.`/`,`/`:` in the input
string attach to the *previous* cell's mark list instead of creating a new
cell — matches real hardware behavior (a `"12,345.67"`-style string doesn't
waste a cell per punctuation mark).

### macOS setup gotcha (already solved, don't re-solve it)

`cairosvg` needs the native `cairo` library. Homebrew has it
(`/opt/homebrew/lib/libcairo.2.dylib`) but Python's `ctypes.util.find_library`
doesn't search Homebrew's lib path by default, so a bare `import cairosvg`
fails with "no library called cairo" even though it's installed.
`renderer.py`'s `render_png()` already works around this by setting
`os.environ.setdefault("DYLD_LIBRARY_PATH", "/opt/homebrew/lib:/usr/local/lib")`
before importing `cairosvg` — no action needed, just don't be confused if
you see this error outside of `render.py` (e.g. testing `cairosvg` directly
in a fresh shell).

## The bigger picture: soynut + quad-register display integration

The actual goal driving this project: build a **new, separate physical
unit** — soynut's emulator core driving a 400x240 Sharp Memory LCD
(LS027B7DH01) via SPI from a Pico 2, instead of soynut's current 144x32
NHD14432 (ST7920, 8-bit parallel), showing **all four stack registers
(T/Z/Y/X)** at once instead of just X.
Magellan's `data/segments.py`/`data/charset_41.py` are meant to become the
authoritative source that a new build-time Python generator (living in
soynut, not here) rasterizes into a precomputed C pixel-lookup table — the
same idiom soynut's existing `font-tables/gen_display_tables.py` already
uses for its current display, just fed by Magellan's vector geometry
instead of a hand-authored pixel mask.

**Full plan**: `/Users/jake/.claude/plans/gentle-mapping-dewdrop.md`
(5 phases — summarized below since plan files aren't guaranteed durable).

### Why this isn't starting from zero

soynut already has almost exactly the register-decode logic this needs,
just wired to the wrong (tiny, 144x32) display. A dormant "Elite User Mode"
easter egg (`firmware/hp41_elite_display_bridge.c`, triggered by a hidden
`XEQ ALPHA L E E T ALPHA` key sequence) decodes T/Z/Y/X directly from the
emulator's raw RAM (`espaceRAM[8200]`, a flat array of 8-byte registers —
`emu41gcc` has no C-level "stack" concept at all, it's pure Nut-CPU
microcode; T/Z/Y/X live at fixed indices 0/1/2/3, each register 8 bytes:
byte 0 = write-protect flag, bytes 1-7 = 14 packed BCD nibbles) into a
`hp41_elite_number_t {mantissa_negative, mantissa_digits[10],
exponent_negative, exponent_tens, exponent_units}` via
`hp41_elite_decode_register(stack_index, &out)` — pure logic, no hardware
access, already host-testable. **This is the exact function the new
display's framebuffer-compute code will call.**

**Known risk, not yet resolved**: soynut's `CLAUDE.md` records that Elite
Mode reached real hardware once and hit two undiagnosed bugs — the ALPHA
annunciator getting stuck lit, and "the elite grid always showing all
zeros no matter what was actually on the stack." Neither has been
investigated. The stuck-annunciator bug lives specifically in Elite Mode's
key-bridge trigger/interception machinery, which the new display's design
deliberately avoids reusing at all (it always shows the 4-register view, no
toggle needed) — but the "always zero" bug could mean
`hp41_elite_decode_register()` itself misbehaves against real ROM-computed
values (its existing host tests only ever poke synthetic byte patterns
directly into `espaceRAM`, never real ROM output). Per the user's explicit
direction, diagnosing this is Phase 0 of the plan, done first and cheaply
on the *existing* NHD14432 hardware, before any new display code depends
on the decode function.

### The 5 phases (see the plan file for full detail)

- **Phase 0 — diagnose the Elite Mode bug.** Temporary `dbg()`
  instrumentation added to soynut's `firmware/main.c` render block, calling
  `hp41_elite_decode_register()` for T/Z/Y/X unconditionally (never
  triggers the buggy toggle machinery) and printing the decoded values
  alongside the existing per-frame checksum log. **Status: code written and
  building cleanly under soynut's strict `-Wall -Wextra -Wpedantic -Werror`
  flags (confirmed via `ninja soynut` in `firmware/build/`), but not yet
  flashed or tested — no Pico is currently connected to this machine.**
  Once connected: reflash via `picotool reboot -f -u` (forces BOOTSEL) +
  `cp firmware/build/soynut.uf2 /Volumes/RP2350/` (soynut's own documented,
  scriptable reflash pattern — no physical button-press needed), drive
  known key sequences via soynut's `tools/hp41_keyboard_gui.py`, compare
  printed values against expected stack contents over USB serial.
- **Phase 1 — Sharp LCD hardware bring-up sandbox** (independent of Phase
  2, not yet started). New standalone `quad_bringup/` directory in soynut,
  mirroring its existing `lcd_bringup/` sandbox pattern (permanent, not a
  staging area). Vendors exactly 4 files from
  `/Users/jake/pico_sharpmem_display-main` (LGPL-2.1, already confirmed
  working on real Pico-2 + LS027B7DH01 hardware by that repo's own prior
  session): `sharpdisp.c/h` + `bitmap.c/h` — nothing else from that library
  (no fonts/shapes/text/console layers; this project always writes packed
  1bpp buffers directly, matching soynut's existing style). **Watch for**:
  the Sharp panel's polarity is the *opposite* of soynut's current ST7920
  convention — `clear_byte = 0xFF`, and a lit/visible (dark) segment means
  *clearing* the bit, not setting it. Easy to get backwards on first
  bring-up.
- **Phase 2 — 400x240 segment font-table generation** (independent of
  Phase 1, not yet started). New Python generator living in soynut
  (`font-tables/gen_quad_segment_table.py`), importing this repo's
  `data/segments.py`/`data/charset_41.py` directly, rasterizing each
  polygon at a chosen cell pixel size via point-in-polygon fill, and
  emitting a C header in the same flattened-pixel-array shape as soynut's
  existing `gen_display_tables.py` output. Uses this repo's own `render.py`
  to preview the chosen 400x240 layout before committing cell sizes.
- **Phase 3 — shared register-decode extraction + new framebuffer bridge**
  (not yet started). Small refactor: pull `hp41_elite_decode_register()`
  out of `hp41_elite_display_bridge.c` into its own hardware-agnostic
  module so the new display doesn't need to compile in Elite Mode's
  144x32-specific pixel-plotting code just to reuse one function. New pure,
  host-testable `hp41_quad_display_compute_framebuffer()`.
- **Phase 4 — new `quad/` firmware build target** (not yet started). New
  top-level directory in soynut, sibling to `firmware/`, own CMakeLists.txt
  modeled on it. First use of `hardware_spi` anywhere in soynut. Needs a
  new periodic-forced-refresh mechanism (reusing soynut's existing
  heartbeat idiom in `main.c`) since the Sharp LCD's VCOM/DC-bias health
  requires periodic refreshing even when idle — the ST7920 never needed
  this (it has its own GDRAM).

### soynut conventions worth remembering when working in that repo

- NASA/JPL "Power of 10" style: **no function pointers**, minimal
  conditional compilation, bounded loops. Display-backend selection is done
  by which `.c` files a given build target compiles, never `#ifdef` or a
  vtable.
- Every existing display path is precomputed-pixel-table lookup, zero
  floating point/polygon math at runtime — the new QUAD path should match
  this, which is exactly why Phase 2 rasterizes Magellan's vector geometry
  at Python build time rather than drawing polygons on-device.
- `sim/sim_main.c` (a full second `main.c`, "adapted line-by-line" from
  `firmware/main.c`) is the established precedent for Phase 4's new
  main-loop variant.
- soynut is GPL-2.0-or-later; LGPL-2.1 (the Sharp LCD library's license)
  is explicitly compatible with static-linking into a GPL program — not a
  gray area, just keep the vendored files' license headers/text intact.

## Status as of last session

`hp41-display/` is complete and verified (digits, full alphabet,
punctuation, negative numbers, transparent/no-ghost render options all
tested visually). The soynut integration plan is approved and Phase 0's
code change is written and compiles, but real-hardware verification is
blocked on the Pico 2 being connected to this machine. Phases 1-4 not
started.
