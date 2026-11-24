#!/usr/bin/env python3
"""Rechenbeispiele der Seite P2 Grundlagen „Konvektion“: Wärmeübergangskoeffizienten aus den Formeln von Çengel 2002.

Aufruf:  python3 tools/sollwerte/p2_konvektion.py

Quellen: Çengel, Heat Transfer. A Practical Approach, 2. Aufl. 2002 (Tab. 9-1 S. 468, Tab. 15-1 S. 815,
Gl. 7-21/7-22/7-24 S. 374, Gl. 7-35 S. 385, Gl. 8-59/8-61 S. 436, Gl. 8-65/8-68/8-70 S. 441).
Stoffwerte Luft: Çengel Tab. A-15, wie in den Rechenbeispielen des Buchs zitiert (Seite in LUFT);
Stoffwerte Wasser: NIST Chemistry WebBook, siedendes Wasser (Sättigung).
"""
import math

G = 9.81
# T in °C: (Wärmeleitfähigkeit W/(m K), kinematische Viskosität m²/s, Prandtl-Zahl, Buchseite)
LUFT = {7: (0.02416, 1.399e-5, 0.7344, 482), 25: (0.02551, 1.562e-5, 0.7296, 388), 45: (0.02699, 1.749e-5, 0.7241, 470),
        60: (0.02808, 1.896e-5, 0.7202, 387), 80: (0.02953, 2.097e-5, 0.7154, 377)}
WASSER = {10: (0.5787, 1.3061e-6, 9.465), 20: (0.5980, 1.0032e-6, 7.007), 30: (0.6143, 0.8006e-6, 5.423),
          40: (0.6284, 0.6577e-6, 4.340), 50: (0.6406, 0.5531e-6, 3.567), 60: (0.6510, 0.4739e-6, 2.996),
          70: (0.6597, 0.4127e-6, 2.563), 80: (0.6670, 0.3643e-6, 2.227)}


def stoffwerte(tabelle, T):
    """Lineare Interpolation (λ, ν, Pr) zwischen den Tabellenpunkten."""
    ts = sorted(tabelle)
    if not ts[0] <= T <= ts[-1]:
        raise ValueError(f"{T} °C außerhalb der Tabelle {ts[0]} bis {ts[-1]} °C")
    for a, b in zip(ts, ts[1:]):
        if a <= T <= b:
            s = (T - a) / (b - a)
            return tuple(tabelle[a][i] + s * (tabelle[b][i] - tabelle[a][i]) for i in range(3))
    return tabelle[ts[-1]][:3]


def rayleigh(T_O, T_F, L, tabelle=LUFT):
    """Ra = g β ΔT L³ / ν² · Pr mit Stoffwerten bei der Filmtemperatur, β = 1/T_f (ideales Gas)."""
    Tf = (T_O + T_F) / 2
    lam, nu, Pr = stoffwerte(tabelle, Tf)
    beta = 1 / (Tf + 273.15)
    return G * beta * abs(T_O - T_F) * L ** 3 / nu ** 2 * Pr, lam, Pr


def churchill_chu_zylinder(Ra, Pr):          # Tab. 9-1, Gl. 9-25, Ra ≤ 1e12
    return (0.6 + 0.387 * Ra ** (1 / 6) / (1 + (0.559 / Pr) ** (9 / 16)) ** (8 / 27)) ** 2


def churchill_chu_wand(Ra, Pr):              # Tab. 9-1, Gl. 9-21, gesamter Bereich
    return (0.825 + 0.387 * Ra ** (1 / 6) / (1 + (0.492 / Pr) ** (9 / 16)) ** (8 / 27)) ** 2


def gnielinski(Re, Pr):                      # Gl. 8-70 mit f nach Gl. 8-65, 3e3 < Re < 5e6, 0,5 ≤ Pr ≤ 2000
    f = (0.790 * math.log(Re) - 1.64) ** -2
    return (f / 8) * (Re - 1000) * Pr / (1 + 12.7 * (f / 8) ** 0.5 * (Pr ** (2 / 3) - 1))


def dittus_boelter(Re, Pr, n):               # Gl. 8-68, n = 0,4 Erwärmen, 0,3 Abkühlen des Fluids
    return 0.023 * Re ** 0.8 * Pr ** n


def platte_oben(Ra, Pr):                     # Tab. 9-1, warme Seite oben, L = A/p
    return 0.54 * Ra ** 0.25 if Ra < 1e7 else 0.15 * Ra ** (1 / 3)


