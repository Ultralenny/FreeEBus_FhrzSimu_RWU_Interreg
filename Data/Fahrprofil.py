import pandas as pd


def Datafield_range_to_elevation():
    Datafield = pd.read_csv(
        r"C:\Users\Leonard Schmitz\Documents\VisualStudio\FreeEBus_RWU.venv\Leo\Fahrprofil 410315_6\inclination_410315_6.csv.csv",
        delimiter=",",
        header=None,
        decimal=".",
        names=["strecke", "steigung_deg"],
    )
    Datafield.set_index("strecke", inplace=True)
    return Datafield


def Datafield_Speed_Vector():
    Datafield = pd.read_csv(
        r"C:\Users\Leonard Schmitz\Documents\VisualStudio\FreeEBus_RWU.venv\Leo\Fahrprofil 410315_6\v_uni_matched_410315_6.csv.csv",
        delimiter=",",
        header=None,
        names=["velocity_ms"],
        decimal=".",
    )
    return Datafield


def Datafield_validation():
    Datafield = pd.read_csv(
        r"C:\Users\Leonard Schmitz\Documents\VisualStudio\FreeEBus_RWU.venv\Leo\Fahrprofil 410315_6\Valdierung_80kmh_1Stunde.csv",
        delimiter=",",
        header=None,
        names=["velocity_ms"],
        decimal=".",
    )
    return Datafield

def load_profile_data():
    """Lädt Höhen- und Geschwindigkeitsprofil und bereitet Index/Angle vor."""
    range_elevation = Datafield_range_to_elevation()
    dist_idx = range_elevation.index.to_numpy(float)
    angles = range_elevation.iloc[:, 0].to_numpy(float)
    speed_vector = Datafield_Speed_Vector()
    return range_elevation, dist_idx, angles, speed_vector
