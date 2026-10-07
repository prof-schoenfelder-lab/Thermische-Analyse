#!/usr/bin/env python3
"""Aufgabenskizzen P1 (Wandschnitt, 1D-Netz) als SVG in docs/P1_Einfuehrung/images/.

Aufruf:  python3 tools/skizzen/p1_wand.py

Die SVGs werden in Originalgröße angezeigt (Breite = viewBox-Breite), damit die
Beschriftung (18 px) so groß ist wie der normale Text der Kursseite (0,82 rem
bei 135 % Grundschrift = 17,7 px). Maßstab der Schichten: 1 px je mm.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "docs/P1_Einfuehrung/images"
CYAN, DUNKEL, GRAU, ROT = "#009EE3", "#022541", "#2E3639", "#E53009"
FS = 18                                   # Schriftgröße wie Fließtext
SCHRIFT = "'Source Sans Pro', 'Source Sans 3', Arial, sans-serif"  # Namen mit Leerzeichen/Ziffer in Anführungszeichen
FUELL = {"KS": ("#d9dcde", "Kalksandstein"), "EPS": ("#e6f5fc", "EPS"), "VZ": ("#e8c9b8", "Vollziegel")}
W, H, Y0, Y1 = 960, 450, 74, 334          # Bildgröße, Ober- und Unterkante der Wand


def text(x, y, inhalt, anker="middle", farbe=GRAU, fett=False, kursiv=False, halo=False):
    stil = (' font-weight="700"' if fett else "") + (' font-style="italic"' if kursiv else "")
    if halo:  # weißer Rand: lesbar auf der gepunkteten Dämmung
        stil += ' stroke="white" stroke-width="5" stroke-linejoin="round" paint-order="stroke"'
    return f'<text x="{x:.0f}" y="{y:.0f}" text-anchor="{anker}" font-size="{FS}" fill="{farbe}"{stil}>{inhalt}</text>'


def svg_datei(datei, w, h, elemente):
    kopf = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'font-family="{SCHRIFT}">')
    (OUT / datei).write_text("\n".join([kopf, f'<rect width="{w}" height="{h}" fill="white"/>', *elemente, "</svg>"]) + "\n",
                             encoding="utf-8")


def defs():
    return ('<defs><marker id="pf" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{ROT}"/></marker>'
            '<marker id="pm" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{GRAU}"/></marker>'
            '<marker id="plr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{ROT}"/></marker>'
            '<marker id="plc" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{CYAN}"/></marker>'
            '<pattern id="eps" width="14" height="14" patternUnits="userSpaceOnUse">'
            f'<circle cx="7" cy="7" r="3" fill="none" stroke="{CYAN}" stroke-width="1" opacity="0.5"/></pattern></defs>')


def wand(datei, schichten, modus, links, rechts):
    """schichten: [(typ, dicke_text, dicke_mm, lambda)]; modus 'temp' (Oberflächentemperatur) oder 'konv'."""
    breite = sum(s[2] for s in schichten)
    x = (W - breite) / 2
    xl, el = x, [defs()]
    for typ, dtext, dmm, lam in schichten:
        fuell, name = FUELL[typ]
        el.append(f'<rect x="{x}" y="{Y0}" width="{dmm}" height="{Y1 - Y0}" fill="{fuell}" stroke="{GRAU}" stroke-width="1.5"/>')
        if typ == "EPS":
            el.append(f'<rect x="{x}" y="{Y0}" width="{dmm}" height="{Y1 - Y0}" fill="url(#eps)"/>')
        cx, ym = x + dmm / 2, (Y0 + Y1) / 2
        el += [text(cx, ym - 26, name, farbe=DUNKEL, fett=True, halo=True), text(cx, ym, f"λ = {lam}", halo=True),
               text(cx, ym + 24, "W/(m·K)", halo=True)]
        yb = Y1 + 30  # Bemaßung
        el += [f'<line x1="{x}" y1="{Y1 + 6}" x2="{x}" y2="{yb + 8}" stroke="{GRAU}"/>',
               f'<line x1="{x + dmm}" y1="{Y1 + 6}" x2="{x + dmm}" y2="{yb + 8}" stroke="{GRAU}"/>',
               f'<line x1="{x + 3}" y1="{yb}" x2="{x + dmm - 3}" y2="{yb}" stroke="{GRAU}" marker-start="url(#pm)" marker-end="url(#pm)"/>',
               text(cx, yb + 26, dtext)]
        x += dmm
    xr = x
    el += [text(xl - 95, 40, "innen", farbe=DUNKEL, fett=True), text(xr + 95, 40, "außen", farbe=DUNKEL, fett=True)]
    ym = (Y0 + Y1) / 2
    for xs, txt, farbe, seite in ((xl, links, ROT, -1), (xr, rechts, CYAN, 1)):
        anker = "end" if seite < 0 else "start"
        if modus == "temp":  # vorgegebene Temperatur auf der ganzen Fläche
            xb = xs + seite * 4
            el.append(f'<line x1="{xb}" y1="{Y0}" x2="{xb}" y2="{Y1}" stroke="{farbe}" stroke-width="6"/>')
            el.append(text(xs + seite * 18, ym + 6, txt, anker, farbe, fett=True))
        else:  # Konvektion: Luft strömt an der ganzen Fläche entlang
            el.append(f'<line x1="{xs + seite * 3}" y1="{Y0}" x2="{xs + seite * 3}" y2="{Y1}" stroke="{farbe}" '
                      f'stroke-width="3" stroke-dasharray="8 6"/>')
            for k in range(3):
                xx = xs + seite * (18 + 13 * k)
                el.append(f'<path d="M{xx},{Y1} C{xx + seite * 7},{Y1 - 65} {xx - seite * 7},{Y1 - 130} {xx},{ym} '
                          f'S{xx - seite * 7},{Y0 + 65} {xx},{Y0 + 4}" fill="none" stroke="{farbe}" stroke-width="1.6" '
                          f'opacity="0.7" marker-end="url(#{"plr" if farbe == ROT else "plc"})"/>')
            xt = xs + seite * 70
            el += [text(xt, ym - 6, txt[0], anker, farbe, fett=True), text(xt, ym + 18, txt[1], anker, farbe)]
    yq = Y1 - 34  # Wärmestrom durch die Wand
    el += [f'<line x1="{xl + 12}" y1="{yq}" x2="{xr - 12}" y2="{yq}" stroke="{ROT}" stroke-width="2.5" marker-end="url(#pf)"/>',
           text(xl + 26, yq - 10, "q̇", "start", ROT, kursiv=True),
           text(W / 2, H - 10, "Wandausschnitt 100 mm × 100 mm (Schnitt)")]
    svg_datei(datei, W, H, el)


def netz_1d(datei):
    """Wand in vier Elemente, je Knoten eine Temperatur, stückweise linear."""
    w, h, x0, x1, yw0, yw1 = 900, 380, 170, 730, 210, 285
    xs = [x0 + i * (x1 - x0) / 4 for i in range(5)]
    T = [20, 14, 8, 2, -4]  # nur Darstellung
    yT = lambda t: 165 - (t + 4) * 4.4
    el = [f'<rect x="{x0}" y="{yw0}" width="{x1 - x0}" height="{yw1 - yw0}" fill="#d9dcde" stroke="{GRAU}" stroke-width="1.5"/>']
    for i in range(4):
        el.append(text((xs[i] + xs[i + 1]) / 2, yw1 + 30, f"Element {i + 1}"))
    for i, x in enumerate(xs):
        ym = (yw0 + yw1) / 2
        el += [f'<line x1="{x}" y1="{yw0}" x2="{x}" y2="{yw1}" stroke="{GRAU}" stroke-width="1.5"/>',
               f'<line x1="{x}" y1="{yT(T[i])}" x2="{x}" y2="{yw0}" stroke="{CYAN}" stroke-dasharray="3 4" opacity="0.6"/>',
               f'<circle cx="{x}" cy="{ym}" r="8" fill="{CYAN}" stroke="white" stroke-width="2"/>',
               f'<text x="{x + 11:.0f}" y="{ym - 12:.0f}" font-size="{FS}" font-weight="700" fill="{DUNKEL}">T'
               f'<tspan baseline-shift="sub" font-size="13">{i + 1}</tspan></text>']
    el.append(f'<polyline points="{" ".join(f"{x},{yT(t)}" for x, t in zip(xs, T))}" fill="none" stroke="{ROT}" stroke-width="2.5"/>')
    el += [f'<circle cx="{x}" cy="{yT(t)}" r="5" fill="{ROT}"/>' for x, t in zip(xs, T)]
    el += [text(x1 + 18, yT(T[-1]) + 6, "T(x)", "start", ROT), text(x0 - 18, (yw0 + yw1) / 2 + 6, "innen", "end", DUNKEL),
           text(x1 + 18, (yw0 + yw1) / 2 + 6, "außen", "start", DUNKEL),
           text(w / 2, h - 12, "Je Knoten eine Unbekannte: die Temperatur. Dazwischen wird interpoliert.")]
    svg_datei(datei, w, h, el)


if __name__ == "__main__":
    KS = ("KS", "175 mm", 175, "0,99")
    luft = (("Luft 20 °C", "h = 7,7 W/(m²·K)"), ("Luft −10 °C", "h = 25 W/(m²·K)"))
    wand("p1_aussenwand_a.svg", [KS, ("EPS", "140 mm", 140, "0,035")], "temp", "T = 20 °C", "T = −10 °C")
    wand("p1_aussenwand_b.svg", [KS, ("EPS", "140 mm", 140, "0,035")], "konv", *luft)
    wand("p1_uebung1.svg", [KS, ("EPS", "200 mm", 200, "0,035")], "konv", *luft)
    wand("p1_uebung2.svg", [("VZ", "365 mm", 365, "0,68")], "konv", *luft)
    wand("p1_uebung3.svg", [("VZ", "365 mm", 365, "0,68"), ("EPS", "d = ?", 121, "0,035")], "konv", *luft)
    netz_1d("p1_fem_1d.svg")
    print("Skizzen geschrieben nach", OUT)
