"""Cut portraits out of the original YouTube thumbnails.

Usage (needs `pip install "rembg[cpu]" pillow numpy`):
    python tools/cutout.py            # all portraits
    python tools/cutout.py A F        # only these keys

All coordinates are full-frame pixels of the 1280x720 thumbnail.

Each entry:
  crop     region handed to the background remover
  kill     polygons over the headline text; forced transparent
  restore  the body outline where the text hides it (usually a shoulder),
           traced along where the edge would run. It is always kept opaque;
           where it overlaps kill it is repainted with the shirt colour.
  src      where to sample that shirt colour (keep skin and hands out of it)
  keep     body parts the background remover wrongly drops; forced opaque
  model    optional rembg model override
Output: portraits/<key>.png (RGBA, trimmed to the visible area).
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from rembg import new_session, remove

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src_thumbs"
OUT = ROOT / "portraits"
MODEL = "isnet-general-use"
# Repaint the shoulder parts the headline hides? Off: those parts are made up,
# so the cutout stops at the text instead.
REPAINT = False

PORTRAITS = {
    "A": dict(vid="bqZrUzdVzaM", crop=(0, 0, 700, 720), model="u2net",  # isnet drops the raised hand
              kill=[[(585, 100), (700, 100), (700, 645), (628, 645), (628, 585), (525, 578), (525, 355), (585, 345)]],
              restore=[[(460, 495), (520, 510), (565, 540), (600, 575), (625, 630), (655, 710), (660, 720), (460, 720)]],
              src=[[(330, 520), (500, 520), (560, 600), (600, 720), (330, 720)]]),
    "C": dict(vid="ZvAMTs781zc", crop=(0, 0, 660, 720),
              kill=[[(490, 70), (660, 70), (660, 578), (590, 585), (500, 568), (494, 330)]],
              restore=[[(460, 425), (510, 450), (555, 480), (585, 520), (597, 560), (600, 590), (470, 590)]],
              src=[[(360, 430), (480, 520), (600, 600), (615, 710), (330, 710)]]),
    "D": dict(vid="JMeeuJU0_Bk", crop=(0, 0, 570, 720),  # the shoulder runs on past the text
              kill=[[(442, 90), (570, 90), (570, 720), (405, 720), (405, 425), (422, 395), (442, 372)]],
              restore=[[(400, 330), (460, 328), (505, 340), (535, 365), (550, 410), (556, 500), (560, 620),
                        (562, 720), (400, 720)]],
              src=[[(250, 420), (405, 420), (405, 720), (250, 720)]]),
    "E": dict(vid="wlcXUV9htGM", crop=(440, 0, 1280, 720),
              # wipe stops at the pointing hand's edge
              kill=[[(440, 0), (700, 0), (700, 470), (680, 560), (664, 610), (658, 668), (440, 668)]],
              # dark shirt the background remover lost; the strip below the text is real shirt
              # a rounded shoulder behind the pointing hand
              restore=[[(700, 470), (680, 560), (664, 610), (658, 668), (655, 720), (480, 720), (495, 660),
                        (530, 600), (580, 545), (640, 500)]],
              src=[[(500, 674), (650, 674), (650, 720), (500, 720)]]),
    "F": dict(vid="A6hF2LNIglU", crop=(0, 0, 720, 720),
              # the background remover drops the shoulder at the left edge of the frame
              keep=[[(0, 442), (40, 428), (100, 411), (150, 406), (195, 404), (230, 520), (230, 720), (0, 720)]],
              # everything right of the shoulder line is text or background
              kill=[[(530, 150), (720, 150), (720, 720), (682, 720), (670, 660), (650, 610), (620, 565), (580, 527),
                     (566, 520), (560, 400), (530, 330)]]),
    "G": dict(vid="sDy3Efq-NhY", crop=(0, 0, 620, 720),
              keep=[[(0, 440), (40, 415), (80, 395), (115, 378), (135, 370), (160, 470), (160, 720), (0, 720)]],
              kill=[[(445, 120), (620, 120), (620, 720), (562, 720), (552, 610), (532, 560), (505, 505), (470, 468),
                     (440, 448)]]),
    "H": dict(vid="say5cFD5rLg", crop=(0, 0, 720, 720),
              kill=[[(560, 120), (720, 120), (720, 720), (686, 720), (680, 680), (660, 620), (630, 570), (580, 525),
                     (560, 512)]]),
    "I": dict(vid="g6ZJ36JSn_c", crop=(800, 0, 1280, 720),
              kill=[[(800, 170), (907, 170), (907, 500), (800, 500)]],
              restore=[[(918, 316), (900, 328), (880, 350), (855, 390), (840, 430), (833, 470), (830, 500), (907, 500), (907, 325)]],
              src=[[(915, 340), (1050, 340), (1050, 560), (845, 560), (845, 480)]]),
}


def poly_mask(size, polys, crop):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    for poly in polys:
        d.polygon([(x - crop[0], y - crop[1]) for x, y in poly], fill=255)
    return np.asarray(m) > 127


def push_pull(rgb, known):
    """Fill unknown pixels from the known ones, coarse to fine (no OpenCV needed)."""
    if known.all() or not known.any():
        return rgb.astype(np.float32)
    w = known.astype(np.float32)
    c = rgb.astype(np.float32) * w[..., None]
    levels = []
    while min(w.shape) > 2:
        levels.append((c, w))
        # pad odd sizes with empty pixels; cropping them would throw samples away
        ph, pw = w.shape[0] % 2, w.shape[1] % 2
        c = np.pad(c, ((0, ph), (0, pw), (0, 0)))
        w = np.pad(w, ((0, ph), (0, pw)))
        h2, w2 = w.shape
        c = c.reshape(h2 // 2, 2, w2 // 2, 2, 3).sum((1, 3))
        w = w.reshape(h2 // 2, 2, w2 // 2, 2).sum((1, 3))
    col = c / np.maximum(w, 1e-6)[..., None]
    col[w == 0] = c.sum((0, 1)) / w.sum()               # empty coarse cells: overall average
    for c, w in reversed(levels):
        up = np.repeat(np.repeat(col, 2, 0), 2, 1)[:w.shape[0], :w.shape[1]]
        own = c / np.maximum(w, 1e-6)[..., None]
        k = np.clip(w, 0, 1)[..., None]
        col = own * k + up * (1 - k)
    out = rgb.astype(np.float32).copy()
    out[~known] = col[~known]
    return out


def main(keys):
    sessions = {}
    OUT.mkdir(exist_ok=True)
    for key in keys:
        p = PORTRAITS[key]
        crop, model = p["crop"], p.get("model", MODEL)
        session = sessions.setdefault(model, new_session(model))
        im = Image.open(SRC / f"{p['vid']}.jpg").convert("RGB").crop(crop)
        cut = remove(im, session=session, post_process_mask=True)
        alpha = np.asarray(cut.getchannel("A")).astype(np.float32) / 255
        rgb = np.asarray(im).astype(np.float32)

        kill = poly_mask(im.size, p.get("kill", []), crop)
        body = poly_mask(im.size, p.get("restore", []), crop)
        restore = body & kill
        # stay clear of the text's black glow when sampling the shirt colour
        near = np.asarray(Image.fromarray(kill.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(25))) > 127
        src = poly_mask(im.size, p.get("src", []), crop) & ~near

        if REPAINT and restore.any():
            # repaint the hidden shoulder: shirt colour pulled in from the sample
            # area, blurred so the coarse-to-fine steps don't show, plus a
            # little grain so it doesn't look airbrushed
            fill = push_pull(rgb, src)
            fill_img = Image.fromarray(np.clip(fill, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))
            fill = np.asarray(fill_img).astype(np.float32)
            grain = np.random.default_rng(7).normal(0, 2.5, fill.shape[:2])[..., None]
            # feather the repaint ~10px past the text's edge so neither a seam
            # nor the leftover black glow shows; inside the text it is all repaint
            grow = Image.fromarray(restore.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(15))
            w = np.asarray(grow.filter(ImageFilter.GaussianBlur(5))).astype(np.float32) / 255
            w = np.where(restore, 1.0, w * (body | (alpha > .5)))[..., None]
            rgb = (fill + grain) * w + rgb * (1 - w)

        keep = poly_mask(im.size, p.get("keep", []), crop)
        if REPAINT:
            alpha[kill] = 0
            alpha[body] = 1
        else:
            # only real pixels: the body outline is kept where nothing covers it
            alpha[(body | keep) & ~kill] = 1
            alpha[kill] = 0
        alpha[keep & ~kill] = 1
        a = Image.fromarray((alpha * 255).astype(np.uint8))
        # soften the straight edges the polygons leave behind
        a = a.filter(ImageFilter.GaussianBlur(0.8))
        out = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert("RGBA")
        out.putalpha(a)
        bbox = a.point(lambda v: 255 if v > 8 else 0).getbbox()
        out = out.crop(bbox)
        out.save(OUT / f"{key}.png")
        print(key, out.size, "offset", (crop[0] + bbox[0], crop[1] + bbox[1]))


if __name__ == "__main__":
    main(sys.argv[1:] or list(PORTRAITS))
