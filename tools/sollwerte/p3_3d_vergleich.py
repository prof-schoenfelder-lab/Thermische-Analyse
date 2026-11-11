# /// script
# requires-python = ">=3.10"
# dependencies = ["gmsh", "scikit-fem", "numpy", "pyamg"]
# ///
"""Vorabrechnung P3, 3D-Vergleich zur Seite „Abstraktionen“: Fernwärmerohr als 1 m langes 3D-Stück gegen den
2D-Querschnitt, bei gleicher Netzfeinheit am Rohr. Modell nur Dämmung, Bodenblock 6 m × 3 m (× 1 m in 3D),
Enden des 3D-Stücks adiabat. Erwartung: gleicher Wärmeverlust je Meter, aber ein Vielfaches an Elementen.

Aufruf:  uv run tools/sollwerte/p3_3d_vergleich.py

Elementgröße überall Min(h_max, h_0 + k·r) mit r = Abstand zur Rohrachse. 2D quadratische Dreiecke,
3D quadratische Tetraeder (wie ANSYS mit Zwischenknoten). Die Elementzahlen in ANSYS hängen vom Vernetzer ab;
die Zahlen hier zeigen die Größenordnung, die Werte für die Seite kommen aus dem Klicktest.
"""
import time

import gmsh
import numpy as np
import pyamg
from skfem import Basis, BilinearForm, ElementTetP2, MeshTet, asm, condense, solve, solver_iter_pcg
from skfem.helpers import dot, grad

from p3_fernwaermerohr import H, LAM_ERDE, LAM_PUR, R2, R3, T_OBERFLAECHE, T_VORLAUF, fem

H0, K, HMAX = 0.008, 0.15, 0.4
LAENGE = 1.0


def netz_3d(breite=6.0, tiefe=3.0, laenge=LAENGE):
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("m3")
    occ = gmsh.model.occ
    block = occ.addBox(-breite / 2, -tiefe, 0, breite, tiefe, laenge)
    ring = occ.addCylinder(0, -H, 0, 0, 0, laenge, R3)
    occ.synchronize()
    teile, _ = occ.fragment([(3, block)], [(3, ring)])
    loch = occ.addCylinder(0, -H, 0, 0, 0, laenge, R2)
    occ.synchronize()
    occ.cut(teile, [(3, loch)], removeTool=True)
    occ.synchronize()
    feld = gmsh.model.mesh.field.add("MathEval")
    gmsh.model.mesh.field.setString(feld, "F", f"Min({HMAX}, {H0} + {K}*Sqrt(x*x+(y+{H})*(y+{H})))")
    gmsh.model.mesh.field.setAsBackgroundMesh(feld)
    for option in ("Mesh.MeshSizeExtendFromBoundary", "Mesh.MeshSizeFromPoints", "Mesh.MeshSizeFromCurvature"):
        gmsh.option.setNumber(option, 0)
    gmsh.model.mesh.generate(3)
    tags, xyz, _ = gmsh.model.mesh.getNodes()
    p = xyz.reshape(-1, 3)
    idx = {t: i for i, t in enumerate(tags)}
    typen, _, knoten = gmsh.model.mesh.getElements(3)
    t = np.array([idx[k] for k in knoten[list(typen).index(4)]]).reshape(-1, 4)
    gmsh.finalize()
    return MeshTet(p.T, t.T)


def fem_3d():
    start = time.perf_counter()
    m = netz_3d()
    basis = Basis(m, ElementTetP2())
    xm = m.p[:, m.t].mean(axis=1)
    lam = np.where(np.hypot(xm[0], xm[1] + H) < R3, LAM_PUR, LAM_ERDE)
    K_ = asm(BilinearForm(lambda u, v, w: w["lam"] * dot(grad(u), grad(v))), basis,
             lam=np.repeat(lam[:, None], basis.X.shape[1], axis=1))
    oben = basis.get_dofs(m.facets_satisfying(lambda x: np.abs(x[1]) < 1e-9, boundaries_only=True)).all()
    rand = m.boundary_facets()
    pkt = m.p[:, m.facets[:, rand]]
    auf_zylinder = np.all(np.abs(np.hypot(pkt[0], pkt[1] + H) - R2) < 1e-6, axis=0)
    innen = basis.get_dofs(rand[auf_zylinder]).all()
    x = np.zeros(basis.N)
    x[oben], x[innen] = T_OBERFLAECHE, T_VORLAUF
    system = condense(K_, np.zeros(basis.N), x=x, D=np.concatenate([oben, innen]))
    u = solve(*system, solver=solver_iter_pcg(M=pyamg.smoothed_aggregation_solver(system[0]).aspreconditioner(), rtol=1e-10))
    q = (K_ @ u)[innen].sum() / LAENGE
    return q, m.t.shape[1], m.p.shape[1], basis.N, time.perf_counter() - start


if __name__ == "__main__":
    start = time.perf_counter()
    (q2,), n2 = fem(h0=H0, k=K, hmax=HMAX)
    t2 = time.perf_counter() - start
    print(f"2D-Querschnitt: q = {q2:.3f} W/m, {n2} Dreiecke, {t2:.1f} s")
    q3, n3, knoten3, dofs3, t3 = fem_3d()
    print(f"3D-Stück {LAENGE:.0f} m: q = {q3:.3f} W/m ({q3 / q2 - 1:+.2%}), {n3} Tetraeder, {knoten3} Eckknoten,"
          f" {dofs3} Unbekannte, {t3:.1f} s")
    print(f"Faktor Elemente 3D/2D: {n3 / n2:.0f}")
