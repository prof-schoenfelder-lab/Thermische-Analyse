# /// script
# requires-python = ">=3.10"
# dependencies = ["gmsh", "scikit-fem", "numpy", "scipy"]
# ///
"""Sollwerte für P2 (Randbedingungen), FEM unabhängig von ANSYS.

Aufruf:  uv run tools/sollwerte/p2_uebungen.py [roehre|rohr|kuehlkoerper|kabel] [--fein]

Stationäre Wärmeleitung, quadratische Elemente (P2), Konvektion als Robin-Rand,
Strahlung To Ambient als Robin-Rand mit Sekantenzahl (Picard-Iteration),
Strahlung Surface to Surface mit Radiosity und eigenen Sichtfaktoren (2D, mit Verschattung).
Längen in m, Temperaturen in °C. Die 3D-Modelle in ANSYS sind Stücke mit isolierten
Stirnflächen; wo nichts entlang der Achse fließt, ist das genau der 2D-Schnitt.
"""
import sys

import gmsh
import numpy as np
from skfem import (Basis, BilinearForm, ElementTetP2, ElementTriP2, FacetBasis, LinearForm, MeshTet, MeshTri, asm,
                   condense, solve)
from skfem.helpers import dot, grad

SIGMA = 5.670374419e-8
K0 = 273.15


@BilinearForm
def _leitung(u, v, w):
    return w["lam"] * dot(grad(u), grad(v))


@BilinearForm
def _robin(u, v, w):
    return w["h"] * u * v


@LinearForm
def _last(v, w):
    return w["g"] * v


def netz2d(bauen, h_max, verfeinern=()):
    """2D-Geometrie mit gmsh (OCC) vernetzen. verfeinern: [(Punkt-Auswahl xy -> bool, Größe)]."""
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("m")
    bauen(gmsh.model.occ)
    gmsh.model.occ.synchronize()
    gmsh.option.setNumber("Mesh.MeshSizeMax", h_max)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 24)
    for wahl, groesse in verfeinern:
        pkt = [t for d, t in gmsh.model.getEntities(0) if wahl(gmsh.model.getValue(0, t, []))]
        gmsh.model.mesh.setSize([(0, t) for t in pkt], groesse)
    gmsh.model.mesh.generate(2)
    tags, xyz, _ = gmsh.model.mesh.getNodes()
    p = xyz.reshape(-1, 3)[:, :2]
    idx = {t: i for i, t in enumerate(tags)}
    typen, _, knoten = gmsh.model.mesh.getElements(2)
    t = np.array([idx[k] for k in knoten[list(typen).index(2)]]).reshape(-1, 3)
    gmsh.finalize()
    benutzt = np.unique(t)                      # Knoten ohne Element (Geometriepunkte) entfernen
    neu = -np.ones(len(p), dtype=int)
    neu[benutzt] = np.arange(len(benutzt))
    return MeshTri(p[benutzt].T, neu[t].T)


def _element(mesh):
    return ElementTetP2() if isinstance(mesh, MeshTet) else ElementTriP2()


def netz3d(bauen, h_max):
    """3D-Geometrie mit gmsh (OCC) in Tetraeder vernetzen (konform an gemeinsamen Flächen)."""
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("m")
    bauen(gmsh.model.occ)
    gmsh.model.occ.synchronize()
    gmsh.option.setNumber("Mesh.MeshSizeMax", h_max)
    gmsh.model.mesh.generate(3)
    tags, xyz, _ = gmsh.model.mesh.getNodes()
    p = xyz.reshape(-1, 3)
    idx = {t: i for i, t in enumerate(tags)}
    typen, _, knoten = gmsh.model.mesh.getElements(3)
    t = np.array([idx[k] for k in knoten[list(typen).index(4)]]).reshape(-1, 4)
    gmsh.finalize()
    benutzt = np.unique(t)
    neu = -np.ones(len(p), dtype=int)
    neu[benutzt] = np.arange(len(benutzt))
    return MeshTet(p[benutzt].T, neu[t].T)


class Randstueck:
    """Randkanten einer Gruppe mit Facet-Basis und Hilfsgrößen."""

    def __init__(self, mesh, facets):
        self.facets = np.asarray(facets)
        self.fb = FacetBasis(mesh, _element(mesh), facets=self.facets)
        self.nqp = self.fb.X.shape[-1]
        self.dx = self.fb.dx

    def je_kante(self, werte):
        return np.repeat(np.asarray(werte, float)[:, None], self.nqp, axis=1)

    def mittel(self, u):
        val = self.fb.interpolate(u).value
        return (val * self.dx).sum(1) / self.dx.sum(1)

    def integral(self, feld):
        return float((feld * self.dx).sum())

    def laenge(self):
        return self.dx.sum(1)


