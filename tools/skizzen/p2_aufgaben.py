#!/usr/bin/env python3
"""Aufgabenskizzen P2 (Vakuumröhre, Heizungsrohr, Kühlkörper, Erdkabel) als SVG in docs/P2_Randbedingungen/images/.

Aufruf:  python3 tools/skizzen/p2_aufgaben.py

Stil wie tools/skizzen/p1_wand.py: Anzeige in Originalgröße, Schrift 18 px, HTWK-Farben.
Maße stehen in der Beschriftung; die Zeichnungen sind nicht überall maßstäblich.
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "docs/P2_Randbedingungen/images"
CYAN, DUNKEL, GRAU, ROT = "#009EE3", "#022541", "#2E3639", "#E53009"
FS = 18
SCHRIFT = "'Source Sans Pro', 'Source Sans 3', Arial, sans-serif"
GLAS, WASSER, STAHL, ALU, CU, BODEN, DAEMM = "#e6f5fc", "#cfe8f7", "#d9dcde", "#e3e6e8", "#e8b48f", "#eadfcc", "#fbf3dc"


def text(x, y, inhalt, anker="start", farbe=GRAU, fett=False, halo=False):
    stil = ' font-weight="700"' if fett else ""
    if halo:
        stil += ' stroke="white" stroke-width="5" stroke-linejoin="round" paint-order="stroke"'
    return f'<text x="{x:.0f}" y="{y:.0f}" text-anchor="{anker}" font-size="{FS}" fill="{farbe}"{stil}>{inhalt}</text>'


def sub(zeichen, index, rest=""):
    return f'{zeichen}<tspan baseline-shift="sub" font-size="13">{index}</tspan><tspan dx="3">{rest}</tspan>'


def defs():
    m = ""
    for name, farbe in (("pr", ROT), ("pc", CYAN), ("pg", GRAU)):
        m += (f'<marker id="{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
              f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{farbe}"/></marker>')
    return f"<defs>{m}</defs>"


def pfeil(x1, y1, x2, y2, farbe=ROT, breite=1.8):
    mk = {ROT: "pr", CYAN: "pc"}.get(farbe, "pg")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{farbe}" stroke-width="{breite}" '
            f'marker-end="url(#{mk})"/>')


def welle(x1, y1, x2, y2, amp=4.0, perioden=3.25, farbe=ROT):
    """Wellenpfeil (Wärmestrahlung) von (x1, y1) nach (x2, y2)."""
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    pkt = []
    for i in range(121):
        f = i / 120
        s = amp * math.sin(2 * math.pi * perioden * f)
        pkt.append(f"{x1 + ux * L * f - uy * s:.1f},{y1 + uy * L * f + ux * s:.1f}")
    return (f'<path d="M{" L".join(pkt)}" fill="none" stroke="{farbe}" stroke-width="1.6" opacity="0.8" '
            f'stroke-linejoin="round" marker-end="url(#pr)"/>')


def fuehrung(x1, y1, x2, y2):
    """Hinweislinie mit Punkt am Bauteil."""
    return (f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="3" fill="{GRAU}"/>'
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{GRAU}" stroke-width="1"/>')


def mass(x1, y1, x2, y2, beschr, versatz=(0, -10), anker="middle"):
    mx, my = (x1 + x2) / 2 + versatz[0], (y1 + y2) / 2 + versatz[1]
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{GRAU}" stroke-width="1" '
            f'marker-start="url(#pg)" marker-end="url(#pg)"/>' + text(mx, my, beschr, anker=anker, halo=True))


def ring(cx, cy, ra, ri, fuell, rand=GRAU):
    return (f'<path d="M{cx - ra},{cy} a{ra},{ra} 0 1,0 {2 * ra},0 a{ra},{ra} 0 1,0 {-2 * ra},0 Z '
            f'M{cx - ri},{cy} a{ri},{ri} 0 1,1 {2 * ri},0 a{ri},{ri} 0 1,1 {-2 * ri},0 Z" fill="{fuell}" '
            f'fill-rule="evenodd" stroke="{rand}" stroke-width="1.5"/>')


def speichern(datei, w, h, el):
    kopf = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="{SCHRIFT}">'
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / datei).write_text("\n".join([kopf, f'<rect width="{w}" height="{h}" fill="white"/>', defs(), *el, "</svg>"]) + "\n",
                             encoding="utf-8")


def roehre(datei):
    W, H, cx, cy, s = 960, 560, 300, 300, 6.0          # 6 px je mm
    rg_a, rg_i, rr_a, rr_i, b, t = 35 * s, 32.5 * s, 6 * s, 5 * s, 30 * s, 0.5 * s
    el = [ring(cx, cy, rg_a, rg_i, GLAS),
          f'<circle cx="{cx}" cy="{cy}" r="{rr_i}" fill="{WASSER}"/>',
          f'<rect x="{cx - b}" y="{cy - t / 2 - 0.5}" width="{2 * b}" height="{t + 1}" fill="{DUNKEL}"/>',
          ring(cx, cy, rr_a, rr_i, DUNKEL, rand=DUNKEL)]
    for x in (cx - 150, cx - 90, cx + 90, cx + 150):                     # Sonne auf die Blechflügel
        el.append(pfeil(x, 36, x, cy - t / 2 - 4, ROT, 2))
    el.append(text(cx - 150, 26, "Sonne: 700 W/m² auf die Oberseite der Bleche", anker="start", farbe=ROT))
    el += [welle(cx - rg_a - 6, cy + 60, cx - rg_a - 70, cy + 60),
           pfeil(cx + rg_a + 6, cy + 60, cx + rg_a + 56, cy + 60, CYAN)]
    el.append(text(cx, cy + 92, "Vakuum", anker="middle"))
    xl = 600
    el += [fuehrung(cx + rg_a * math.cos(-0.5), cy + rg_a * math.sin(-0.5), xl - 8, 140),
           text(xl, 136, "Glasrohr Ø 70 × 2,5 mm", fett=True, farbe=DUNKEL), text(xl, 160, "λ = 1,1 W/(m·K), ε = 0,9"),
           fuehrung(cx + b - 4, cy, xl - 8, 240),
           text(xl, 236, "Absorberblech 60 × 0,5 mm", fett=True, farbe=DUNKEL),
           text(xl, 260, "Kupfer, a) ε = 0,05  b) ε = 0,9"),
           fuehrung(cx + rr_a * 0.7, cy + rr_a * 0.7, xl - 8, 340),
           text(xl, 336, "Kupferrohr Ø 12 × 1 mm", fett=True, farbe=DUNKEL),
           text(xl, 360, "Wasser 50 °C, α = 1000 W/(m²·K)"),
           text(xl, 440, "außen: Luft 20 °C, α = 10 W/(m²·K)", farbe=CYAN),
           text(xl, 464, "Himmel 5 °C (Strahlung)", farbe=ROT),
           text(cx, H - 22, "Querschnitt, Länge des Stücks 20 mm", anker="middle")]
    speichern(datei, W, H, el)


def heizungsrohr(datei):
    W, H, cx, cy, s = 960, 460, 260, 230, 4.0
    ra, ri, rd = 13.45 * s, 10.85 * s, 33.45 * s
    el = [f'<circle cx="{cx}" cy="{cy}" r="{rd}" fill="none" stroke="{GRAU}" stroke-width="1.2" stroke-dasharray="7 5"/>',
          ring(cx, cy, ra, ri, STAHL), f'<circle cx="{cx}" cy="{cy}" r="{ri}" fill="{WASSER}"/>']
    for w in (200, 250, 300, 340):
        a = math.radians(w)
        el.append(welle(cx + (ra + 8) * math.cos(a), cy + (ra + 8) * math.sin(a),
                        cx + (rd + 40) * math.cos(a), cy + (rd + 40) * math.sin(a)))
    el += [pfeil(cx - 25, cy - ra - 6, cx - 25, cy - rd - 50, CYAN), pfeil(cx + 25, cy - ra - 6, cx + 25, cy - rd - 50, CYAN)]
    xl = 520
    el += [fuehrung(cx + ra * 0.7, cy - ra * 0.7, xl - 8, 120),
           text(xl, 116, "Stahlrohr DN 20: Ø 26,9 × 2,6 mm", fett=True, farbe=DUNKEL), text(xl, 140, "λ = 50 W/(m·K), lackiert ε = 0,9"),
           fuehrung(cx, cy, xl - 8, 200), text(xl, 204, "Wasser 60 °C, α = 1000 W/(m²·K)"),
           fuehrung(cx + rd * 0.7, cy + rd * 0.7, xl - 8, 300),
           text(xl, 296, "c) optional: Dämmung 20 mm", fett=True, farbe=DUNKEL), text(xl, 320, "λ = 0,035 W/(m·K), ε = 0,9"),
           text(xl, 390, "Kellerluft 15 °C, α = 7 W/(m²·K)", farbe=CYAN),
           text(xl, 414, "Kellerwände 15 °C (Strahlung)", farbe=ROT)]
    speichern(datei, W, H, el)


def kuehlkoerper(datei):
    W, H, s = 960, 470, 3.6
    x0, yb = 80, 330                                  # links, Unterkante der Grundplatte
    b, t, hr, tr, n = 100 * s, 8 * s, 40 * s, 2 * s, 8
    teil = (b - tr) / (n - 1)
    el = [f'<rect x="{x0}" y="{yb - t}" width="{b}" height="{t}" fill="{ALU}" stroke="{GRAU}" stroke-width="1.5"/>']
    for i in range(n):
        el.append(f'<rect x="{x0 + i * teil:.1f}" y="{yb - t - hr}" width="{tr}" height="{hr}" fill="{ALU}" '
                  f'stroke="{GRAU}" stroke-width="1.5"/>')
    m0, mb = x0 + (b - 50 * s) / 2, 50 * s
    el += [f'<rect x="{m0}" y="{yb + 2}" width="{mb}" height="22" fill="#fbe0d9" stroke="{ROT}" stroke-width="1.5"/>',
           text(x0 + b / 2, yb + 19, "Modul 50 × 50 mm", anker="middle", farbe=ROT),
           pfeil(x0 + b / 2 - 60, yb + 70, x0 + b / 2 - 60, yb + 28, ROT, 2),
           pfeil(x0 + b / 2 + 60, yb + 70, x0 + b / 2 + 60, yb + 28, ROT, 2),
           text(x0 + b / 2, yb + 96, "Wärmestrom 40 W", anker="middle", farbe=ROT, fett=True),
           mass(x0, yb - t - hr - 26, x0 + b, yb - t - hr - 26, "100 mm"),
           mass(x0 - 22, yb - t - hr, x0 - 22, yb - t, "40", versatz=(-8, 6), anker="end"),
           mass(x0 - 22, yb - t, x0 - 22, yb, "8", versatz=(-8, 6), anker="end"),
           pfeil(x0 + teil * 3.5 + tr / 2, yb - t - 40, x0 + teil * 3.5 + tr / 2, yb - t - hr - 6, CYAN),
           welle(x0 + b + 8, yb - t - hr / 2, x0 + b + 64, yb - t - hr / 2)]
    xl = 560
    el += [text(xl, 70, "Aluminium, λ = 200 W/(m·K)", fett=True, farbe=DUNKEL),
           text(xl, 96, "8 Rippen, je 2 mm dick, 40 mm hoch"),
           text(xl, 120, "Länge der Rippen 100 mm"),
           text(xl, 176, "Luft 40 °C, α = 6 W/(m²·K)", farbe=CYAN),
           text(xl, 202, "Umgebung 40 °C (Strahlung)", farbe=ROT),
           text(xl, 228, "a) schwarz eloxiert ε = 0,85"), text(xl, 252, "b) blank ε = 0,05"),
           text(xl, 310, "Rückseite neben dem Modul:"), text(xl, 334, "liegt am Gehäuse, isoliert")]
    speichern(datei, W, H, el)


def erdkabel(datei):
    W, H, s = 960, 500, 100.0                          # 100 px je m
    x0, y0, bw, bt = 70, 80, 4 * s, 3 * s
    cx, cy = x0 + bw / 2, y0 + 1 * s
    el = [f'<rect x="{x0}" y="{y0}" width="{bw}" height="{bt}" fill="{BODEN}" stroke="{GRAU}" stroke-width="1.5"/>',
          f'<line x1="{x0}" y1="{y0 + bt}" x2="{x0 + bw}" y2="{y0 + bt}" stroke="{DUNKEL}" stroke-width="5"/>',
          f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + bt}" stroke="{GRAU}" stroke-width="5"/>',
          f'<line x1="{x0 + bw}" y1="{y0}" x2="{x0 + bw}" y2="{y0 + bt}" stroke="{GRAU}" stroke-width="5"/>',
          f'<circle cx="{cx}" cy="{cy}" r="12" fill="#f3f3f3" stroke="{GRAU}" stroke-width="1.2"/>',
          f'<circle cx="{cx}" cy="{cy}" r="6" fill="{CU}" stroke="{GRAU}" stroke-width="1"/>',
          pfeil(x0 + 120, y0 - 4, x0 + 120, y0 - 40, CYAN), pfeil(x0 + 280, y0 - 4, x0 + 280, y0 - 40, CYAN),
          text(x0 + bw / 2, y0 - 50, "Luft 20 °C, α = 10 W/(m²·K)", anker="middle", farbe=CYAN),
          text(x0 + bw / 2, y0 + bt + 30, "in 3 m Tiefe: T = 10 °C", anker="middle", farbe=DUNKEL),
          mass(x0, y0 + bt + 66, x0 + bw, y0 + bt + 66, "4 m", versatz=(0, 22)),
          mass(cx + 40, y0, cx + 40, cy, "1 m", versatz=(10, 6), anker="start"),
          text(x0 + 14, y0 + bt / 2 + 60, "Boden λ: a) 1,0  b) 0,4 W/(m·K)", halo=True),
          text(x0 - 10, y0 + bt / 2, "isoliert", anker="end"),
          text(x0 + bw + 10, y0 + bt / 2 + 60, "isoliert")]
    # Detail des Kabels
    dx, dy, R1, R2 = 720, 220, 40.0 * 2.2, 17.5 * 2.2
    el += [f'<line x1="{cx + 14}" y1="{cy}" x2="{dx - R1 / 2 - 12}" y2="{dy}" stroke="{GRAU}" stroke-width="1" stroke-dasharray="4 4"/>',
           f'<circle cx="{dx}" cy="{dy}" r="{R1 / 2}" fill="#f3f3f3" stroke="{GRAU}" stroke-width="1.5"/>',
           f'<circle cx="{dx}" cy="{dy}" r="{R2 / 2}" fill="{CU}" stroke="{GRAU}" stroke-width="1.2"/>',
           text(dx, dy - R1 / 2 - 50, "Kabel 1 × 240 mm² Aluminium", anker="middle", fett=True, farbe=DUNKEL),
           text(dx, dy - R1 / 2 - 26, "Strom I = 550 A", anker="middle", farbe=ROT),
           text(dx, dy + R1 / 2 + 30, "Leiter Ø 17,5 mm, λ = 230 W/(m·K)", anker="middle"),
           text(dx, dy + R1 / 2 + 54, "Isolierung Ø 40 mm, λ = 0,3 W/(m·K)", anker="middle")]
    speichern(datei, W, H, el)


if __name__ == "__main__":
    roehre("p2_roehre.svg")
    heizungsrohr("p2_heizungsrohr.svg")
    kuehlkoerper("p2_kuehlkoerper.svg")
    erdkabel("p2_erdkabel.svg")
    print("Skizzen geschrieben nach", OUT)