def platte_unten(Ra, Pr):                    # Tab. 9-1, warme Seite unten, L = A/p
    return 0.27 * Ra ** 0.25


def platte_laengs(Re, Pr):                   # Gl. 7-21 laminar (Re < 5e5), sonst Gl. 7-24 vorn laminar, hinten turbulent
    return 0.664 * Re ** 0.5 * Pr ** (1 / 3) if Re < 5e5 else (0.037 * Re ** 0.8 - 871) * Pr ** (1 / 3)


def churchill_bernstein(Re, Pr):             # Gl. 7-35, Rohr quer angeströmt, Re · Pr > 0,2
    return 0.3 + 0.62 * Re ** 0.5 * Pr ** (1 / 3) / (1 + (0.4 / Pr) ** (2 / 3)) ** 0.25 \
        * (1 + (Re / 282000) ** (5 / 8)) ** 0.8


# Runde Werte für Luft um 25 °C, wie in den Fallkarten der Seite: Ra ≈ 1e8 · ΔT · L³, Re ≈ 6,4e4 · v · L
RUND = dict(lam=0.026, Pr=0.73, ra=1e8, re=6.4e4)


def ra_faktor(T):
    """g β Pr / ν² für Luft bei der Filmtemperatur T in °C, damit Ra = Faktor · ΔT · L³ (ΔT in K, L in m)."""
    lam, nu, Pr = stoffwerte(LUFT, T)
    return G / (T + 273.15) * Pr / nu ** 2


def frei(nu_fkt, L, dT, T, rund):
    """α in ruhender Luft, genau bei der Filmtemperatur T oder mit den runden Werten der Karten."""
    if rund:
        lam, Pr, Ra = RUND["lam"], RUND["Pr"], RUND["ra"] * dT * L ** 3
    else:
        lam, nu, Pr = stoffwerte(LUFT, T)
        Ra = ra_faktor(T) * dT * L ** 3
    return nu_fkt(Ra, Pr) * lam / L


def wind(nu_fkt, L, v, T, rund):
    """α im Wind, genau bei der Filmtemperatur T oder mit den runden Werten der Karten."""
    if rund:
        lam, Pr, Re = RUND["lam"], RUND["Pr"], RUND["re"] * v * L
    else:
        lam, nu, Pr = stoffwerte(LUFT, T)
        Re = v * L / nu
    return nu_fkt(Re, Pr) * lam / L


