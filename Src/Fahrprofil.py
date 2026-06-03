import pandas as pd
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]


def _resolve_data_path(path):
    path = Path(path)
    if path.is_absolute():
        return path
    repo_candidate = _REPO_ROOT / path
    if repo_candidate.exists():
        return repo_candidate
    return _REPO_ROOT / "Data" / path


def _read_table_raw(path, header):
    suffix = Path(path).suffix.lower()
    if suffix in {".xlsx", ".xls", ".xlsm"}:
        return pd.read_excel(path, header=header)
    return pd.read_csv(path, delimiter=",", decimal=".", header=header)


def _read_table_auto(path):
    df = _read_table_raw(path, header=None)
    if df.empty:
        return df
    header_row = [str(x).strip().lower() for x in df.iloc[0].tolist()]
    known_headers = {"time_s", "speed_kph", "distance_m", "cum_distance_m", "cycle", "velocity_ms"}
    has_alpha = any(any(c.isalpha() for c in h) for h in header_row if h)
    if any(h in known_headers for h in header_row) or has_alpha:
        df = _read_table_raw(path, header=0)
    return df


def Datafield_range_to_elevation(path=r"Data\Fahrprofil 410315_6\inclination_410315_6.csv"):
    df = _read_table_auto(_resolve_data_path(path))
    if df.empty:
        return df

    lower_cols = {str(c).strip().lower() for c in df.columns}
    speed_markers = {"time_s", "speed_kph", "velocity_ms", "distance_m", "cum_distance_m", "cycle"}
    if lower_cols & speed_markers:
        raise ValueError(
            "Ausgewaehlte Datei sieht wie ein Fahrprofil aus. "
            "Bitte ein Hoehenprofil mit Strecke + Steigung waehlen."
        )

    if "strecke" in df.columns and "steigung_deg" in df.columns:
        elev = df[["strecke", "steigung_deg"]].copy()
    else:
        if df.shape[1] < 2:
            raise ValueError("Hoehenprofil muss mindestens zwei Spalten haben (Strecke, Steigung).")
        elev = df.iloc[:, :2].copy()
        elev.columns = ["strecke", "steigung_deg"]

    elev = elev.astype(float)
    elev.set_index("strecke", inplace=True)
    return elev


def load_speed_profile(path):
    df = _read_table_auto(_resolve_data_path(path))
    if df.empty:
        return df
    if "velocity_ms" in df.columns:
        v_ms = df["velocity_ms"].astype(float)
    elif "speed_kph" in df.columns:
        v_ms = df["speed_kph"].astype(float) / 3.6
    elif "v_kmh" in df.columns:
        v_ms = df["v_kmh"].astype(float) / 3.6
    else:
        first_col = df.columns[0]
        v_ms = df[first_col].astype(float)
    return v_ms.to_frame(name="velocity_ms")


def load_route_profile(path):
    """Load a combined route CSV (t_s, s_m, v_kmh, slope_rad) and return normalised DataFrame."""
    df = _read_table_raw(_resolve_data_path(path), header=0)
    if 'v_kmh' in df.columns:
        df['velocity_ms'] = df['v_kmh'].astype(float) / 3.6
    elif 'speed_kph' in df.columns:
        df['velocity_ms'] = df['speed_kph'].astype(float) / 3.6
    elif 'velocity_ms' not in df.columns:
        df['velocity_ms'] = df.iloc[:, 0].astype(float)
    return df


def Datafield_Speed_Vector(path=r"Data\Fahrprofil 410315_6\v_uni_matched_410315_6.csv"):
    return load_speed_profile(path)


def Datafield_validation(path=r"Data\Fahrprofil 410315_6\Valdierung_100kmh_1Stunde.csv"):
    Datafield = pd.read_csv(
        _resolve_data_path(path),
        delimiter=",",
        header=None,
        names=["velocity_ms"],
        decimal=".",
    )
    return Datafield


def load_Elevation_profile(path):
    """Load elevation profile and return elevation, dist_idx, angles."""
    range_elevation = Datafield_range_to_elevation(path)
    dist_idx = range_elevation.index.to_numpy(float)
    angles = range_elevation.iloc[:, 0].to_numpy(float)
    return range_elevation, dist_idx, angles


def Testfield_Speed_Vector(path=r"Data\SORT1_like_cycle.csv"):
    Datafield = pd.read_csv(
        _resolve_data_path(path),
        delimiter=",",
        header=0,
        decimal=".",
        usecols=["speed_kph"],
    )
    Datafield["velocity_ms"] = Datafield["speed_kph"] / 3.6
    return Datafield[["velocity_ms"]]

def Nebenverbauch(Jahreszeit):
    match (Jahreszeit):
        case 0:                 # Nebenverbrauch aus 
            return 0
        case 1:                 # Nebenverbrauch für Frühling
            return 10 / 3600
        case 2:                 # Nebenverbrauch für Sommer
            return 20 / 3600
        case 3:                 # Nebenverbrauch für Herbst
            return 15 / 3600
        case 4:                 # Nebenverbrauch für Winter
            return 20 / 3600
        case _:
            return 0 
            
            