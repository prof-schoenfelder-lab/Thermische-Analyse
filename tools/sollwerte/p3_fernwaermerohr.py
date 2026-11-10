# /// script
# requires-python = ">=3.10"
# dependencies = ["gmsh", "scikit-fem", "numpy"]
# ///
"""Sollwerte P3, Vorzeigebeispiel Fernwärmerohr im Erdreich: Handrechnung und 2D-FEM unabhängig von ANSYS.

Aufruf:  uv run tools/sollwerte/p3_fernwaermerohr.py

Kunststoffmantelrohr (KMR) DN 100, Dämmserie 1, als Einzelrohr (Vorlauf) im Erdreich:
- Maße und λ der PUR-Dämmung: Logstor-Produktkatalog 06/2025, Einzelrohr Serie 1
  (Stahl 114,3 × 3,6 mm, PE-Mantel 200 × 3,2 mm; PUR λ50 = 0,027 W/(m·K), klassisch gefertigt)
- λ Stahl 50 und PE 0,4 W/(m·K) nach EN 253 (zitiert in HCU Hamburg 2022, Tab. 2)
- Verlegung nach den isoplus-Bezugsbedingungen: Überdeckung 0,8 m, Erdreich λ = 1,0 W/(m·K), 10 °C
- Vorlauf 80 °C an der Stahlinnenwand (Übergang Wasser/Stahl vernachlässigt), Oberfläche 10 °C,
  Bodenblock mit adiabaten Seiten und adiabatem Boden

Handrechnung: Schichten als Hohlzylinder in Reihe, Boden als Zylinder unter isothermer Oberfläche
im unendlich ausgedehnten Erdreich, R_Boden = arcosh(2H/D) / (2 π λ_E), H Tiefe der Rohrachse.
FEM: quadratische Dreiecke (P2), Wärmestrom als Reaktion an der Stahlinnenwand, in W je Meter Rohr.
"""
import math

import gmsh
import numpy as np
from skfem import Basis, BilinearForm, ElementTriP2, MeshTri, asm, condense, solve
from skfem.helpers import dot, grad

# Radien in m: Stahl innen, Stahl außen, PUR außen (= PE innen), PE außen
R1, R2, R3, R4 = 114.3e-3 / 2 - 3.6e-3, 114.3e-3 / 2, 200e-3 / 2 - 3.2e-3, 200e-3 / 2
LAM_STAHL, LAM_PUR, LAM_PE, LAM_ERDE = 50.0, 0.027, 0.4, 1.0
UEBERDECKUNG = 0.8
H = UEBERDECKUNG + R4  # Tiefe der Rohrachse
T_VORLAUF, T_OBERFLAECHE = 80.0, 10.0


def r_zylinder(ra, rb, lam):
    return math.log(rb / ra) / (2 * math.pi * lam)


def handrechnung(lam_erde=LAM_ERDE, ueberdeckung=UEBERDECKUNG):
    """Widerstände in m·K/W und Wärmeverlust in W/m."""
    h = ueberdeckung + R4
    r = {
        "Stahl": r_zylinder(R1, R2, LAM_STAHL),
        "PUR": r_zylinder(R2, R3, LAM_PUR),
        "PE": r_zylinder(R3, R4, LAM_PE),
        "Boden": math.acosh(2 * h / (2 * R4)) / (2 * math.pi * lam_erde),
    }
    return r, (T_VORLAUF - T_OBERFLAECHE) / sum(r.values())


