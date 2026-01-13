import math

# Gravitationskonstante (Erdbeschleunigung)
G = 9.81  # m/s²
# Standard-Luftdichte auf Meereshöhe (ca.)
RHO_LUFT = 1.225  # kg/m³


def rollwiderstand(masse_kg: float, c_r: float, g: float = G) -> float:
    return c_r * masse_kg * g


def luftwiderstand(
    v_m_s: float, cw: float, stirnflaeche_m2: float, rho: float = RHO_LUFT
) -> float:
    return 0.5 * rho * cw * stirnflaeche_m2 * v_m_s**2


def steigungswiderstand(masse_kg: float, alpha_Grad: float, g: float = G) -> float:
    alpha_rad = math.radians(alpha_Grad)
    return masse_kg * g * math.sin(alpha_rad)


def beschleunigungswiderstand(
    masse_Fahrzeug_kg: float,
    beschleunigung_m_s2: float,
    massenfaktor: float = 1.07,
) -> float:
    m_eff = massenfaktor * masse_Fahrzeug_kg
    return m_eff * beschleunigung_m_s2


def kurvenwiderstand(
    masse_kg: float,
    v_m_s: float,
    kurvenradius_m: float,
    widerstandsbeiwert: float = 0.01,
) -> float:
    a_q = v_m_s**2 / kurvenradius_m
    return widerstandsbeiwert * masse_kg * a_q


def gesamtfahrwiderstand(*kraefte_neu: float) -> float:
    return sum(kraefte_neu)
