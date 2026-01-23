from dataclasses import dataclass
from Elektromotor import MotorUebersetzung


@dataclass
class MAN_Lions_City_12e:
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


# Fahrzeugdaten für MAN Lion’s City 12 E (z.B. Batterie bis 480 kWh; Abmessungen 12.200 x 2.550 x 3.320 m; Fahrgastkapazität 45).
def build_MAN_Lions_City_12e() -> MAN_Lions_City_12e:
    m_Fahrz = 0
    m_zusatz = 0
    anzahl_passenger = 45
    m_passenger = 75 * anzahl_passenger
    m_ges = m_Fahrz + m_passenger + m_zusatz

    c_r = 0.012
    cw = 0.7
    hoehe = 3.32
    breite = 2.55
    A = hoehe * breite
    RadDurchmesser = 1.0
    eta_Antrieb = 0.9
    eta_reku = 0.7
    E_Battrie = 480
    Energie_verbrauch = 0
    i = 8.56 # Gesamt übersetzung (Antriebübersetzung * Achsübersetzung)

    return MAN_Lions_City_12e(
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
