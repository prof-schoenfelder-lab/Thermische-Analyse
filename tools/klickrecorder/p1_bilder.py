#!/usr/bin/env python3
"""Bilder der P1-Klickanleitungen neu bauen: ganzes Fenster plus Lupe, aus der Aufnahme vom 07.10.2026.
Texte, Notizen und tutorial.json bleiben unverändert, nur die step-N.png werden ersetzt.

Aufruf (im Repo):  python3 tools/klickrecorder/p1_bilder.py [slug ...] [--ziel DIR]
Ohne slug alle Anleitungen. Mit --ziel landen die Bilder dort statt in docs/tutorials (zum Vergleichen).
"""
import argparse
import json
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
REPO = HIER.parents[1]
A = HIER / "aufnahmen/2026-10-07_0729_P1-Vorzeigebeispiel"
QUELLE = REPO / "docs/tutorials"
sys.path.insert(0, str(HIER))
import aufnahme2tutorial as A2T  # noqa: E402

# slug: (Kapitel der Aufnahme, Schritte der Aufnahme je Anleitungsschritt, Schritte die bleiben (von Hand bearbeitet))
M = {
    "p1-analyse-anlegen": (1, [[1], [2], [4], [5], [6]], {2, 3}),
    "p1-material-anlegen": (2, [[i] for i in range(10)], set()),
    "p1-geometrie-wand": (3, [[0], [1], [2], [3, 4], [5], [24], [25], [26, 27, 28], [29], [31], [34], [37], [39, 40], [41]], set()),
    "p1-material-zuweisen": (4, [[0], [1], [3], [4, 6, 7], [8, 10, 11]], set()),
    "p1-vernetzung": (5, [[0], [1], [3], [4]], set()),
    "p1-temperatur-anbringen": (5, [[6, 7], [8], [9], [11], [12], [13], [15], [16]], set()),
    "p1-loesen": (6, [[0], [1]], set()),
    "p1-auswertung": (7, [[1], [2], [3], [5], [7], [8, 9], [10], [11], [12], [14], [16]], set()),
    "p1-konvektion-anlegen": (8, [[0], [1], [2]], set()),
    "p1-konvektion": (9, [[0, 1], [2], [3], [5], [6], [8], [10], [24], [25], [27], [29], [31], [33], [36]], set()),
}
# Klicks, die nicht zum Text passen: SpaceClaim schließen, aufgenommen ist die Knopfgruppe am Minimieren-Knopf
KORREKTUR = {("p1-geometrie-wand", 41): {"x": 1494, "element": {"typ": "ButtonControl", "name": "Schließen", "rechteck": [1482, 5, 1507, 30]}}}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--ziel", type=Path, default=QUELLE)
    a = ap.parse_args()
    evs = sorted(json.loads((A / "events.json").read_text(encoding="utf-8"))["events"], key=lambda e: e["t"])
    for slug, (k, nummern, bleibt) in M.items():
        if a.slugs and slug not in a.slugs:
            continue
        kev = [e for e in evs if e["kapitel"] == k and e["art"] != "kapitel" and not e.get("verworfen")]
        alle = A2T.schritte_bilden(kev)
        for (sl, nr), neu in KORREKTUR.items():
            if sl == slug:
                g = alle[nr]["glieder"][0]
                g["x"], g["element"] = neu["x"], {**g.get("element", {}), **neu["element"]}
        tut = json.loads((QUELLE / slug / "tutorial.json").read_text(encoding="utf-8"))
        assert len(tut["steps"]) == len(nummern), (slug, len(tut["steps"]), len(nummern))
        (a.ziel / slug).mkdir(parents=True, exist_ok=True)
        for i, (st, nrs) in enumerate(zip(tut["steps"], nummern)):
            if i in bleibt:
                continue
            assert st["media"] == [f"step-{i}.png"], (slug, i, st["media"])
            A2T.bild_uebersicht(A, [alle[n] for n in nrs], a.ziel / slug / f"step-{i}.png",
                                vorher=alle[nrs[0] - 1] if nrs[0] else None)
        print(slug, "ok")


if __name__ == "__main__":
    main()
