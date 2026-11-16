#!/usr/bin/env python3
"""Copy project media from sibling checkouts into src/media."""
import json, shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
out = ROOT / "src/media"; out.mkdir(exist_ok=True)
for p in json.loads((ROOT / "src/projects.json").read_text()):
    m = p.get("media")
    if m:
        src = ROOT.parent / m["src"]
        shutil.copy(src, out / f"{p['slug']}{src.suffix}")
        print("copied", src)
