#!/usr/bin/env python3
"""Klickanleitungen P2 (Vakuumröhre) aus der Aufnahme vom 01.11.2026 bauen.

Die Aufnahme entstand per Fernsteuerung: Klicks dauern dort unter 10 ms, das Foto zeigt deshalb den Zustand NACH dem
Klick (aufgeklapptes Menü erst im Foto des Klicks davor). Ab Kapitel 4 wählt die Aufnahme Flächen über Named Selections
(Worksheet), weil Klicks ins 3D-Fenster ferngesteuert nicht ankamen.

Aufruf (im Repo):
    python3 tools/klickrecorder/p2_anleitungen.py                 alle Anleitungen nach docs/tutorials
    python3 tools/klickrecorder/p2_anleitungen.py p2-sonne        nur diese
    python3 tools/klickrecorder/p2_anleitungen.py --probe 4 13+14 27 --ziel DIR   Schritte eines Kapitels zum Sichten
"""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HIER = Path(__file__).resolve().parent
REPO = HIER.parents[1]
A = HIER / "aufnahmen/2026-11-01_1111_P2_Vakuumroehre"
ZIEL = REPO / "docs/tutorials"
sys.path.insert(0, str(HIER))
import aufnahme2tutorial as A2T  # noqa: E402

FREMD = [(3299, 20, 3821, 741)]   # Fenster der Fernsteuerung, liegt über SpaceClaim und Mechanical


def flaeche(r):
    return (r[2] - r[0]) * (r[3] - r[1])


def schnitt(a, b):
    r = (max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]))
    return r if r[2] > r[0] and r[3] > r[1] else None


def ausschnitt(box, W, H, rand=60, mw=900, mh=520):
    """Rahmen um die Marker; Mindestgröße fest statt anteilig (die Aufnahme ist 3840 px breit, Schrift in Originalgröße)."""
    if not box:
        return (0, 0, W, H)
    xs, ys = [p[0] for p in box], [p[1] for p in box]
    x0, x1, y0, y1 = min(xs) - rand, max(xs) + rand, min(ys) - rand, max(ys) + rand
    if x1 - x0 < mw:
        x0, x1 = (x0 + x1 - mw) / 2, (x0 + x1 + mw) / 2
    if y1 - y0 < mh:
        y0, y1 = (y0 + y1 - mh) / 2, (y0 + y1 + mh) / 2
    dx = max(0, -x0) - max(0, x1 - W)
    dy = max(0, -y0) - max(0, y1 - H)
    return (round(max(0, x0 + dx)), round(max(0, y0 + dy)), round(min(W, x1 + dx)), round(min(H, y1 + dy)))


def rendern(schritte, datei):
    """Schritte in einem Bild, Marker fortlaufend, Foto des letzten Schritts."""
    img = Image.open(A / schritte[-1]["frame"]).convert("RGB")
    W, H = img.size
    fenster = [f for s in schritte for f in A2T.sichtbar(s)]
    img = A2T.abdecken(img, fenster)
    d = ImageDraw.Draw(img)
    for r in FREMD:
        d.rectangle(r, fill=A2T.GRAU_HG)
    roh = img.copy()
    box, n = [], 1
    for s in schritte:
        r, punkte, ziel, b = A2T.geometrie(s, W, H, roh)
        A2T.zeichnen(img, r, punkte, ziel, n)
        n += len(punkte)
        box += b
    rahmen = ausschnitt(box, W, H)
    haupt = max(fenster, key=flaeche) if fenster else None
    if haupt and flaeche(haupt) > 0.1 * W * H:          # nur im Programmfenster, nicht über den Bildschirm hinaus
        rahmen = schnitt(rahmen, (max(0, haupt[0]), max(0, haupt[1]), min(W, haupt[2]), min(H, haupt[3]))) or rahmen
    for f in FREMD:                                      # Fenster der Fernsteuerung aus dem Ausschnitt halten
        if schnitt(rahmen, f) and box:
            xs, ys = [p[0] for p in box], [p[1] for p in box]
            if max(xs) < f[0] - 20:
                rahmen = (rahmen[0], rahmen[1], min(rahmen[2], f[0]), rahmen[3])
            elif min(ys) > f[3] + 20:
                rahmen = (rahmen[0], max(rahmen[1], f[3]), rahmen[2], rahmen[3])
    img.crop(rahmen).save(datei, optimize=True)


