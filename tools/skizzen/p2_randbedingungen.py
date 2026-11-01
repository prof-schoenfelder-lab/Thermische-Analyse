#!/usr/bin/env python3
"""Übersicht P2: drei Gruppen von Randbedingungen (an der Systemgrenze, im ganzen Körper, überall) als SVG.

Aufruf:  python3 tools/skizzen/p2_randbedingungen.py

Bilder vereinfacht aus den Aufgabenskizzen (Vakuumröhre, Erdkabel), Farben wie dort:
rot Wärme hinein und Strahlung, cyan Konvektion, dunkelblau feste Temperatur.
"""
import math

from p2_aufgaben import BODEN, CU, CYAN, DUNKEL, GLAS, GRAU, ROT, SCHRIFT, WASSER, OUT, defs, pfeil, ring, welle

W, H, PB = 960, 452, 304                 # Bildgröße, Breite eines Feldes
LINIE, FLAECHE = "#E2E8EC", "#F2F6F9"


def t(x, y, inhalt, gr=18, anker="middle", farbe=GRAU, fett=False):
    stil = ' font-weight="700"' if fett else ""
    return f'<text x="{x:.0f}" y="{y:.0f}" text-anchor="{anker}" font-size="{gr}" fill="{farbe}"{stil}>{inhalt}</text>'


def wuerfel(cx, oben, art):
    """Kleiner Würfel, hervorgehoben ist Fläche, Kante, Punkt oder der ganze Körper."""
    a, d = 28, 12
    fx, fy = cx - (a + d) / 2, oben + d
    F = [(fx, fy), (fx + a, fy), (fx + a, fy + a), (fx, fy + a)]
    B = [(x + d, y - d) for x, y in F[:3]]
    poly = lambda p: " ".join(f"{x:.1f},{y:.1f}" for x, y in p)
    flaechen = {"vorn": F, "oben": [F[0], F[1], B[1], B[0]], "rechts": [F[1], B[1], B[2], F[2]]}
    tint = {"vorn": "white", "oben": FLAECHE, "rechts": LINIE}
    deck = {"vorn": 0.45, "oben": 0.7, "rechts": 0.6}
    el = []
    for name, p in flaechen.items():
        fuell, op = tint[name], 1
        if art == "koerper" or (art == "flaeche" and name == "vorn"):
            fuell, op = CYAN, deck[name]
        el.append(f'<polygon points="{poly(p)}" fill="{fuell}" fill-opacity="{op}" stroke="{GRAU}" stroke-width="1.2" '
                  f'stroke-linejoin="round"/>')
    if art == "kante":
        el.append(f'<line x1="{F[1][0]}" y1="{F[1][1]}" x2="{F[2][0]}" y2="{F[2][1]}" stroke="{CYAN}" stroke-width="5" '
                  f'stroke-linecap="round"/>')
    if art == "punkt":
        el.append(f'<circle cx="{F[1][0]}" cy="{F[1][1]}" r="5" fill="{CYAN}"/>')
    name = {"flaeche": "Fläche", "kante": "Kante", "punkt": "Punkt", "koerper": "Körper"}[art]
    return el + [t(cx, oben + a + d + 20, name, gr=16)]


def feld(x0, titel, unter, bild, arten):
    el = [f'<rect x="1" y="1" width="{PB - 2}" height="{H - 2}" rx="8" fill="white" stroke="{LINIE}" stroke-width="1.5"/>',
          t(PB / 2, 36, titel, gr=21, farbe=DUNKEL, fett=True), t(PB / 2, 60, unter, gr=17),
          *bild,
          f'<line x1="16" y1="342" x2="{PB - 16}" y2="342" stroke="{LINIE}" stroke-width="1.2"/>',
          t(PB / 2, 366, "wirkt auf", gr=16)]
    for i, art in enumerate(arten):
        el += wuerfel(PB / 2 + (i - (len(arten) - 1) / 2) * 66, 376, art)
    return [f'<g transform="translate({x0},0)">', *el, "</g>"]


