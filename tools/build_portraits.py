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

# key -> (label, side the portrait sits on by default)
META = {
    "A": ("舉手說教", "left"),
    "C": ("托腮沉思", "left"),
    "D": ("抱頭驚訝", "left"),
    "E": ("指著你", "right"),
    "F": ("皺眉托腮", "left"),
    "G": ("托腮斜眼", "left"),
    "H": ("握拳", "left"),
    "I": ("雙手抱胸", "right"),
    "J": ("連帽口罩", "right"),
    "K": ("閉眼大叫", "left"),
    "L": ("傻眼", "left"),
    "M": ("攤手解釋", "right"),
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
