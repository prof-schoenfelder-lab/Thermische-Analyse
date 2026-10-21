#!/usr/bin/env python3
"""Theorie-Skizze P2: Strahlung To Ambient gegen Surface to Surface als SVG in docs/P2_Randbedingungen/images/.

Aufruf:  python3 tools/skizzen/p2_strahlung.py

Stil und Schriftgröße wie tools/skizzen/p1_wand.py (Anzeige in Originalgröße, 18 px).
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "docs/P2_Randbedingungen/images"
CYAN, DUNKEL, GRAU, ROT = "#009EE3", "#022541", "#2E3639", "#E53009"
FS = 18
SCHRIFT = "'Source Sans Pro', 'Source Sans 3', Arial, sans-serif"
WARM, GLAS = "#fbe0d9", "#e6f5fc"        # Füllung warme Fläche, Glas
W, H = 960, 400


def text(x, y, inhalt, anker="middle", farbe=GRAU, fett=False):
    stil = ' font-weight="700"' if fett else ""
    return f'<text x="{x:.0f}" y="{y:.0f}" text-anchor="{anker}" font-size="{FS}" fill="{farbe}"{stil}>{inhalt}</text>'


def welle(x, y_start, y_ende, deckkraft=0.75, breite=1.6, amp=4.0, perioden=4.25, schritte=200):
    """Senkrechte Sinuswelle (Wärmestrahlung) von y_start nach y_ende, Pfeilspitze am Ende."""
    pkt = []
    for i in range(schritte + 1):
        f = i / schritte
        pkt.append(f"{x + amp * math.sin(2 * math.pi * perioden * f):.1f},{y_start + (y_ende - y_start) * f:.1f}")
    return (f'<path d="M{" L".join(pkt)}" fill="none" stroke="{ROT}" stroke-width="{breite}" opacity="{deckkraft}" '
            f'stroke-linejoin="round" marker-end="url(#pr)"/>')


def platte(x, y, w, fuell):
    return f'<rect x="{x}" y="{y}" width="{w}" height="14" rx="2" fill="{fuell}" stroke="{GRAU}" stroke-width="1.5"/>'


def strahlung_arten(datei):
    el = [f'<defs><marker id="pr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
          f'<path d="M0,0 L10,5 L0,10 z" fill="{ROT}"/></marker></defs>']
    # Links: To Ambient
    el += [text(240, 40, "To Ambient", farbe=DUNKEL, fett=True),
           f'<rect x="90" y="66" width="300" height="56" rx="6" fill="none" stroke="{GRAU}" stroke-width="1.2" stroke-dasharray="7 5"/>',
           text(240, 100, "Umgebung, Temperatur vorgegeben"),
           *(welle(x, 284, 134) for x in (170, 240, 310)),
           platte(110, 290, 260, WARM),
           text(240, 346, "Fläche strahlt in die Umgebung"),
           text(240, 372, "Gegenüber: feste Temperatur")]
    # Rechts: Surface to Surface
    el += [text(710, 40, "Surface to Surface", farbe=DUNKEL, fett=True),
           platte(590, 96, 240, GLAS), text(842, 109, "Glas", anker="start"),
           *(welle(x, 284, 116) for x in (630, 750)),
           *(welle(x, 116, 284, deckkraft=0.4, breite=1.2) for x in (690, 810)),
           platte(590, 290, 240, WARM), text(842, 303, "Absorber", anker="start"),
           text(710, 346, "Flächen strahlen sich gegenseitig an"),
           text(710, 372, "Beide Temperaturen werden berechnet")]
    kopf = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'font-family="{SCHRIFT}">')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / datei).write_text("\n".join([kopf, f'<rect width="{W}" height="{H}" fill="white"/>', *el, "</svg>"]) + "\n",
                             encoding="utf-8")


if __name__ == "__main__":
    strahlung_arten("p2_strahlung_arten.svg")
    print("Skizzen geschrieben nach", OUT)
