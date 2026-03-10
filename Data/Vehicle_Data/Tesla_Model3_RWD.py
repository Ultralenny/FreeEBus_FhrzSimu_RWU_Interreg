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
    i: float


# Parameter-Set: Tesla Model 3 Standard / RWD (grobe Auslegung)
# Werte orientieren sich an veroeffentlichten Spezifikationen (Masse/Abmessungen/Top-Speed)
def build_config_tesla() -> Config:
    
    m_Fahrz = 1760.0    # Fahrzeugmasse (Leergewicht / curb mass)
    m_zusatz = 0.0      # zusaetzliche Masse (z.B. Gepaeck/Extras)

    anzahl_passenger = 1    
    m_passenger = 75.0 * anzahl_passenger
    m_ges = m_Fahrz + m_passenger + m_zusatz    # Gesamtmasse

    v_max = 201.0 / 3.6     # Höchstgeschwindigkeit [m/s]
    n_max = 18000.0 # maximale Drehzahl der E-Maschine in [1/min]

    c_r = 0.0101     # Rollwiderstandsbeiwert
    cw = 0.219 # Luftwiderstandsbeiwert 


    hoehe = 1.442   # Abmessungen (m)
    breite = 1.848
    A = 0.905 * hoehe * breite # Stirnflaeche [m^2]
    RadDurchmesser = 0.6687     # Raddurchmesser [m] basierend auf 235/45R18: ca. 668.7 mm
    eta_Antrieb = 0.93  # Wirkungsgrade
    eta_reku = 0.70
    E_Battrie = 57.0 # Batterieenergie [kWh]
    Energie_verbrauch = 0.0

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
        i,
    )
