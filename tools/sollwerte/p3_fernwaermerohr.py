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
- Vorlauf 80 °C, Oberfläche 10 °C, Bodenblock mit adiabaten Seiten und adiabatem Boden

Modell der Studierenden (Felix 10.11.): nur die Dämmung. Stahlrohr und PE-Mantel tragen zusammen 0,4 % des
Wärmewiderstands und fallen weg: 80 °C an der Innenseite der Dämmung (Ø 114,3 mm), Erdreich direkt außen an der
Dämmung (Ø 193,6 mm). Zum Vergleich gerechnet: alle Schichten und der falsche Weg, den PE-Mantel der Dämmung
zuzuschlagen (die Dämmung wird dann 3,2 mm dicker).

Handrechnung: Schichten als Hohlzylinder in Reihe, Boden als Zylinder unter isothermer Oberfläche
im unendlich ausgedehnten Erdreich, R_Boden = arcosh(2H/D) / (2 π λ_E), H Tiefe der Rohrachse, D Außendurchmesser
des Rohrs im Modell. FEM: quadratische Dreiecke (P2), Wärmestrom als Reaktion am Innenrand, in W je Meter Rohr.
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
H = UEBERDECKUNG + R4  # Tiefe der Rohrachse, gleich für alle Modelle
T_VORLAUF, T_OBERFLAECHE = 80.0, 10.0

# Modell: Innenrand mit der Rohrtemperatur und Ringe (Name, Außenradius, λ) von innen nach außen, außen Erdreich
NUR_DAEMMUNG = (R2, [("PUR", R3, LAM_PUR)])
ALLE_SCHICHTEN = (R1, [("Stahl", R2, LAM_STAHL), ("PUR", R3, LAM_PUR), ("PE", R4, LAM_PE)])
PE_ZUR_DAEMMUNG = (R2, [("PUR", R4, LAM_PUR)])


def r_zylinder(ra, rb, lam):
    return math.log(rb / ra) / (2 * math.pi * lam)


def handrechnung(modell=NUR_DAEMMUNG, lam_erde=LAM_ERDE, ueberdeckung=UEBERDECKUNG):
    """Widerstände in m·K/W und Wärmeverlust in W/m."""
    h = ueberdeckung + R4
    r_innen, ringe = modell
    r, ra = {}, r_innen
    for name, rb, lam in ringe:
        r[name] = r_zylinder(ra, rb, lam)
        ra = rb
    r["Boden"] = math.acosh(h / ra) / (2 * math.pi * lam_erde)
    return r, (T_VORLAUF - T_OBERFLAECHE) / sum(r.values())


def netz(achsen, modell, breite, tiefe, xmin, h0=0.002, k=0.05, hmax=0.15):
    """Bodenblock (Oberfläche bei y = 0, links bei xmin) mit Rohren an den Achsen x in achsen, Inneres ausgeschnitten.

    Was über den Block hinausragt (Rohr auf der Symmetrielinie beim Halbmodell), wird abgeschnitten.
    """
    r_innen, ringe = modell
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("m")
    occ = gmsh.model.occ
    block = occ.addRectangle(xmin, -tiefe, 0, breite, tiefe)
    scheiben = [occ.addDisk(x, -H, 0, ra, ra) for x in achsen for _, ra, _ in ringe]
    occ.synchronize()
    teile, _ = occ.fragment([(2, block)], [(2, s) for s in scheiben])
    loecher = [occ.addDisk(x, -H, 0, r_innen, r_innen) for x in achsen]
    occ.synchronize()
    teile, _ = occ.cut(teile, [(2, l) for l in loecher], removeTool=True)
    aussen = [occ.addRectangle(xmin - 10, -tiefe - 10, 0, 10, tiefe + 20),
              occ.addRectangle(xmin + breite, -tiefe - 10, 0, 10, tiefe + 20)]
    occ.synchronize()
    occ.cut(teile, [(2, a) for a in aussen], removeTool=True)
    occ.synchronize()
    abstand = [f"Sqrt((x-({x}))*(x-({x}))+(y+{H})*(y+{H}))" for x in achsen]
    naechster = abstand[0] if len(abstand) == 1 else f"Min({abstand[0]}, {abstand[1]})"
    feld = gmsh.model.mesh.field.add("MathEval")
    gmsh.model.mesh.field.setString(feld, "F", f"Min({hmax}, {h0} + {k}*{naechster})")
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