def ereignisse():
    return {e["nr"]: e for e in json.loads((A / "events.json").read_text(encoding="utf-8"))["events"]}


def schritt(evs, angabe):
    """'171+173@0172': Marker an den Ereignissen 171 und 173 (in dieser Reihenfolge), Foto frames/0172.png.
    Ohne @ das Foto des letzten Ereignisses. Tasten zählen als Marker an der Mausposition. '430:-19' verschiebt."""
    teil, _, foto = str(angabe).partition("@")
    glieder = []
    for n in teil.split("+"):
        nr, _, dy = n.partition(":")      # "430:-19": Marker 19 px höher (Zeilen im Detailfenster verrutscht)
        g = dict(evs[int(nr)])
        if dy:
            g["y"] += int(dy)
            g["element"] = dict(g.get("element") or {}, rechteck=None)
        glieder.append(g)
    frame = f"frames/{foto}.png" if foto else glieder[-1]["frame"]
    quelle = [e for e in evs.values() if e.get("frame") == frame]
    fenster = [g.get("fenster_rechteck") for g in glieder + quelle]
    ziehen = next(({"x2": g["x2"], "y2": g["y2"]} for g in glieder if g["art"] == "ziehen"), None)
    return {"glieder": glieder, "frame": frame, "monitor": glieder[0].get("monitor") or {"left": 0, "top": 0},
            "ziehen": ziehen, "fenster": [r for r in dict.fromkeys(map(tuple, filter(None, fenster)))]}


