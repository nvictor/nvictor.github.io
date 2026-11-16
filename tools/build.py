#!/usr/bin/env python3
"""Build the static showcase into dist/. Media comes from src/media (refresh with tools/sync_media.py)."""
import json, shutil, sys, html, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
args = ap.parse_args()
MEDIA = ROOT / "src/media"
DIST = ROOT / "dist"
projects = json.loads((ROOT / "src/projects.json").read_text())
content = json.loads((ROOT / "src/content.json").read_text())
e = html.escape
KIND = {"app": "macOS apps", "notation": "Notation systems", "demo": "Demo effects"}
KIND_ONE = {"app": "macOS app", "notation": "Notation system", "demo": "Demo effect"}
GH = "https://github.com/nvictor/"

if DIST.exists():
    shutil.rmtree(DIST)
(DIST / "assets").mkdir(parents=True)
shutil.copy(ROOT / "src/style.css", DIST / "assets/style.css")

for p in projects:
    m = p.get("media")
    if m:
        src = MEDIA / f"{p['slug']}{Path(m['src']).suffix}"
        if not src.exists():
            sys.exit(f"missing media: {src}")
        ext = src.suffix
        out = f"media/{p['slug']}{ext}"
        (DIST / "media").mkdir(exist_ok=True)
        shutil.copy(src, DIST / out)
        m["out"] = out

def page(title, body, depth, desc):
    b = "../" * depth
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="stylesheet" href="{b}assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header><nav aria-label="Main"><a class="brand" href="{b}index.html">nvictor</a><a href="{b}projects/index.html">All projects</a></nav></header>
<main id="main">
{body}
</main>
<footer><p>Source for each project is on <a href="https://github.com/nvictor">GitHub</a>.</p></footer>
</body>
</html>
"""

def card(p, depth):
    b = "../" * depth
    return (f'<li><a class="card" href="{b}projects/{p["slug"]}/index.html">'
            f'<span class="kind">{KIND_ONE[p["kind"]]}</span>'
            f'<strong>{e(p["name"])}</strong><span>{e(p["tagline"])}</span></a></li>')

def write(rel, text):
    f = DIST / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text)

stand = [p for p in projects if p.get("standout")]
body = ('<h1>Apps, notations, and demos</h1>'
        '<p class="lead">macOS apps, notation systems, and TIC-80 demo effects.</p>'
        '<h2>Standouts</h2><ul class="grid">' + "".join(card(p, 0) for p in stand) + '</ul>'
        '<p><a href="projects/index.html">See all %d projects</a></p>' % len(projects))
write("index.html", page("nvictor", body, 0, "macOS apps, notation systems, and TIC-80 demo effects."))

body = '<h1>All projects</h1>'
for k, label in KIND.items():
    items = [p for p in projects if p["kind"] == k]
    body += f'<h2>{label}</h2><ul class="grid">' + "".join(card(p, 1) for p in items) + '</ul>'
write("projects/index.html", page("All projects", body, 1, "Full collection of projects."))

for p in projects:
    d = 2
    b = "../" * d
    h = f'<p class="kind">{KIND_ONE[p["kind"]]}</p><h1>{e(p["name"])}'
    if p.get("full"):
        h += f' <small>{e(p["full"])}</small>'
    h += f'</h1><p class="lead">{e(p["tagline"])}</p><p>{e(p["summary"])}</p>'
    m = p.get("media")
    if m:
        h += f'<figure><img src="{b}{m["out"]}" alt="{e(m["alt"])}" loading="lazy"></figure>'
    if p.get("example"):
        h += f'<h2>Example</h2><pre><code>{e(p["example"])}</code></pre>'
    if p.get("version"):
        h += f'<p>Version {e(p["version"])}.</p>'
    if p.get("features"):
        h += '<h2>What it does</h2><ul>' + "".join(f"<li>{e(f)}</li>" for f in p["features"]) + '</ul>'
    for n in p.get("notes", []):
        h += f"<p>{e(n)}</p>"
    if p.get("requirements"):
        h += f'<p>Requires {e(p["requirements"])}</p>'
    c = content.get(p["slug"], {})
    labels = [("problem", "The problem"), ("decisions", "Key design decisions"), ("lessons", "Lessons learned")]
    mine = [(l, c[k]) for k, l in labels if c.get(k)]
    if mine:
        h += '<section class="mine">'
        for l, t in mine:
            h += f"<h2>{l}</h2><p>{e(t)}</p>"
        h += "</section>"
    links = [f'<a href="{GH}{p["slug"]}">Source on GitHub</a>']
    if p["kind"] == "app":
        links.insert(0, f'<a href="{GH}{p["slug"]}/releases/latest">Download the latest release</a>')
    h += '<p class="links">' + " &middot; ".join(links) + "</p>"
    h += f'<p><a href="{b}projects/index.html">Back to all projects</a></p>'
    write(f"projects/{p['slug']}/index.html", page(p["name"], h, d, p["tagline"]))

print(f"built {len(projects)} project pages, size {sum(f.stat().st_size for f in DIST.rglob('*') if f.is_file())//1024} KiB")