def sichtfaktoren(P, Q, n, verdeckt, k=6):
    """2D-Sichtfaktoren zwischen geraden Randkanten (P->Q, Normale n in den Strahlungsraum).

    F_ij = 1/L_i ∫∫ cos θi cos θj / (2 r) ds_i ds_j, Gauß-Legendre mit k Punkten je Kante,
    verdeckt(A, B) -> bool-Feld: Strahl A->B schneidet einen Körper.
    """
    g, wg = np.polynomial.legendre.leggauss(k)
    s, ws = (g + 1) / 2, wg / 2
    L = np.linalg.norm(Q - P, axis=1)
    X = P[:, None, :] + (Q - P)[:, None, :] * s[None, :, None]         # (N, k, 2)
    N = len(P)
    F = np.zeros((N, N))
    for i in range(N):
        A = np.broadcast_to(X[i][:, None, None, :], (k, N, k, 2))      # Punkte auf i
        B = np.broadcast_to(X[None, :, :, :], (k, N, k, 2))            # Punkte auf allen j
        d = B - A
        r = np.linalg.norm(d, axis=-1)
        r = np.where(r < 1e-12, np.inf, r)
        ci = (d @ n[i]) / r
        cj = -np.einsum("ajbx,jx->ajb", d, n) / r
        ker = np.where((ci > 0) & (cj > 0), ci * cj / (2 * r), 0.0)
        offen = ker > 0
        if offen.any():
            sel = np.nonzero(offen)
            blk = verdeckt(A[sel], B[sel])
            ker[sel] = np.where(blk, 0.0, ker[sel])
        gew = ws[:, None, None] * ws[None, None, :] * L[None, :, None] * L[i]
        F[i] = (ker * gew).sum(axis=(0, 2)) / L[i]
    np.fill_diagonal(F, 0.0)
    return F


def normalen_aussen(mesh, facets):
    """Normale je Randkante, zeigt vom angrenzenden Element weg."""
    P = mesh.p[:, mesh.facets[0, facets]].T
    Q = mesh.p[:, mesh.facets[1, facets]].T
    d = Q - P
    n = np.stack([d[:, 1], -d[:, 0]], axis=1) / np.linalg.norm(d, axis=1)[:, None]
    el = mesh.f2t[0, facets]
    c = mesh.p[:, mesh.t[:, el]].mean(axis=1).T
    mitte = (P + Q) / 2
    n[((mitte - c) * n).sum(1) < 0] *= -1
    return P, Q, n


