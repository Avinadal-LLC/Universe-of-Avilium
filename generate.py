"""
Universe of Avilium — Static Site Generator

Queries the Atlas API and PostgreSQL DB, then renders Jinja2 templates
into static HTML files for GitHub Pages delivery.

Prerequisites:
  pip install -r requirements.txt
  Atlas API running at http://localhost:8000
  Atlas DB at postgresql://atlas:atlas@localhost:5432/atlas
"""

import json
import sys
from pathlib import Path

try:
    import psycopg2
except ImportError:
    sys.exit("psycopg2 not found. Run: pip install -r requirements.txt")

try:
    import requests
except ImportError:
    sys.exit("requests not found. Run: pip install -r requirements.txt")

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    sys.exit("jinja2 not found. Run: pip install -r requirements.txt")

try:
    from slugify import slugify
except ImportError:
    sys.exit("python-slugify not found. Run: pip install -r requirements.txt")

# ── Configuration ───────────────────────────────────────────────────
BASE_URL = "http://localhost:8000"
DB_URL   = "postgresql://atlas:atlas@localhost:5432/atlas"
OUT      = Path(__file__).parent
TEMPLATES= OUT / "templates"


# ── API helpers ─────────────────────────────────────────────────────
def fetch(path: str) -> list:
    try:
        resp = requests.get(f"{BASE_URL}{path}", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        sys.exit(f"Cannot reach Atlas API at {BASE_URL}. Is it running?")
    except requests.exceptions.HTTPError as e:
        sys.exit(f"API error on {path}: {e}")


# ── DB supplementary data ────────────────────────────────────────────
def fetch_db():
    try:
        conn = psycopg2.connect(DB_URL)
    except psycopg2.OperationalError as e:
        sys.exit(f"Cannot connect to Atlas DB: {e}")

    cur = conn.cursor()

    cur.execute("SELECT id::text, label FROM ref_species")
    species_map = dict(cur.fetchall())

    cur.execute("SELECT id::text, label FROM ref_genders")
    gender_map = dict(cur.fetchall())

    cur.execute("""
        SELECT let.lore_entry_id::text, lt.name
        FROM lore_entry_tags let
        JOIN lore_tags lt ON lt.id = let.tag_id
        ORDER BY lt.name
    """)
    entry_tags: dict = {}
    for eid, tag in cur.fetchall():
        entry_tags.setdefault(eid, []).append(tag)

    cur.execute("""
        SELECT character_id::text, alias, alias_type, is_primary
        FROM character_aliases
        ORDER BY is_primary DESC, alias
    """)
    char_aliases: dict = {}
    for cid, alias, atype, primary in cur.fetchall():
        char_aliases.setdefault(cid, []).append(
            {"alias": alias, "type": atype, "primary": primary}
        )

    cur.execute("""
        SELECT cr.character_id::text, c.name, c.id::text, cr.relationship_type
        FROM character_relationships cr
        JOIN characters c ON c.id = cr.related_character_id
        WHERE c.is_active = TRUE
        ORDER BY cr.relationship_type, c.name
    """)
    char_rels: dict = {}
    for cid, rel_name, rel_id, rel_type in cur.fetchall():
        char_rels.setdefault(cid, []).append(
            {"name": rel_name, "id": rel_id, "type": rel_type}
        )

    cur.close()
    conn.close()
    return species_map, gender_map, entry_tags, char_aliases, char_rels


# ── Data enrichment ──────────────────────────────────────────────────
def enrich_characters(raw: list, species_map, gender_map, char_aliases, char_rels):
    chars = [
        c for c in raw
        if c.get("isActive") and c.get("narrativeLayer") == "canonical"
    ]
    for c in chars:
        c["slug"]          = slugify(c["name"])
        c["species_label"] = species_map.get(c.get("speciesId") or "", "")
        c["gender_label"]  = gender_map.get(c.get("genderId") or "", "")
        c["initials"]      = "".join(w[0] for w in c["name"].split()[:2]).upper()
        bio                = c.get("bio") or ""
        c["bio_excerpt"]   = (bio[:150].rstrip() + "…") if len(bio) > 150 else bio
        c["aliases"]       = char_aliases.get(c["id"], [])
        rels               = char_rels.get(c["id"], [])
        # Group relationships by type
        rel_by_type: dict = {}
        for r in rels:
            rel_by_type.setdefault(r["type"], []).append(r)
        c["relationships"] = rels
        c["rel_by_type"]   = rel_by_type
        c["portrait_url"]  = None   # populated when asset URLs exist in DB
    return chars


def enrich_lore(raw: list, entry_tags, char_by_id):
    entries = [
        e for e in raw
        if e.get("isActive")
        and e.get("narrativeLayer") == "canonical"
        and e.get("visibility") == "public"
        and e.get("canonStatus") != "apocrypha"
    ]
    for e in entries:
        e["tags"]             = entry_tags.get(e["id"], [])
        e["linked_characters"]= [
            char_by_id[cid]
            for cid in e.get("characterIds", [])
            if cid in char_by_id
        ]
        content               = e.get("content") or ""
        e["content_search"]   = content[:500].lower()
        e["title_search"]     = e["title"].lower()
    return entries


# ── Search index ─────────────────────────────────────────────────────
def build_search_index(characters, lore_entries):
    index = []
    for c in characters:
        index.append({
            "type":    "character",
            "title":   c["name"],
            "subtitle":c["species_label"],
            "text":    (c.get("bio") or "")[:300],
            "url":     f"characters/{c['slug']}.html",
            "tags":    [],
            "species": c["species_label"],
        })
    for e in lore_entries:
        index.append({
            "type":    "lore",
            "title":   e["title"],
            "subtitle":" · ".join(e.get("tags", [])),
            "text":    (e.get("content") or "")[:300],
            "url":     f"lore.html#lore-{e['id']}",
            "tags":    e.get("tags", []),
        })
    return index


# ── Rendering ─────────────────────────────────────────────────────────
def render(env, template_name, output_path, **ctx):
    html = env.get_template(template_name).render(**ctx)
    out  = OUT / output_path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"  OK {output_path}")


