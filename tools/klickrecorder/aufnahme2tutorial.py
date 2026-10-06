#!/usr/bin/env python3
"""Aufnahme des Klickrecorders -> Klickanleitung für die Tutorial-Datenbank.

Aufruf:  python3 aufnahme2tutorial.py <Aufnahmeordner> [--ziel DIR] [--slug NAME] [--titel TEXT]
                                      [--kategorie TEXT] [--software TEXT] [--gif]

Je Kapitel der Aufnahme entsteht <ziel>/<slug>[-kN]/ mit
  tutorial.json   (Format wie docs/tutorials/<slug>/tutorial.json)
  step-N.png      (Ausschnitt mit nummerierten Markern)
  entwurf.md      (Schritte mit Rohdaten und [PRÜFEN]-Stellen zum Nacharbeiten)
  ablauf.gif      (nur mit --gif: ganzer Ablauf, gleicher Ausschnitt, Zähler je Schritt)
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
GRAU_HG = (238, 240, 241)   # Fläche außerhalb der aktiven Anwendung
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
def schritt(caption, glieder, ev, *felder, ziehen=None):
    """Schritt mit dem ersten vorhandenen Foto aus felder (Standard: Foto beim Klick)."""
    frame = next((ev.get(f) for f in (*felder, "frame") if ev and ev.get(f)), None)
    if ev and ev.get("t_frame", 0) > ev.get("t_los", 1e9) and typ(ev) in MENU:
        caption += " [PRÜFEN: Foto erst nach dem Loslassen]"
    fenster = [g.get("fenster_rechteck") for g in glieder] + [(ev or {}).get("fenster_rechteck")]
    return {"caption": caption, "glieder": glieder, "frame": frame, "film": [frame] if frame else [],
            "monitor": (ev or {}).get("monitor"), "ziehen": ziehen,
            "fenster": [r for r in dict.fromkeys(map(tuple, filter(None, fenster)))]}


def mit_mods(ev, cap):
    mods = [m for m in ev.get("mods", []) if m != "Alt" or ev["art"] == "taste"]
    if not mods or ev["art"] == "taste":
        return cap
    halten = f"Mit gedrückter `{' + '.join(mods)}`"
    return f"{halten}: {cap}" if cap.startswith("`") else f"{halten} {cap[0].lower()}{cap[1:]}"


def eingabe_danach(evs, j):
    """Leertasten, Tab (Feldwechsel) und abschließendes Enter einsammeln (Feld, F2, Skizzenmaße, Pull)."""
    tasten = []
    while j < len(evs) and (evs[j]["art"] == "hover" or
                            (evs[j]["art"] == "taste" and evs[j]["taste"] in ("Leertaste", "Tab", "Enter"))):
        if evs[j]["art"] == "taste":
            tasten.append(evs[j])
            if evs[j]["taste"] == "Enter":
                return tasten, j + 1
        j += 1
    return tasten, j


def wert_von(t):
    """Eingegebener Wert; zeigt das Detailfenster ihn mit Einheit an, diese Form."""
    wert = (t.get("wert_direkt") or t.get("wert") or "").strip()
    anzeige = (t.get("wert_angezeigt") or "").strip()
    return anzeige if anzeige and (not wert or anzeige.startswith(wert)) else wert


def eingaben(tasten, klick=None):
    """Text der Eingabe(n), Feldname, alle Werte bekannt?, Taste mit dem letzten Foto."""
    enden = [t for t in tasten if t["taste"] != "Leertaste"]
    if not enden:
        return "", "", False, None
    werte = [wert_von(t) for t in enden]
    if len(enden) == 1:
        text = (f"`{werte[0]}` eingeben" if werte[0] else "den Wert eingeben") + f" und `{enden[0]['taste']}`"
    else:  # z.B. Skizzenmaße in SpaceClaim: 20mm Tab 20mm Enter
        text = "nacheinander " + " ".join(f"`{w or '?'}` `{t['taste']}`" for w, t in zip(werte, enden)) + " eingeben"
    letzte = enden[-1]
    anzeige = (letzte.get("wert_angezeigt") or "").strip()
    feld = (letzte.get("beschriftung") or "").strip()
    if not feld and anzeige and not re.search(r"\d", anzeige):
        feld = anzeige  # an der Klickstelle stand der Zeilenname
    if not feld and (letzte.get("feld") or {}).get("typ") == "ListItemControl":
        feld = letzte["feld"].get("name", "").strip()  # aktive Zeile im Detailfenster
    if not feld and klick and typ(klick) in FELD:
        feld = name(klick)
    return text, ("" if feld in werte else feld), all(werte), letzte


def schritte_bilden(evs):
    """Liste von Schritten: {caption, glieder (Ereignisse mit Marker), frame, monitor, ziehen}."""
    out, i, n = [], 0, len(evs)
    while i < n:
        ev = evs[i]
        art = ev["art"]
        if art == "hover" or not in_ansys(ev):
            i += 1
            continue
        if art == "rechtsklick":  # Menü mit Esc abgebrochen: kein Schritt
            j = i + 1
            while j < n and evs[j]["art"] == "hover":
                j += 1
            if j < n and evs[j]["art"] == "taste" and evs[j]["taste"] == "Esc":
                i = j + 1
                continue

        # Kette: Rechtsklick oder Reiter/Menü/Dropdown, gefolgt von Menüeinträgen
        oeffnet_menue = any(typ(e) in MENU for e in evs[i + 1:i + 3] if e["art"] in ("hover", "klick"))
        if art == "rechtsklick" or (art == "klick" and (typ(ev) in KETTENSTART or oeffnet_menue)):
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
                if typ(ev) in ("MenuControl", "MenuItemControl") and art == "rechtsklick":
                    teile[0] = "?"  # Menü lag beim Nachschlagen schon über dem Ziel
                # Untermenü übersprungen (Maus nicht lange genug über z.B. Insert)?
                if art == "rechtsklick" and len(kette) == 2 and abs(el(kette[1]).get("rechteck", [ev["x"]])[0] - ev["x"]) > 60:
                    teile.insert(1, "?")
                cap = f"`{aktion}{' → '.join(teile)}`"
                if "?" in teile:
                    cap += PRUEFEN
                bild = next((k for k in reversed(kette) if k.get("frame")), ev)
                out.append(schritt(mit_mods(ev, cap), kette, bild))
                i = j
                continue

        if art in ("klick", "doppelklick", "mittelklick"):
            tasten, j = eingabe_danach(evs, i + 1)
            text, feld, komplett, ende = eingaben(tasten, ev)
            if typ(ev) in FELD or ende:
                # Klick ins Feld (oder Skizzenpunkt), Werte tippen, Enter: Werte per UI Automation gelesen
                if im_grafikfenster(ev):
                    cap = f"Im Grafikfenster klicken, dann {text or 'den Wert eingeben'}" + PRUEFEN
                else:
                    cap = f"Bei **{feld}** {text or 'den Wert eingeben'}" if feld else (text or "den Wert eingeben")
                    cap = cap[0].upper() + cap[1:]
                    if ort(ev) == "Detailfenster ":
                        cap = "Im `Detailfenster` " + cap[0].lower() + cap[1:]
                    if not komplett or not feld:
                        cap += PRUEFEN
                if ort(ev) == "Detailfenster ":  # Foto kurz nach Enter zeigt den übernommenen Wert
                    bild = ende if ende and ende.get("frame_danach") else ev
                    out.append(schritt(cap, [ev], bild, "frame_danach"))
                else:
                    out.append(schritt(cap, [ev], ende or ev, "frame"))
                i = j
                continue
            if im_grafikfenster(ev):
                cap = "Im Grafikfenster auswählen" + PRUEFEN
            elif im_projektmenue(ev):
                cap = "Im Projektmenü klicken" + PRUEFEN
            elif ohne_namen(ev):
                cap = "Klicken" + PRUEFEN
            elif art == "doppelklick":
                cap = f"`Doppelklick {ort(ev)}{name(ev)}`"
            elif art == "mittelklick":
                cap = f"`Mittlere Maustaste` auf **{name(ev)}**"
            else:
                cap = f"`Linksklick {ort(ev)}{name(ev)}`"
            out.append(schritt(mit_mods(ev, cap), [ev], ev))
        elif art == "ziehen":
            tasten, j = eingabe_danach(evs, i + 1)
            text, _, komplett, ende = eingaben(tasten)
            leer = any(t["taste"] == "Leertaste" for t in tasten)
            mods = set(ev.get("mods", []))
            if ev.get("taste") == "middle":
                wirkung = "verschieben" if "Strg" in mods else "zoomen" if "Shift" in mods else "drehen"
                cap = f"Mit gedrückter `mittlerer Maustaste` ziehen (Ansicht {wirkung})"
                cap = (f"`{' + '.join(sorted(mods))}` halten und " + cap[0].lower() + cap[1:]) if mods else cap
            else:
                von, auf = name(ev), (ev.get("ziel_element") or {}).get("name", "").strip()
                if von and auf and auf != von:
                    cap = f"**{von}** mit gedrückter Maustaste auf **{auf}** ziehen"
                else:
                    cap = "Mit gedrückter Maustaste ziehen"
                if leer:
                    cap += ", dabei `Leertaste` drücken"
                if text:
                    cap += ", " + text
                cap = mit_mods(ev, cap)
                if not (von and auf and auf != von) and not (text and komplett):
                    cap += PRUEFEN
            # Foto: Enter (Wert sichtbar) vor Leertaste (Eingabefeld) vor Loslassen vor Beginn;
            # im GIF alle Zwischenstände der Reihe nach
            letzte = ende or next((t for t in reversed(tasten) if t.get("frame")), None)
            if letzte and letzte.get("frame"):
                st = schritt(cap, [ev], letzte, "frame", ziehen=ev)
                st["monitor"] = st["monitor"] or ev.get("monitor")
            else:
                st = schritt(cap, [ev], ev, "frame_ende", ziehen=ev)
            folge = [ev.get("frame")] + [t.get("frame") for t in tasten if t.get("taste") == "Leertaste"] \
                + [ev.get("frame_ende")] + [ende.get("frame") if ende else None]
            st["film"] = list(dict.fromkeys(f for f in folge if f))
            out.append(st)
            i = j
            continue
        elif art == "taste":
            if ev["taste"] == "F2":
                tasten, j = eingabe_danach(evs, i + 1)
                _, _, _, ende = eingaben(tasten)
                wert = wert_von(ende) if ende else ""
                und = f" und `{ende['taste']}`" if ende else ""
                cap = f"`F2` drücken, **{wert}** eingeben{und}" if wert else "`F2` drücken, Namen eingeben" + und + PRUEFEN
                out.append(schritt(cap, [], ende, "frame"))
                i = j
                continue
            if ev["taste"] in ("Enter", "Tab") and (ev.get("wert_direkt") or ev.get("beschriftung")):
                # ohne Klick weitergetippt (Mechanical springt nach Enter in die nächste Zeile)
                tasten, j = eingabe_danach(evs, i)
                text, feld, komplett, ende = eingaben(tasten)
                cap = f"bei **{feld}** {text}" if feld else text
                cap = ("Im `Detailfenster` " + cap if ev.get("beschriftung") else cap[0].upper() + cap[1:])
                out.append(schritt(cap + ("" if komplett and feld else PRUEFEN), [], ende, "frame_danach"))
                i = j
                continue
            if ev["taste"] != "Leertaste":  # einzelne Leertasten sind Tippen, nicht Bedienung
                kombi = " + ".join(ev.get("mods", []) + [ev["taste"]])
                out.append(schritt(f"`{kombi}` drücken", [], None))
        elif art == "foto":
            out.append(schritt("Ergebnis beschreiben" + PRUEFEN, [], ev))
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
        if el(g).get("typ") in FELD:  # links neben das Feld, damit der Wert lesbar bleibt
            return rect[0] - r - 2, (rect[1] + rect[3]) / 2
        return rect[0] + r, (rect[1] + rect[3]) / 2
    return g["x"], g["y"]


def geometrie(schritt, W, H):
    """Markergröße, Markerpunkte, Zielpunkt beim Ziehen und Punkte für den Ausschnitt (Bildkoordinaten)."""
    mon = schritt["monitor"] or {"left": 0, "top": 0}
    ox, oy = mon["left"], mon["top"]
    # Markergröße an der Zeilenhöhe der Oberfläche ausrichten (Menü, Baum), sonst 22 px
    hoehen = [r[3] - r[1] for g in schritt["glieder"] if (r := el(g).get("rechteck")) and 0 < r[3] - r[1] < 60]
    r = max(10, round(0.6 * (min(hoehen) if hoehen else 22)))
    punkte = [(x - ox, y - oy) for x, y in (marker_punkt(g, W, H, r) for g in schritt["glieder"])]
    box = list(punkte)
    for g in schritt["glieder"]:
        rect = el(g).get("rechteck")
        if rect and rect[2] - rect[0] < W * 0.4 and rect[3] - rect[1] < H * 0.1:  # Menüzeilen mit ins Bild, keine Fenster
            box += [(rect[0] - ox, rect[1] - oy), (rect[2] - ox, rect[3] - oy)]
    ziel = None
    if schritt.get("ziehen"):
        ziel = (schritt["ziehen"]["x2"] - ox, schritt["ziehen"]["y2"] - oy)
        box.append(ziel)
    return r, punkte, ziel, box


def zeichnen(img, r, punkte, ziel):
    """Nummerierte Marker, beim Ziehen mit Pfeil zum Zielpunkt."""
    d = ImageDraw.Draw(img)
    if ziel and punkte:
        d.line([punkte[0], ziel], fill=ROT, width=max(3, r // 4))
        d.ellipse([ziel[0] - r // 2, ziel[1] - r // 2, ziel[0] + r // 2, ziel[1] + r // 2], fill=ROT)
    f = schrift(round(r * 1.3))
    for k, (x, y) in enumerate(punkte, 1):
        d.ellipse([x - r, y - r, x + r, y + r], fill=ROT, outline="white", width=max(2, r // 7))
        d.text((x, y), str(k), fill="white", font=f, anchor="mm")


def ausschnitt(box, W, H):
    """Rahmen um alle Punkte, mit Rand und Mindestgröße, innerhalb des Bildes."""
    if not box:
        return (0, 0, W, H)
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
    return (round(max(0, x0 + dx)), round(max(0, y0 + dy)), round(min(W, x1 + dx)), round(min(H, y1 + dy)))


def sichtbar(schritt):
    """Fenster dieses Schritts (Programmfenster plus Menü-Popups) in Bildkoordinaten."""
    mon = schritt["monitor"] or {"left": 0, "top": 0}
    return [[r[0] - mon["left"], r[1] - mon["top"], r[2] - mon["left"], r[3] - mon["top"]]
            for r in schritt.get("fenster", []) if r]


def abdecken(img, rechtecke):
    """Alles außerhalb der Fenster hellgrau, damit nur die aktive Anwendung zu sehen ist."""
    if not rechtecke:
        return img
    maske = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(maske)
    for r in rechtecke:
        d.rectangle(r, fill=255)
    return Image.composite(img, Image.new("RGB", img.size, GRAU_HG), maske)


def begrenzen(rahmen, rechtecke):
    """Ausschnitt nicht über die Fenster hinaus (keine großen grauen Flächen)."""
    if not rechtecke:
        return rahmen
    x0, y0, x1, y1 = rahmen
    return (max(x0, min(r[0] for r in rechtecke)), max(y0, min(r[1] for r in rechtecke)),
            min(x1, max(r[2] for r in rechtecke)), min(y1, max(r[3] for r in rechtecke)))


def bild_rendern(aufnahme, schritt, datei):
    img = Image.open(aufnahme / schritt["frame"]).convert("RGB")
    fenster = sichtbar(schritt)
    img = abdecken(img, fenster)
    r, punkte, ziel, box = geometrie(schritt, *img.size)
    zeichnen(img, r, punkte, ziel)
    img.crop(begrenzen(ausschnitt(box, *img.size), fenster)).save(datei, optimize=True)


def gif_bauen(aufnahme, schritte, datei, breite=1280, ms=1600):
    """Ablauf eines Kapitels als GIF: alle Fotos je Schritt, gleicher Ausschnitt, Zähler „3 / 9".
    Marker werden erst nach dem Verkleinern gezeichnet, damit sie lesbar bleiben."""
    mit_bild = [st for st in schritte if st["film"]]
    if not mit_bild:
        return
    W, H = Image.open(aufnahme / mit_bild[0]["film"][0]).size
    geo = [geometrie(st, W, H) for st in mit_bild]
    alle_fenster = [r for st in mit_bild for r in sichtbar(st)]
    x0, y0, x1, y1 = begrenzen(ausschnitt([p for g in geo for p in g[3]], W, H), alle_fenster)
    k = min(1.0, breite / (x1 - x0))
    tf = lambda p: ((p[0] - x0) * k, (p[1] - y0) * k)
    f = schrift(28)
    film, dauer = [], []
    for nr, (st, (r, punkte, ziel, _)) in enumerate(zip(mit_bild, geo), 1):
        for frame in st["film"]:
            b = abdecken(Image.open(aufnahme / frame).convert("RGB").resize((W, H)), sichtbar(st))
            b = b.crop((x0, y0, x1, y1))
            b = b.resize((round(b.width * k), round(b.height * k)), Image.LANCZOS)
            zeichnen(b, max(11, round(r * k)), [tf(p) for p in punkte], tf(ziel) if ziel else None)
            d = ImageDraw.Draw(b)
            text = f"{nr} / {len(mit_bild)}"
            tx0, ty0, tx1, ty1 = d.textbbox((0, 0), text, font=f)
            d.rounded_rectangle([10, 10, 30 + tx1 - tx0, 30 + ty1 - ty0], radius=8, fill=(2, 37, 65))
            d.text((20, 20 - ty0), text, fill="white", font=f)
            film.append(b.quantize(colors=255, method=Image.Quantize.FASTOCTREE))  # hält das Marker-Rot
            dauer.append(ms)
    dauer[-1] = ms * 2
    film[0].save(datei, save_all=True, append_images=film[1:], duration=dauer, loop=0, optimize=True)


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
    ap.add_argument("--gif", action="store_true", help="je Kapitel zusätzlich ablauf.gif")
    a = ap.parse_args()

    daten = json.loads((a.aufnahme / "events.json").read_text(encoding="utf-8"))
    evs = sorted(daten["events"], key=lambda e: e["t"])
    kapitel = sorted({e["kapitel"] for e in evs if e["art"] != "kapitel"})
    basis = a.slug or slugify(re.sub(r"^\d{4}-\d{2}-\d{2}_\d{4}_", "", daten["name"]))
    ziel_dir = a.ziel or a.aufnahme / "tutorial"

    for k in kapitel:
        kev = [e for e in evs if e["kapitel"] == k and e["art"] != "kapitel" and not e.get("verworfen")]
        slug = basis if len(kapitel) == 1 else f"{basis}-k{k}"
        out = ziel_dir / slug
        out.mkdir(parents=True, exist_ok=True)
        steps, entwurf = [], [f"# Entwurf {slug}\n", f"Aufnahme: `{a.aufnahme.name}`, Kapitel {k}\n"]
        schritte = schritte_bilden(kev)
        for st in schritte:
            st["film"] = [f for f in st["film"] if (a.aufnahme / f).exists()]
        if a.gif:
            gif_bauen(a.aufnahme, schritte, out / "ablauf.gif")
        for nr, s in enumerate(schritte):
            media = []
            if s["frame"] and (a.aufnahme / s["frame"]).exists():
                datei = f"step-{nr}.png"
                bild_rendern(a.aufnahme, s, out / datei)
                media = [datei]
            steps.append({"caption": s["caption"], "media": media})
            entwurf.append(f"{nr + 1}. {s['caption']}" + (f"  ![]({media[0]})" if media else ""))
            for g in s["glieder"]:
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
