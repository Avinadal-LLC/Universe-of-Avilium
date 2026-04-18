# Universe of Avilium — Claude Code Guide

## Project Overview

Static HTML website showcasing characters and lore from the Avilium Universe.
Generated from the **Atlas** content platform (`C:\Avinadal LLC\Atlas`) and deployed via GitHub Pages.

**Live site:** https://avinadal-llc.github.io/Universe-of-Avilium/
**GitHub remote:** https://github.com/Avinadal-LLC/Universe-of-Avilium.git
**License:** CC BY-NC-SA 4.0

## Architecture

This is a **generated static site** — do not edit `index.html`, `characters.html`, `lore.html`,
`characters/*.html`, or `data/search-index.json` directly. All changes must go through the
source files:

| Source | Purpose |
|--------|---------|
| `generate.py` | Main generator — queries Atlas and emits HTML |
| `templates/*.html.j2` | Jinja2 page templates |
| `static/css/style.css` | All styles (brand guide from `avilium-brand-guide.html`) |
| `static/js/filter.js` | Client-side filtering, hamburger nav |

## Regenerating the Site

1. Start Atlas: `cd "C:\Avinadal LLC\Atlas" && uvicorn app.main:app`
2. Install deps (first time): `pip install -r requirements.txt`
3. Generate: `python generate.py`
4. Preview locally: `python -m http.server 3000` → http://localhost:3000
5. Deploy: `git add -A && git commit -m "Regenerate site" && git push origin main`

## Atlas Data Sources

| Source | Data |
|--------|------|
| Atlas API `http://localhost:8000` | Characters, lore entries, tags |
| Atlas DB `postgresql://atlas:atlas@localhost:5432/atlas` | Species/gender labels, tag associations, aliases, relationships |

## Design System

Follows `avilium-brand-guide.html` (at `C:\Users\villa\Downloads\avilium-brand-guide.html`).

**Fonts:** Cinzel (display) · EB Garamond (body) · Space Mono (UI/labels)
**Key colors:** `#08090d` void · `#c8a558` imperial gold · `#4a8fc7` institutional blue
**Myst:** `#c04a6f` (crimson-rose, space) · **Malei:** `#4a7bc7` (azure, time)

## Footer Social Links

The footer links currently use `https://avinadal.com` paths. Update if the actual
platform URLs change:
- Discord: `https://avinadal.com/discord`
- Patreon: `https://avinadal.com/patreon`

## GR Protocol

Track GR scans and apply the Gradual Refinement protocol per global CLAUDE.md.
Last GR scan: _(not yet performed)_