# ── Main ──────────────────────────────────────────────────────────────
def main():
    print("Fetching from Atlas API…")
    raw_chars = fetch("/characters/")
    raw_lore  = fetch("/lore/")
    all_tags  = fetch("/lore/tags")

    print("Fetching supplementary data from DB…")
    species_map, gender_map, entry_tags, char_aliases, char_rels = fetch_db()

    print("Enriching data…")
    characters = enrich_characters(raw_chars, species_map, gender_map, char_aliases, char_rels)
    char_by_id = {c["id"]: c for c in characters}
    char_id_to_slug = {c["id"]: c["slug"] for c in characters}

    lore_entries = enrich_lore(raw_lore, entry_tags, char_by_id)

    # Lore entries grouped by character for detail pages
    char_lore: dict = {}
    for entry in lore_entries:
        for cid in entry.get("characterIds", []):
            char_lore.setdefault(cid, []).append(entry)

    all_species = sorted({c["species_label"] for c in characters if c["species_label"]})
    tag_names   = sorted(t["name"] for t in all_tags)

    stats = {
        "char_count": len(characters),
        "lore_count": len(lore_entries),
        "tag_count":  len(tag_names),
    }

    print("Rendering templates…")
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=True,
    )

    render(env, "index.html.j2", "index.html",
           root_path="",
           featured_chars=characters[:6],
           **stats)

    render(env, "characters.html.j2", "characters.html",
           root_path="",
           characters=characters,
           all_species=all_species,
           char_count=len(characters))

    render(env, "lore.html.j2", "lore.html",
           root_path="",
           lore_entries=lore_entries,
           tag_names=tag_names,
           lore_count=len(lore_entries))

    for char in characters:
        render(env, "character_detail.html.j2",
               f"characters/{char['slug']}.html",
               root_path="../",
               char=char,
               char_entries=char_lore.get(char["id"], []),
               char_id_to_slug=char_id_to_slug)

    # Search index
    search_index = build_search_index(characters, lore_entries)
    data_dir = OUT / "data"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "search-index.json").write_text(
        json.dumps(search_index, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print("  OK data/search-index.json")

    total = 3 + len(characters)  # index + characters + lore + 20 detail pages
    print(f"\nDone. {total} HTML files generated.")


if __name__ == "__main__":
    main()
