# /// script
# requires-python = ">=3.10"
# dependencies = ["gmsh", "scikit-fem", "numpy"]
# ///
"""Sollwerte P3, Übung Vor- und Rücklauf: zwei Fernwärmerohre nebeneinander im Erdreich, unabhängig von ANSYS.

Aufruf:  uv run tools/sollwerte/p3_vor_ruecklauf.py

Rohre, Boden, Bodenblock und Modell wie im Vorzeigebeispiel (p3_fernwaermerohr.py): KMR DN 100 Serie 1, nur die
Dämmung modelliert (Stahlrohr und PE-Mantel weggelassen), Überdeckung 0,8 m, Erdreich λ 1,0 W/(m·K),
Oberfläche 10 °C, Block 6 m × 3 m mit adiabaten Seiten und Boden.
- Vorlauf 80 °C, Rücklauf 50 °C an der Innenseite der Dämmung
- Abstand der Mantelrohre 100 mm wie in den isoplus-Bezugsbedingungen (ISOPEX-Datenblatt; isoplus rechnet das
  Rohrpaar mit der Mitteltemperatur aus Vor- und Rücklauf). Logstor empfiehlt für Mantelrohre von 90 bis 225 mm
  150 mm (Handbuch Handhabung und Verlegung), zum Vergleich mitgerechnet. Die Achsen bleiben dort, wo die Rohre mit
  PE-Mantel (Ø 200 mm) liegen.

Aufgabenteile:
a) Vollmodell: Wärmeverlust Vorlauf, Rücklauf und zusammen in W/m. Gegenprobe Handrechnung nach EN 13941
   (Wallentén) mit der Rückwirkung R_m = ln(√(1 + (2H/E)²)) / (2π λ_E), E Achsabstand
b) Halbmodell mit Symmetrie in der Mitte (adiabat) und 80 °C: falsch, es rechnet zwei Vorläufe
c) zwei einzeln verlegte Rohre, linear aus dem Vorzeigebeispiel (Wärmestrom proportional zu T − T_Oberfläche)
d) Halbmodell mit der Mitteltemperatur 65 °C: trifft die Summe aus a), weil der antisymmetrische Anteil (±15 K)
   netto keinen Wärmeverlust hat
"""
import math

from p3_fernwaermerohr import H, LAM_ERDE, LAM_PUR, R2, R3, R4, T_OBERFLAECHE, fem, r_zylinder

T_VORLAUF, T_RUECKLAUF = 80.0, 50.0


def hand_paar(t1, t2, e):
    """Wärmeverlust beider Rohre in W/m nach EN 13941 (Wallentén), Boden mit ln(4H/D) für H >> D."""
    r_einzel = r_zylinder(R2, R3, LAM_PUR) + math.log(2 * H / R3) / (2 * math.pi * LAM_ERDE)
    r_m = math.log(math.sqrt(1 + (2 * H / e) ** 2)) / (2 * math.pi * LAM_ERDE)
    nenner = r_einzel**2 - r_m**2
    q1 = ((t1 - T_OBERFLAECHE) * r_einzel - (t2 - T_OBERFLAECHE) * r_m) / nenner
    q2 = ((t2 - T_OBERFLAECHE) * r_einzel - (t1 - T_OBERFLAECHE) * r_m) / nenner
    return q1, q2


if __name__ == "__main__":
    (q_einzel,), _ = fem()
    t_mittel = (T_VORLAUF + T_RUECKLAUF) / 2
    for abstand in (0.10, 0.15):
        e = 2 * R4 + abstand
        paar = dict(achsen=(-e / 2, e / 2), temperaturen=(T_VORLAUF, T_RUECKLAUF))
        print(f"\nAbstand der Mantelrohre {1000 * abstand:.0f} mm (Achsabstand {1000 * e:.0f} mm):")
        (qv, qr), n = fem(**paar)
        summe = qv + qr
        print(f" a) Vollmodell: Vorlauf {qv:.2f}, Rücklauf {qr:.2f}, zusammen {summe:.2f} W/m ({n} Elemente)")
        hv, hr = hand_paar(T_VORLAUF, T_RUECKLAUF, e)
        print(f"    Handrechnung EN 13941: Vorlauf {hv:.2f}, Rücklauf {hr:.2f}, zusammen {hv + hr:.2f} W/m"
              f" ({(hv + hr) / summe - 1:+.1%})")
        if abstand == 0.10:
            (bv, br), _ = fem(**paar, breite=10.0, tiefe=5.0)
            print(f"    Block 10 m x 5 m: zusammen {bv + br:.2f} W/m ({(bv + br) / summe - 1:+.1%})")
            (fv, fr), nf = fem(**paar, h0=0.001, k=0.03)
            print(f"    feiner vernetzt: zusammen {fv + fr:.2f} W/m ({nf} Elemente)")
        (qh,), nh = fem(achsen=(e / 2,), breite=3.0, xmin=0.0)
        print(f" b) Halbmodell 80 °C: {qh:.2f} W/m, doppelt {2 * qh:.2f} W/m ({2 * qh / summe - 1:+.1%}), {nh} Elemente")
        q_rl = q_einzel * (T_RUECKLAUF - T_OBERFLAECHE) / (T_VORLAUF - T_OBERFLAECHE)
        print(f" c) zwei Einzelrohre: {q_einzel:.2f} + {q_rl:.2f} = {q_einzel + q_rl:.2f} W/m,"
              f" das Paar verliert {1 - summe / (q_einzel + q_rl):.1%} weniger")
        (qm,), _ = fem(achsen=(e / 2,), temperaturen=(t_mittel,), breite=3.0, xmin=0.0)
        print(f" d) Halbmodell {t_mittel:.0f} °C: {qm:.2f} W/m, doppelt {2 * qm:.2f} W/m")
