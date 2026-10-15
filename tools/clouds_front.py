"""Which parts of the cloud are in front of the ladder and the man -> assets/clouds_front.png

    python3 tools/clouds_front.py assets/clouds.webp assets/clouds_front.png

The page draws the cloud twice: once behind the 3D scene and once, masked by this matte, on top of it.
The matte picks the brighter, bulging puffs (brighter than their surroundings at the puff scale), which
read as the nearer ones, so the ladder and the man go behind them and come out in the shadowed gaps.
Along the ladder's column (under the peak) the threshold is lowered for longer stretches, a little more
where the climb starts so he can start hidden. Above that (the top of the cloud down to row ~205) the
ladder and the man stay in front: the matte is cleared in a soft strip around the ladder there.
Saved at half size: it is soft anyway.
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
near = np.exp(-((xx - PEAK_X) / 80) ** 2)
start = np.exp(-((yy - 260) / 60) ** 4)
t = -.02 - .035 * near - .08 * near * start
m = np.clip((loc - t) / .04, 0, 1)
m = m * m * (3 - 2 * m)
m = cv2.GaussianBlur(m, (0, 0), 2.5) * np.clip((a - .5) / .4, 0, 1)
# ladder and man in front from the top of the cloud down to the stretch where the climb starts
strip = np.clip((70 - np.abs(xx - PEAK_X)) / 30, 0, 1)
top = np.clip((215 - yy) / 20, 0, 1)
m *= 1 - strip * top

half = cv2.resize(m, ((W + 1) // 2, (H + 1) // 2), interpolation=cv2.INTER_AREA)
Image.fromarray((half * 255).astype(np.uint8)).save(dst, optimize=True)
print(f"saved {dst}; {m[a > .9].mean():.0%} of the cloud is in front")
