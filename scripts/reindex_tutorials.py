#!/usr/bin/env python3
"""docs/tutorials/index.json aus allen tutorial.json neu aufbauen.

Nützlich nach dem ZIP-Export aus dem Tutorial-Studio oder nach manuellen
Änderungen. Aufruf:  python3 scripts/reindex_tutorials.py
"""
import json
from pathlib import Path

DST = Path("docs/tutorials")
ORDER = ["Setup", "Geometrie", "Material", "Vernetzung", "Lagerung", "Belastung", "Postprocessing"]


def main():
    register = []
    for sub in sorted(DST.iterdir()):
        tj = sub / "tutorial.json"
        if not sub.is_dir() or not tj.exists():
            continue
        t = json.loads(tj.read_text(encoding="utf-8"))
        steps = t.get("steps", [])
        thumb = None
        for st in steps:
            if st.get("media"):
                thumb = st["media"][0]
                break
        register.append({
            "slug": t.get("slug", sub.name),
            "title": t.get("title", sub.name),
            "category": t.get("category", ""),
            "software": t.get("software", ""),
            "tags": t.get("tags", []),
            "steps": len(steps),
            "thumb": thumb,
        })
    register.sort(key=lambda t: (ORDER.index(t["category"]) if t["category"] in ORDER else 99, t["title"]))
    (DST / "index.json").write_text(
        json.dumps({"tutorials": register}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Register neu aufgebaut:", len(register), "Tutorials")


if __name__ == "__main__":
    main()