if __name__ == "__main__":
    # Heizungsrohr (P2 Übung 1): Rohr außen 26,9 mm, Oberfläche 59,3 °C (ANSYS), Kellerluft 15 °C
    D, T_O, T_F = 0.0269, 59.3, 15.0
    ueberschlag = 1.32 * ((T_O - T_F) / D) ** 0.25                    # Tab. 15-1, waagerechter Zylinder
    Ra, lam, Pr = rayleigh(T_O, T_F, D)
    Nu = churchill_chu_zylinder(Ra, Pr)
    print(f"Heizungsrohr, freie Konvektion: Überschlag α = {ueberschlag:.2f}, Ra = {Ra:.3g}, "
          f"Churchill-Chu Nu = {Nu:.3f}, α = {Nu * lam / D:.2f} W/(m²K)")

    # Wasser im Heizungsrohr: innen 21,7 mm, 60 °C, angenommen 0,5 m/s
    Di, v = 0.0217, 0.5
    lam, nu, Pr = stoffwerte(WASSER, 60)
    Re = v * Di / nu
    print(f"Wasser im Rohr: Re = {Re:.0f}, Gnielinski α = {gnielinski(Re, Pr) * lam / Di:.0f}, "
          f"Dittus-Boelter (Abkühlen) α = {dittus_boelter(Re, Pr, 0.3) * lam / Di:.0f} W/(m²K)")

    # Innenwand eines Raums: Höhe 2,5 m, Wand 17 °C, Raumluft 20 °C
    L, T_O, T_F = 2.5, 17.0, 20.0
    Ra, lam, Pr = rayleigh(T_O, T_F, L)
    print(f"Raumwand 2,5 m, ΔT 3 K: Ra = {Ra:.3g} (turbulent ab 1e9), Churchill-Chu α = "
          f"{churchill_chu_wand(Ra, Pr) * lam / L:.2f} W/(m²K), Überschlag (laminar, hier nicht gültig) "
          f"{1.42 * (abs(T_O - T_F) / L) ** 0.25:.2f}")

    # Überschlag Platte im Wind (laminar, Luft): Gl. 7-21 ausgeschrieben, α = 0,664 λ Pr^(1/3) / √ν · √(v/L)
    k = {T: 0.664 * lam * Pr ** (1 / 3) / nu ** 0.5 for T, (lam, nu, Pr, _) in LUFT.items()}
    print("Platte im Wind, laminar, Luft: α = k · √(v/L) mit k = " + ", ".join(f"{k[T]:.2f} ({T} °C)" for T in sorted(k))
          + f"; laminar bis v · L = 5e5 · ν = {5e5 * LUFT[7][1]:.1f} m²/s (7 °C)")

    # Faktor für Ra in Luft (Zeile der Stoffwerttabelle) und Prüfung der runden Werte in den Fallkarten
    print("Ra-Faktor g β Pr / ν² in 1e8 1/(K m³): " + ", ".join(f"{ra_faktor(T) / 1e8:.2f} ({T} °C)" for T in sorted(LUFT))
          + f"; 1/ν bei 25 °C {1 / LUFT[25][1]:.0f} s/m²")
    lam, nu, Pr = stoffwerte(WASSER, 60)
    print(f"Wasser 60 °C: λ = {lam:.3f} W/(m K), Pr = {Pr:.2f}, 1/ν = {1 / nu:.3g} s/m²")
    faelle = {
        "Wand 2,5 m, ΔT 3 K": lambda T, r: frei(churchill_chu_wand, 2.5, 3, T, r),
        "Wand 0,5 m, ΔT 20 K": lambda T, r: frei(churchill_chu_wand, 0.5, 20, T, r),
        "Rohr Ø 26,9 mm, ΔT 44 K": lambda T, r: frei(churchill_chu_zylinder, 0.0269, 44, T, r),
        "Rohr Ø 100 mm, ΔT 20 K": lambda T, r: frei(churchill_chu_zylinder, 0.1, 20, T, r),
        "Platte oben A/p 0,1 m, ΔT 20 K": lambda T, r: frei(platte_oben, 0.1, 20, T, r),
        "Platte oben A/p 0,5 m, ΔT 20 K": lambda T, r: frei(platte_oben, 0.5, 20, T, r),
        "Platte unten A/p 0,25 m, ΔT 20 K": lambda T, r: frei(platte_unten, 0.25, 20, T, r),
        "Platte 1 m im Wind 3 m/s": lambda T, r: wind(platte_laengs, 1.0, 3, T, r),
        "Platte 5 m im Wind 5 m/s": lambda T, r: wind(platte_laengs, 5.0, 5, T, r),
        "Rohr Ø 50 mm im Wind 3 m/s": lambda T, r: wind(churchill_bernstein, 0.05, 3, T, r),
        "Vakuumröhre Ø 70 mm im Wind 1 m/s": lambda T, r: wind(churchill_bernstein, 0.07, 1, T, r),
    }
    for name, f in faelle.items():
        abw = [f(T, True) / f(T, False) - 1 for T in range(7, 46)]
        print(f"Runde Werte, {name}: α = {f(25, True):.2f} W/(m²K) (genau bei 25 °C {f(25, False):.2f}), "
              f"Abweichung bei 7 bis 45 °C Filmtemperatur {min(abw):+.1%} bis {max(abw):+.1%}")
    T_f = (59.3 + 15.0) / 2                                     # Heizungsrohr: runde Werte gegen Stoffwerte bei 37 °C
    print(f"Heizungsrohr mit runden Werten: Ra = {RUND['ra'] * 44.3 * 0.0269 ** 3:.3g}, α = "
          f"{frei(churchill_chu_zylinder, 0.0269, 44.3, T_f, True):.2f}; genau bei {T_f:.1f} °C: Ra = "
          f"{ra_faktor(T_f) * 44.3 * 0.0269 ** 3:.3g}, α = {frei(churchill_chu_zylinder, 0.0269, 44.3, T_f, False):.2f} W/(m²K)")

    # Bauphysik: konvektiver Anteil innen nach DIN EN ISO 6946
    h_r = 0.9 * 4 * 5.67e-8 * 293.15 ** 3
    print(f"Strahlungsanteil innen bei ε 0,9 und 20 °C: {h_r:.2f} W/(m²K); 1/0,13 = {1 / 0.13:.2f} W/(m²K)")
