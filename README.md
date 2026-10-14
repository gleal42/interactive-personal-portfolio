# GL — personal homepage

A single-page site built around one image: a man in a birdcage hanging in the sky.
Click **let go** and he pushes the door open, crouches through, turns on the edge of the
cage, and leaps backwards into the clouds.

> *Sometimes you have to let go of the life you planned to find the life that's waiting for you.*
> (often attributed to Joseph Campbell)

## How it works

- **Clouds** are a real photo (`assets/plate.jpg`), cleaned of the original cage, ladder and watermark.
- **Cage, chain, ladder and the man** are drawn live in 3D with [three.js](https://threejs.org) (r160, loaded from jsDelivr).
- **The face** is projected from four photos (front, left, right, back) onto a head shaped to match them (`assets/face_*.jpg`).
- **Motion**: hands and feet are placed on real points (bars, door frame, rim) and the arms and legs are solved to reach them, so nothing slides. The jump is a ballistic arc with backward rotation, and the cage recoils from the push.
- The layout adapts to phones: the quote sits above, and the cage is bigger and kept clear of the text.

## Run locally

Any static file server works:

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

Opening `index.html` directly from disk will not load the textures (browsers block that), so use a server.

## Deploy

It is plain static files, so GitHub Pages, Netlify, Vercel or Cloudflare Pages all work with no build step.
For GitHub Pages: *Settings → Pages → Deploy from branch → `main` / root*.

## Structure

```
index.html           the homepage (HTML, CSS and the three.js scene in one file)
assets/              cloud background and face textures
style-guide/         the visual style guide (palette, type, motifs, generator prompt)
tools/               Python scripts used to clean the cloud plate and build the face textures
```

## Tweaking

Most things are a single constant near the top of the script in `index.html`:

| What | Constant |
|---|---|
| Cage size on wide screens / phones | `CAGE_SCALE_WIDE`, `CAGE_SCALE_TALL` |
| Cage position on the photo | `ANCHOR` |
| Man's size | `FIG_S` |
| Bar thickness | `THICK` |
| Timing of the sequence | the `body` keyframes and `T_RELEASE` |

## Note on privacy

`assets/face_*.jpg` are cropped photos of a real person. Keep this repository **private**
unless you are happy for those photos to be public.
