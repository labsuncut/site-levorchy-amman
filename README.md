# Levorchy: website preview

A new website for Levorchy, the haute couture house in Um Uthaina, Amman (founder: Norjan Alkharouf). Built by LabsUncut as a free preview.

Preview: https://labsuncut.github.io/site-levorchy-amman/

## What is here

- `index.html`: home, with the scroll "runway" (six Aurora Bordeaux looks walk toward you)
- `collection.html`: all 35 pieces with filters
- `looks/*.html`: one page per piece, with a WhatsApp "Book a fitting for this piece" button
- `story.html`, `visit.html`, `404.html`
- English and Arabic on every page (the button in the header switches)

## How to change something

All facts live in `business.json` and `data/looks.json`. The pages are written from them by:

    python3 tools/build.py

Run it after any change, then commit the pages it wrote. GitHub Pages serves them as they are.

## Before launch

- Go through `to_confirm` in `business.json` with Zaid.
- Set `PREVIEW = False` in `tools/build.py` (removes the "draft preview" bar and the noindex tag), rebuild.
- Photos and texts come from levorchy.com; we need Levorchy's permission and the original files.
