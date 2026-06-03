from dataclasses import dataclass
from Elektromotor import MotorUebersetzung

@dataclass
class Mercedes_Actros:
    m_Fahrz: float
        
    m_Zuladung: float
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
def build_Mercedes_Actros() -> Volvo_7900E:
    m_Fahrz = 22000
   
    m_Zuladung = 10000
    m_Ges = min(44000,m_Fahrz + m_Zuladung)
    
    c_r = 0.012
    cw = 0.7
    hoehe = 3
    breite = 3
    A = hoehe * breite
    RadDurchmesser = 1.053
    eta_Antrieb = 0.90
    eta_reku = 0.7
    E_Battrie = 400
    Energie_verbrauch = 0
    
    v_max = 90 / 3.6
    n_max = 11000
    i = MotorUebersetzung(v_max, n_max, RadDurchmesser)
       
    
    return Mercedes_Actros(
        m_Fahrz,
        m_Zuladung,
        m_Ges,
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
