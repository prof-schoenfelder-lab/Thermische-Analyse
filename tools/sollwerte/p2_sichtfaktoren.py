#!/usr/bin/env python3
"""Sichtfaktoren der Vakuumröhre per Strahlverfolgung (Monte-Carlo): Glas innen und Absorber, Stück der Länge L.

Aufruf:  python3 tools/sollwerte/p2_sichtfaktoren.py [Strahlen je Fläche, Standard 200000]

Geometrie in mm wie im ANSYS-Modell: Glas innen R 32,5; Kupferrohr außen R 6; Blech 60 × 0,5 mittig,
Stirnflächen offen. Ausgabe je Länge: Anteile Glas → Absorber / Glas / Enden und Absorber → Glas / Absorber /
Enden, die Probe auf Reziprozität und um wie viel Perfect (jede Zeile einzeln auf 1 hochgerechnet) dem Glas
mehr Austausch zuschreibt als dem Absorber. Quelle der Zahlen auf der Seite Wärmestrahlung (P2 Grundlagen).
"""
import math
import random
import sys

RG, RT, B, H = 32.5, 6.0, 30.0, 0.25           # Glas innen, Rohr außen, halbe Blechbreite, halbe Blechdicke
XA = math.sqrt(RT * RT - H * H)                 # hier setzt das Blech am Rohr an
ALPHA = math.asin(H / RT)
EPS = 1e-9


def richtung(nx, ny):
    """Kosinusverteilte Richtung um die Normale (nx, ny, 0)."""
    u1, u2 = random.random(), random.random()
    r, phi = math.sqrt(u1), 2 * math.pi * u2
    a, b, c = r * math.cos(phi), r * math.sin(phi), math.sqrt(max(0.0, 1 - u1))
    return a * (-ny) + c * nx, a * nx + c * ny, b


def verfolge(px, py, pz, dx, dy, dz, L, quelle):
    """Erste getroffene Fläche: 'A' Absorber, 'G' Glas, 'E' offenes Ende."""
    beste = (L - pz) / dz if dz > 0 else (-pz / dz if dz < 0 else math.inf)
    treffer = "E"
    A = dx * dx + dy * dy
    if A > 1e-14:
        Bq = 2 * (px * dx + py * dy)
        disk = Bq * Bq - 4 * A * (px * px + py * py - RG * RG)
        if disk >= 0:
            tg = (-Bq + math.sqrt(disk)) / (2 * A)
            if EPS < tg < beste:
                beste, treffer = tg, "G"
        if quelle != "T":
            disk2 = Bq * Bq - 4 * A * (px * px + py * py - RT * RT)
            if disk2 > 0:
                tt = (-Bq - math.sqrt(disk2)) / (2 * A)
                if EPS < tt < beste:
                    beste, treffer = tt, "A"
    if dy < 0 and py > H - 1e-12 and quelle != "P+":
        tp = (H - py) / dy
        if EPS < tp < beste and XA <= abs(px + tp * dx) <= B:
            beste, treffer = tp, "A"
    if dy > 0 and py < -H + 1e-12 and quelle != "P-":
        tp = (-H - py) / dy
        if EPS < tp < beste and XA <= abs(px + tp * dx) <= B:
            beste, treffer = tp, "A"
    if dx != 0:
        for xe in (B, -B):
            te = (xe - px) / dx
            if EPS < te < beste and abs(py + te * dy) <= H:
                beste, treffer = te, "A"
    return treffer


def glas(L, n):
    z = {"A": 0, "G": 0, "E": 0}
    for _ in range(n):
        th = 2 * math.pi * random.random()
        c, s = math.cos(th), math.sin(th)
        z[verfolge(RG * c, RG * s, L * random.random(), *richtung(-c, -s), L, "G")] += 1
    return {k: v / n for k, v in z.items()}


def absorber(L, n):
    a_bl = 2 * (B - XA) * L                      # je Seite (oben bzw. unten), beide Flügel
    a_ro = RT * (2 * math.pi - 4 * ALPHA) * L     # Rohr außen ohne die Ansätze des Blechs
    a_ges = 2 * a_bl + a_ro
    z = {"A": 0, "G": 0, "E": 0}
    for _ in range(n):
        u, zz = random.random() * a_ges, L * random.random()
        if u < 2 * a_bl:
            x = random.choice((-1, 1)) * (XA + (B - XA) * random.random())
            y, ny, q = (H, 1.0, "P+") if u < a_bl else (-H, -1.0, "P-")
            z[verfolge(x, y, zz, *richtung(0.0, ny), L, q)] += 1
        else:
            w = ALPHA + (math.pi - 2 * ALPHA) * random.random() + (math.pi if random.random() < 0.5 else 0.0)
            c, s = math.cos(w), math.sin(w)
            z[verfolge(RT * c, RT * s, zz, *richtung(c, s), L, "T")] += 1
    return {k: v / n for k, v in z.items()}, a_ges


if __name__ == "__main__":
    random.seed(1)
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
    for L in (20.0, 200.0, 1e6):
        fg = glas(L, n)
        fa, aa = absorber(L, n)
        ag = 2 * math.pi * RG * L
        rez = (ag * fg["A"]) / (aa * fa["G"])
        perfect = (ag * fg["A"] / (1 - fg["E"])) / (aa * fa["G"] / (1 - fa["E"]))
        print(f"L = {L:g} mm:  Glas → Absorber {fg['A']:.3f}, Glas → Glas {fg['G']:.3f}, Glas → Enden {fg['E']:.3f}")
        print(f"            Absorber → Glas {fa['G']:.3f}, Absorber → Absorber {fa['A']:.3f}, Absorber → Enden {fa['E']:.3f}")
        print(f"            A_G F_GA / (A_A F_AG) = {rez:.3f} (soll 1)   mit Perfect: {perfect:.3f}")
