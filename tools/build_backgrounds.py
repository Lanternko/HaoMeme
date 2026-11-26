"""Pack the built-in photo backgrounds, and the red paint drawn behind the
"crash" and "nope" lettering, into backgrounds.js as base64 WebP.

Like portraits.js, they are embedded so the page also works from file://
(separately loaded images would taint the canvas and block PNG export).

    python tools/build_backgrounds.py      # needs pillow
"""
import base64
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
W, H = 1280, 720


def smoke():
    """Blue smoke and light bars: the left half of the hoodie photo (clear of
    the person, who starts at x=1019) with its mirror image laid beside it."""
    im = Image.open(ROOT / "src_photos" / "hoodie.jpg").convert("RGB")
    half = im.crop((0, 0, 1005, im.height))
    both = Image.new("RGB", (half.width * 2, half.height))
    both.paste(half, (0, 0))
    both.paste(ImageOps.mirror(half), (half.width, 0))
    return ImageOps.fit(both, (W, H), Image.LANCZOS)


def room():
    """Grey out-of-focus room behind the 律師傳票 cover: Gemini redrew it from
    the cover with the text, the person and the paint taken out."""
    im = Image.open(ROOT / "src_photos" / "sue_bg.jpg").convert("RGB")
    return ImageOps.fit(im, (W, H), Image.LANCZOS)


def red_paint(name, solid=1.0, tint=None):
    """Red paint on white: turn the white into transparency.
    The paint is red, so the green channel says how much paint covers a pixel;
    the colour is then the paint with the white taken back out.
    solid: paint this strong or stronger is fully opaque (lower for flat colour,
    so the dark picture behind does not show through it).
    tint: one flat colour for all the paint, keeping only its brush texture."""
    im = Image.open(next((ROOT / "src_photos").glob(name + ".*"))).convert("RGB")
    im = im.resize((1100, round(im.height * 1100 / im.width)), Image.LANCZOS)
    px = np.asarray(im).astype(np.float32) / 255
    a = 1 - np.minimum(px[..., 1], px[..., 2])
    a = np.clip((a - .06) / (solid - .06), 0, 1)                  # paper grain and compression noise
    rgb = (px - (1 - a[..., None])) / np.maximum(a[..., None], 1e-3)
    if tint:
        rgb = np.broadcast_to(np.array(tint, np.float32) / 255, rgb.shape)
    out = np.dstack([np.clip(rgb, 0, 1), a])
    return Image.fromarray((out * 255 + .5).astype(np.uint8), "RGBA")


def pack(table, var):
    out = {}
    for key, make in table.items():
        buf = io.BytesIO()
        make().save(buf, "WEBP", quality=88, method=6)
        out[key] = "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()
        print(key, len(buf.getvalue()) // 1024, "KB")
    return f"window.{var} = " + json.dumps(out) + ";\n"


# brush key -> its picture in src_photos/ (any image type); a missing one is left out
# and the page falls back to drawing that brush itself
# (the "sue" pictures were drawn by Gemini after the 律師傳票 cover: the red swoosh
# under the last line, the black smear behind the first, the three yellow dashes;
# the red is painted over in the cover's brighter red)
BRUSHES = {"crash": ("red_brush",), "nope": ("nope_block", .9),
           "sue": ("sue_red", 1.0, (246, 18, 28)), "sueSmear": ("sue_smear",), "sueSpark": ("sue_spark",)}

dst = ROOT / "backgrounds.js"
dst.write_text(pack({"smoke": smoke, "room": room}, "BACKGROUNDS") + pack({key: (lambda a=args: red_paint(*a)) for key, args in BRUSHES.items()
                                                       if any((ROOT / "src_photos").glob(args[0] + ".*"))}, "BRUSHES"), encoding="utf-8")
print(dst)
