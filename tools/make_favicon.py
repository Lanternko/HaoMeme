"""Make the favicon from portrait C's face: a round red badge like the
「教育我了？」 backdrop, with the face clipped inside.

    python tools/make_favicon.py      # needs pillow, numpy
Writes favicon.ico (16/32/48), favicon-64.png and apple-touch-icon.png (180).
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
S = 720                                     # draw big, then scale down
face = Image.open(ROOT / "portraits" / "C.png").convert("RGBA")
# square around the head (portrait C is 663x712; head spans about x 160-430, y 0-340)
box = (150, 0, 445, 295)                    # tight, so the face still reads at 16 px
head = Image.new("RGBA", (box[2] - box[0], box[3] - box[1]))
head.alpha_composite(face.crop((box[0], max(box[1], 0), box[2], box[3])), (0, max(-box[1], 0)))
head = head.resize((S, S), Image.LANCZOS)

# red radial backdrop
yy, xx = np.mgrid[0:S, 0:S] / S
d = np.clip(np.hypot(xx - .5, yy - .35) / .75, 0, 1)[..., None]
inner, outer = np.array([235, 22, 26]), np.array([70, 4, 8])
bg = (inner * (1 - d) + outer * d).astype(np.uint8)
badge = Image.fromarray(np.dstack([bg, np.full((S, S), 255, np.uint8)]), "RGBA")
badge.alpha_composite(head)

mask = Image.new("L", (S, S), 0)
ImageDraw.Draw(mask).ellipse((0, 0, S - 1, S - 1), fill=255)
icon = Image.new("RGBA", (S, S))
icon.paste(badge, (0, 0), mask)

icon.resize((64, 64), Image.LANCZOS).save(ROOT / "favicon-64.png")
icon.resize((48, 48), Image.LANCZOS).save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
# iOS rounds the corners itself and shows transparency as black, so no circle there
badge.convert("RGB").resize((180, 180), Image.LANCZOS).save(ROOT / "apple-touch-icon.png")
print("done")
