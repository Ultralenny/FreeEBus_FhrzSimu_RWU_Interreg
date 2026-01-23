from dataclasses import dataclass
from Elektromotor import MotorUebersetzung




@dataclass
class Your_VehicleName:
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
    i : float
    


# Diese Daten entsprechen dem Volvo 7900 Electric Bus
def build_Your_VehicleName() -> Your_VehicleName:
    m_Fahrz = 0
    m_zusatz = 0
    anzahl_passenger = 0
    m_passenger = 75 * anzahl_passenger
    m_ges = m_Fahrz + m_passenger + m_zusatz
    
    c_r = 0.012
    cw = 0.7
    hoehe = 0
    breite = 0
    A = hoehe * breite
    RadDurchmesser = 1.
    eta_Antrieb = 0.90
    eta_reku = 0.7
    E_Battrie = 0
    Energie_verbrauch = 0
    i = 8.56 # Gesamt übersetzung (Antriebübersetzung * Achsübersetzung)
    
    return Your_VehicleName(
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
