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

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageStat

MENU = {"MenuItemControl"}
KETTENSTART = {"TabItemControl", "MenuItemControl", "SplitButtonControl"}
FELD = {"EditControl", "ComboBoxControl", "DataItemControl", "SpinnerControl"}
ANSYS = ("Workbench", "SpaceClaim", "Mechanical")
# Fremde Fenster: Taskleiste, Recorder-Konsole, Benachrichtigungen (Outlook), Fensterwechsel, Explorer
FREMD = ("Taskleiste", "system32\\cmd", "Eingabeaufforderung", "Benachrichtigung", "Aufgabenumschalt",
         "Fotoanzeige", "Explorer", "klickrecorder")
GRAFIK = ("WBGfxSplitWindow", "graphicsViewHost")  # Grafikfenster Mechanical, SpaceClaim
ROT = (229, 48, 9)          # HTWK Rot
GRAU_HG = (238, 240, 241)   # Fläche außerhalb der aktiven Anwendung
CYAN = (0, 158, 227)        # HTWK Cyan (Lupe)
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
    """Klicks in fremden Fenstern gehören nicht in die Anleitung. Dialoge von ANSYS
    (Speichern unter, Import Material) bleiben, auch wenn ihr Titel kein ANSYS enthält."""
    return not el(ev) or not any(f in t for t in texte(ev) for f in FREMD)


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


def klein(rect, W, H):
    """Kleines Bedienelement (Menü-, Baum-, Listeneintrag, Feld, Knopf), kein Fenster."""
    return rect and rect[2] - rect[0] < W * 0.4 and rect[3] - rect[1] < H * 0.08


