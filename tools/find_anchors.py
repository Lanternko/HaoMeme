"""Find where each original cutout (portraits_orig/<K>.png) sits inside the
widened portrait (portraits/<K>.png) and write portraits/anchors.json.

The page places a portrait by this box, so by default it looks exactly like
the original cutout (the cut side runs off the frame edge) and the extra
shoulder only shows when the portrait is flipped to the other side.

    python tools/find_anchors.py      # needs pillow, numpy, opencv-python
"""
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
D = 4  # search on 1/4 size, then refine at full size


def load(p):
    a = np.asarray(Image.open(p).convert("RGBA")).astype(np.float32)
    return a[..., :3].mean(2), a[..., 3] / 255


def best(new_g, old_g, old_a, scales):
    """Return (score, scale, x, y) of the best masked match of old in new."""
    out = None
    for s in scales:
        w, h = round(old_g.shape[1] * s), round(old_g.shape[0] * s)
        if w > new_g.shape[1] or h > new_g.shape[0]:
            continue
        t = cv2.resize(old_g, (w, h), interpolation=cv2.INTER_AREA)
        m = (cv2.resize(old_a, (w, h), interpolation=cv2.INTER_AREA) > 0.9).astype(np.float32)
        r = cv2.matchTemplate(new_g, t, cv2.TM_SQDIFF, mask=m) / max(m.sum(), 1)
        v, _, loc, _ = cv2.minMaxLoc(r)
        if out is None or v < out[0]:
            out = (v, s, *loc)
    return out


anchors = {}
for p in sorted((ROOT / "portraits_orig").glob("*.png")):
    k = p.stem
    ng, _ = load(ROOT / "portraits" / f"{k}.png")
    og, oa = load(p)
    small = lambda a: cv2.resize(a, (a.shape[1] // D, a.shape[0] // D), interpolation=cv2.INTER_AREA)
    _, s, x, y = best(small(ng), small(og), small(oa), np.arange(0.85, 1.40, 0.01))
    # refine at full size around the coarse hit
    x0, y0 = max(x * D - 12, 0), max(y * D - 12, 0)
    w1, h1 = round(og.shape[1] * (s + 0.015)), round(og.shape[0] * (s + 0.015))
    win = ng[y0:y0 + h1 + 24, x0:x0 + w1 + 24]
    v, s, x, y = best(win, og, oa, np.arange(s - 0.012, s + 0.0121, 0.002))
    w, h = round(og.shape[1] * s), round(og.shape[0] * s)
    anchors[k] = dict(x=x0 + x, y=y0 + y, w=w, h=h)
    print(k, anchors[k], f"scale={s:.3f} err={np.sqrt(v):.1f}", "new size", ng.shape[::-1])

out = ROOT / "portraits" / "anchors.json"
out.write_text(json.dumps(anchors, indent=1), encoding="utf-8")
print(out)
