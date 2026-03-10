from dataclasses import dataclass
from Elektromotor import MotorUebersetzung

# Technische Daten des MAN LION's City 10E Bus
# Länge 10.5 meter
# max sitzplätze: 33

@dataclass
class MAN_CityLion_10E:
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
def build_MAN_Lion10E() -> MAN_CityLion_10E:
    m_Fahrz = 12000
    m_zusatz = 50
    
    anzahl_passenger = 10
    m_passenger = 75 * anzahl_passenger
    m_ges = m_Fahrz + m_passenger + m_zusatz

    c_r = 0.012 # Standart annahmen
    cw = 0.7
    hoehe = 3.320
    breite = 2.550
    A = hoehe * breite
    RadDurchmesser = 1.1 #[m] Annahme Durchschnittlicher Durchmesser ziwschen 1 - 1.1m
    eta_Antrieb = 0.90  # Standart annahmen
    eta_reku = 0.7 # Standart annahmen
    E_Battrie = 356
    Energie_verbrauch = 0
    
    i = 1.595 * 5.12  # Gesamtübersetzung (Motorübersetzung * Achsübersetzung)
    
    return MAN_CityLion_10E(
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
