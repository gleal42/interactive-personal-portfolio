# GL — personal homepage

**Live site: [gleal42.github.io/interactive-personal-portfolio](https://gleal42.github.io/interactive-personal-portfolio/)**

A single-page site built around one image: a man in a birdcage hanging in the sky.
The page opens with him climbing the ladder toward the cage.

- Click **let go** while he is on the ladder and he lets go right there, falling backwards into the clouds.
- Otherwise he climbs up through a hatch in the cage floor, steps off, and sits cross-legged.
  Click **let go** then and he stands up, pushes the door open, crouches through, turns on the
  edge of the cage, leans back on straight arms, lets go, and falls backwards head-first.
- After a fall, clicking again starts the climb over.

> *Sometimes you have to let go of the life you planned to find the life that's waiting for you.*
> (often attributed to Joseph Campbell)

## How it works

- **The sky and the cloud are separate layers.** The cloud is a real photo cut out with a soft, transparent edge
  (`assets/clouds.webp`, made by `tools/clouds.py`). Its peak sits right under the cage; it is big, runs off the
  right edge and continues below the fold, so scrolling down to *about* reveals the rest of it.
  The sky behind it is painted: the gradient sampled from the same photo (dark at the top, lighter toward the
  cloud, warm haze below, deeper again behind *about*), with a little light around the cloud and film grain.
- **In and out of the cloud**: the cloud's brighter, nearer puffs (`assets/clouds_front.png`, made by
  `tools/clouds_front.py`) are drawn again on top of the 3D scene, so the ladder dips behind them and the man
  climbs out of the cloud and falls back into it. Along the ladder the behind/in-front stretches are set by hand
  (`BEHIND` in `tools/clouds_front.py`) and switch at puff edges. The ladder ends, and the climb starts, inside the
  cloud; the climb runs faster while he is completely hidden (`HIDDEN_SPEED`) and is capped at `MAX_CLIMB` seconds.
- **Cage, chain, ladder and the man** are drawn live in 3D with [three.js](https://threejs.org) (r160, loaded from jsDelivr).
- **The face** is projected from four photos (front, left, right, back) onto a head shaped to match them (`assets/face_*.jpg`).
- **Motion**: hands and feet are placed on real points (knees, bars, door frame, rim) and the arms and legs are solved to reach them, so nothing slides. Every joint is lightly smoothed between frames.
- **The fall** is simulated: he tips backwards around his heels under gravity, leaves the rim with that speed, then follows a ballistic arc while air resistance settles him face-up. The cage leans toward his weight and swings back when he's gone.
- The layout adapts to phones: the quote sits above, and the cage is bigger and kept clear of the text.

## Run locally

Any static file server works:

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

Opening `index.html` directly from disk will not load the textures (browsers block that), so use a server.

## Deploy

The site is published with **GitHub Pages** from the `main` branch: every push to `main`
goes live at <https://gleal42.github.io/interactive-personal-portfolio/> within a minute or two.

It is plain static files with no build step, so it also works on Netlify, Vercel or Cloudflare Pages.

To set up Pages on a fork:

1. *Settings → Pages*
2. *Build and deployment → Source:* **Deploy from a branch**
3. *Branch:* **`main`**, folder **`/ (root)`** → **Save**

The site appears at `https://<username>.github.io/<repository>/`.

## Structure

```
index.html           the homepage (HTML, CSS and the three.js scene in one file)
assets/              the cut-out cloud and face textures
style-guide/         the visual style guide (palette, type, motifs, generator prompt)
tools/               Python scripts: cut out the cloud (clouds.py), its front puffs (clouds_front.py), the face textures, the old plate clean-up
```

## Tweaking

Most things are a single constant near the top of the script in `index.html`:

| What | Constant |
|---|---|
| Cage size on wide screens / phones | `CAGE_SCALE_WIDE`, `CAGE_SCALE_TALL` |
| Cage position | `SKY.ANCHOR` |
| The cloud's peak under the cage, the gap, its size | `SKY.PEAK`, `SKY.GAP`, `skyLayout()` |
| Sky colours | `skyRow()` in the background shader |
| Man's size | `FIG_S` |
| Bar thickness | `THICK` |
| Timing of the sequence | the `body` keyframes, `T_STAND` and `T_LET` |
| Climbing speed | `CLIMB_P` (seconds per two rungs) |

## License

© 2026 Gonçalo. **All rights reserved.** The code, design, animation and images are not
open source: you may view them, but not copy, reuse or redistribute them without written
permission. See [LICENSE](LICENSE). This includes `assets/face_*.jpg`, which are photos of
the site's owner.

Third-party parts keep their own licenses: three.js (MIT) and Crimson Pro (SIL OFL 1.1).
