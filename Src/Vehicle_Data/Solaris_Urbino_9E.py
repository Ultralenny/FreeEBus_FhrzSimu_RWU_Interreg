from dataclasses import dataclass
from Elektromotor import MotorUebersetzung


@dataclass
class Solaris_Urbino_9E:
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


# Fahrzeugdaten für Solaris Urbino 9 LE electric (Batterie bis 350 kWh; Abmessungen 9.270 x 2.450 x 3.300 m; GVW 16 t; Fahrgastkapazität bis 73). m_Fahrz hier als grobe Abschätzung aus GVW - (75 kg * max. Fahrgäste).
def build_Solaris_Urbino_9E() -> Solaris_Urbino_9E:
    m_Fahrz = 10525
    m_zusatz = 0
    anzahl_passenger = 73
    m_passenger = 75 * anzahl_passenger
    m_ges = m_Fahrz + m_passenger + m_zusatz

    c_r = 0.012
    cw = 0.7
    hoehe = 3.3
    breite = 2.45
    A = hoehe * breite
    RadDurchmesser = 1.0
    eta_Antrieb = 0.9
    eta_reku = 0.7
    E_Battrie = 350
    Energie_verbrauch = 0
    i = 8.56 # Gesamt übersetzung (Antriebübersetzung * Achsübersetzung)

    return Solaris_Urbino_9E(
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
