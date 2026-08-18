"""
Character-to-segment mapping for the HP-41C/CV/CX FOCAL character set.

Segment ids ('a'..'n') match data/segments.py and refer to the "sunburst"
14-segment layout described there.

SOURCE / PROVENANCE
--------------------
The segment-on/off pattern for each character was transcribed from the
"coconut_lcd" chargen table in Eric Smith's Nonpareil project:

    https://github.com/brouhaha/nonpareil
    ncd/41c/41cv.ncd.tmpl  (CC-BY-SA 2.5, Copyright 2006, 2008 Eric Smith)

That XML table is keyed by the LCD driver chip's internal character-ROM
address (a hardware index, e.g. id="0x41"), NOT by the 7-bit FOCAL
character code used in ALPHA strings/programs -- those are two different
numbering spaces. Wikipedia's "FOCAL character set" article documents the
*logical* 7-bit code table (which byte value produces which glyph) but,
as of this writing, does not give segment-level on/off patterns; it was
used here only to cross-check character identities (e.g. confirming the
HP-41C/CV/CX table is the intended one, distinct from the revised HP-42S
table on the same page), not segment shapes.

Because of that id/code mismatch, this module is keyed directly by the
displayed character itself (the "text" field in the source table), which
is the only unambiguous, source-independent identifier. A handful of
source entries had no usable ASCII "text" (shown as a bare "?" placeholder
for glyphs the Nonpareil author described only in a comment, e.g. Greek
letters or the calculator's animated "hangman" BUSY indicator). Where the
comment unambiguously identified a real symbol, it's included here keyed
by its natural Unicode character (noted per entry below); purely
animation-only glyphs (hangman frames, an unlabeled "unknown" entry, and
two unlabeled ambiguous "?" duplicates) are intentionally omitted.

The decimal point and comma are NOT in this table. On the real hardware
they are dedicated dots living in the gap between character cells rather
than full 14-segment glyphs -- see DECIMAL_POINT / COMMA in
data/segments.py and how renderer.py attaches them to the previous cell.
Likewise ':' has no dedicated 14-segment glyph in the source ROM table;
it's rendered the same way, as a small stacked-dot punctuation mark.
"""

# {character: "on segments"} -- e.g. "abc" means segments a, b, and c are
# lit and all others are off. Order within the string doesn't matter.
_RAW = {
    # --- uppercase letters (source ids 0x01-0x1a) ---
    "@": "abdefhi",
    "A": "abcefgh",
    "B": "abcdhij",
    "C": "adef",
    "D": "abcdij",
    "E": "adefgh",
    "F": "aefgh",
    "G": "acdefh",
    "H": "bcefgh",
    "I": "adij",
    "J": "bcde",
    "K": "efgkm",
    "L": "def",
    "M": "bcefkl",
    "N": "bceflm",
    "O": "abcdef",
    "P": "abefgh",
    "Q": "abcdefm",
    "R": "abefghm",
    "S": "acdfgh",
    "T": "aij",
    "U": "bcdef",
    "V": "efkn",
    "W": "bcefmn",
    "X": "klmn",
    "Y": "jkl",
    "Z": "adkn",

    # --- brackets / punctuation (source ids 0x1b-0x2f) ---
    "[": "adef",        # reuses the 'C' shape; source gives no closer bracket glyph
    "\\": "lm",
    "]": "abcd",
    "?": "abkn",         # source id 0x1e; a second unlabeled "?" at 0x3f (pattern
                          # "abfhj") was dropped as an unresolved duplicate
    "_": "d",
    " ": "",
    "!": "ij",
    '"': "fi",           # source comments this shape "???" (uncertain) but keeps it
    "#": "bcdghij",
    "$": "acdfghij",
    "%": "cfghklmn",
    "&": "acdklmn",
    "'": "i",
    "(": "km",
    ")": "ln",
    "*": "ghijklmn",
    "+": "ghij",
    "-": "gh",
    "/": "kn",

    # --- digits (source ids 0x30-0x39) ---
    "0": "abcdefkn",     # slashed zero, distinguishes from letter O
    "1": "bc",
    "2": "abdegh",
    "3": "abcdgh",
    "4": "bcfgh",
    "5": "acdhl",
    "6": "acdefgh",
    "7": "abc",
    "8": "abcdefgh",
    "9": "abcdfgh",

    # --- more punctuation (source ids 0x3b-0x3e) ---
    ";": "gn",
    "<": "dkn",
    "=": "dgh",
    ">": "dlm",

    # --- lowercase letters (source ids 0x41-0x45, 0x66-0x7a) ---
    "a": "cdegm",
    "b": "cdefgh",
    "c": "degh",
    "d": "bcdegh",
    "e": "deg",
    "f": "hjk",
    "g": "cdhm",
    "h": "cefgh",
    "i": "e",
    "j": "cd",
    "k": "efghm",
    "l": "ef",
    "m": "cghj",
    "n": "cgh",
    "o": "cdegh",
    "p": "efgl",
    "q": "fglm",
    "r": "egh",
    "s": "dhm",
    "t": "ghim",
    "u": "cde",
    "v": "en",
    "w": "en",           # source gives 'v' and 'w' the identical pattern
    "x": "ghjn",
    "y": "cdm",
    "z": "dgn",

    # --- braces (source ids 0x7b, 0x7d) ---
    "{": "hkm",
    "}": "gln",          # source labels this text=")" but comments "right brace";
                          # corrected here to pair with '{' at 0x7b

    # --- Greek letters / math symbols identified by source comments,
    #     keyed by their natural Unicode character (source itself only
    #     gave these a bare "?" placeholder text) ---
    "μ": "bhin",     # mu     (source id 0x4c, comment "MIC Greek mu")
    "≠": "dghkn",    # ne     (source id 0x4d, comment "NOT not equal")
    "Σ": "adln",     # Sigma  (source id 0x4e, comment "SIG Greek Sigma")
    "∠": "djkn",     # angle  (source id 0x4f, comment "ANG angle symbol")
    "π": "ghmn",     # pi     (source id 0x50, comment "DC1 Greek pi")
    "α": "dmn",      # alpha  (source id 0x51, comment "BEL Greek alpha")
    "β": "adgkmn",   # beta   (source id 0x52, comment "BAC Greek beta")
    "γ": "ghj",      # gamma  (source id 0x53, comment "HTA Greek gamma")
    "σ": "eghn",     # sigma  (source id 0x55, comment "VTA Greek sigma")
    "λ": "lmn",      # lambda (source id 0x5e, comment "DC3 Greek lamda")
    "δ": "dkmn",     # delta  (source id 0x7c, comment "DEL delta")
}

# {character: frozenset(segment ids)} -- what renderer.py actually consumes.
CHAR_SEGMENTS = {ch: frozenset(pattern) for ch, pattern in _RAW.items()}

# Every segment lit -- the classic LCD test/"starburst" pattern (source id
# 0x3a). Not tied to any particular character; exposed for --test-pattern
# style use.
ALL_SEGMENTS_ON = frozenset("abcdefghijklmn")

# Characters that render as a small mark in the gap after the *previous*
# cell rather than as their own full 14-segment glyph (see segments.py).
GAP_PUNCTUATION = {".", ",", ":"}
