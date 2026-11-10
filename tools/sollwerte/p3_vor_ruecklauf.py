# /// script
# requires-python = ">=3.10"
# dependencies = ["gmsh", "scikit-fem", "numpy"]
# ///
"""Sollwerte P3, Übung Vor- und Rücklauf: zwei Fernwärmerohre nebeneinander im Erdreich, unabhängig von ANSYS.

Aufruf:  uv run tools/sollwerte/p3_vor_ruecklauf.py

Rohre, Boden und Bodenblock wie im Vorzeigebeispiel (p3_fernwaermerohr.py): KMR DN 100 Serie 1, Überdeckung 0,8 m,
Erdreich λ 1,0 W/(m·K), Oberfläche 10 °C, Block 6 m × 3 m mit adiabaten Seiten und Boden.
- Vorlauf 80 °C, Rücklauf 50 °C an der Stahlinnenwand
- Abstand der Mantelrohre 100 mm wie in den isoplus-Bezugsbedingungen (ISOPEX-Datenblatt; isoplus rechnet das
  Rohrpaar mit der Mitteltemperatur aus Vor- und Rücklauf). Logstor empfiehlt für Mantelrohre von 90 bis 225 mm
  150 mm (Handbuch Handhabung und Verlegung), zum Vergleich mitgerechnet.

Aufgabenteile:
a) Vollmodell: Wärmeverlust Vorlauf, Rücklauf und zusammen in W/m. Gegenprobe Handrechnung nach EN 13941
   (Wallentén) mit der Rückwirkung R_m = ln(√(1 + (2H/E)²)) / (2π λ_E), E Achsabstand
b) Halbmodell mit Symmetrie in der Mitte (adiabat) und 80 °C: falsch, es rechnet zwei Vorläufe
c) zwei einzeln verlegte Rohre, linear aus dem Vorzeigebeispiel (Wärmestrom proportional zu T − T_Oberfläche)
d) Halbmodell mit der Mitteltemperatur 65 °C: trifft die Summe aus a), weil der antisymmetrische Anteil (±15 K)
   netto keinen Wärmeverlust hat
"""
import math

import gmsh
import numpy as np
from skfem import Basis, BilinearForm, ElementTriP2, MeshTri, asm, condense, solve
from skfem.helpers import dot, grad

from p3_fernwaermerohr import H, LAM_ERDE, LAM_PE, LAM_PUR, LAM_STAHL, R1, R2, R3, R4, T_OBERFLAECHE, r_zylinder

T_VORLAUF, T_RUECKLAUF = 80.0, 50.0


def netz(achsen, breite, tiefe, xmin, h0=0.002, k=0.05, hmax=0.15):
    """Bodenblock (Oberfläche bei y = 0) mit Rohrringen an den Achsen x in achsen, ohne Wasser."""
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("m")
    occ = gmsh.model.occ
    block = occ.addRectangle(xmin, -tiefe, 0, breite, tiefe)
    ringe = [occ.addDisk(x, -H, 0, r, r) for x in achsen for r in (R2, R3, R4)]
    occ.synchronize()
    teile, _ = occ.fragment([(2, block)], [(2, t) for t in ringe])
    wasser = [occ.addDisk(x, -H, 0, R1, R1) for x in achsen]
    occ.synchronize()
    occ.cut(teile, [(2, w) for w in wasser], removeTool=True)
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


def fem(achsen, temperaturen, breite=6.0, tiefe=3.0, xmin=None, **netz_kw):
    """Wärmestrom je Rohr in W/m (Reaktion an der Stahlinnenwand) und Zahl der Elemente."""
    xmin = -breite / 2 if xmin is None else xmin
    m = netz(achsen, breite, tiefe, xmin, **netz_kw)
    basis = Basis(m, ElementTriP2())
    xm = m.p[:, m.t].mean(axis=1)
    r = np.min([np.hypot(xm[0] - x, xm[1] + H) for x in achsen], axis=0)
    lam = np.where(r < R2, LAM_STAHL, np.where(r < R3, LAM_PUR, np.where(r < R4, LAM_PE, LAM_ERDE)))
    K = asm(BilinearForm(lambda u, v, w: w["lam"] * dot(grad(u), grad(v))), basis,
            lam=np.repeat(lam[:, None], basis.X.shape[1], axis=1))
    oben = basis.get_dofs(m.facets_satisfying(lambda x: np.abs(x[1]) < 1e-9, boundaries_only=True)).all()
    x = np.zeros(basis.N)
    x[oben] = T_OBERFLAECHE
    rand, innen = [oben], []
    for xa, temp in zip(achsen, temperaturen):
        d = basis.get_dofs(m.facets_satisfying(
            lambda p, xa=xa: np.abs(np.hypot(p[0] - xa, p[1] + H) - R1) < 1e-4, boundaries_only=True)).all()
        x[d] = temp
        rand.append(d)
        innen.append(d)
    u = solve(*condense(K, np.zeros(basis.N), x=x, D=np.concatenate(rand)))
    reaktion = K @ u
    return [reaktion[d].sum() for d in innen], m.t.shape[1]


