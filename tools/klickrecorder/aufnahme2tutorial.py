#!/usr/bin/env python3
"""Aufnahme des Klickrecorders -> Klickanleitung für die Tutorial-Datenbank.

Aufruf:  python3 aufnahme2tutorial.py <Aufnahmeordner> [--ziel DIR] [--slug NAME] [--titel TEXT]
                                      [--kategorie TEXT] [--software TEXT]

Je Kapitel der Aufnahme entsteht <ziel>/<slug>[-kN]/ mit
  tutorial.json   (Format wie docs/tutorials/<slug>/tutorial.json)
  step-N.png      (Ausschnitt mit nummerierten Markern)
  entwurf.md      (Schritte mit Rohdaten und [PRÜFEN]-Stellen zum Nacharbeiten)
Standardziel ist <Aufnahmeordner>/tutorial. Braucht Pillow.

Zusammenfassung zu einem Schritt: Rechtsklick + Menüeinträge
(`Rechtsklick Static Structural → Insert → Fixed Support`), Reiter + Knopf
(`Reiter Environment → Temperature`). Eingetippte Werte zeichnet der Recorder
nicht auf; Klicks in Felder werden „Wert eingeben [PRÜFEN]".
"""
import argparse
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

MENU = {"MenuItemControl"}
KETTENSTART = {"TabItemControl", "MenuItemControl", "SplitButtonControl"}
FELD = {"EditControl", "ComboBoxControl", "DataItemControl", "SpinnerControl"}
ANSYS = ("Workbench", "SpaceClaim", "Mechanical")
GRAFIK = ("WBGfxSplitWindow", "graphicsViewHost")  # Grafikfenster Mechanical, SpaceClaim
ROT = (229, 48, 9)          # HTWK Rot
PRUEFEN = " [PRÜFEN]"


def slugify(s):
    s = s.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def el(ev):
    return ev.get("element") or {}


def name(ev):
    """Elementname; fällt beim Schließen eines Menüs manchmal leer aus, dann aus der Kette."""
    kette = el(ev).get("kette") or [{}]
    return (el(ev).get("name") or kette[0].get("name") or "").strip()


def texte(ev):
    e = el(ev)
    return [e.get("fenster", "")] + [f"{k.get('name', '')} {k.get('klasse', '')}" for k in e.get("kette", [])]


def in_ansys(ev):
    """Klicks außerhalb von ANSYS (Explorer, Bildanzeige) gehören nicht in die Anleitung."""
    return not el(ev) or any(a in t for t in texte(ev) for a in ANSYS)


def im_grafikfenster(ev):
    return any(g in t for t in texte(ev) for g in GRAFIK)


def im_projektmenue(ev):
    return not name(ev) and el(ev).get("fenster", "").endswith("- Workbench")


def typ(ev):
    return el(ev).get("typ", "")


def ort(ev):
    """Ort-Präfix für die Chip-Syntax (Strukturbaum, Detailfenster)."""
    kette = el(ev).get("kette", [])
    if typ(ev) == "TreeItemControl" and "Mechanical" in el(ev).get("fenster", ""):
        return "Strukturbaum "
    if any(k.get("name", "").startswith("Details of") for k in kette):
        return "Detailfenster "
    return ""


def ziel(ev):
    """Name eines Kettenglieds; Reiter mit Präfix."""
    n = name(ev) or "?"
    return f"Reiter {n}" if typ(ev) == "TabItemControl" else n


def ohne_namen(ev):
    return not name(ev)


def spalte(ev):
    """Menüspalte eines Eintrags: gleiche linke und rechte Kante = gleiches (Unter-)Menü."""
    r = el(ev).get("rechteck") or [0, 0, 0, 0]
    return (r[0], r[2])


def menuepfad(glieder):
    """Nur den genommenen Weg behalten: rückwärts vom Klick, je Untermenü der Eintrag,
    über dem die Maus stand, bevor das nächste Untermenü aufging."""
    wurzel, rest = glieder[0], glieder[1:]
    if not rest:
        return [wurzel]
    pfad = [rest[-1]]
    erste = {}
    for k, g in enumerate(rest):
        erste.setdefault(spalte(g), k)
    grenze = erste[spalte(rest[-1])]
    for k in range(len(rest) - 2, -1, -1):
        sp = spalte(rest[k])
        if k < grenze and sp not in {spalte(p) for p in pfad}:
            pfad.insert(0, rest[k])
            grenze = erste[sp]
    return [wurzel] + pfad