def rand_auf_kreis(m, xa, r, tol=1e-6):
    """Randkanten, deren Knoten alle auf dem Kreis mit Radius r um die Achse x = xa liegen.

    Über die Knoten statt über den Kantenmittelpunkt: Bei groben Netzen liegt der Mittelpunkt einer geraden Kante
    merklich innerhalb des Kreises, und Kanten auf einer Symmetrielinie, die am Kreis beginnen, bleiben draußen.
    """
    rand = m.boundary_facets()
    pkt = m.p[:, m.facets[:, rand]]
    abstand = np.hypot(pkt[0] - xa, pkt[1] + H)
    return rand[np.all(np.abs(abstand - r) < tol, axis=0)]


def fem(achsen=(0.0,), temperaturen=(T_VORLAUF,), modell=NUR_DAEMMUNG, breite=6.0, tiefe=3.0, xmin=None,
        **netz_kw):
    """Wärmestrom je Rohr in W/m (Reaktion am Innenrand) und Zahl der Elemente."""
    xmin = -breite / 2 if xmin is None else xmin
    m = netz(achsen, modell, breite, tiefe, xmin, **netz_kw)
    basis = Basis(m, ElementTriP2())
    r_innen, ringe = modell
    xm = m.p[:, m.t].mean(axis=1)
    r = np.min([np.hypot(xm[0] - x, xm[1] + H) for x in achsen], axis=0)
    lam = np.full(r.shape, LAM_ERDE)
    for _, ra, la in reversed(ringe):
        lam[r < ra] = la
    K = asm(BilinearForm(lambda u, v, w: w["lam"] * dot(grad(u), grad(v))), basis,
            lam=np.repeat(lam[:, None], basis.X.shape[1], axis=1))
    oben = basis.get_dofs(m.facets_satisfying(lambda x: np.abs(x[1]) < 1e-9, boundaries_only=True)).all()
    x = np.zeros(basis.N)
    x[oben] = T_OBERFLAECHE
    rand, innen = [oben], []
    for xa, temp in zip(achsen, temperaturen):
        d = basis.get_dofs(rand_auf_kreis(m, xa, r_innen)).all()
        x[d] = temp
        rand.append(d)
        innen.append(d)
    u = solve(*condense(K, np.zeros(basis.N), x=x, D=np.concatenate(rand)))
    reaktion = K @ u
    return [reaktion[d].sum() for d in innen], m.t.shape[1]


if __name__ == "__main__":
    r, q = handrechnung()
    summe = sum(r.values())
    print(f"Handrechnung nur Dämmung (unendlich ausgedehnter Boden): q = {q:.2f} W/m, U = {1 / summe:.3f} W/(m·K)")
    for lam_e in (1.0, 1.5, 2.0):
        print(f"  Boden λ = {lam_e}: q = {handrechnung(lam_erde=lam_e)[1]:.2f} W/m")
    r_alle, q_alle = handrechnung(ALLE_SCHICHTEN)
    summe_alle = sum(r_alle.values())
    print(f"Handrechnung alle Schichten: q = {q_alle:.2f} W/m; Anteile am Widerstand (Begründung fürs Weglassen):")
    for name, wert in r_alle.items():
        print(f"  R {name:<6} {wert:.4f} m·K/W  ({wert / summe_alle:.1%})")
    print(f"Handrechnung PE zur Dämmung (falsch): q = {handrechnung(PE_ZUR_DAEMMUNG)[1]:.2f} W/m")
    print("Logstor-Angabe U = 0,271 W/(m·K) (600 mm Überdeckung): q =", f"{0.271 * (T_VORLAUF - T_OBERFLAECHE):.2f} W/m")
    print("\nFEM nur Dämmung, Größe des Bodenblocks (Breite x Tiefe):")
    for breite, tiefe in [(4, 3), (6, 3), (10, 5), (20, 10)]:
        (q_fem,), n = fem(breite=breite, tiefe=tiefe)
        print(f"  {breite:>2} m x {tiefe:>2} m: q = {q_fem:.3f} W/m ({q_fem / q - 1:+.1%}), {n} Elemente")
    (q_ref,), n_ref = fem()
    (q_halb,), n_halb = fem(breite=3.0, xmin=0.0)
    print(f"Halbmodell 3 m x 3 m: q = {q_halb:.3f} W/m, doppelt {2 * q_halb:.3f} W/m, {n_halb} Elemente")
    (q_fein,), n_fein = fem(h0=0.001, k=0.03)
    print(f"Block 6 m x 3 m feiner vernetzt: q = {q_fein:.3f} W/m, {n_fein} Elemente")
    print("\nVergleich, Block 6 m x 3 m:")
    for name, modell in (("alle Schichten", ALLE_SCHICHTEN), ("PE zur Dämmung (falsch)", PE_ZUR_DAEMMUNG)):
        (qv,), nv = fem(modell=modell)
        print(f"  {name:<24} q = {qv:.3f} W/m ({qv / q_ref - 1:+.2%} gegen nur Dämmung), {nv} Elemente")
