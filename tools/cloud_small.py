"""Cut the small sunlit cloud he jumps to out of the big cloud (assets/clouds.webp -> assets/cloud_small.webp).

It is a puff from the big cloud's sunlit right side, so its light, colour and grain match exactly.
The crop is faded with a soft, wide oval that is fuller toward the top, plus a flat feathered base,
so it reads as a small cloud of its own floating in the sky.
Also prints where his feet land on it (cut-out px), for SMALL.LAND in index.html.

    python3 tools/cloud_small.py
"""
from PIL import Image
import numpy as np

SRC, OUT = "assets/clouds.webp", "assets/cloud_small.webp"
X0, Y0, X1, Y1 = 690, 292, 940, 478           # the puff, in clouds.webp px

im = np.asarray(Image.open(SRC).convert("RGBA")).astype(float)
c = im[Y0:Y1, X0:X1].copy()
h, w = c.shape[:2]
yy, xx = np.mgrid[0:h, 0:w]

ex = (xx - w * .5) / (w * .54)
ey = (yy - h * .62) / (h * .64)
oval = np.clip((1 - np.sqrt(ex ** 2 + ey ** 2)) / .32, 0, 1)
base = np.clip((h * .9 - yy) / (h * .26), 0, 1)       # flat, soft underside
m = np.minimum(oval, base) ** 1.2
c[..., 3] *= m

# trim empty margins
a = c[..., 3] > 3
ys, xs = np.where(a)
c = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
Image.fromarray(c.astype("uint8"), "RGBA").save(OUT, quality=92, method=6)

# landing spot: a little left of centre, just inside the top edge
al = c[..., 3]
lx = int(c.shape[1] * .46)
ly = int(np.argmax(al[:, lx] > 150)) + 6
print(f"{OUT}: {c.shape[1]}x{c.shape[0]}  land at x={lx} y={ly}")