# ---- Schritte bilden ------------------------------------------------------
def schritte_bilden(evs):
    """Liste von Schritten: {caption, glieder (Ereignisse mit Marker), bild (Ereignis), info}."""
    out, i, n = [], 0, len(evs)
    while i < n:
        ev = evs[i]
        art = ev["art"]
        if art == "hover" or not in_ansys(ev):
            i += 1
            continue

        # Kette: Rechtsklick oder Reiter/Menü/Dropdown, gefolgt von Menüeinträgen
        if art == "rechtsklick" or (art == "klick" and typ(ev) in KETTENSTART):
            kette, j = [ev], i + 1
            while j < n and evs[j]["art"] in ("hover", "klick") and typ(evs[j]) in MENU:
                kette.append(evs[j])
                j += 1
            while len(kette) > 1 and kette[-1]["art"] == "hover":  # Maus ohne Klick weitergezogen
                kette.pop()
            kette = menuepfad(kette)
            if typ(ev) == "TabItemControl" and len(kette) == 1 and j < n and evs[j]["art"] == "klick":
                kette.append(evs[j])  # Reiter -> Knopf im Menüband
                j += 1
            if len(kette) > 1 or art == "rechtsklick":
                aktion = "Rechtsklick " + ort(ev) if art == "rechtsklick" else ""
                teile = [ziel(k) for k in kette]
                # Untermenü übersprungen (Maus nicht lange genug über z.B. Insert)?
                if art == "rechtsklick" and len(kette) == 2 and abs(el(kette[1]).get("rechteck", [ev["x"]])[0] - ev["x"]) > 60:
                    teile.insert(1, "?")
                cap = f"`{aktion}{' → '.join(teile)}`"
                if "?" in teile:
                    cap += PRUEFEN
                bild = next((k for k in reversed(kette) if k.get("frame")), ev)
                out.append({"caption": cap, "glieder": kette, "bild": bild})
                i = j
                continue

        if art in ("klick", "doppelklick", "mittelklick"):
            if im_grafikfenster(ev):
                cap = "Im Grafikfenster auswählen" + PRUEFEN
            elif im_projektmenue(ev):
                cap = "Im Projektmenü klicken" + PRUEFEN
            elif typ(ev) in FELD:  # Werte werden nicht aufgezeichnet, kommen aus der Aufgabe
                cap = (f"Bei **{name(ev)}** den Wert eingeben" if name(ev) else "Wert eingeben") + PRUEFEN
                if ort(ev) == "Detailfenster ":
                    cap = "Im `Detailfenster` " + (cap[0].lower() + cap[1:] if cap.startswith("Bei") else cap)
            elif ohne_namen(ev):
                cap = "Klicken" + PRUEFEN
            elif art == "doppelklick":
                cap = f"`Doppelklick {ort(ev)}{name(ev)}`"
            elif art == "mittelklick":
                cap = f"`Mittlere Maustaste` auf **{name(ev)}**"
            else:
                cap = f"`Linksklick {ort(ev)}{name(ev)}`"
            out.append({"caption": cap, "glieder": [ev], "bild": ev})
        elif art == "ziehen":
            if ev.get("taste") == "middle":
                cap = "Mit gedrückter `mittlerer Maustaste` ziehen (Ansicht drehen)"
            else:
                cap = "Mit gedrückter Maustaste ziehen" + PRUEFEN
            out.append({"caption": cap, "glieder": [ev], "bild": ev, "ziehen": True})
        elif art == "foto":
            out.append({"caption": "Ergebnis beschreiben" + PRUEFEN, "glieder": [], "bild": ev})
        i += 1
    return out


# ---- Bilder ---------------------------------------------------------------
def schrift(px):
    try:
        return ImageFont.load_default(size=px)
    except TypeError:  # Pillow < 10.1
        return ImageFont.load_default()


def marker_punkt(g, W, H, r):
    """Marker an den linken Rand kleiner Elemente (Menüeintrag, Baumeintrag), sonst an den Klickpunkt."""
    rect = el(g).get("rechteck")
    if not g.get("x2") and rect and rect[2] - rect[0] < W * 0.4 and rect[3] - rect[1] < H * 0.08:
        return rect[0] + r, (rect[1] + rect[3]) / 2
    return g["x"], g["y"]