def loesen(mesh, lam_el, konv=(), to_ambient=(), flux=(), s2s=None, quelle=None, dirichlet=None,
           T0=20.0, tol=1e-7, max_it=300, relax=1.0):
    """Stationäre Wärmeleitung mit Picard-Iteration für Strahlung.

    konv:       [(Randstueck, alpha, T_luft)]
    to_ambient: [(Randstueck, eps, T_umgebung)]
    flux:       [(Randstueck, q)]                 q in W/m² in das Modell hinein
    s2s:        (Randstueck, eps je Kante, F)    geschlossener Hohlraum (Perfect)
    quelle:     q''' je Element (W/m³) oder None
    dirichlet:  [(Randstueck, T)]
    """
    basis = Basis(mesh, _element(mesh))
    lam_q = np.repeat(np.asarray(lam_el, float)[:, None], basis.X.shape[-1], axis=1)
    K_fest = asm(_leitung, basis, lam=lam_q)
    f_fest = np.zeros(basis.N)
    for rs, a, T in konv:
        K_fest += asm(_robin, rs.fb, h=rs.je_kante(np.full(len(rs.facets), a)))
        f_fest += asm(_last, rs.fb, g=rs.je_kante(np.full(len(rs.facets), a * T)))
    for rs, q in flux:
        f_fest += asm(_last, rs.fb, g=rs.je_kante(np.full(len(rs.facets), q)))
    if quelle is not None:
        f_fest += asm(_last, basis, g=np.repeat(np.asarray(quelle, float)[:, None], basis.X.shape[-1], axis=1))
    D, x0 = None, np.zeros(basis.N)
    if dirichlet:
        D = np.unique(np.concatenate([basis.get_dofs(rs.facets).all() for rs, _ in dirichlet]))
        for rs, T in dirichlet:
            x0[basis.get_dofs(rs.facets).all()] = T
    u = np.full(basis.N, T0)
    s2s_q = None
    for it in range(max_it):
        K, f = K_fest.copy(), f_fest.copy()
        for rs, eps, Ta in to_ambient:
            Tq = rs.fb.interpolate(u).value + K0
            Tak = Ta + K0
            h = eps * SIGMA * (Tq ** 2 + Tak ** 2) * (Tq + Tak)
            K += asm(_robin, rs.fb, h=h)
            f += asm(_last, rs.fb, g=h * Ta)
        if s2s is not None:
            rs, eps, F = s2s
            Tf = rs.mittel(u) + K0
            Eb = SIGMA * Tf ** 4
            A = np.eye(len(Tf)) - (1 - eps)[:, None] * F
            J = np.linalg.solve(A, eps * Eb)
            q_aus = eps / (1 - eps) * (Eb - J)
            s2s_q = q_aus
            h = 4 * eps * SIGMA * Tf ** 3                     # Näherung der Ableitung, nur zur Stabilisierung
            K += asm(_robin, rs.fb, h=rs.je_kante(h))
            f += asm(_last, rs.fb, g=rs.je_kante(h * (Tf - K0) - q_aus))
        u_neu = solve(*condense(K, f, x=x0, D=D)) if D is not None else solve(K, f)
        diff = np.max(np.abs(u_neu - u))
        u = u + relax * (u_neu - u)
        if diff < tol:
            break
    return basis, u, it + 1, s2s_q


# ---------------------------------------------------------------------------------------------
# Vorzeigebeispiel: Vakuumröhre (Glasrohr, Absorberblech mit Wasserrohr, Vakuum dazwischen)
# ---------------------------------------------------------------------------------------------
ROEHRE = dict(
    r_glas_a=0.035, r_glas_i=0.0325,            # Glasrohr Ø 70 × 2,5 mm
    r_rohr_a=0.006, r_rohr_i=0.005,              # Kupferrohr Ø 12 × 1 mm
    b_blech=0.060, t_blech=0.0005,               # Absorberblech 60 × 0,5 mm
    lam_glas=1.1, lam_cu=400.0,
    q_sonne=800 * 0.92 * 0.95,                   # Einstrahlung × Durchlässigkeit Glas × Absorptionsgrad
    alpha_w=1000.0, T_w=50.0,                    # Wasser im Rohr
    alpha_l=10.0, T_l=20.0,                      # Luft außen
    eps_glas=0.9, T_himmel=5.0,
)


