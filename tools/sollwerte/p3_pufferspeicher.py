# /// script
# requires-python = ">=3.10"
# dependencies = ["gmsh", "scikit-fem", "numpy"]
# ///
"""Sollwerte P3, Pufferspeicher rotationssymmetrisch: Wärmeverlust über die Dämmung, unabhängig von ANSYS.

Aufruf:  uv run tools/sollwerte/p3_pufferspeicher.py

Vorbild Wolf BSH-800 (Montageanleitung 3062690_201702, Technische Daten; Wolf Datenheft Speichersysteme):
- Behälter Ø 790 mm ohne, 1030 mm mit Wärmedämmung: Mantel 120 mm
- Höhe 1840 mm ohne Wärmedämmung (bis Entlüftung), 1940 mm mit: Deckel rund 100 mm
- Boden: in der Zeichnung liegt Dämmung unter dem gewölbten Boden, Dicke nicht angegeben, angenommen 100 mm
- 800 l, im Modell als Zylinder mit ebenen Böden und gleichem Volumen (Ø 790 × 1632 mm)
- Bereitschaftswärmeaufwand 2,32 kWh/24 h, also 96,7 W; eine Energieklasse gibt Wolf nur bis 500 l an,
  weil die Kennzeichnung nach (EU) 812/2013 nur für Speicher bis 500 l gilt
Dämmung Polyestervlies λ = 0,038 W/(m·K) (NEVEON tank.TI.PES/PV; die Ausführung PS hat 0,043).
Prüfbedingung des Bereitschaftsverlusts: Wasser 65 °C, Raum 20 °C (45 K). Außen α = 8 W/(m²·K) für Konvektion
und Strahlung zusammen (Annahme). Behälterwand aus Stahl weggelassen, 65 °C direkt an der Innenseite der Dämmung.
Grenzen für V in l: Ökodesign (EU) 814/2013 seit 26.09.2017 für Speicher bis 2000 l S < 16,66 + 8,33·V^0,4 W
(gleich der Obergrenze von Klasse C), Klasse B nach 812/2013 S < 12 + 5,93·V^0,4 W (nur zur Orientierung).

FEM: Halbschnitt in der r-z-Ebene, quadratische Dreiecke (P2), Steifigkeit mit 2πr gewichtet. Der Wärmestrom
als Reaktion an der Behälterwand und als Integral α(T − T_Raum)·2πr über Mantel, Deckel und Boden gilt für
den ganzen Speicher (360°).
"""
import math

import gmsh
import numpy as np
from skfem import Basis, BilinearForm, ElementTriP2, FacetBasis, Functional, LinearForm, MeshTri, asm, condense, solve
from skfem.helpers import dot, grad

RI = 0.395                      # Behälterradius in m
VOLUMEN_L = 800
D_MANTEL, D_DECKEL, D_BODEN = 0.12, 0.10, 0.10
LAM_VLIES, ALPHA = 0.038, 8.0
T_WASSER, T_RAUM = 65.0, 20.0
S_HERSTELLER = 2.32 * 1000 / 24  # W


def grenzen(volumen_l=VOLUMEN_L):
    """Obergrenzen für den Bereitschaftsverlust in W: Klasse B und Ökodesign (Klasse C)."""
    return 12 + 5.93 * volumen_l**0.4, 16.66 + 8.33 * volumen_l**0.4


def netz(hi, ra, z0, z1, h):
    """Dämmung als Rechteck um das ausgeschnittene Wasser, Drehachse bei r = 0."""
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("m")
    occ = gmsh.model.occ
    aussen = occ.addRectangle(0, z0, 0, ra, z1 - z0)
    wasser = occ.addRectangle(0, 0, 0, RI, hi)
    occ.cut([(2, aussen)], [(2, wasser)])
    occ.synchronize()
    gmsh.option.setNumber("Mesh.MeshSizeMax", h)
    gmsh.model.mesh.generate(2)
    tags, xyz, _ = gmsh.model.mesh.getNodes()
    p = xyz.reshape(-1, 3)[:, :2]
    idx = {t: i for i, t in enumerate(tags)}
    typen, _, knoten = gmsh.model.mesh.getElements(2)
    t = np.array([idx[k] for k in knoten[list(typen).index(2)]]).reshape(-1, 3)
    gmsh.finalize()
    return MeshTri(p.T, t.T)


