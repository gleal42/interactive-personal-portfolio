"""Cut the cloud out of a sky photo -> assets/clouds.webp (transparent background).

    python3 tools/clouds.py photo.png assets/clouds.webp

1. Fit a smooth 2D polynomial to the sky (iteratively ignoring the cloud) to know the sky colour
   behind every pixel.
2. Alpha comes from how far each pixel is from that sky colour: a solid core (holes filled, thin
   haze streaks below the base dropped) plus a soft ramp at the edges, so wisps stay wispy.
3. Colour decontamination: F = (P - (1-a) * sky) / a removes the blue sky from the soft edges, and
   hidden pixels under alpha 0 get nearby cloud colours so filtering never pulls in a fringe.

The script also prints the sky colour per photo row: those are the gradient stops in index.html.
Needs: numpy, scipy, opencv-python, pillow.
"""
import sys
import cv2
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

src, dst = sys.argv[1], sys.argv[2]
a = cv2.imread(src)[:, :, ::-1].astype(np.float32)
H, W, _ = a.shape

# 1. smooth sky model
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
X, Y = xx / W - .5, yy / H - .5
Bm = np.stack([X**i * Y**j for i in range(5) for j in range(5 - i)], -1)
sky = np.ones((H, W), bool)
sky[int(H * .49):int(H * .91), :int(W * .98)] = False      # first guess: the cloud's box
for _ in range(6):
    m = sky[::3, ::3].ravel()
    A = Bm[::3, ::3].reshape(-1, Bm.shape[-1])[m]
    B = np.zeros_like(a)
    for c in range(3):
        coef, *_ = np.linalg.lstsq(A, a[::3, ::3, c].ravel()[m], rcond=None)
        B[:, :, c] = Bm @ coef
    d = np.sqrt(((a - B) ** 2).sum(-1))
    sky = d < 14

# 2. alpha
ell = lambda n: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (n, n))
core = cv2.morphologyEx((d > 42).astype(np.uint8), cv2.MORPH_CLOSE, ell(7))
core = ndi.binary_fill_holes(core)
lab, n = ndi.label(core)
areas = ndi.sum(core, lab, range(1, n + 1))
keep = np.zeros_like(core)
for i, ar in enumerate(areas, 1):
    if ar > .15 * core.sum():
        keep |= lab == i                                       # the cloud itself, not the streaks
core = ndi.binary_fill_holes(cv2.morphologyEx(keep.astype(np.uint8), cv2.MORPH_CLOSE, ell(15)))
soft = np.clip((d - 12) / (55 - 12), 0, 1)
soft = soft * soft * (3 - 2 * soft)
inner = cv2.GaussianBlur(cv2.erode(core.astype(np.uint8), ell(9)).astype(np.float32), (0, 0), 3)
zone = cv2.GaussianBlur(cv2.dilate(core.astype(np.uint8), ell(21)).astype(np.float32), (0, 0), 5)
al = np.clip(np.maximum(inner, soft) * zone, 0, 1)

# 3. decontaminate edges
aa = np.maximum(al, 1e-3)[..., None]
F = np.clip((a - (1 - aa) * B) / aa, 0, 255)
def spread(img, mask, sigma):
    num = cv2.GaussianBlur(img * mask[..., None], (0, 0), sigma)
    den = cv2.GaussianBlur(mask, (0, 0), sigma)[..., None]
    return num / np.maximum(den, 1e-5), den
Fb, den = spread(F, (al > .35).astype(np.float32), 6)
w = np.clip((al - .15) / .35, 0, 1)[..., None]
F = np.where(den > 1e-3, w * F + (1 - w) * Fb, F)
fill, _ = spread(F, (al > .3).astype(np.float32), 18)
w = np.clip(al / .08, 0, 1)[..., None]
F = np.clip(w * F + (1 - w) * fill, 0, 255)

# crop to the cloud and save
ys, xs = np.where(al > .01)
pad = 6
y0, x0 = max(0, ys.min() - pad), max(0, xs.min() - pad)
y1, x1 = min(H, ys.max() + 1 + pad), min(W, xs.max() + 1 + pad)
rgba = np.dstack([F, al * 255]).astype(np.uint8)[y0:y1, x0:x1]
Image.fromarray(rgba).save(dst, quality=90, method=6, exact=True)
print(f"saved {dst}: {x1 - x0}x{y1 - y0}, first photo row {y0}")
print("sky colour by photo row (centre column):")
for y in (0, 400, y0, 1050, 1300, 1420, H - 1):
    if y < H:
        print(f"  {y:5d}", tuple(int(v) for v in B[y, W // 2]))
