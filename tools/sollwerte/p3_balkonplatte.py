# /// script
# requires-python = ">=3.10"
# dependencies = ["gmsh", "scikit-fem", "numpy"]
# ///
"""Sollwerte P3, Übung Wärmebrücke Balkonplatte: 2D-Schnitt, Wärmestrom und ψ nach DIN EN ISO 10211, unabhängig
von ANSYS und von Wandschnitt 2D.

Aufruf:  uv run tools/sollwerte/p3_balkonplatte.py

Daten wie die Vorlage in Wandschnitt 2D (Felix 11.11.2026, Maße in mm):
- Außenwand wie in P1: EPS 035 (λ 0,035) x = 0 bis 140, Kalksandstein 1800 (λ 0,99) x = 140 bis 315
- Decke Stahlbeton (λ 2,3) 200 mm dick (y = 1000 bis 1200), kragt 1,50 m aus (x = −1500) und reicht 1 m in den Raum
- Schnitte 1 m über und unter der Decke (y = 0 und 2200) und 1 m im Raum (x = 1315), adiabat
- außen −5 °C mit R_se 0,04, innen 20 °C mit R_si 0,13 an allen Innenflächen (U-Wert, ψ);
  Mindestwärmeschutz nach DIN 4108-2 mit R_si 0,25 und f_Rsi ≥ 0,70
- mit Trennung: Dämmkörper 80 mm in der Dämmebene (x = 60 bis 140) mit λ_eq 0,15 W/(m·K); Schöck, Bauphysikalische
  Kennwerte Isokorb T (CH, Juli 2024), Typ KL, H 200 mm: 0,077 bis 0,261 je nach Tragstufe, 0,150 z. B. bei M5-V2

ψ_e = Φ/ΔT − U·l mit l = 2,2 m (Außenmaß), ψ_i mit l = 2,0 m (Innenmaß). Der Dämmkörper ist ein eigener Körper im
Netz: Wird er nur über die Elementmittelpunkte zugewiesen, konvergiert ψ sehr langsam.
"""
import gmsh
import numpy as np
from skfem import Basis, BilinearForm, ElementTriP2, FacetBasis, LinearForm, MeshTri, asm, solve
from skfem.helpers import dot, grad

MM = 1e-3
LAM_EPS, LAM_KS, LAM_STB, LAM_EQ = 0.035, 0.99, 2.3, 0.15
T_INNEN, T_AUSSEN = 20.0, -5.0
R_SI, R_SI_SCHIMMEL, R_SE = 0.13, 0.25, 0.04
U_WAND = 1 / (R_SI + 0.175 / LAM_KS + 0.14 / LAM_EPS + R_SE)


def netz(h):
    """Rechtecke der Vorlage als eigene Körper, der Dämmkörper immer dabei (Material je nach Fall)."""
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("balkon")
    occ = gmsh.model.occ
    flaechen = [
        occ.addRectangle(0, 0, 0, 140 * MM, 1000 * MM),            # EPS unten
        occ.addRectangle(0, 1200 * MM, 0, 140 * MM, 1000 * MM),    # EPS oben
        occ.addRectangle(140 * MM, 0, 0, 175 * MM, 1000 * MM),     # Kalksandstein unten
        occ.addRectangle(140 * MM, 1200 * MM, 0, 175 * MM, 1000 * MM),  # Kalksandstein oben
        occ.addRectangle(-1500 * MM, 1000 * MM, 0, 2815 * MM, 200 * MM),  # Decke
        occ.addRectangle(60 * MM, 1000 * MM, 0, 80 * MM, 200 * MM),       # Dämmkörper
    ]
    occ.synchronize()
    occ.fragment([(2, f) for f in flaechen], [])
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