# ---- Anleitungen ---------------------------------------------------------------------------------------------------
# Je Schritt: (Ereignisse und Foto wie in schritt(), Text, Notiz oder None).
ANLEITUNGEN = {
    "p2-named-selection": dict(titel="Named Selection über das Worksheet", kategorie="Randbedingungen", software="Mechanical",
                               tags=["Named Selection", "Worksheet"], schritte=[
        ("167+168@0168", "`Rechtsklick Strukturbaum Model (A4) → Insert → Named Selection`",
         "Gibt es den Ordner **Named Selections** schon, geht es kürzer: `Rechtsklick Named Selections → Insert → Named Selection`."),
        ("171+173@0172", "Im `Detailfenster` bei **Scoping Method** `Worksheet` wählen", None),
        ("174@0175", "Unten im **Worksheet** `Rechtsklick → Add Row`: Es erscheint eine gelbe Zeile", None),
        ("176+188+184@0190", "In der Zeile **Entity Type** `Face`, **Criterion** `Location X`, bei **Value** `0,00025` (m) eingeben, `Enter`",
         "0,00025 m ist die halbe Blechdicke, also die Oberseite des Blechs. Findet `Generate` keine 2 Flächen, liegt das Blech bei Ihnen in einer anderen Achse: `Location Y` oder `Location Z` probieren."),
        ("191@0192", "`Generate`: Die Named Selection enthält jetzt die **2** Oberseiten der Blechflügel", None),
        ("192@0194", "Im Strukturbaum die neue **Selection** anklicken, mit `F2` umbenennen in **Oberseiten Blech**", None),
    ]),
    "p2-sonne": dict(titel="Sonne: Heat Flux auf eine Named Selection", kategorie="Randbedingungen", software="Mechanical",
                     tags=["Heat Flux", "Named Selection"], schritte=[
        ("151+152@0152", "`Rechtsklick Strukturbaum Steady-State Thermal (A5) → Insert → Heat Flux`", None),
        ("196+198@0198", "Im `Detailfenster` bei **Scoping Method** `Named Selection` wählen", None),
        ("199+202@0203", "Bei **Named Selection** `Oberseiten Blech` wählen, bei **Magnitude** `700` (W/m²) eingeben, `Enter`", None),
        ("204@0207", "Im Strukturbaum mit `F2` umbenennen in **Sonne**", None),
    ]),
    "p2-konvektion": dict(titel="Wasser und Luft: Convection", kategorie="Randbedingungen", software="Mechanical",
                          tags=["Convection", "Named Selection"], schritte=[
        ("233+234@0234", "`Rechtsklick Strukturbaum Steady-State Thermal (A5) → Insert → Convection`", None),
        ("237+239@0238", "Im `Detailfenster` bei **Scoping Method** `Named Selection` wählen", None),
        ("240+243+245@0248", "**Named Selection** `Rohr innen`, **Film Coefficient** `1000` (W/m²·°C), **Ambient Temperature** `50` (°C), jeweils `Enter`", None),
        ("247@0250", "Mit `F2` umbenennen in **Wasser**", None),
        ("274+275@0276", "Zweite Konvektion: wieder `Rechtsklick Steady-State Thermal (A5) → Insert → Convection`", None),
        ("280+283+285@0290", "**Scoping Method** `Named Selection`, **Named Selection** `Glas aussen`, **Film Coefficient** `10`, **Ambient Temperature** `20`", None),
        ("287@0292", "Mit `F2` umbenennen in **Luft**", None),
    ]),
    "p2-strahlung-himmel": dict(titel="Himmel: Radiation To Ambient", kategorie="Randbedingungen", software="Mechanical",
                                tags=["Radiation", "To Ambient"], schritte=[
        ("291+292@0294", "`Rechtsklick Strukturbaum Steady-State Thermal (A5) → Insert → Radiation`", None),
        ("294@0297", "Im `Detailfenster` bei **Scoping Method** `Named Selection` wählen", None),
        ("297+300+302@0308", "**Named Selection** `Glas aussen`, **Emissivity** `0,9`, **Ambient Temperature** `5` (°C). **Correlation** bleibt `To Ambient`",
         "Dieselbe Fläche wie die Luft: Konvektion und Strahlung gelten gleichzeitig."),
        ("304@0310", "Mit `F2` umbenennen in **Himmel**", None),
    ]),
    "p2-strahlung-s2s": dict(titel="Absorber und Glas: Radiation Surface to Surface", kategorie="Randbedingungen", software="Mechanical",
                             tags=["Radiation", "Surface to Surface", "Enclosure"], schritte=[
        ("323+345+364+366@0369", "Zuerst zwei Named Selections anlegen. **Absorber aussen** braucht drei Zeilen: `Location X` = `0,00025` und `-0,00025` (Ober- und Unterseiten des Blechs), `Radius` = `0,006` (Rohr außen), dann `Generate`. **Glas innen**: `Radius` = `0,0325`", None),
        ("394+395@0398", "`Rechtsklick Strukturbaum Steady-State Thermal (A5) → Insert → Radiation`", None),
        ("398@0401", "Im `Detailfenster` bei **Scoping Method** `Named Selection` wählen", None),
        ("401+404+407+409:-19@0415", "**Named Selection** `Absorber aussen`, **Correlation** `Surface To Surface`, **Emissivity** `0,05`, **Enclosure** bleibt `1`, **Enclosure Type** `Perfect`",
         "Gleiche Enclosure-Nummer heißt: Diese Flächen strahlen sich gegenseitig an."),
        ("412@0417", "Mit `F2` umbenennen in **Absorber zum Glas**", None),
        ("415+416@0419", "Zweite Strahlung: wieder `Rechtsklick Steady-State Thermal (A5) → Insert → Radiation`", None),
        ("422+425+428+430:-19@0436", "**Scoping Method** `Named Selection`, **Named Selection** `Glas innen`, **Correlation** `Surface To Surface`, **Emissivity** `0,9`, **Enclosure Type** `Perfect`", None),
        ("433@0438", "Mit `F2` umbenennen in **Glas zum Absorber**", None),
    ]),
    "p2-temperatur-koerper": dict(titel="Temperatur je Körper", kategorie="Postprocessing", software="Mechanical",
                                  tags=["Temperature", "Named Selection"], schritte=[
        ("446+449+455+458@0459", "Zwei weitere Named Selections für die Körper: **Entity Type** `Body`, **Criterion** `Material`, **Value** `Kupfer`, `Generate`, umbenennen in **Koerper Absorber**. Genauso mit `Glas`: **Koerper Glas**", None),
        ("487+488+490@0489", "`Rechtsklick Strukturbaum Solution (A6) → Insert → Thermal → Temperature`", None),
        ("493+495@0493", "Im `Detailfenster` bei **Scoping Method** `Named Selection` wählen", None),
        ("496+498@0496", "Bei **Named Selection** `Koerper Absorber` wählen", None),
        ("499@0499", "Mit `F2` umbenennen in **Temperatur Absorber**. Genauso **Temperatur Glas** mit **Koerper Glas**", None),
    ]),
    "p2-reaction-probe": dict(titel="Reaction Probe: Wärmestrom einer Randbedingung", kategorie="Postprocessing", software="Mechanical",
                              tags=["Reaction Probe"], schritte=[
        ("518+519+521@0517", "`Rechtsklick Solution (A6) → Insert → Probe → Reaction`", None),
        ("534+536@0529", "Im `Detailfenster` bei **Boundary Condition** die Randbedingung wählen, hier **Luft**", None),
        ("537@0532", "Mit `F2` umbenennen in **Reaktion Luft**. Genauso **Reaktion Wasser** und **Reaktion Himmel**",
         "Für die Sonne gibt es keine Reaction Probe: Ihr Wärmestrom ist vorgegeben."),
    ]),
    "p2-schwarz": dict(titel="Zweite Analyse auf demselben Modell", kategorie="Setup", software="Workbench",
                       tags=["Analyse", "Copy", "Paste"], schritte=[
        ("560@0549", "Im Projektmenü **Steady-State Thermal** aus der Toolbox mit gedrückter Maustaste auf die Zelle **Model** der Analyse A ziehen, die neue Analyse in **b) Schwarz** umbenennen, dann `Rechtsklick Setup → Edit...`", None),
        ("562+563@0555", "Unter **Steady-State Thermal (A5)** **Sonne** anklicken, mit `Shift` **Glas zum Absorber** dazunehmen, `Rechtsklick → Copy`", None),
        ("566@0557", "`Rechtsklick Steady-State Thermal 2 (B5) → Paste`", None),
        ("568+569@0562", "Genauso die Ergebnisse unter **Solution (A6)** markieren, `Rechtsklick → Copy`", None),
        ("574@0564", "`Rechtsklick Solution (B6) → Paste`", None),
        ("576+577@0569", "Unter **B5** **Absorber zum Glas** anklicken, **Emissivity** `0,9`, `Enter`", None),
    ]),
    "p2-stillstand": dict(titel="Stillstand: Wasser abschalten", kategorie="Setup", software="Mechanical",
                          tags=["Suppress"], schritte=[
        ("582@0574", "Wie bei b): eine dritte **Steady-State Thermal** auf die Zelle **Model** ziehen, in **c) Stillstand** umbenennen", None),
        ("584+585@0580", "Randbedingungen und Ergebnisse wie bei b) mit `Copy` und `Paste` übernehmen", None),
        ("598@0592", "Unter **Steady-State Thermal 3 (C5)** `Rechtsklick Wasser → Suppress`",
         "Die Randbedingung bleibt im Baum, wirkt aber nicht mehr: Die Rohrinnenseite ist jetzt isoliert."),
    ]),
}


