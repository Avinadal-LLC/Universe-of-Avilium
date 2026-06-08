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

## Naming Conventions

This project follows the Avinadal Semantic Naming Conventions. Names are ambient documentation — a well-named symbol explains what it does or represents without a comment.

### General Rules

- **Never abbreviate** — `btn`, `nav`, `usr`, `hdr` are banned; spell them out
- **No generic nouns** — `card`, `item`, `data` tell you nothing; qualify them
- **Consistency** — pick one word per concept and use it everywhere

---

### CSS Classes (BEM, fully spelled)

Custom component classes use BEM with fully spelled-out block and element names. No abbreviations in block, element, or modifier names.

```css
/* ❌ */
.char-card {}
.char-card__hdr {}
.btn--pri {}

/* ✅ */
.character-profile-card {}
.character-profile-card__canonical-display-name {}
.character-profile-card__lore-excerpt-for-public-profile {}
.character-profile-card--featured-on-homepage {}
.site-navigation__primary-menu-item {}
.site-navigation__primary-menu-item--currently-active {}
```

Tailwind component compositions also use full semantic names:
```css
@layer components {
  .character-summary-card-for-public-profile-pages { @apply ...; }
  .lore-entry-card-for-character-detail-pages { @apply ...; }
}
```

---

### JavaScript / TypeScript

**Variables and parameters:** domain role, not type
```js
// ❌
const data = await fetch('/chars');
const x = chars.filter(c => c.active);

// ✅
const activeCharactersForPublicGallery = await fetchActiveCharactersForPublicGallery();
const featuredCharactersForHomepageBanner = activeCharacters.filter(character => character.isFeatureOnHomepage);
```

**Functions:** verb-first full phrase
```js
// ❌
function filterChars(chars) {}
function setupNav() {}

// ✅
function filterCharactersBySelectedFactionAndSpecies(characters, selectedFactionId, selectedSpeciesId) {}
function initializePrimaryNavigationWithHamburgerToggle() {}
```

**Booleans:** `is`, `has`, `can`, `should` prefix
```js
// ❌
let active = true;
let loaded = false;

// ✅
let isFilterPanelVisible = true;
let hasCharacterDataFinishedLoading = false;
```

---

### File Names

- Templates: `kebab-case` matching content — `character-detail-page.html.j2`, `lore-entry-card.html.j2`
- Scripts: `kebab-case` describing function — `initialize-filter-panel.js`, `fetch-character-data-for-gallery.js`
- Stylesheets: `kebab-case` — `character-profile-card.css`, `site-navigation.css`

---

### REST Query Parameters (when calling Atlas API)

Explicit, no abbreviations:
```
# ❌
?nl=canonical&p=1

# ✅
?narrative_layer=canonical&page_number=1&results_per_page=20
```

---

## GR Protocol

Track GR scans and apply the Gradual Refinement protocol per global CLAUDE.md.
Last GR scan: _(not yet performed)_
