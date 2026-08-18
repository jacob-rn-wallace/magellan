# One-off provenance script: measures segment_polygons.json (checked in)
# from a local nonpareil clone. nonpareil/ is gitignored (see
# CLAUDE.md/.gitignore) and not needed to use segments.py - only to
# re-derive it. Re-clone with:
#   git clone --depth 1 https://github.com/brouhaha/nonpareil.git
import json
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage import measure

SRC = "/Users/jake/magellan/nonpareil/nui/nut/41c/lcd_segments_template.png"
SEGMENT_COLORS = {
    'a': (255,0,0), 'b': (0,255,0), 'c': (0,0,255), 'd': (255,255,0),
    'e': (255,0,255), 'f': (0,255,255), 'g': (255,128,0), 'h': (255,0,128),
    'i': (128,0,0), 'j': (0,128,0), 'k': (0,0,128), 'l': (127,255,212),
    'm': (233,150,122), 'n': (0,0,0),
}

im = Image.open(SRC).convert("RGB")
arr = np.array(im)
H, W, _ = arr.shape

results = {}
for letter, color in SEGMENT_COLORS.items():
    mask = np.all(arr == np.array(color), axis=-1)
    lbl, num = ndimage.label(mask, structure=np.ones((3,3)))
    best = None
    for i in range(1, num+1):
        blob = (lbl == i)
        ys, xs = np.nonzero(blob)
        w = xs.max()-xs.min(); h = ys.max()-ys.min()
        if w > 0.85*W or h > 0.85*H:
            continue
        size = blob.sum()
        if best is None or size > best[0]:
            best = (size, i)
    size, i = best
    blob = (lbl==i).astype(np.uint8)
    # pad to avoid edge contour issues
    padded = np.pad(blob, 1)
    contours = measure.find_contours(padded, 0.5)
    contours.sort(key=len, reverse=True)
    contour = contours[0] - 1  # undo pad; contour is (row=y, col=x) pairs
    # simplify
    simplified = measure.approximate_polygon(contour, tolerance=1.6)
    # convert to (x,y) and round
    pts = [[round(float(x),1), round(float(y),1)] for y,x in simplified]
    # drop duplicate closing point
    if pts[0] == pts[-1]:
        pts = pts[:-1]
    results[letter] = pts
    print(letter, len(pts), "verts:", pts)

with open("/Users/jake/magellan/hp41-display/tools/segment_polygons.json","w") as f:
    json.dump(results, f, indent=2)
