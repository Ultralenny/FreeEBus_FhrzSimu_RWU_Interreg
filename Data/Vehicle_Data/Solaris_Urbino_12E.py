from dataclasses import dataclass
from Elektromotor import MotorUebersetzung


@dataclass
class Solaris_Urbino_12E:
    m_Fahrz: float
    m_zusatz: float
    anzahl_passenger: int
    m_passenger: float
    m_ges: float
    c_r: float
    cw: float
    hoehe: float
    breite: float
    A: float
    RadDurchmesser: float
    eta_Antrieb: float
    eta_reku: float
    E_Battrie: float
    Energie_verbrauch: float
    i: float


# Fahrzeugdaten für Solaris Urbino 12 electric (modular drive) (Batterie 600 kWh; Abmessungen 12.000 x 2.550 x 3.250 m; GVW 19.500 kg; Fahrgastkapazität bis 100). m_Fahrz hier als grobe Abschätzung aus GVW - (75 kg * max. Fahrgäste).
def build_Solaris_Urbino_12E() -> Solaris_Urbino_12E:
    m_Fahrz = 12000
    m_zusatz = 0
    anzahl_passenger = 100
    m_passenger = 75 * anzahl_passenger
    m_ges = m_Fahrz + m_passenger + m_zusatz

    c_r = 0.012
    cw = 0.7
    hoehe = 3.25
    breite = 2.55
    A = hoehe * breite
    RadDurchmesser = 1.0
    eta_Antrieb = 0.9
    eta_reku = 0.7
    E_Battrie = 600
    Energie_verbrauch = 0
    i = 8.56 # Gesamt übersetzung (Antriebübersetzung * Achsübersetzung)

    return Solaris_Urbino_12E(
        m_Fahrz,
        m_zusatz,
        anzahl_passenger,
        m_passenger,
        m_ges,
        c_r,
        cw,
        hoehe,
        breite,
        A,
        RadDurchmesser,
        eta_Antrieb,
        eta_reku,
        E_Battrie,
        Energie_verbrauch,
        i
    )