def rechnen(trennung, lam_eq=LAM_EQ, r_si=R_SI, h=0.0125):
    """Wärmestrom in W/m (Dicke 1 m), kleinste Innenoberflächentemperatur in °C und Zahl der Elemente."""
    m = netz(h)
    xm, ym = m.p[:, m.t].mean(axis=1) / MM
    in_decke = (ym > 1000) & (ym < 1200)
    lam = np.where(in_decke, LAM_STB, np.where(xm < 140, LAM_EPS, LAM_KS))
    if trennung:
        lam = np.where(in_decke & (xm > 60) & (xm < 140), lam_eq, lam)
    e = ElementTriP2()
    basis = Basis(m, e)
    K = asm(BilinearForm(lambda u, v, w: w["lam"] * dot(grad(u), grad(v))), basis,
            lam=np.repeat(lam[:, None], basis.X.shape[1], axis=1))
    eps = 1e-6 / MM

    def aussen(x):
        X, Y = x[0] / MM, x[1] / MM
        wand = (np.abs(X) < eps) & ((Y < 1000 + eps) | (Y > 1200 - eps))
        platte = (X < eps) & ((np.abs(Y - 1000) < eps) | (np.abs(Y - 1200) < eps) | (np.abs(X + 1500) < eps))
        return wand | platte

    def innen(x):
        X, Y = x[0] / MM, x[1] / MM
        wand = (np.abs(X - 315) < eps) & ((Y < 1000 + eps) | (Y > 1200 - eps))
        platte = (X > 315 - eps) & ((np.abs(Y - 1000) < eps) | (np.abs(Y - 1200) < eps))
        return wand | platte

    fa = FacetBasis(m, e, facets=m.facets_satisfying(aussen, boundaries_only=True))
    rand_innen = m.facets_satisfying(innen, boundaries_only=True)
    fi = FacetBasis(m, e, facets=rand_innen)
    h_i, h_e = 1 / r_si, 1 / R_SE
    K = K + asm(BilinearForm(lambda u, v, w: h_e * u * v), fa) + asm(BilinearForm(lambda u, v, w: h_i * u * v), fi)
    f = asm(LinearForm(lambda v, w: h_e * T_AUSSEN * v), fa) + asm(LinearForm(lambda v, w: h_i * T_INNEN * v), fi)
    u = solve(K, f)
    phi = asm(LinearForm(lambda v, w: h_i * (T_INNEN - w["u"]) * v), fi, u=fi.interpolate(u)).sum()
    return phi, u[basis.get_dofs(rand_innen).all()].min(), m.t.shape[1]


if __name__ == "__main__":
    dt = T_INNEN - T_AUSSEN
    print(f"U der Wand = {U_WAND:.4f} W/(m²·K); ψ_e = Φ/ΔT − U·2,2 m, ψ_i = Φ/ΔT − U·2,0 m, ΔT = {dt:.0f} K")
    for name, trennung in (("ohne Trennung", False), ("mit Trennung (λ_eq 0,15)", True)):
        phi, theta, n = rechnen(trennung)
        print(f"\n{name}: Φ = {phi:.2f} W/m, ψ_e = {phi / dt - U_WAND * 2.2:.3f}, ψ_i = {phi / dt - U_WAND * 2.0:.3f}"
              f" W/(m·K), tiefste Innenoberfläche {theta:.2f} °C ({n} Elemente)")
        for h in (0.025, 0.00625):
            phi_h, _, n_h = rechnen(trennung, h=h)
            print(f"  Netz {1000 * h:5.2f} mm: Φ = {phi_h:.2f} W/m, ψ_e = {phi_h / dt - U_WAND * 2.2:.3f} ({n_h} Elemente)")
        _, theta_s, _ = rechnen(trennung, r_si=R_SI_SCHIMMEL)
        f_rsi = (theta_s - T_AUSSEN) / dt
        print(f"  Mindestwärmeschutz (R_si 0,25): {theta_s:.2f} °C, f_Rsi = {f_rsi:.3f}"
              f" ({'erfüllt' if f_rsi >= 0.70 else 'nicht erfüllt'}, Grenze 0,70)")
    print("\nψ_e je nach Tragstufe des Kragplattenanschlusses (Schöck Typ KL, H 200 mm):")
    for lam_eq in (0.077, 0.10, 0.15, 0.20, 0.261):
        phi, _, _ = rechnen(True, lam_eq=lam_eq)
        print(f"  λ_eq {lam_eq:.3f}: Φ = {phi:.2f} W/m, ψ_e = {phi / dt - U_WAND * 2.2:.3f} W/(m·K)")
