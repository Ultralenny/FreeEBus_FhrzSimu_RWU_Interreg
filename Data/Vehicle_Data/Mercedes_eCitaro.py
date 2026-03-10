from dataclasses import dataclass
from Elektromotor import MotorUebersetzung


@dataclass
class Mercedes_eCitaro:
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


# Fahrzeugdaten für Mercedes-Benz eCitaro (Länge 12.135 m; Breite 2.550 m; Höhe 3.400 m; Leergewicht ca. 14 t; max. Batteriekapazität 666 kWh).
def build_Mercedes_eCitaro() -> Mercedes_eCitaro:
    m_Fahrz = 14000
    m_zusatz = 0
    anzahl_passenger = 88
    m_passenger = 75 * anzahl_passenger
    m_ges = m_Fahrz + m_passenger + m_zusatz

    c_r = 0.012
    cw = 0.7
    hoehe = 3.4
    breite = 2.55
    A = hoehe * breite
    RadDurchmesser = 1.0
    eta_Antrieb = 0.9
    eta_reku = 0.7
    E_Battrie = 666
    Energie_verbrauch = 0
    i = 8.56 # Gesamt übersetzung (Antriebübersetzung * Achsübersetzung)

    return Mercedes_eCitaro(
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
