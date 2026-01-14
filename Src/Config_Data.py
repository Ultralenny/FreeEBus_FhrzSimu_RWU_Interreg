from dataclasses import dataclass
from Elektromotor import MotorUebersetzung

@dataclass
class Config:
    m_Fahrz: float
    m_zusatz: float
    anzahl_passenger: int
    m_passenger: float
    m_ges: float
    v_max: float
    n_max: float
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

def build_config() -> Config:
    m_Fahrz = 18000
    m_zusatz = 200
    anzahl_passenger = 20
    m_passenger = 80 * anzahl_passenger
    m_ges = m_Fahrz + m_passenger + m_zusatz

    v_max = 120 / 3.6
    n_max = 11000
    c_r = 0.006
    cw = 0.4
    hoehe = 2.96
    breite = 2.55
    A = hoehe * breite
    RadDurchmesser = 1.053
    eta_Antrieb = 0.90
    eta_reku = 0.7
    E_Battrie = 565
    Energie_verbrauch = 0
    
    i = MotorUebersetzung(v_max, n_max, RadDurchmesser)
       
    
    return Config(
        m_Fahrz,
        m_zusatz,
        anzahl_passenger,
        m_passenger,
        m_ges,
        v_max,
        n_max,
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