def roehre(eps_abs, alpha_w=None, h=0.001, h_blech=0.000125, k=6, P=ROEHRE):
    alpha_w = P["alpha_w"] if alpha_w is None else alpha_w

    def bauen(occ):
        ga = occ.addDisk(0, 0, 0, P["r_glas_a"], P["r_glas_a"])
        gi = occ.addDisk(0, 0, 0, P["r_glas_i"], P["r_glas_i"])
        occ.cut([(2, ga)], [(2, gi)])
        ra = occ.addDisk(0, 0, 0, P["r_rohr_a"], P["r_rohr_a"])
        bl = occ.addRectangle(-P["b_blech"] / 2, -P["t_blech"] / 2, 0, P["b_blech"], P["t_blech"])
        abs_, _ = occ.fuse([(2, ra)], [(2, bl)])
        ri = occ.addDisk(0, 0, 0, P["r_rohr_i"], P["r_rohr_i"])
        occ.cut(abs_, [(2, ri)])

    mesh = netz2d(bauen, h, verfeinern=[(lambda xy: np.hypot(*xy[:2]) < 0.031, h_blech)])
    mitte = mesh.p[:, mesh.facets].mean(axis=1)
    r = np.hypot(*mitte)
    rand = mesh.boundary_facets()
    rr = r[rand]
    glas_a = rand[rr > (P["r_glas_a"] + P["r_glas_i"]) / 2 + 0.0005]
    glas_i = rand[(rr > 0.031) & (rr < (P["r_glas_a"] + P["r_glas_i"]) / 2)]
    rohr_i = rand[rr < (P["r_rohr_a"] + P["r_rohr_i"]) / 2]
    abs_a = np.setdiff1d(rand, np.concatenate([glas_a, glas_i, rohr_i]))
    y = mitte[1, abs_a]
    sonne = abs_a[np.abs(y - P["t_blech"] / 2) < 1e-9]          # nur Oberseite der Bleche, Rohr selbst nicht

    zentren = mesh.p[:, mesh.t].mean(axis=1)
    lam = np.where(np.hypot(*zentren) > 0.031, P["lam_glas"], P["lam_cu"])

    strahl = np.concatenate([glas_i, abs_a])
    Pp, Qp, n = normalen_aussen(mesh, strahl)

    def verdeckt(A, B):
        """Strahl A->B schneidet das Absorberblech (Mittellinie) oder das Rohr (Kreis r_rohr_a)."""
        d = B - A
        # Blech: Schnitt mit y = 0, |x| <= b/2; Startpunkt auf dem Blech selbst zählt nicht
        with np.errstate(divide="ignore", invalid="ignore"):
            t = -A[:, 1] / d[:, 1]
        xs = A[:, 0] + t * d[:, 0]
        blech = (t > 1e-6) & (t < 1 - 1e-6) & (np.abs(xs) <= P["b_blech"] / 2) & (np.abs(A[:, 1]) > 1e-9) \
            & (np.abs(B[:, 1]) > 1e-9)
        # Rohr: kürzester Abstand der Strecke zum Mittelpunkt kleiner als Radius (etwas Spiel)
        tt = np.clip(-(A * d).sum(1) / np.maximum((d * d).sum(1), 1e-30), 0, 1)
        nah = A + tt[:, None] * d
        rohr = (np.hypot(*nah.T) < P["r_rohr_a"] * (1 - 1e-3)) & (tt > 1e-6) & (tt < 1 - 1e-6)
        return blech | rohr

    F_roh = sichtfaktoren(Pp, Qp, n, verdeckt, k=k)
    summe = F_roh.sum(1)
    F = F_roh / summe[:, None]                    # Perfect: Zeilen auf 1 skalieren (wie ANSYS VFSM)
    eps = np.where(np.isin(strahl, glas_i), P["eps_glas"], eps_abs)

    R = {k: Randstueck(mesh, v) for k, v in dict(glas_a=glas_a, rohr_i=rohr_i, sonne=sonne, strahl=strahl).items()}
    konv = [(R["glas_a"], P["alpha_l"], P["T_l"])]
    if alpha_w > 0:
        konv.append((R["rohr_i"], alpha_w, P["T_w"]))
    basis, u, it, q_s2s = loesen(mesh, lam, konv=konv,
                                 to_ambient=[(R["glas_a"], P["eps_glas"], P["T_himmel"])],
                                 flux=[(R["sonne"], P["q_sonne"])],
                                 s2s=(R["strahl"], eps, F), T0=40.0, relax=0.7)

    knoten = mesh.p
    T_kn = u[: knoten.shape[1]]                   # P2: erste Freiheitsgrade = Eckknoten
    r_kn = np.hypot(*knoten)
    glas = r_kn > 0.031
    Tw = R["rohr_i"].fb.interpolate(u).value
    Q_nutz = R["rohr_i"].integral(alpha_w * (Tw - P["T_w"])) if alpha_w > 0 else 0.0
    Q_sonne = P["q_sonne"] * R["sonne"].laenge().sum()
    Tg = R["glas_a"].fb.interpolate(u).value
    Q_luft = R["glas_a"].integral(P["alpha_l"] * (Tg - P["T_l"]))
    Q_himmel = R["glas_a"].integral(P["eps_glas"] * SIGMA * ((Tg + K0) ** 4 - (P["T_himmel"] + K0) ** 4))
    n_abs = np.isin(strahl, abs_a)
    L_s = R["strahl"].laenge()
    Q_s2s_abs = float((q_s2s * L_s)[n_abs].sum())
    gross = summe > 1.01
    if gross.any():
        print(f"  Zeilensumme > 1,01 an {gross.sum()} Kanten, z. B. bei", np.round((Pp[gross][:3] + Qp[gross][:3]) / 2 * 1000, 2).tolist(), "mm")
    return dict(it=it, knoten=mesh.p.shape[1], F_summe=(summe.min(), summe.max()),
                T_abs=(T_kn[~glas].min(), T_kn[~glas].max()), T_glas=(T_kn[glas].min(), T_kn[glas].max()),
                T_glas_aussen_mittel=R["glas_a"].integral(Tg) / R["glas_a"].laenge().sum(),
                Q_sonne=Q_sonne, Q_nutz=Q_nutz, Q_luft=Q_luft, Q_himmel=Q_himmel, Q_abs_glas=Q_s2s_abs,
                bilanz=Q_sonne - Q_nutz - Q_luft - Q_himmel)