def schrift_laeufe(img, box):
    """Waagerechte Läufe von Schrift und Symbolen in box (Bildkoordinaten): Spalten, die sich vom Hintergrund
    (Median der Zeile) abheben; Lücken zwischen Buchstaben und Wörtern werden überbrückt."""
    x0, y0 = max(0, round(box[0])), max(0, round(box[1]) + 2)   # oben und unten 2 px weg: Fokusrahmen
    x1, y1 = min(img.width, round(box[2])), min(img.height, round(box[3]) - 2)
    if x1 - x0 < 6 or y1 - y0 < 4:
        return []
    zeile = img.crop((x0, y0, x1, y1)).convert("L")
    w, h = zeile.size
    px, hg = zeile.load(), ImageStat.Stat(zeile).median[0]
    laeufe, luecke = [], max(5, h // 3)
    for i in range(w):
        if any(abs(px[i, j] - hg) > 60 for j in range(h)):
            if laeufe and i - laeufe[-1][1] <= luecke:
                laeufe[-1][1] = i
            else:
                laeufe.append([i, i])
    return [(x0 + a, x0 + b) for a, b in laeufe if b - a >= 2 or 0 < a and b < w - 1]   # Rahmenlinien weg


def schrift_unter(img, x, y, r):
    """Schrift unter einem Marker (Kreis um x, y mit Radius r und 2 px Rand, Bildkoordinaten): Punkte im Kreis und
    Anteil im Quadrat darum; None, wenn der Marker über den Bildrand ragt. Linien (Rahmen, Trennstriche: Zeilen
    oder Spalten, die zu mehr als 60 % durchgehen) zählen nicht."""
    k = r + 2
    if x - k < 0 or y - k < 0 or x + k > img.width or y + k > img.height:
        return None
    x0, y0 = round(x - k), round(y - k)
    flaeche = img.crop((x0, y0, round(x + k), round(y + k))).convert("L")
    w, h = flaeche.size
    px, hg = flaeche.load(), ImageStat.Stat(flaeche).median[0]
    tinte = [[abs(px[i, j] - hg) > 60 for j in range(h)] for i in range(w)]
    spalten = {i for i in range(w) if sum(tinte[i]) > 0.6 * h}
    zeilen = {j for j in range(h) if sum(tinte[i][j] for i in range(w)) > 0.6 * w}
    rest = [(i, j) for i in range(w) if i not in spalten for j in range(h) if j not in zeilen and tinte[i][j]]
    im_kreis = sum((x0 + i + 0.5 - x) ** 2 + (y0 + j + 0.5 - y) ** 2 <= k * k for i, j in rest)
    return im_kreis, len(rest) / (w * h)


def frei(img, x, y, r, streng=True):
    """Kein Stück Schrift unter dem Marker. Nicht streng: höchstens 2 % Schrift im Quadrat um den Kreis (große
    Marker im Gesamtbild sind höher als eine Zeile)."""
    s = schrift_unter(img, x, y, r)
    return s is not None and (s[0] <= 3 if streng else s[1] < 0.02)


def beschriftung(img, x, y, rect, bis):
    """Rechteck um die Schrift am Klickpunkt x, y bei Elementen, die keine eigene Zeile melden (Liste in einer
    Webseite, Tabelle, Werkzeugkasten); None, wenn dort keine waagerechte Schrift steht. rect: das Element,
    bis: Rand eines Menüs rechts vom Klick. Alles in Bildkoordinaten."""
    x0, x1 = round(max(rect[0], x - 300)), round(min(rect[2], x + 300, bis))
    y0, y1 = round(max(rect[1], y - 14)), round(min(rect[3], y + 15))
    if x1 - x0 < 10 or y1 - y0 < 12:
        return None
    feld = img.crop((x0, y0, x1, y1)).convert("L")
    w, h = feld.size
    px, hg = feld.load(), ImageStat.Stat(feld).median[0]
    tinte = [[abs(px[i, j] - hg) > 60 for j in range(h)] for i in range(w)]
    # Schriftzeile am Klick: Zeilen mit Schrift nahe am Klickpunkt, ohne waagerechte Linien (Rahmen, Kopfzeilen)
    cx, cy = round(x) - x0, round(y) - y0
    nah = range(max(0, cx - 20), min(w, cx + 21))
    gruppen = []
    for j in range(h):
        n = sum(tinte[i][j] for i in nah)
        if 0 < n <= 0.6 * len(nah):
            if gruppen and j - gruppen[-1][1] <= 2:
                gruppen[-1][1] = j
            else:
                gruppen.append([j, j])
    if not gruppen:
        return None
    t, u = min(gruppen, key=lambda q: max(q[0] - cy, cy - q[1], 0))
    if t == 0 or u == h - 1 or u - t > 24:   # reicht über den Ausschnitt hinaus: senkrechte Schrift, Bild
        return None
    # Läufe in dieser Zeile; senkrechte Linien (Zellränder, Feldrahmen) reichen über die Zeile hinaus
    linie = lambda i: all(tinte[i][j] for j in range(max(0, t - 2), min(h, u + 3)))
    laeufe, luecke = [], max(4, (u - t + 1) // 2)   # Lücken zwischen Wörtern überbrücken
    for i in range(w):
        if any(tinte[i][j] for j in range(t, u + 1)) and not linie(i):
            if laeufe and i - laeufe[-1][1] <= luecke:
                laeufe[-1][1] = i
            else:
                laeufe.append([i, i])
    k = next((k for k, l in enumerate(laeufe) if l[0] - 3 <= cx <= l[1] + 3), None)
    if k is None:
        return None
    a, b = laeufe[k]
    if b - a <= 20 and k + 1 < len(laeufe) and laeufe[k + 1][0] - b <= 12:   # Symbol oder Aufklapper: Name daneben
        b = laeufe[k + 1][1]
    if b - a > 0.8 * w:   # ganze Zeile hebt sich ab: keine Schrift erkennbar
        return None
    return x0 + a - 2, y0 + t - 3, x0 + b + 2, y0 + u + 3


# Baumeinträge (SpaceClaim meldet sie als Kästchen, dort steht der Name rechts außerhalb): Beschriftung in der
# ganzen Zeile suchen, rechts daneben ist es leer
OFFEN = {"TreeItemControl", "TextControl", "CheckBoxControl"}
KNOPF = {"ButtonControl", "SplitButtonControl", "TabItemControl", "CheckBoxControl", "RadioButtonControl"}


def ueberlappt(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def anker(g, W, H, img=None, off=(0, 0), menues=()):
    """Rechteck, neben das der Marker kommt: das Element, bei großen Elementen (Tabelle, Liste in einer Webseite)
    die Schrift am Klickpunkt im Foto img; None beim Ziehen, im Grafikfenster und ohne Schrift (dann zählt der
    Klickpunkt). off: Lage des Fotos, menues: aufgeklappte Menüs."""
    rect = el(g).get("rechteck")
    if g.get("x2") or not rect:
        return None
    if klein(rect, W, H):
        return rect
    if img is None or im_grafikfenster(g):
        return None
    ox, oy = off
    bis = min([m[0] for m in menues if m[0] > g["x"] - 4 and m[1] < g["y"] + 8 and g["y"] - 8 < m[3]] + [rect[2]])
    b = beschriftung(img, g["x"] - ox, g["y"] - oy, (rect[0] - ox, rect[1] - oy, rect[2] - ox, rect[3] - oy), bis - ox)
    return b and [b[0] + ox, b[1] + oy, b[2] + ox, b[3] + oy]


def marker_punkt(g, W, H, r, img=None, off=(0, 0), menues=()):
    """Marker bei kleinen Elementen direkt neben die Beschriftung, nicht darauf. Reihenfolge: rechts neben der
    Beschriftung (in der eigenen Zeile, bei Schrift in den Nachbarzeilen weiter rechts), links daneben, direkt
    rechts oder links neben dem Element, darüber, darunter; nie bei einem anderen Element und nie auf einem
    fremden Menü (menues: aufgeklappte Menüs des Schritts). Ist nirgends Platz: Knöpfe in ihre obere rechte Ecke
    (dicht gedrängte Knopfleisten), sonst links neben das Element (Rechtsklick in den Baum, das Menü liegt darüber).
    Große Elemente (Tabelle, Liste in einer Webseite): die Schrift am Klickpunkt gilt als Element, ist nirgends
    Platz, kommt der Marker an die Stelle mit der wenigsten Schrift. Ziehen, Klicks im Grafikfenster und ohne
    Schrift: am Klickpunkt."""
    rect = anker(g, W, H, img, off, menues)
    if rect is None:
        return g["x"], g["y"]
    ox, oy = off
    erkannt, ganz = None, el(g)["rechteck"]   # erkannt: Beschriftung, die bei großen Elementen im Foto gefunden wurde
    if not klein(ganz, W, H):
        # Marker nicht außerhalb des Elements (dort liegen andere Fenster): wie ein fremdes Menü behandeln
        menues = [*menues, (ganz[0] - W, ganz[1], ganz[0], ganz[3]), (ganz[2], ganz[1], ganz[2] + W, ganz[3])]
        g, erkannt = {**g, "element": {**el(g), "typ": "TextControl", "rechteck": rect}}, (rect[0] + 2, rect[2] - 2)
    y, typ = (rect[1] + rect[3]) / 2, el(g).get("typ")
    feld_links = rect[0] - r - 2
    if img is None:
        return (feld_links if typ in FELD else rect[0] + r), y
    eigen = lambda m: m[0] - 2 <= rect[0] and rect[2] <= m[2] + 2 and m[1] - 2 <= rect[1] and rect[3] <= m[3] + 2
    fremd = [m for m in menues if not eigen(m)]   # Menüs, in denen das Element nicht selbst steht
    sicht = list(rect)   # sichtbarer Teil: bis zum Rand eines Menüs, das darüber liegt
    for m in fremd:
        if ueberlappt(m, rect) and m[0] > rect[0]:
            sicht[2] = min(sicht[2], m[0])
    rand = sicht[2]
    if typ in OFFEN and sicht[2] == rect[2]:
        zeile = (rect[0], rect[1], W + ox, rect[3])
        rand = min([m[0] for m in fremd if ueberlappt(m, zeile) and m[0] > rect[0]] + [rect[2] + 400, W + ox])
    laeufe = [(a + ox, b + ox) for a, b in schrift_laeufe(img, (sicht[0] - ox, rect[1] - oy, rand - ox, rect[3] - oy))]
    text = erkannt or next((l for l in laeufe if l[0] - 3 <= g["x"] <= l[1] + 3),
                           max(laeufe, key=lambda l: l[1] - l[0], default=None))
    wahl = []   # (x, y, wie weit nach außen ausweichen, Richtung)
    if text:
        rechts = min((l[0] for l in laeufe if l[0] > text[1]), default=None)
        grenze = rechts - 4 if rechts is not None else rand if typ in OFFEN else sicht[2]
        x = text[1] + 5 + r
        if x + r <= grenze:   # nur wenn der Marker in die eigene Zeile passt
            wahl.append((x, y, grenze - r - x, 1))
        links = max((l[1] for l in laeufe if l[1] < text[0]), default=None)
        x, ende = text[0] - 5 - r, links + 4 if links is not None else rect[0]
        if x - r >= ende:
            wahl.append((x, y, x - r - ende, -1))
    wahl += [(rect[2] + 4 + r, y, 0, 1), (feld_links, y, 0, -1)]
    mx = (text[1] if text else rect[2]) - r
    if typ not in OFFEN:   # Baumeinträge: über und unter ihnen stehen andere Einträge, dann lieber links aufs Symbol
        wahl += [(mx, rect[1] - 3 - r, 0, 1), (mx, rect[3] + 3 + r, 0, 1)]
    stellen = [(x + richtung * k * r / 2, yy) for x, yy, weite, richtung in wahl for k in range(int(weite // (r / 2)) + 1)]
    stellen = [(x, yy) for x, yy in stellen if not any(ueberlappt(m, (x - r, yy - r, x + r, yy + r)) for m in fremd)]
    for streng in (True, False):   # erste Stelle ohne Schrift (sonst mit wenig) und außerhalb fremder Menüs
        for x, yy in stellen:
            if frei(img, x - ox, yy - oy, r, streng):
                return x, yy
    if erkannt:   # lieber etwas Schrift daneben verdecken als die angeklickte
        rest = [(s[0], i) for i, (x, yy) in enumerate(stellen) if (s := schrift_unter(img, x - ox, yy - oy, r))]
        return stellen[min(rest)[1]] if rest else (g["x"], g["y"])
    if typ in KNOPF and typ not in OFFEN:   # auf dem eigenen Knopf, nicht auf dem Nachbarn
        return rect[2] - 0.7 * r, rect[1] + 0.7 * r
    return feld_links, y   # links daneben verdeckt höchstens ein Symbol, keine Beschriftung


def geometrie(schritt, W, H, img=None, rad=None):
    """Markergröße, Markerpunkte, Zielpunkt beim Ziehen und Punkte für den Ausschnitt (Bildkoordinaten).
    Mit dem Foto img stehen die Marker neben der Beschriftung, passend zum Radius rad (sonst r)."""
    mon = schritt["monitor"] or {"left": 0, "top": 0}
    ox, oy = mon["left"], mon["top"]
    # Markergröße an der Zeilenhöhe der Oberfläche ausrichten (Menü, Baum), sonst 22 px
    hoehen = [r[3] - r[1] for g in schritt["glieder"] if (r := el(g).get("rechteck")) and 0 < r[3] - r[1] < 60]
    r = max(10, round(0.6 * (min(hoehen) if hoehen else 22)))
    menues = [(w[0] + ox, w[1] + oy, w[2] + ox, w[3] + oy) for w in sichtbar(schritt) if (w[2] - w[0]) * (w[3] - w[1]) < 0.4 * W * H]
    # Kontextmenüs fehlen manchmal unter den Fenstern: Sie gehen am Klickpunkt eines Rechtsklicks auf
    menue_folgt = any(el(h).get("typ") in MENU for h in schritt["glieder"])
    kontext = lambda g: [(g["x"], g["y"] - 4, W + ox, H + oy)] if g["art"] == "rechtsklick" and menue_folgt else []
    punkte = [(x - ox, y - oy) for x, y in (marker_punkt(g, W, H, rad or r, img, (ox, oy), menues + kontext(g))
                                            for g in schritt["glieder"])]
    box = list(punkte)
    for g in schritt["glieder"]:
        rect = el(g).get("rechteck")
        if img is not None and rect and not klein(rect, W, H):   # großes Element: die Beschriftung am Klickpunkt
            rect = anker(g, W, H, img, (ox, oy), menues + kontext(g))
        elif img is not None and rect and typ(g) in MENU:   # Menüzeilen sind breit und hinter der Beschriftung leer
            ende = rect[0] - ox
            for a, b in schrift_laeufe(img, (rect[0] - ox, rect[1] - oy, rect[2] - ox, rect[3] - oy)):
                if ende > rect[0] - ox and a - ende > 24:   # Symbol und Wörter, ohne Tastenkürzel und Pfeil
                    break
                ende = b
            rect = [rect[0], rect[1], min(rect[2], ende + ox + 10), rect[3]]
        if rect and rect[2] - rect[0] < W * 0.4 and rect[3] - rect[1] < H * 0.1:  # Menüzeilen mit ins Bild, keine Fenster
            box += [(rect[0] - ox, rect[1] - oy), (rect[2] - ox, rect[3] - oy)]
            if img is not None and typ(g) in FELD:   # Eingabefeld: mit dem Namen der Eigenschaft links davor
                ym = (rect[1] + rect[3]) / 2 - oy
                box.append((links_daneben(img, rect[0] - ox, ym, 0, 200), ym))
    ziel = None
    if schritt.get("ziehen"):
        ziel = (schritt["ziehen"]["x2"] - ox, schritt["ziehen"]["y2"] - oy)
        box.append(ziel)
    return r, punkte, ziel, box


def zeichnen(img, r, punkte, ziel, start=1):
    """Nummerierte Marker (ab start), beim Ziehen mit Pfeil zum Zielpunkt."""
    d = ImageDraw.Draw(img)
    if ziel and punkte:
        d.line([punkte[0], ziel], fill=ROT, width=max(3, r // 4))
        d.ellipse([ziel[0] - r // 2, ziel[1] - r // 2, ziel[0] + r // 2, ziel[1] + r // 2], fill=ROT)
    f = schrift(round(r * 1.3))
    for k, (x, y) in enumerate(punkte, start):
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
    bild_zusammen(aufnahme, [schritt], datei)


def bild_zusammen(aufnahme, schritte, datei):
    """Mehrere Schritte in einem Bild (z. B. Feld anklicken, dann Wert wählen): Foto des letzten Schritts,
    Fenster aller Schritte sichtbar, Marker aller Schritte fortlaufend nummeriert."""
    img = Image.open(aufnahme / schritte[-1]["frame"]).convert("RGB")
    fenster = [f for s in schritte for f in sichtbar(s)]
    img = abdecken(img, fenster)
    roh = img.copy()   # Schrift im Foto ohne Marker suchen
    box, n = [], 1
    for s in schritte:
        r, punkte, ziel, b = geometrie(s, *img.size, roh)
        zeichnen(img, r, punkte, ziel, n)
        n += len(punkte)
        box += b
    img.crop(begrenzen(ausschnitt(box, *img.size), fenster)).save(datei, optimize=True)


def links_daneben(img, x, y, r, abstand=30):
    """Anfang der Beschriftung, die links an einen Marker (Mitte x, y, Radius r, Bildkoordinaten) grenzt, höchstens
    abstand entfernt; ohne Beschriftung der linke Rand des Markers."""
    a = x - r
    for l0, l1 in reversed(schrift_laeufe(img, (x - r - 250, y - 7, x - r, y + 7))):
        if a - l1 > (abstand if a == x - r else 8):   # Abstand zum Marker, dann Lücken zwischen Wörtern
            break
        a = l0
    return a


def bild_uebersicht(aufnahme, schritte, datei, f=2, vorher=None):
    """Für Einsteiger: ganzes Fenster statt Ausschnitt, damit man sieht, wo im Programm geklickt wird.
    Klickt der letzte Schritt auf ein kleines Bedienelement, kommt eine Lupe (f-fach) dazu, die an der
    ruhigsten Stelle des Fensters liegt. Sind nur kleine Fenster bekannt (z. B. ein aufgeklapptes Menü),
    kommt das Programmfenster aus dem Schritt davor (vorher) dazu."""
    img = Image.open(aufnahme / schritte[-1]["frame"]).convert("RGB")
    fenster = [w for s in schritte for w in sichtbar(s)]
    flaeche = sum((w[2] - w[0]) * (w[3] - w[1]) for w in fenster)
    if vorher and flaeche < 0.4 * img.width * img.height:
        fenster += sichtbar(vorher)
    img = abdecken(img, fenster)
    W, H = img.size
    gx0, gy0, gx1, gy1 = ganz = begrenzen((0, 0, W, H), fenster)
    roh = img.copy()
    alle, n, letzte = [], 1, None
    for s in schritte:
        r, punkte, ziel, box = geometrie(s, W, H, roh)
        R = max(r, round((gx1 - gx0) * 0.016))  # Marker groß genug für das verkleinerte Gesamtbild
        gross = geometrie(s, W, H, roh, R)[1]   # neben der Beschriftung, passend zum großen Marker
        zeichnen(img, R, gross, ziel, n)
        letzte = (s, r, punkte, ziel, n, box)
        alle += gross
        n += len(punkte)
    s, r, punkte, ziel, n0, box = letzte
    rect = el(s["glieder"][-1]).get("rechteck") if s["glieder"] else None
    if punkte and klein(rect, W, H) and not ziel:
        # Lupe über Marker und angeklickte Einträge, damit die Beschriftung neben dem Marker ganz drin ist
        ecken = [(x + d, y) for x, y in punkte for d in (-r, r)] + box
        ecken += [(links_daneben(roh, x, y, r), y) for x, y in punkte]
        xs, ys = [p[0] for p in ecken], [p[1] for p in ecken]
        lw, lh = round(max(300, max(xs) - min(xs) + 80)), round(max(130, max(ys) - min(ys) + 60))
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        q0 = max(gx0, min(round(cx - lw / 2), gx1 - lw))
        q1 = max(gy0, min(round(cy - lh / 2), gy1 - lh))
        quelle = (q0, q1, q0 + lw, q1 + lh)
        lupe = roh.crop(quelle)
        zeichnen(lupe, r, [(x - q0, y - q1) for x, y in punkte], None, n0)
        f = min(f, max(1.4, 0.4 * (gx1 - gx0) / lw))  # weite Menüketten: Lupe nicht breiter als 40 % des Fensters
        f = min(f, (gy1 - gy0 - 90) / lh)   # lange Menüs: Lupe nicht höher als das Fenster
        lupe = lupe.resize((round(lw * f), round(lh * f)), Image.LANCZOS)
        # ruhigste Stelle: geringste Helligkeitsstreuung, nicht über Markern oder der Quelle
        frei = alle + [(quelle[0], quelle[1]), (quelle[2], quelle[3]), (quelle[0], quelle[3]), (quelle[2], quelle[1])]
        best = None
        for lx in range(gx0 + 20, gx1 - lupe.width - 19, 40):
            for ly in range(gy0 + 60, gy1 - lupe.height - 19, 40):
                if any(lx - 40 < x < lx + lupe.width + 40 and ly - 40 < y < ly + lupe.height + 40 for x, y in frei):
                    continue
                if lx < quelle[2] and quelle[0] < lx + lupe.width and ly < quelle[3] and quelle[1] < ly + lupe.height:
                    continue
                v = sum(ImageStat.Stat(roh.crop((lx, ly, lx + lupe.width, ly + lupe.height)).convert("L")).stddev)
                if best is None or v < best[0]:
                    best = (v, lx, ly)
        if best:
            _, lx, ly = best
            d = ImageDraw.Draw(img)
            d.rectangle(quelle, outline=CYAN, width=3)
            rechts = lx > quelle[2]
            d.line([(quelle[2] if rechts else quelle[0], (quelle[1] + quelle[3]) / 2),
                    (lx if rechts else lx + lupe.width, ly + lupe.height / 2)], fill=CYAN, width=3)
            schatten = Image.new("L", (lupe.width + 40, lupe.height + 40), 0)
            ImageDraw.Draw(schatten).rectangle((20, 20, lupe.width + 20, lupe.height + 20), fill=110)
            img.paste((0, 0, 0), (lx - 14, ly - 14), schatten.filter(ImageFilter.GaussianBlur(9)))
            img.paste(lupe, (lx, ly))
            ImageDraw.Draw(img).rectangle((lx - 2, ly - 2, lx + lupe.width + 1, ly + lupe.height + 1), outline=CYAN, width=4)
    img.crop(ganz).save(datei, optimize=True)


def gif_bauen(aufnahme, schritte, datei, breite=1280, ms=1600):
    """Ablauf eines Kapitels als GIF: alle Fotos je Schritt, gleicher Ausschnitt, Zähler „3 / 9".
    Marker werden erst nach dem Verkleinern gezeichnet, damit sie lesbar bleiben."""
    mit_bild = [st for st in schritte if st["film"]]
    if not mit_bild:
        return
    W, H = Image.open(aufnahme / mit_bild[0]["film"][0]).size
    geo = [geometrie(st, W, H, Image.open(aufnahme / st["film"][0]).convert("RGB")) for st in mit_bild]
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
    ap.add_argument("--uebersicht", action="store_true", help="ganzes Fenster plus Lupe statt Ausschnitt (Einsteiger)")
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
                if a.uebersicht:
                    bild_uebersicht(a.aufnahme, [s], out / datei, vorher=schritte[nr - 1] if nr else None)
                else:
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
