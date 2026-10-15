"""Which parts of the cloud are in front of the ladder and the man -> assets/clouds_front.png

    python3 tools/clouds_front.py assets/clouds.webp assets/clouds_front.png

The page draws the cloud twice: once behind the 3D scene and once, masked by this matte, on top of it.
The matte picks the brighter, bulging puffs (brighter than their surroundings at the puff scale), which
read as the nearer ones, so the ladder and the man go behind them and come out in the shadowed gaps.
Along the ladder's column (under the peak) the stretches are set by hand (BEHIND), and each switch
follows the outline of the puff there, so he goes into the cloud at the top of a lit puff and comes
out at its lower edge. Saved at half size: it is soft anyway.
Needs: numpy, opencv-python, pillow.
"""
import sys
import cv2
import numpy as np
from PIL import Image

PEAK_X = 438                       # the ladder's column in the cut-out (SKY.PEAK.x in index.html)
src, dst = sys.argv[1], sys.argv[2]
im = np.asarray(Image.open(src)).astype(np.float32) / 255.
rgb, a = im[..., :3], im[..., 3]
H, W = a.shape
L = rgb @ np.array([.3, .59, .11], np.float32)
w = (a > .6).astype(np.float32)
def blur(x, s):                     # blur that ignores the transparent sky
    return cv2.GaussianBlur(x * w, (0, 0), s) / np.maximum(cv2.GaussianBlur(w, (0, 0), s), 1e-4)
loc = blur(L, 7) - blur(L, 48)     # puffs brighter than their surroundings

xx = np.arange(W, dtype=np.float32)[None, :]
yy = np.arange(H, dtype=np.float32)[:, None]

# everywhere: the brighter, nearer puffs are in front (the man falls through these)
m = np.clip((loc + .02) / .04, 0, 1)
m = m * m * (3 - 2 * m)

# along the ladder: behind the cloud / in front of it by stretches, switching at puff edges.
# Going down the column: behind the lit top puffs, out at their lower edge, behind the lit puff
# at rows ~235-300, out again, then behind the lower puff group down to the base (where he starts).
BEHIND = [(0, 166), (232, 304), (440, H)]          # rows (cut-out px) where ladder and man are behind
target = np.zeros((H, 1), np.float32)
for r0, r1 in BEHIND:
    target[r0:r1] = 1
target = cv2.GaussianBlur(target, (1, 0), sigmaX=0.1, sigmaY=9)   # soft across each switch...
puff = np.clip(loc / .05 + .5, 0, 1)                               # ...where the puff shapes decide
ladder = np.clip(target + (puff - .5) * 1.6 * (1 - np.abs(2 * target - 1)), 0, 1)
strip = np.clip((75 - np.abs(xx - PEAK_X)) / 30, 0, 1)
m = m * (1 - strip) + ladder * strip
m = cv2.GaussianBlur(m, (0, 0), 2) * np.clip((a - .5) / .4, 0, 1)

half = cv2.resize(m, ((W + 1) // 2, (H + 1) // 2), interpolation=cv2.INTER_AREA)
Image.fromarray((half * 255).astype(np.uint8)).save(dst, optimize=True)
print(f"saved {dst}; {m[a > .9].mean():.0%} of the cloud is in front")
