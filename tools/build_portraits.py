"""Pack portraits/*.png into portraits.js as base64 WebP data URIs.

The page is opened straight from disk (file://), where separately loaded
images would taint the canvas and block PNG export, so they are embedded.

    python tools/build_portraits.py      # needs pillow
"""
import base64
import io
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

# key -> (label, side the portrait sits on by default), in the order the page
# shows them: by shirt colour, dark to light. The page keeps one more slot for
# an uploaded portrait; portraits/C.png, L.png and M.png are left out.
META = {
    "A": ("舉手說教", "left"),       # black
    "E": ("指著你", "right"),
    "J": ("連帽口罩", "right"),
    "N": ("麥克風", "right"),       # src_photos/sue_person_green.jpg, redrawn sharp by Gemini, green keyed out
    "G": ("托腮斜眼", "left"),       # navy
    "H": ("握拳", "left"),
    "K": ("閉眼大叫", "left"),       # khaki
    "F": ("皺眉托腮", "left"),       # beige
    "O": ("托腮沉思", "left"),       # white; src_photos/crash_person_green.jpg, redrawn by Gemini from the 翻車了？ cover, green keyed out
    "D": ("抱頭驚訝", "left"),
    "I": ("雙手抱胸", "right"),
}

# where the original cutout sits inside each widened portrait (tools/find_anchors.py)
anchors_file = ROOT / "portraits" / "anchors.json"
ANCHORS = json.loads(anchors_file.read_text(encoding="utf-8")) if anchors_file.exists() else {}

items = []
for key, (label, side) in META.items():
    im = Image.open(ROOT / "portraits" / f"{key}.png")
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=92, method=6)
    b64 = base64.b64encode(buf.getvalue()).decode()
    items.append({"key": key, "label": label, "side": side, "w": im.width, "h": im.height,
                  "anchor": ANCHORS.get(key), "src": "data:image/webp;base64," + b64})

out = ROOT / "portraits.js"
out.write_text("window.PORTRAITS = " + json.dumps(items, ensure_ascii=False) + ";\n", encoding="utf-8")
print(out, out.stat().st_size // 1024, "KB")