def roehre():
    cx, cy, ra, ri = PB / 2, 205, 70, 65
    el = [ring(cx, cy, ra, ri, GLAS),
          f'<rect x="{cx - 60}" y="{cy - 1.5}" width="120" height="3" fill="{DUNKEL}"/>',
          f'<circle cx="{cx}" cy="{cy}" r="10" fill="{WASSER}"/>',              # Blech endet am Rohr
          ring(cx, cy, 12, 10, DUNKEL, rand=DUNKEL)]
    el += [pfeil(x, 104, x, cy - 6, ROT, 2) for x in (cx - 48, cx - 26, cx + 26, cx + 48)]
    el += [t(cx, 96, "Heat Flux", farbe=ROT, fett=True),
           welle(cx - ra - 4, cy + 30, cx - ra - 52, cy + 30),
           t(8, 268, "Radiation", anker="start", farbe=ROT, fett=True), t(8, 287, "Himmel", gr=16, anker="start"),
           pfeil(cx + ra + 4, cy + 30, cx + ra + 48, cy + 30, CYAN),
           t(PB - 8, 268, "Convection", anker="end", farbe=CYAN, fett=True), t(PB - 8, 287, "Luft", gr=16, anker="end"),
           f'<line x1="{cx}" y1="{cy + 8}" x2="{cx}" y2="{cy + 84}" stroke="{GRAU}" stroke-width="1"/>',
           f'<circle cx="{cx}" cy="{cy}" r="2.5" fill="{GRAU}"/>',
           t(cx, 308, "Convection", farbe=CYAN, fett=True), t(cx, 327, "Wasser im Rohr", gr=16)]
    return el


def kabel():
    cx, cy, r1, r2 = PB / 2, 195, 72, 31.5
    el = ['<defs><radialGradient id="glut"><stop offset="0" stop-color="#f08a6c"/>'
          f'<stop offset="1" stop-color="{CU}"/></radialGradient></defs>',
          f'<circle cx="{cx}" cy="{cy}" r="{r1}" fill="#f3f3f3" stroke="{GRAU}" stroke-width="1.5"/>',
          f'<circle cx="{cx}" cy="{cy}" r="{r2}" fill="url(#glut)" stroke="{GRAU}" stroke-width="1.2"/>']
    for i in range(-3, 4):                                    # Wärmequellen im Leiter
        for j in range(-3, 4):
            x, y = cx + 9 * i + (4.5 if j % 2 else 0), cy + 7.8 * j
            if math.hypot(x - cx, y - cy) < r2 - 6:
                el.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.8" fill="{ROT}"/>')
    el += [t(cx, cy - r1 - 14, "Isolierung", gr=16),
           f'<line x1="{cx}" y1="{cy + r2 + 2}" x2="{cx}" y2="{cy + 88}" stroke="{GRAU}" stroke-width="1"/>',
           t(cx, 308, "Internal Heat Generation", farbe=ROT, fett=True), t(cx, 327, "Stromwärme im Leiter", gr=16)]
    return el


def erdreich():
    x0, y0, bw, bt = 32, 100, 240, 150
    cx, cy = x0 + bw / 2, y0 + bt / 3
    return [f'<rect x="{x0}" y="{y0}" width="{bw}" height="{bt}" fill="{BODEN}" stroke="{GRAU}" stroke-width="1.5"/>',
            f'<circle cx="{cx}" cy="{cy}" r="9" fill="#f3f3f3" stroke="{GRAU}" stroke-width="1.2"/>',
            f'<circle cx="{cx}" cy="{cy}" r="4.5" fill="{CU}"/>',
            t(cx, y0 + bt - 30, "Erdreich", gr=16),
            f'<line x1="{x0}" y1="{y0 + bt}" x2="{x0 + bw}" y2="{y0 + bt}" stroke="{DUNKEL}" stroke-width="6"/>',
            t(cx, 284, "Temperature", farbe=DUNKEL, fett=True), t(cx, 303, "10 °C in 3 m Tiefe", gr=16)]


def uebersicht(datei):
    lu = (W - 3 * PB) / 4
    el = [*feld(lu, "An der Systemgrenze", "Wärme geht über die Oberfläche", roehre(), ["flaeche"]),
          *feld(2 * lu + PB, "Im ganzen Körper", "Wärme entsteht im Material", kabel(), ["koerper"]),
          *feld(3 * lu + 2 * PB, "Überall", "Temperatur steht fest", erdreich(), ["flaeche", "kante", "punkt", "koerper"])]
    kopf = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{SCHRIFT}">'
    (OUT / datei).write_text("\n".join([kopf, f'<rect width="{W}" height="{H}" fill="white"/>', defs(), *el, "</svg>"]) + "\n",
                             encoding="utf-8")


if __name__ == "__main__":
    uebersicht("p2_rb_gruppen.svg")
    print("Skizze geschrieben nach", OUT)
