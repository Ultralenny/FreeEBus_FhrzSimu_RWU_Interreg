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
    # Fahrzeugmasse (Leergewicht / curb mass)
    m_Fahrz = 1760.0

    # zusaetzliche Masse (z.B. Gepaeck/Extras)
    m_zusatz = 0.0

    # Insassen
    anzahl_passenger = 1
    m_passenger = 75.0 * anzahl_passenger

    # Gesamtmasse
    m_ges = m_Fahrz + m_passenger + m_zusatz

    # v_max: 201 km/h
    v_max = 201.0 / 3.6

    # n_max (Schaetzwert fuer Tesla Model 3 Drive Unit)
    n_max = 18000.0

    # Rollwiderstandsbeiwert (typisch fuer Pkw mit effizienten Reifen)
    c_r = 0.0101

    # Luftwiderstandsbeiwert (Model 3 Highland: Cd ~ 0.219)
    cw = 0.219

    # Abmessungen (m)
    hoehe = 1.442
    breite = 1.848

    # Stirnflaeche (m^2) - publizierter/haeufig genutzter Wert fuer Model 3
    A = 0.905 * hoehe * breite

    # Raddurchmesser (m) basierend auf 235/45R18: ca. 668.7 mm
    RadDurchmesser = 0.6687

    # Wirkungsgrade
    eta_Antrieb = 0.93
    eta_reku = 0.70

    # Batterieenergie (kWh) - nutzbare Kapazitaet (Model 3 RWD)
    E_Battrie = 57.0

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