def netz(breite, tiefe, halb, h0, k, hmax):
    """Bodenblock (Oberfläche bei y = 0) mit Rohrringen, ohne Wasser; halb: nur x >= 0."""
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("m")
    occ = gmsh.model.occ
    block = occ.addRectangle(0.0 if halb else -breite / 2, -tiefe, 0, breite / 2 if halb else breite, tiefe)
    ringe = [occ.addDisk(0, -H, 0, r, r) for r in (R2, R3, R4)]
    occ.synchronize()
    teile, _ = occ.fragment([(2, block)], [(2, t) for t in ringe])
    wasser = occ.addDisk(0, -H, 0, R1, R1)
    occ.synchronize()
    teile, _ = occ.cut(teile, [(2, wasser)], removeTool=True)
    if halb:
        links = occ.addRectangle(-1, -tiefe - 1, 0, 1, tiefe + 2)
        occ.synchronize()
        teile, _ = occ.cut(teile, [(2, links)], removeTool=True)
    occ.synchronize()
    feld = gmsh.model.mesh.field.add("MathEval")
    gmsh.model.mesh.field.setString(feld, "F", f"Min({hmax}, {h0} + {k}*Sqrt(x*x+(y+{H})*(y+{H})))")
    gmsh.model.mesh.field.setAsBackgroundMesh(feld)
    for option in ("Mesh.MeshSizeExtendFromBoundary", "Mesh.MeshSizeFromPoints", "Mesh.MeshSizeFromCurvature"):
        gmsh.option.setNumber(option, 0)
    gmsh.model.mesh.generate(2)
    tags, xyz, _ = gmsh.model.mesh.getNodes()
    p = xyz.reshape(-1, 3)[:, :2]
    idx = {t: i for i, t in enumerate(tags)}
    typen, _, knoten = gmsh.model.mesh.getElements(2)
    t = np.array([idx[kk] for kk in knoten[list(typen).index(2)]]).reshape(-1, 3)
    gmsh.finalize()
    return MeshTri(p.T, t.T)


def fem(breite, tiefe, halb=False, h0=0.002, k=0.05, hmax=0.15):
    """Wärmestrom aus dem Rohr in W/m und Zahl der Elemente."""
    m = netz(breite, tiefe, halb, h0, k, hmax)
    basis = Basis(m, ElementTriP2())
    xm = m.p[:, m.t].mean(axis=1)
    r = np.hypot(xm[0], xm[1] + H)
    lam = np.where(r < R2, LAM_STAHL, np.where(r < R3, LAM_PUR, np.where(r < R4, LAM_PE, LAM_ERDE)))
    K = asm(BilinearForm(lambda u, v, w: w["lam"] * dot(grad(u), grad(v))), basis,
            lam=np.repeat(lam[:, None], basis.X.shape[1], axis=1))
    oben = m.facets_satisfying(lambda x: np.abs(x[1]) < 1e-9, boundaries_only=True)
    innen = m.facets_satisfying(lambda x: np.abs(np.hypot(x[0], x[1] + H) - R1) < 1e-4, boundaries_only=True)
    d_oben, d_innen = basis.get_dofs(oben).all(), basis.get_dofs(innen).all()
    x = np.zeros(basis.N)
    x[d_oben], x[d_innen] = T_OBERFLAECHE, T_VORLAUF
    u = solve(*condense(K, np.zeros(basis.N), x=x, D=np.concatenate([d_oben, d_innen])))
    return (K @ u)[d_innen].sum(), m.t.shape[1]


if __name__ == "__main__":
    r, q = handrechnung()
    summe = sum(r.values())
    print(f"Handrechnung (unendlich ausgedehnter Boden): q = {q:.2f} W/m, U = {1 / summe:.3f} W/(m·K)")
    for name, wert in r.items():
        print(f"  R {name:<6} {wert:.4f} m·K/W  ({wert / summe:.1%})")
    for lam_e in (1.0, 1.5, 2.0):
        print(f"  Boden λ = {lam_e}: q = {handrechnung(lam_erde=lam_e)[1]:.2f} W/m")
    print("Logstor-Angabe U = 0,271 W/(m·K) (600 mm Überdeckung): q =", f"{0.271 * (T_VORLAUF - T_OBERFLAECHE):.2f} W/m")
    print("\nFEM, Größe des Bodenblocks (Breite x Tiefe):")
    for breite, tiefe in [(4, 3), (6, 3), (10, 5), (20, 10)]:
        q_fem, n = fem(breite, tiefe)
        print(f"  {breite:>2} m x {tiefe:>2} m: q = {q_fem:.3f} W/m ({q_fem / q - 1:+.1%}), {n} Elemente")
    q_halb, n_halb = fem(6, 3, halb=True)
    print(f"Halbmodell 3 m x 3 m: q = {q_halb:.3f} W/m, doppelt {2 * q_halb:.3f} W/m, {n_halb} Elemente")
    q_fein, n_fein = fem(6, 3, h0=0.001, k=0.03)
    print(f"Block 6 m x 3 m feiner vernetzt: q = {q_fein:.3f} W/m, {n_fein} Elemente")
