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


def sichtfaktor(datei):
    """Längsschnitt durch einen Blechflügel der Vakuumröhre: links das offene 20-mm-Stück, rechts die lange Röhre."""
    w, h, s = 960, 480, 4.0                                   # 4 px je mm
    l2, ri, wg = 10 * s, 32.5 * s, 2.5 * s                    # halbe Stücklänge, Glas innen, Glaswand
    y0 = 120                                                  # Innenseite des oberen Glases
    yc, y1 = y0 + ri, y0 + 2 * ri                             # Blech, Innenseite des unteren Glases
    hell = "#9aa3a8"

    def stueck(cx, blass=False):
        return ['<g opacity="0.45">' if blass else "<g>",
                f'<rect x="{cx - l2}" y="{y0 - wg}" width="{2 * l2}" height="{wg}" fill="{GLAS}" stroke="{GRAU}" stroke-width="1.2"/>',
                f'<rect x="{cx - l2}" y="{y1}" width="{2 * l2}" height="{wg}" fill="{GLAS}" stroke="{GRAU}" stroke-width="1.2"/>',
                f'<rect x="{cx - l2}" y="{yc - 2}" width="{2 * l2}" height="4" fill="{DUNKEL}"/>', "</g>"]

    def schnitt(x):
        return f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" stroke="{hell}" stroke-width="1.2" stroke-dasharray="6 5"/>'

    def strahl(x, winkel, cx, offen=False, blass=False):
        """Strahl vom oberen Glas bei x unter winkel (Grad gegen die Senkrechte) bis zum Blech oder zum offenen Ende."""
        tn = math.tan(math.radians(winkel))
        xa = x + (yc - 2 - y0) * tn
        op = ' opacity="0.45"' if blass else ""
        punkt = f'<circle cx="{x:.1f}" cy="{y0 + 1}" r="3.5" fill="{ROT}"{op}/>'
        if not offen or abs(xa - cx) <= l2:
            return [punkt, f'<line x1="{x:.1f}" y1="{y0}" x2="{xa:.1f}" y2="{yc - 3}" stroke="{ROT}" stroke-width="1.6"{op} '
                           f'marker-end="url(#pr)"/>']
        xe = cx + math.copysign(l2, tn)                        # hier verlässt der Strahl das Stück
        ye = y0 + (xe - x) / tn
        a = math.radians(winkel)
        return [punkt, f'<line x1="{x:.1f}" y1="{y0}" x2="{xe:.1f}" y2="{ye:.1f}" stroke="{ROT}" stroke-width="1.6"/>',
                f'<line x1="{xe:.1f}" y1="{ye:.1f}" x2="{xe + 60 * math.sin(a):.1f}" y2="{ye + 60 * math.cos(a):.1f}" '
                f'stroke="{hell}" stroke-width="1.6" stroke-dasharray="5 4" marker-end="url(#pg)"/>']

    winkel = (0, 12, -12, 24, -24, 40, -40)
    el = [f'<defs><marker id="pr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
          f'<path d="M0,0 L10,5 L0,10 z" fill="{ROT}"/></marker>'
          f'<marker id="pg" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
          f'<path d="M0,0 L10,5 L0,10 z" fill="{hell}"/></marker></defs>']
    # Links: Modell, vorn und hinten offen
    c1 = 230
    el += [text(c1, 40, "Modell: 20 mm langes Stück", farbe=DUNKEL, fett=True),
           text(c1, y0 - wg - 14, "vorn offen · hinten offen"),
           *stueck(c1), schnitt(c1 - l2), schnitt(c1 + l2)]
    for wi in winkel:
        el += strahl(c1, wi, c1, offen=True)
    el += [text(c1, y1 + wg + 44, "Ein großer Teil der Strahlung geht"),
           text(c1, y1 + wg + 68, "vorn und hinten hinaus und trifft nichts")]
    # Mitte: Beschriftung
    el += [text(462, y0 - wg / 2 + 6, "Glas"), text(462, yc + 6, "Absorber"), text(462, y1 + wg / 2 + 6, "Glas")]
    # Rechts: lange Röhre mit Nachbarstücken
    c2 = 720
    el += [text(c2, 40, "Wirklichkeit: lange Röhre", farbe=DUNKEL, fett=True),
           text(c2 - 2 * l2, y0 - wg - 14, "Nachbar", anker="middle"), text(c2 + 2 * l2, y0 - wg - 14, "Nachbar"),
           *stueck(c2 - 2 * l2, blass=True), *stueck(c2 + 2 * l2, blass=True), *stueck(c2),
           schnitt(c2 - l2), schnitt(c2 + l2)]
    for wi in winkel:
        el += strahl(c2, wi, c2)
    for x, wi in ((c2 + ri * math.tan(math.radians(40)), -40), (c2 - ri * math.tan(math.radians(24)), 24)):
        el += strahl(x, wi, c2, blass=True)
    el += [text(c2, y1 + wg + 44, "Was hinausgeht, trifft die Nachbarstücke,"),
           text(c2, y1 + wg + 68, "genauso viel kommt von dort zurück")]
    kopf = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'font-family="{SCHRIFT}">')
    (OUT / datei).write_text("\n".join([kopf, f'<rect width="{w}" height="{h}" fill="white"/>', *el, "</svg>"]) + "\n",
                             encoding="utf-8")


if __name__ == "__main__":
    strahlung_arten("p2_strahlung_arten.svg")
    sichtfaktor("p2_sichtfaktor.svg")
    print("Skizzen geschrieben nach", OUT)