# ---------------------------------------------------------------------------------------------
# Übung 1: ungedämmtes Heizungsrohr im Keller (Konvektion und Strahlung auf derselben Fläche)
# ---------------------------------------------------------------------------------------------
ROHR = dict(r_a=0.02690 / 2, s=0.0026, lam_stahl=50.0, alpha_w=1000.0, T_w=60.0,
            alpha_l=7.0, T_l=15.0, eps=0.9, T_wand=15.0, d_daemm=0.020, lam_daemm=0.035)


def rohr(strahlung=True, daemmung=False, h=0.0005, P=ROHR):
    """Querschnitt, Ergebnisse je Meter Rohr."""
    r_i, r_a = P["r_a"] - P["s"], P["r_a"]
    r_aus = r_a + (P["d_daemm"] if daemmung else 0.0)

    def bauen(occ):
        teile = [(2, occ.addDisk(0, 0, 0, r_a, r_a))]
        if daemmung:
            teile.append((2, occ.addDisk(0, 0, 0, r_aus, r_aus)))
        occ.fragment(teile, [])
        occ.cut(occ.getEntities(2), [(2, occ.addDisk(0, 0, 0, r_i, r_i))])
        occ.removeAllDuplicates()

    mesh = netz2d(bauen, h)
    mitte = mesh.p[:, mesh.facets].mean(axis=1)
    rand = mesh.boundary_facets()
    rr = np.hypot(*mitte[:, rand])
    innen, aussen = rand[rr < (r_i + r_a) / 2], rand[rr > r_aus - 0.0005]
    zentren = np.hypot(*mesh.p[:, mesh.t].mean(axis=1))
    lam = np.where(zentren < r_a, P["lam_stahl"], P["lam_daemm"])
    Ri, Ra = Randstueck(mesh, innen), Randstueck(mesh, aussen)
    basis, u, it, _ = loesen(mesh, lam, konv=[(Ri, P["alpha_w"], P["T_w"]), (Ra, P["alpha_l"], P["T_l"])],
                             to_ambient=[(Ra, P["eps"], P["T_wand"])] if strahlung else [], T0=40.0)
    Ta = Ra.fb.interpolate(u).value
    Q_konv = Ra.integral(P["alpha_l"] * (Ta - P["T_l"]))
    Q_str = Ra.integral(P["eps"] * SIGMA * ((Ta + K0) ** 4 - (P["T_wand"] + K0) ** 4)) if strahlung else 0.0
    return dict(it=it, knoten=mesh.p.shape[1], T_aussen=Ra.integral(Ta) / Ra.laenge().sum(),
                Q_konv=Q_konv, Q_str=Q_str, Q=Q_konv + Q_str, anteil_str=Q_str / (Q_konv + Q_str))


# ---------------------------------------------------------------------------------------------
# Übung 2: Kühlkörper eines Wechselrichters (3D, Wärmestrom auf einem Teil der Rückseite)
# ---------------------------------------------------------------------------------------------
KUEHL = dict(b=0.100, l=0.100, t=0.008, n_rippen=8, t_rippe=0.002, h_rippe=0.040,
             modul=0.050, Q=40.0, lam=200.0, alpha=6.0, T_l=40.0, T_umg=40.0)