def hand_paar(t1, t2, e):
    """Wärmeverlust beider Rohre in W/m nach EN 13941 (Wallentén), Boden mit ln(4H/D) für H >> D."""
    r_einzel = (r_zylinder(R1, R2, LAM_STAHL) + r_zylinder(R2, R3, LAM_PUR) + r_zylinder(R3, R4, LAM_PE)
                + math.log(2 * H / R4) / (2 * math.pi * LAM_ERDE))
    r_m = math.log(math.sqrt(1 + (2 * H / e) ** 2)) / (2 * math.pi * LAM_ERDE)
    nenner = r_einzel**2 - r_m**2
    q1 = ((t1 - T_OBERFLAECHE) * r_einzel - (t2 - T_OBERFLAECHE) * r_m) / nenner
    q2 = ((t2 - T_OBERFLAECHE) * r_einzel - (t1 - T_OBERFLAECHE) * r_m) / nenner
    return q1, q2


if __name__ == "__main__":
    (q_einzel,), _ = fem([0.0], [T_VORLAUF])
    t_mittel = (T_VORLAUF + T_RUECKLAUF) / 2
    for abstand in (0.10, 0.15):
        e = 2 * R4 + abstand
        print(f"\nAbstand der Mantelrohre {1000 * abstand:.0f} mm (Achsabstand {1000 * e:.0f} mm):")
        (qv, qr), n = fem([-e / 2, e / 2], [T_VORLAUF, T_RUECKLAUF])
        summe = qv + qr
        print(f" a) Vollmodell: Vorlauf {qv:.2f}, Rücklauf {qr:.2f}, zusammen {summe:.2f} W/m ({n} Elemente)")
        hv, hr = hand_paar(T_VORLAUF, T_RUECKLAUF, e)
        print(f"    Handrechnung EN 13941: Vorlauf {hv:.2f}, Rücklauf {hr:.2f}, zusammen {hv + hr:.2f} W/m"
              f" ({(hv + hr) / summe - 1:+.1%})")
        if abstand == 0.10:
            (bv, br), _ = fem([-e / 2, e / 2], [T_VORLAUF, T_RUECKLAUF], breite=10.0, tiefe=5.0)
            print(f"    Block 10 m x 5 m: zusammen {bv + br:.2f} W/m ({(bv + br) / summe - 1:+.1%})")
            (fv, fr), nf = fem([-e / 2, e / 2], [T_VORLAUF, T_RUECKLAUF], h0=0.001, k=0.03)
            print(f"    feiner vernetzt: zusammen {fv + fr:.2f} W/m ({nf} Elemente)")
        (qh,), nh = fem([e / 2], [T_VORLAUF], breite=3.0, xmin=0.0)
        print(f" b) Halbmodell 80 °C: {qh:.2f} W/m, doppelt {2 * qh:.2f} W/m ({2 * qh / summe - 1:+.1%}), {nh} Elemente")
        q_rl = q_einzel * (T_RUECKLAUF - T_OBERFLAECHE) / (T_VORLAUF - T_OBERFLAECHE)
        print(f" c) zwei Einzelrohre: {q_einzel:.2f} + {q_rl:.2f} = {q_einzel + q_rl:.2f} W/m,"
              f" das Paar verliert {1 - summe / (q_einzel + q_rl):.1%} weniger")
        (qm,), _ = fem([e / 2], [t_mittel], breite=3.0, xmin=0.0)
        print(f" d) Halbmodell {t_mittel:.0f} °C: {qm:.2f} W/m, doppelt {2 * qm:.2f} W/m")
