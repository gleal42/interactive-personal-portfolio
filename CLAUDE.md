# Gonçalo Leal — personal website

Live: https://gleal42.github.io/interactive-personal-portfolio/ (GitHub Pages, deploys from `main` on every push).
One file does almost everything: `index.html` (HTML, CSS and the three.js scene). How the scene works and which
constants to tweak: see README.md.

## Working on it
- Push changes straight to `main` (that is how Gonçalo wants it); use a `prototype/...` branch only for bigger experiments he wants to compare first.
- Check every visual change on desktop (1440×900) and phone (390×844) before pushing; nothing may overlap the text or the menu.
- three.js r160 loads from jsDelivr; no build step.

## The story (keep it)
A bronze birdcage hangs in a teal sky above a big sunlit cloud. A man modelled on Gonçalo (his face; his green plaid
shirt) climbs a ladder up through the cloud at a normal walking pace, comes in through the floor hatch and holds the
front bars, facing the viewer. A red balloon is tied to the cage's top ring by the door.
"take the first step" → he lets go, opens the door, crouches in the doorway, looks up, unties the balloon and jumps;
a short drop on the slack string, the string snaps taut, and the balloon carries him off on a breeze, out of frame.
Then: *The door was never locked.* + one "let's talk" button + a quiet "watch again".
Returning visitors skip the climb. The take-off must stay smooth (no snap, no pause).

## Design decisions (settled)
- Palette: teal sky, cream type, the photo cloud in its original colours. The deep red balloon is the only saturated colour on the page.
- Logo: a folded flannel shirt in his own plaid (navy + forest-green blocks, blue stripes, cream windowpane, one red thread), made by `tools/shirt_logo.py`. Top left, alone (the hero already says his name). His shirt in the scene uses the same plaid.
- Nav: logo left; work · services · about · contact right.
- Phones: words on the left, cage and its full-length chain on the right.
- Hero copy: "Hi, I'm Gonçalo." / "I design and build software products: for your business, and of my own."
- Contact is LinkedIn only: https://www.linkedin.com/in/goncaloleal ; a small red balloon waits there ("Where to next?").
- Tried and rejected, don't propose again: fog under the cage, a shaded big cloud, a small second cloud, the umbrella, a gold balloon, hand-drawn SVG logos (balloon-ç, cage-G), his name both in the nav and the hero, scroll-shrinking nav, running up the ladder.

## Content rules
- Work entries come from his Notion skills portfolio. Entries marked confidential never name the employer or the car brand ("an automotive software company").
- Never invent outcomes, numbers or quotes.
- Nothing unfinished on the live site: placeholders stay in HTML comments.

## Still to do
- A line or two of his own story in About (placeholder is in an HTML comment).
- More Work entries as he logs them (ideal next: this website, a Power Apps tool, a side project of his own).
- A custom domain.