def fem(d_mantel=D_MANTEL, d_deckel=D_DECKEL, d_boden=D_BODEN, lam=LAM_VLIES, alpha=ALPHA,
        volumen_l=VOLUMEN_L, h=0.01):
    """Wärmeverlust in W gesamt und je Außenfläche, dazu Höhe des Wasserzylinders und Zahl der Elemente."""
    hi = volumen_l / 1000 / (math.pi * RI**2)
    ra, z0, z1 = RI + d_mantel, -d_boden, hi + d_deckel
    m = netz(hi, ra, z0, z1, h)
    e = ElementTriP2()
    basis = Basis(m, e)
    tol = 1e-7
    flaechen = {
        "Mantel": lambda x: np.abs(x[0] - ra) < tol,
        "Deckel": lambda x: np.abs(x[1] - z1) < tol,
        "Boden": lambda x: np.abs(x[1] - z0) < tol,
    }
    aussen = m.facets_satisfying(lambda x: flaechen["Mantel"](x) | flaechen["Deckel"](x) | flaechen["Boden"](x),
                                 boundaries_only=True)
    innen = m.facets_satisfying(
        lambda x: ((np.abs(x[0] - RI) < tol) & (x[1] > -tol) & (x[1] < hi + tol))
        | (((np.abs(x[1]) < tol) | (np.abs(x[1] - hi) < tol)) & (x[0] < RI + tol)),
        boundaries_only=True)
    fb = FacetBasis(m, e, facets=aussen)
    K = asm(BilinearForm(lambda u, v, w: lam * dot(grad(u), grad(v)) * 2 * np.pi * w.x[0]), basis)
    K = K + asm(BilinearForm(lambda u, v, w: alpha * u * v * 2 * np.pi * w.x[0]), fb)
    f = asm(LinearForm(lambda v, w: alpha * T_RAUM * v * 2 * np.pi * w.x[0]), fb)
    D = basis.get_dofs(innen).all()
    x = np.zeros(basis.N)
    x[D] = T_WASSER
    u = solve(*condense(K, f, x=x, D=D))
    q = (K @ u - f)[D].sum()
    verlust = Functional(lambda w: alpha * (w["u"] - T_RAUM) * 2 * np.pi * w.x[0])
    je_flaeche = {}
    for name, auf in flaechen.items():
        fbn = FacetBasis(m, e, facets=m.facets_satisfying(auf, boundaries_only=True))
        je_flaeche[name] = asm(verlust, fbn, u=fbn.interpolate(u))
    return q, je_flaeche, hi, m.t.shape[1]


def ueberall(d):
    """Wärmeverlust in W bei überall gleicher Dämmdicke d in m."""
    return fem(d_mantel=d, d_deckel=d, d_boden=d)[0]


def grenzdicke(ziel, a=0.04, b=0.16, schritte=12):
    """Überall gleiche Dämmdicke in mm, bei der der Verlust die Grenze ziel in W erreicht (Bisektion)."""
    for _ in range(schritte):
        mitte = (a + b) / 2
        a, b = (mitte, b) if ueberall(mitte) > ziel else (a, mitte)
    return 1000 * (a + b) / 2


if __name__ == "__main__":
    s_b, s_c = grenzen()
    print(f"V = {VOLUMEN_L} l: Klasse B bis {s_b:.1f} W, Ökodesign (Klasse C) bis {s_c:.1f} W")
    print(f"Hersteller Wolf BSH-800: 2,32 kWh/24 h = {S_HERSTELLER:.1f} W")
    q, je, hi, n = fem()
    teile = ", ".join(f"{k} {v:.1f} W" for k, v in je.items())
    print(f"\nModell (Mantel 120, Deckel 100, Boden 100 mm; Wasser Ø 790 × {1000 * hi:.0f} mm): q = {q:.1f} W"
          f" ({q / S_HERSTELLER - 1:+.0%} gegen Hersteller), {n} Elemente")
    print(f"  je Fläche: {teile}; Summe {sum(je.values()):.1f} W")
    print(f"  Netz halb so groß: q = {fem(h=0.005)[0]:.1f} W")
    print("\nVarianten:")
    for name, kw in [("λ 0,043 (Vlies PS)", dict(lam=0.043)), ("Boden 50 mm", dict(d_boden=0.05)),
                     ("Deckel 50 mm", dict(d_deckel=0.05)), ("α 5", dict(alpha=5.0))]:
        qv, jev, _, _ = fem(**kw)
        print(f"  {name:<20} q = {qv:6.1f} W  (" + ", ".join(f"{k} {v:.1f}" for k, v in jev.items()) + ")")
    print("\nDämmung überall gleich dick:")
    for d in (40, 50, 60, 70, 80, 90, 100, 110, 120, 140, 160):
        print(f"  {d:>3} mm: q = {ueberall(d / 1000):6.1f} W")
    print(f"Grenzdicke Klasse B ({s_b:.1f} W): {grenzdicke(s_b):.0f} mm")
    print(f"Grenzdicke Ökodesign ({s_c:.1f} W): {grenzdicke(s_c):.0f} mm")
    q60 = ueberall(0.06)
    print(f"\nOPAL-Frage 60 mm überall: q = {q60:.1f} W, zulässig: {'ja' if q60 < s_c else 'nein'}")