def bauen(slug, ziel):
    d = ANLEITUNGEN[slug]
    evs = ereignisse()
    out = ziel / slug
    out.mkdir(parents=True, exist_ok=True)
    for alt in out.glob("step-*.png"):
        alt.unlink()
    steps = []
    for i, (angabe, text, notiz) in enumerate(d["schritte"]):
        rendern([schritt(evs, angabe)], out / f"step-{i}.png")
        st = {"caption": text, "media": [f"step-{i}.png"]}
        if notiz:
            st["note"] = notiz
        steps.append(st)
    tut = {"slug": slug, "title": d["titel"], "category": d["kategorie"], "software": d["software"],
           "tags": d.get("tags", []), "steps": steps}
    (out / "tutorial.json").write_text(json.dumps(tut, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{slug}: {len(steps)} Schritte")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--probe", nargs="+", help="Schritte zum Sichten, z. B. 171+173@0172 191")
    ap.add_argument("--ziel", type=Path, default=ZIEL)
    a = ap.parse_args()
    if a.probe:
        evs = ereignisse()
        a.ziel.mkdir(parents=True, exist_ok=True)
        for angabe in a.probe:
            rendern([schritt(evs, angabe)], a.ziel / f"p_{angabe.replace('+', '_').replace('@', 'f')}.png")
        return
    for slug in ANLEITUNGEN:
        if not a.slugs or slug in a.slugs:
            bauen(slug, a.ziel)


if __name__ == "__main__":
    main()