def kuehlkoerper(eps, h=0.002, P=KUEHL):
    """x quer zu den Rippen, y entlang der Rippen, z von der Rückseite (z = 0) zu den Rippenspitzen."""
    b, l, t = P["b"], P["l"], P["t"]
    teilung = (b - P["t_rippe"]) / (P["n_rippen"] - 1)

    def bauen(occ):
        koerper = [(3, occ.addBox(0, 0, 0, b, l, t))]
        rippen = [(3, occ.addBox(i * teilung, 0, t - 1e-9, P["t_rippe"], l, P["h_rippe"] + 1e-9))
                  for i in range(P["n_rippen"])]
        ganz, _ = occ.fuse(koerper, rippen)
        m0 = (b - P["modul"]) / 2
        flaeche = occ.addRectangle(m0, (l - P["modul"]) / 2, 0, P["modul"], P["modul"])
        occ.fragment(ganz, [(2, flaeche)])
        occ.removeAllDuplicates()

    mesh = netz3d(bauen, h)
    mitte = mesh.p[:, mesh.facets].mean(axis=1)
    rand = mesh.boundary_facets()
    x, y, z = mitte[:, rand]
    m0, m1 = (b - P["modul"]) / 2, (b + P["modul"]) / 2
    rueck = rand[z < 1e-7]
    modul = rueck[(x[z < 1e-7] > m0) & (x[z < 1e-7] < m1) & (y[z < 1e-7] > m0) & (y[z < 1e-7] < m1)]
    luft = rand[z > 1e-7]
    lam = np.full(mesh.t.shape[1], P["lam"])
    Rm, Rl = Randstueck(mesh, modul), Randstueck(mesh, luft)
    A_modul = Rm.laenge().sum()
    basis, u, it, _ = loesen(mesh, lam, konv=[(Rl, P["alpha"], P["T_l"])],
                             to_ambient=[(Rl, eps, P["T_umg"])], flux=[(Rm, P["Q"] / A_modul)], T0=70.0)
    T_kn = u[: mesh.p.shape[1]]
    Tl = Rl.fb.interpolate(u).value
    Q_konv = Rl.integral(P["alpha"] * (Tl - P["T_l"]))
    Q_str = Rl.integral(eps * SIGMA * ((Tl + K0) ** 4 - (P["T_umg"] + K0) ** 4))
    return dict(it=it, knoten=mesh.p.shape[1], T_max=T_kn.max(), T_min=T_kn.min(), A_modul=A_modul,
                T_modul_mittel=Rm.integral(Rm.fb.interpolate(u).value) / A_modul,
                Q_konv=Q_konv, Q_str=Q_str, A_luft=Rl.laenge().sum())


# ---------------------------------------------------------------------------------------------
# Übung 3: Erdkabel (Wärmeerzeugung im Leiter, feste Temperatur in der Tiefe, Seiten isoliert)
# ---------------------------------------------------------------------------------------------
KABEL = dict(breite=4.0, tiefe=3.0, lage=1.0, A_leiter=240e-6, r_iso=0.020, rho=2.82e-8, I=500.0,
             lam_leiter=230.0, lam_iso=0.3, alpha=10.0, T_l=20.0, T_tief=10.0)


def kabel(lam_boden, P=KABEL, h=0.1, h_kabel=0.0008):
    r_l = np.sqrt(P["A_leiter"] / np.pi)
    yc = -P["lage"]

    def bauen(occ):
        boden = occ.addRectangle(-P["breite"] / 2, -P["tiefe"], 0, P["breite"], P["tiefe"])
        iso = occ.addDisk(0, yc, 0, P["r_iso"], P["r_iso"])
        leiter = occ.addDisk(0, yc, 0, r_l, r_l)
        occ.fragment([(2, boden)], [(2, iso), (2, leiter)])
        occ.removeAllDuplicates()

    mesh = netz2d(bauen, h, verfeinern=[(lambda xy: np.hypot(xy[0], xy[1] - yc) < 0.03, h_kabel)])
    mitte = mesh.p[:, mesh.facets].mean(axis=1)
    rand = mesh.boundary_facets()
    ym = mitte[1, rand]
    oben, unten = rand[ym > -1e-6], rand[ym < -P["tiefe"] + 1e-6]
    zentren = mesh.p[:, mesh.t].mean(axis=1)
    rz = np.hypot(zentren[0], zentren[1] - yc)
    lam = np.where(rz < r_l, P["lam_leiter"], np.where(rz < P["r_iso"], P["lam_iso"], lam_boden))
    q3 = P["I"] ** 2 * P["rho"] / P["A_leiter"] ** 2
    quelle = np.where(rz < r_l, q3, 0.0)
    Ro, Ru = Randstueck(mesh, oben), Randstueck(mesh, unten)
    basis, u, it, _ = loesen(mesh, lam, konv=[(Ro, P["alpha"], P["T_l"])], dirichlet=[(Ru, P["T_tief"])],
                             quelle=quelle, T0=15.0)
    T_kn = u[: mesh.p.shape[1]]
    r_kn = np.hypot(mesh.p[0], mesh.p[1] - yc)
    flaeche = mesh.p[:, mesh.t]
    A_leiter_netz = 0.5 * np.abs((flaeche[0, 1] - flaeche[0, 0]) * (flaeche[1, 2] - flaeche[1, 0])
                                 - (flaeche[0, 2] - flaeche[0, 0]) * (flaeche[1, 1] - flaeche[1, 0]))[rz < r_l].sum()
    To = Ro.fb.interpolate(u).value
    return dict(it=it, knoten=mesh.p.shape[1], q3=q3, P_je_m=q3 * A_leiter_netz, T_max=T_kn.max(),
                T_iso_aussen=T_kn[np.abs(r_kn - P["r_iso"]) < 1e-6].max(),
                T_oberflaeche_max=To.max(), Q_oben=Ro.integral(P["alpha"] * (To - P["T_l"])))


