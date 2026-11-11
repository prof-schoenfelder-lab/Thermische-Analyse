# /// script
# requires-python = ">=3.10"
# dependencies = ["gmsh", "scikit-fem", "numpy", "meshio"]
# ///
"""Vorabrechnung P3, Netzstudie im Vorzeigebeispiel Fernwärmerohr (Modell nur Dämmung, Block 6 m × 3 m).

Aufruf:  uv run tools/sollwerte/p3_netzstudie.py

Ablauf wie in der Strukturmechanik (Sensitivitätsanalyse; Felix 10.11.: global, dann lokal): Elementgröße halbieren,
bis sich die Ergebnisgröße um weniger als 1 % ändert, erst überall, dann nur im Dämmring. Zwei Größen:
- Wärmeverlust in W/m (Reaktion am Innenrand, eine integrale Größe): konvergiert schon im groben Netz
- maximale Wärmestromdichte an der Innenwand in W/m² (eine lokale Größe): braucht ein feines Netz im Dämmring;
  Kontrolle Wärmeverlust durch Innenumfang q / (2π r_i), der Mittelwert über den Umfang (oben etwas mehr, weil der
  Weg zur Oberfläche dort kürzer ist)

Netz wie in ANSYS aus quadratischen Elementen mit gekrümmten Kanten (gmsh zweiter Ordnung), Kreise mit mindestens
12 Teilen. Die Wärmestromdichte ist hier der Randwert je Element, nicht an den Knoten gemittelt wie in der
ANSYS-Standardanzeige. Die Rechnung zeigt den Verlauf; die Zahlen für die Kursseite kommen aus dem Klicktest.
"""
import math
import os
import tempfile

import gmsh
import numpy as np
from skfem import Basis, BilinearForm, ElementTriP2, FacetBasis, MeshTri2, asm, condense, solve
from skfem.helpers import dot, grad

from p3_fernwaermerohr import H, LAM_ERDE, LAM_PUR, R2, R3, T_OBERFLAECHE, T_VORLAUF, handrechnung

BODEN_GROB = 0.2  # Elementgröße im Boden bei der lokalen Verfeinerung in m


def netz(groesse, breite=6.0, tiefe=3.0, kreisteile=12):
    """Netz zweiter Ordnung; groesse ist eine gmsh-Formel für die Elementgröße in m."""
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("m")
    occ = gmsh.model.occ
    block = occ.addRectangle(-breite / 2, -tiefe, 0, breite, tiefe)
    ring = occ.addDisk(0, -H, 0, R3, R3)
    occ.synchronize()
    teile, _ = occ.fragment([(2, block)], [(2, ring)])
    loch = occ.addDisk(0, -H, 0, R2, R2)
    occ.synchronize()
    occ.cut(teile, [(2, loch)], removeTool=True)
    occ.synchronize()
    feld = gmsh.model.mesh.field.add("MathEval")
    gmsh.model.mesh.field.setString(feld, "F", groesse)
    gmsh.model.mesh.field.setAsBackgroundMesh(feld)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", kreisteile)
    gmsh.model.mesh.generate(2)
    gmsh.model.mesh.setOrder(2)
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    pfad = os.path.join(tempfile.mkdtemp(), "netz.msh")
    gmsh.write(pfad)
    gmsh.finalize()
    return MeshTri2.load(pfad)


def rechnen(m):
    """Wärmeverlust in W/m, maximale Wärmestromdichte an der Innenwand in W/m² und Zahl der Elemente."""
    e = ElementTriP2()
    basis = Basis(m, e)
    xm = m.p[:, m.t].mean(axis=1)
    lam = np.where(np.hypot(xm[0], xm[1] + H) < R3, LAM_PUR, LAM_ERDE)
    K = asm(BilinearForm(lambda u, v, w: w["lam"] * dot(grad(u), grad(v))), basis,
            lam=np.repeat(lam[:, None], basis.X.shape[1], axis=1))
    oben = basis.get_dofs(m.facets_satisfying(lambda x: np.abs(x[1]) < 1e-9, boundaries_only=True)).all()
    rand_innen = m.facets_satisfying(lambda x: np.hypot(x[0], x[1] + H) < R2 + 0.01, boundaries_only=True)
    innen = basis.get_dofs(rand_innen).all()
    x = np.zeros(basis.N)
    x[oben], x[innen] = T_OBERFLAECHE, T_VORLAUF
    u = solve(*condense(K, np.zeros(basis.N), x=x, D=np.concatenate([oben, innen])))
    q = (K @ u)[innen].sum()
    g = FacetBasis(m, e, facets=rand_innen).interpolate(u).grad
    return q, LAM_PUR * np.sqrt(g[0] ** 2 + g[1] ** 2).max(), m.t.shape[1]


if __name__ == "__main__":
    q_hand = handrechnung()[1]
    print(f"Handrechnung: q = {q_hand:.2f} W/m, Mittelwert an der Innenwand q / (2π r_i) = "
          f"{q_hand / (2 * math.pi * R2):.1f} W/m²")
    abstand = f"Sqrt(x*x+(y+{H})*(y+{H}))"
    reihen = {
        "global (überall gleiche Elementgröße)":
            [(h, f"{h}") for h in (0.2, 0.1, 0.05, 0.025, 0.0125)],
        f"lokal im Dämmring (Boden {1000 * BODEN_GROB:.0f} mm, Übergang wächst mit 30 % des Abstands)":
            [(h, f"Min({BODEN_GROB}, {h} + 0.3*Max(0, {abstand} - {R3}))") for h in (0.04, 0.02, 0.01, 0.005, 0.0025)],
    }
    for titel, schritte in reihen.items():
        print(f"\n{titel}:")
        vorher = None
        for h, formel in schritte:
            q, q2, n = rechnen(netz(formel))
            aenderung = "" if vorher is None else f"  Änderung {q / vorher[0] - 1:+.2%} bzw. {q2 / vorher[1] - 1:+.1%}"
            print(f"  {1000 * h:6.1f} mm: q = {q:.3f} W/m, q''max innen = {q2:.1f} W/m², {n:>7} Elemente{aenderung}")
            vorher = (q, q2)
    print(f"\nMittelwert an der Innenwand mit dem FEM-Wärmeverlust: {q / (2 * math.pi * R2):.1f} W/m²")
