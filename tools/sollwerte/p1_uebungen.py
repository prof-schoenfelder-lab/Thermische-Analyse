# /// script
# requires-python = ">=3.10"
# dependencies = ["gmsh", "scikit-fem", "numpy"]
# ///
"""Sollwerte für die P1-Übungen 2 (Außenecke) und 3 (Fußbodenheizung), 2D-FEM unabhängig von ANSYS.

Aufruf:  uv run tools/sollwerte/p1_uebungen.py

Stationäre Wärmeleitung, quadratische Dreiecke (P2), Konvektion als Robin-Rand.
Die Werte sind Vorschläge; vor dem Eintragen in ANSYS gegenrechnen.
"""
import gmsh
import numpy as np
from skfem import Basis, BilinearForm, ElementTriP2, FacetBasis, LinearForm, MeshTri, condense, solve, asm
from skfem.helpers import dot, grad


def netz(bauen, h):
    """2D-Geometrie mit gmsh (OCC) vernetzen, konformes Dreiecksnetz zurückgeben."""
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("m")
    bauen(gmsh.model.occ)
    gmsh.model.occ.synchronize()
    gmsh.option.setNumber("Mesh.MeshSizeMax", h)
    gmsh.model.mesh.generate(2)
    tags, xyz, _ = gmsh.model.mesh.getNodes()
    p = xyz.reshape(-1, 3)[:, :2]
    idx = {t: i for i, t in enumerate(tags)}
    typen, _, knoten = gmsh.model.mesh.getElements(2)
    t = np.array([idx[k] for k in knoten[list(typen).index(2)]]).reshape(-1, 3)
    gmsh.finalize()
    return MeshTri(p.T, t.T)


def loesen(mesh, lam_von, robin, dirichlet=None):
    """lam_von(xm) -> λ je Element; robin: [(facets, h, T_inf)]; dirichlet: (facets, T)."""
    basis = Basis(mesh, ElementTriP2())
    lam = lam_von(mesh.p[:, mesh.t].mean(axis=1))
    lam_q = np.repeat(lam[:, None], basis.X.shape[1], axis=1)

    @BilinearForm
    def a(u, v, w):
        return w["lam"] * dot(grad(u), grad(v))

    K = asm(a, basis, lam=lam_q)
    f = np.zeros(basis.N)
    for facets, h, T in robin:
        fb = FacetBasis(mesh, ElementTriP2(), facets=facets)
        K += asm(BilinearForm(lambda u, v, w: h * u * v), fb)
        f += asm(LinearForm(lambda v, w: h * T * v), fb)
    if dirichlet:
        facets, T = dirichlet
        D = basis.get_dofs(facets).all()
        x = np.zeros(basis.N)
        x[D] = T
        return basis, solve(*condense(K, f, x=x, D=D))
    return basis, solve(K, f)


def mittel(basis, u, facets):
    fb = FacetBasis(basis.mesh, basis.elem, facets=facets)
    flaeche = asm(LinearForm(lambda v, w: v), fb).sum()
    return asm(LinearForm(lambda v, w: w["u"] * v), fb, u=fb.interpolate(u)).sum() / flaeche


def aussenecke():
    """Draufsicht: EPS außen (0..0,14 m), Kalksandstein innen (0,14..0,315 m), Schenkel 1 m lang."""
    def bauen(occ):
        r = [occ.addRectangle(0, 0, 0, 1.0, 0.14), occ.addRectangle(0, 0.14, 0, 0.14, 0.86),
             occ.addRectangle(0.14, 0.14, 0, 0.86, 0.175), occ.addRectangle(0.14, 0.315, 0, 0.175, 0.685)]
        occ.fragment([(2, r[0])], [(2, k) for k in r[1:]])
        occ.synchronize()
        gmsh.model.mesh.setSize([(0, 0)], 0.001)

    m = netz(bauen, 0.006)
    eps = lambda x: (x[0] < 0.14 + 1e-9) | (x[1] < 0.14 + 1e-9)
    tol = 1e-7
    aussen = m.facets_satisfying(lambda x: (np.abs(x[0]) < tol) | (np.abs(x[1]) < tol))
    innen = m.facets_satisfying(lambda x: ((np.abs(x[1] - 0.315) < tol) & (x[0] > 0.315 - tol))
                                | ((np.abs(x[0] - 0.315) < tol) & (x[1] > 0.315 - tol)))
    # Mindestwärmeschutz DIN 4108-2: innen R_si = 0,25 (h = 4) bei 20 °C, außen R_se = 0,04 (h = 25) bei -5 °C
    basis, u = loesen(m, lambda x: np.where(eps(x), 0.035, 0.99), [(aussen, 25.0, -5.0), (innen, 4.0, 20.0)])
    ecke = basis.probes(np.array([[0.315], [0.315]])) @ u
    weit = basis.probes(np.array([[1.0], [0.315]])) @ u
    R = 0.25 + 0.175 / 0.99 + 0.14 / 0.035 + 0.04
    flach = 20 - 25 / R * 0.25
    print("Übung 2 Außenecke (h_i = 4, θ_i = 20 °C, h_e = 25, θ_e = -5 °C)")
    print(f"  θ_si Ecke              {ecke[0]:8.3f} °C")
    print(f"  θ_si Schenkelende       {weit[0]:8.3f} °C   (1D-Wand analytisch {flach:.3f} °C)")
    print(f"  f_Rsi Ecke              {(ecke[0] + 5) / 25:8.4f}   (DIN 4108-2: ≥ 0,70)")
    print(f"  f_Rsi ebene Wand        {(flach + 5) / 25:8.4f}")


def fussbodenheizung():
    """Zementestrich 150 x 65 mm (Rohrabstand 150 mm), Rohr Ø 16 mm, Mitte 20 mm über der Dämmung."""
    def bauen(occ):
        r = occ.addRectangle(0, 0, 0, 0.150, 0.065)
        c = occ.addDisk(0.075, 0.020, 0, 0.008, 0.008)
        occ.cut([(2, r)], [(2, c)])

    m = netz(bauen, 0.001)
    tol = 1e-7
    oben = m.facets_satisfying(lambda x: np.abs(x[1] - 0.065) < tol)
    rohr = m.facets_satisfying(lambda x: np.hypot(x[0] - 0.075, x[1] - 0.020) < 0.008 + 1e-5)
    # Oberseite: Gesamtwärmeübergang (Konvektion + Strahlung) 10,8 W/(m²K) nach DIN EN 1264, Raum 20 °C
    basis, u = loesen(m, lambda x: np.full(x.shape[1], 1.4), [(oben, 10.8, 20.0)], dirichlet=(rohr, 35.0))
    tmax = (basis.probes(np.array([[0.075], [0.065]])) @ u)[0]
    tmin = (basis.probes(np.array([[0.0], [0.065]])) @ u)[0]
    tm = mittel(basis, u, oben)
    print("Übung 3 Fußbodenheizung (λ = 1,4, Rohr 35 °C, oben h = 10,8 bei 20 °C, Rest adiabat)")
    print(f"  Oberfläche über dem Rohr   {tmax:7.3f} °C")
    print(f"  Oberfläche zwischen Rohren {tmin:7.3f} °C")
    print(f"  Oberfläche Mittelwert      {tm:7.3f} °C")
    print(f"  Wärmestromdichte nach oben {10.8 * (tm - 20):7.2f} W/m²")


if __name__ == "__main__":
    aussenecke()
    fussbodenheizung()