def bild_rendern(aufnahme, schritt, datei):
    ev = schritt["bild"]
    img = Image.open(aufnahme / ev["frame"]).convert("RGB")
    mon = ev.get("monitor") or {"left": 0, "top": 0}
    ox, oy = mon["left"], mon["top"]
    W, H = img.size
    # Markergröße an der Zeilenhöhe der Oberfläche ausrichten (Menü, Baum), sonst 22 px
    hoehen = [r[3] - r[1] for g in schritt["glieder"] if (r := el(g).get("rechteck")) and 0 < r[3] - r[1] < 60]
    r = max(10, round(0.6 * (min(hoehen) if hoehen else 22)))
    d = ImageDraw.Draw(img)
    punkte = [marker_punkt(g, W, H, r) for g in schritt["glieder"]]
    punkte = [(x - ox, y - oy) for x, y in punkte]
    box = list(punkte)
    for g in schritt["glieder"]:
        rect = el(g).get("rechteck")
        if rect and rect[2] - rect[0] < W * 0.6:   # Menüeinträge etc. mit ins Bild
            box += [(rect[0] - ox, rect[1] - oy), (rect[2] - ox, rect[3] - oy)]
    if schritt.get("ziehen"):
        x2, y2 = ev["x2"] - ox, ev["y2"] - oy
        d.line([punkte[0], (x2, y2)], fill=ROT, width=max(3, r // 4))
        d.ellipse([x2 - r // 2, y2 - r // 2, x2 + r // 2, y2 + r // 2], fill=ROT)
        box.append((x2, y2))
    f = schrift(round(r * 1.3))
    for k, (x, y) in enumerate(punkte, 1):
        d.ellipse([x - r, y - r, x + r, y + r], fill=ROT, outline="white", width=max(2, r // 7))
        d.text((x, y), str(k), fill="white", font=f, anchor="mm")
    if box:  # Ausschnitt um alle Marker, mit Rand und Mindestgröße
        xs, ys = [p[0] for p in box], [p[1] for p in box]
        pad = round(W * 0.05)
        x0, x1 = min(xs) - pad, max(xs) + pad
        y0, y1 = min(ys) - pad, max(ys) + pad
        mw, mh = max(900, round(W * 0.3)), max(550, round(H * 0.3))
        if x1 - x0 < mw:
            c = (x0 + x1) / 2
            x0, x1 = c - mw / 2, c + mw / 2
        if y1 - y0 < mh:
            c = (y0 + y1) / 2
            y0, y1 = c - mh / 2, c + mh / 2
        dx = max(0, -x0) - max(0, x1 - W)
        dy = max(0, -y0) - max(0, y1 - H)
        x0, x1, y0, y1 = max(0, x0 + dx), min(W, x1 + dx), max(0, y0 + dy), min(H, y1 + dy)
        img = img.crop((round(x0), round(y0), round(x1), round(y1)))
    img.save(datei, optimize=True)


def software(evs):
    titel = " ".join(el(e).get("fenster", "") for e in evs)
    for s in ("SpaceClaim", "Mechanical", "Workbench"):
        if s in titel:
            return s
    return ""


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("aufnahme", type=Path)
    ap.add_argument("--ziel", type=Path)
    ap.add_argument("--slug")
    ap.add_argument("--titel")
    ap.add_argument("--kategorie", default="")
    ap.add_argument("--software")
    a = ap.parse_args()

    daten = json.loads((a.aufnahme / "events.json").read_text(encoding="utf-8"))
    evs = sorted(daten["events"], key=lambda e: e["t"])
    kapitel = sorted({e["kapitel"] for e in evs if e["art"] != "kapitel"})
    basis = a.slug or slugify(re.sub(r"^\d{4}-\d{2}-\d{2}_\d{4}_", "", daten["name"]))
    ziel_dir = a.ziel or a.aufnahme / "tutorial"

    for k in kapitel:
        kev = [e for e in evs if e["kapitel"] == k and e["art"] != "kapitel"]
        slug = basis if len(kapitel) == 1 else f"{basis}-k{k}"
        out = ziel_dir / slug
        out.mkdir(parents=True, exist_ok=True)
        steps, entwurf = [], [f"# Entwurf {slug}\n", f"Aufnahme: `{a.aufnahme.name}`, Kapitel {k}\n"]
        for nr, s in enumerate(schritte_bilden(kev)):
            media = []
            if s["bild"] and s["bild"].get("frame") and (a.aufnahme / s["bild"]["frame"]).exists():
                datei = f"step-{nr}.png"
                bild_rendern(a.aufnahme, s, out / datei)
                media = [datei]
            steps.append({"caption": s["caption"], "media": media})
            entwurf.append(f"{nr + 1}. {s['caption']}" + (f"  ![]({media[0]})" if media else ""))
            for g in s["glieder"] or ([s["bild"]] if s["bild"] else []):
                e = el(g)
                entwurf.append(f"    - {g['art']} `{e.get('typ', '')}` „{e.get('name', '')}“ in „{e.get('fenster', '')}“")
        tut = {"slug": slug,
               "title": a.titel or slug.replace("-", " ").capitalize(),
               "category": a.kategorie,
               "software": a.software or software(kev),
               "tags": [],
               "steps": steps}
        (out / "tutorial.json").write_text(json.dumps(tut, ensure_ascii=False, indent=2), encoding="utf-8")
        (out / "entwurf.md").write_text("\n".join(entwurf) + "\n", encoding="utf-8")
        offen = sum(PRUEFEN in s["caption"] for s in steps)
        print(f"{out}: {len(steps)} Schritte, {offen} zu prüfen")


if __name__ == "__main__":
    main()
