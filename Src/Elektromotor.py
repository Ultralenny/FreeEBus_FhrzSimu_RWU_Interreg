def Fahrleistung(FahrRes: float, FahrSpeed: float, eta: float):
    return round((FahrRes * FahrSpeed) / eta, 2)


def RadDrehzahl(Fahrspeed: float, RadDurchmesser: float):
    return (
        (Fahrspeed * 60) / (3.1415 * RadDurchmesser)
    ) * 0.96  # 0.96 wegen Reifenschlupf


def MotorUebersetzung(MaxSpeed: float, MaxDrehzahl: float, RadDruchmesser: float):
    return MaxDrehzahl / RadDrehzahl(MaxSpeed, RadDruchmesser)


def MotorDrehzahl(RadDrehzahl: float, i_Übersetzung: float):
    return RadDrehzahl * i_Übersetzung


def Radmoment(Radkraft: float, RadDurchmesser: float):
    return Radkraft * (RadDurchmesser * 0.5)


def Motormoment(Radmoment: float, eta_Antrieb: float, i: float):
    return Radmoment / (i * eta_Antrieb)


def Reichweite(ElektrischeLeistung: int, BatterieEnergie: int, Geschwindigkeit: float):
    Fahrdauer = BatterieEnergie / ElektrischeLeistung
    return Fahrdauer * Geschwindigkeit


def Rekuperation(MasseFahrzeug, Speed_X, Speed_Y, a_verzögerung):
    Speed_delta = Speed_X - Speed_Y

    E_kinetisch = 0.5 * MasseFahrzeug * Speed_delta * Speed_delta
    E_reku = E_kinetisch * 0.7

    t_verzögerung = Speed_delta / a_verzögerung

    Brems_Leistung = E_reku / t_verzögerung

    return Brems_Leistung


def Disc_Bremsleistung(ClampingForce, mü_o, r_eff, r_dyn):
    F_disc = 2 * ClampingForce * mü_o

    F_Brems_XT = (F_disc * r_eff) / r_dyn
    return round(F_Brems_XT, 2)


def Mech_Bremsleistung(Max_Bremsleistung, Reku_Bremsleistung):
    # Maximale Bremsleistung = Mech_Bremsleistung + Reku_Bremsleistung
    Mech_Bremsleistung = Max_Bremsleistung - Reku_Bremsleistung

    return round(Mech_Bremsleistung, 2)


def Bremse():
    Rekuperation()
    Disc_Bremsleistung()
    Mech_Bremsleistung()
    return
