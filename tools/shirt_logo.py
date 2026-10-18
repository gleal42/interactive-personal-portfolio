"""A shop-folded flannel shirt, front view, woven from Gonçalo's plaid. Renders at 2x and downsamples."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

RED = "--red" in sys.argv
SCALE_T = 2.0 if "--bold" in sys.argv else 1.0      # chunkier plaid for tiny sizes
OUT = sys.argv[1]
S = 2                       # supersample
N = 1000 * S
rng = np.random.default_rng(7)

C = {"navy": (30, 38, 62), "ink": (20, 25, 40), "blue": (50, 74, 128), "green": (48, 74, 52),
     "cream": (214, 216, 200), "red": (178, 58, 46)}
# the sett: navy blocks with two blue stripes, green blocks split by a thin cream line
seq = [("ink", 16), ("blue", 3), ("navy", 3), ("blue", 3), ("ink", 16), ("green", 24), ("cream", 2), ("green", 24)]
if RED:
    seq = [("ink", 16), ("blue", 3), ("navy", 1), ("red", 1), ("navy", 1), ("blue", 3), ("ink", 16), ("green", 24), ("cream", 2), ("green", 24)]
stripe = np.concatenate([np.tile(np.array(C[c], float), (n, 1)) for c, n in seq])   # one thread per row
P = len(stripe)

def weave(h, w, unit, ox=0, oy=0):
    """2/2 twill: alternate warp and weft colour on a diagonal; flannel fuzz on top."""
    y, x = np.mgrid[0:h, 0:w]
    tx = ((x + ox) // unit) % P
    ty = ((y + oy) // unit) % P
    warp, weft = stripe[tx], stripe[ty]
    tw = (((x + ox) // unit + (y + oy) // unit) // 2) % 2 == 0
    col = np.where(tw[..., None], warp, weft)
    # where both threads are light (cream crossings), keep it bright; mix a little everywhere (brushed flannel)
    col = .5 * col + .5 * (warp + weft) / 2
    col *= 1 + rng.normal(0, .05, (h, w, 1))
    return col

UNIT = max(1, int(3 * S * SCALE_T))
def tex(h, w, ox=0, oy=0):
    img = Image.fromarray(np.clip(weave(h, w, UNIT, ox, oy), 0, 255).astype(np.uint8))
    return np.asarray(img.filter(ImageFilter.GaussianBlur(1.3 * S))).astype(float)

def mask(poly=None, ell=None, rr=None):
    m = Image.new("L", (N, N), 0); d = ImageDraw.Draw(m)
    if poly: d.polygon([(x * S, y * S) for x, y in poly], fill=255)
    if ell: d.ellipse([v * S for v in ell], fill=255)
    if rr: d.rounded_rectangle([v * S for v in rr[0]], radius=rr[1] * S, fill=255)
    return np.asarray(m).astype(float) / 255

canvas = np.zeros((N, N, 3)); alpha = np.zeros((N, N))
def paint(m, rgb, shade=None):
    global canvas, alpha
    if shade is not None: rgb = rgb * shade[..., None]
    canvas = canvas * (1 - m[..., None]) + rgb * m[..., None]; alpha = np.maximum(alpha, m)

yy, xx = np.mgrid[0:N, 0:N] / N
light = 1.1 - .22 * (xx * .55 + yy * .45)                  # soft light from the upper left
# soft, low wrinkles in the cloth: smooth noise turned into gentle light and shade
_w = Image.fromarray((rng.random((40, 40)) * 255).astype(np.uint8)).resize((N, N), Image.BICUBIC).filter(ImageFilter.GaussianBlur(14 * S))
_w = np.asarray(_w).astype(float) / 255; _w = (_w - _w.mean()) / (_w.std() + 1e-6)
wrinkle = 1 + .045 * _w

# body: a folded rectangle, shoulders sloping gently from the collar
body = mask(poly=[(205, 318), (400, 296), (600, 296), (795, 318), (812, 340), (812, 832), (790, 858), (210, 858), (188, 832), (188, 340)])
side = np.clip(np.minimum(xx * N / S - 188, 812 - xx * N / S) / 46, 0, 1)        # the sides are folded under: darker near the edges
bottom = np.clip((858 - yy * N / S) / 30, 0, 1)
paint(body, tex(N, N, 37 * S, 11 * S), light * wrinkle * (.62 + .38 * np.sqrt(side)) * (.8 + .2 * np.sqrt(bottom)))
# a soft fold across the lower body (the shirt tail turned under)
fold = np.exp(-((yy * N / S - 792) / 7) ** 2) * body
canvas *= (1 - .16 * fold)[..., None]

# inside of the neck: the back of the collar band and the dark inside of the shirt
paint(mask(ell=(386, 212, 614, 330)), tex(N, N, 5 * S, 60 * S), light * .9)
paint(mask(ell=(404, 228, 596, 316)), np.full((N, N, 3), (15, 19, 31.)), light)
# placket down the middle, pattern not quite matching the body (as on a real shirt)
plk = mask(rr=((470, 318, 530, 860), 4))
paint(plk, tex(N, N, 0, 11 * S), light * .97)
for x in (472, 528):                                       # stitching along the placket edges
    paint(mask(rr=((x - .8, 330, x + .8, 852), .8)), np.full((N, N, 3), 255.), light * .55)

def wing(pts, ox, oy):
    m = mask(poly=pts)
    yy2 = yy * N / S
    under = np.clip((yy2 - 280) / 140, 0, 1)                # the collar casts a little shadow on itself toward the tip
    paint(m, tex(N, N, ox, oy), light * (1.04 - .12 * under))
    return m
# shadows the collar wings cast on the body
sh = Image.fromarray((mask(poly=[(502, 322), (400, 266), (380, 282), (440, 420), (500, 392)]) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(9 * S))
sh2 = Image.fromarray((mask(poly=[(498, 322), (600, 266), (620, 282), (560, 420), (500, 392)]) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(9 * S))
for s_ in (sh, sh2):
    a_ = np.roll(np.roll(np.asarray(s_).astype(float) / 255, 8 * S, 0), 4 * S, 1)
    canvas *= (1 - .38 * a_ * body)[..., None]
wing([(502, 324), (398, 262), (376, 276), (434, 412), (470, 404)], 52 * S, 3 * S)
wing([(498, 324), (602, 262), (624, 276), (566, 412), (530, 404)], 15 * S, 3 * S)

def button(cx, cy, r):
    paint(mask(ell=(cx - r - 1.5, cy - r + 1.5, cx + r - 1.5, cy + r + 3)), np.full((N, N, 3), 0.), np.full((N, N), .35))   # its shadow
    paint(mask(ell=(cx - r, cy - r, cx + r, cy + r)), np.full((N, N, 3), (236, 236, 228.)), light)
    paint(mask(ell=(cx - r * .55, cy - r * .55, cx + r * .55, cy + r * .55)), np.full((N, N, 3), (214, 214, 204.)), light)
    for dx in (-r * .28, r * .28):
        paint(mask(ell=(cx + dx - r * .12, cy - r * .12, cx + dx + r * .12, cy + r * .12)), np.full((N, N, 3), (120, 120, 112.)), light)
button(445, 396, 7); button(555, 396, 7)                  # button-down collar points
for by in (470, 600, 730): button(500, by, 10.5)

# soft shadow under the whole shirt, so it sits on something
shadow = Image.fromarray((body * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(16 * S))
sa = np.roll(np.roll(np.asarray(shadow).astype(float) / 255, 16 * S, 0), 8 * S, 1) * .42
out_a = np.maximum(alpha, sa)
rgb = np.where(alpha[..., None] > 0, canvas / np.maximum(alpha[..., None], 1e-3), 0) * (alpha / np.maximum(out_a, 1e-3))[..., None]
img = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), out_a * 255]).astype(np.uint8), "RGBA")
img = img.resize((1000, 1000), Image.LANCZOS)
img.save(OUT)
print("saved", OUT)