def zeige(name, e, laenge=0.02):
    print(f"\n{name}  (Iterationen {e['it']}, Knoten {e['knoten']}, Zeilensummen F {e['F_summe'][0]:.4f} bis {e['F_summe'][1]:.4f})")
    print(f"  Absorber       {e['T_abs'][0]:8.2f} bis {e['T_abs'][1]:8.2f} °C")
    print(f"  Glas           {e['T_glas'][0]:8.2f} bis {e['T_glas'][1]:8.2f} °C, außen im Mittel {e['T_glas_aussen_mittel']:.2f} °C")
    for k in ("Q_sonne", "Q_nutz", "Q_abs_glas", "Q_luft", "Q_himmel", "bilanz"):
        print(f"  {k:12s} {e[k]:9.3f} W/m   = {e[k] * laenge:8.4f} W je {laenge * 1000:.0f} mm")


if __name__ == "__main__":
    was = sys.argv[1] if len(sys.argv) > 1 else "roehre"
    fein = "--fein" in sys.argv
    if was == "roehre":
        h, hb = (0.0005, 0.0000625) if fein else (0.001, 0.000125)
        zeige("a) selektiv, eps 0,05", roehre(0.05, h=h, h_blech=hb))
        zeige("b) schwarz, eps 0,9", roehre(0.9, h=h, h_blech=hb))
        zeige("c) Stillstand selektiv", roehre(0.05, alpha_w=0.0, h=h, h_blech=hb))
        zeige("   Stillstand schwarz", roehre(0.9, alpha_w=0.0, h=h, h_blech=hb))
    elif was == "rohr":
        h = 0.00025 if fein else 0.0005
        for name, kw in (("a) nur Konvektion", dict(strahlung=False)), ("b) Konvektion und Strahlung", {}),
                         ("c) gedämmt, 20 mm", dict(daemmung=True))):
            e = rohr(h=h, **kw)
            print(f"{name:30s} Oberfläche {e['T_aussen']:6.2f} °C  Q {e['Q']:7.3f} W/m  Konvektion {e['Q_konv']:7.3f}"
                  f"  Strahlung {e['Q_str']:7.3f}  Anteil Strahlung {e['anteil_str'] * 100:5.1f} %  (Knoten {e['knoten']})")
    elif was == "kuehlkoerper":
        h = 0.0015 if fein else 0.0025
        for name, eps in (("a) schwarz eloxiert", 0.85), ("b) blank", 0.05)):
            e = kuehlkoerper(eps, h=h)
            print(f"{name:20s} T_max {e['T_max']:7.2f} °C  Modulfläche Mittel {e['T_modul_mittel']:7.2f} °C  "
                  f"T_min {e['T_min']:7.2f} °C  Konvektion {e['Q_konv']:6.2f} W  Strahlung {e['Q_str']:6.2f} W  "
                  f"A_modul {e['A_modul'] * 1e4:.2f} cm²  (Knoten {e['knoten']}, Iterationen {e['it']})")
    elif was == "kabel":
        hk = 0.0004 if fein else 0.0008
        for name, lb in (("a) feuchter Boden, 1,0", 1.0), ("b) trockener Sand, 0,4", 0.4)):
            e = kabel(lb, h_kabel=hk)
            print(f"{name:24s} Leiter max {e['T_max']:7.2f} °C  Isolierung außen {e['T_iso_aussen']:6.2f} °C  "
                  f"Oberfläche max {e['T_oberflaeche_max']:6.2f} °C  q''' {e['q3']:9.0f} W/m³  P {e['P_je_m']:6.2f} W/m  "
                  f"Q oben {e['Q_oben']:6.2f} W/m  (Knoten {e['knoten']})")
