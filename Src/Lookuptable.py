import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator


def GenLookupTable(path_T, path_n, path_Z):
    # Dateien einlesen
    T = pd.read_csv(path_T, header=None).values.flatten()
    n = pd.read_csv(path_n, header=None).values.flatten()
    Z = pd.read_csv(path_Z, header=None).values

    # Shape prüfen
    if Z.shape != (len(T), len(n)):
        raise ValueError(f"Matrix passt nicht! Z={Z.shape}, T={len(T)}, n={len(n)}")

    # DataFrame erzeugen
    lookup = pd.DataFrame(Z, index=T, columns=n)

    # Werte kommen als Prozentangaben (z.B. 85 = 85 %); in Faktoren umwandeln
    lookup = lookup / 100.0

    print("Lookuptabelle erfolgreich gebaut!")
    return lookup


#
########################################################################


def make_eta_interpolator(lookup):
    """
    Erzeugt eine Interpolationsfunktion eta(trq, rpm) aus der Lookup-Tabelle.
    Gibt eine Funktion zurück, die Skalar oder Arrays annimmt.
    """
    torque = lookup.index.values
    rpm = lookup.columns.values
    eta = lookup.values

    interpolator = RegularGridInterpolator(
        (torque, rpm), eta, bounds_error=False, fill_value=None
    )

    def eta_func(trq, n=None):
        """
        Unterstützt Aufruf als eta(trq, n) oder eta([(trq, n), ...]).
        """
        if n is None:
            pts = np.atleast_2d(trq)  # erwartet (N, 2) oder (2,)
            if pts.shape[1] != 2:
                raise ValueError("Punkte müssen Form (N, 2) haben")
        else:
            trq_arr = np.atleast_1d(trq)
            rpm_arr = np.atleast_1d(n)
            pts = np.column_stack([trq_arr, rpm_arr])
        vals = interpolator(pts)
        vals = np.clip(vals, 0.1, 1.0)  # numerische Robustheit an den Tabellenrändern
        # Skalar zurückgeben, wenn nur ein Punkt angefragt wurde
        if vals.shape == (1,):
            return float(vals[0])
        return vals

    return eta_func


########################################################################


def load_default_eta() -> Tuple[pd.DataFrame, Callable]:
    """
    Baut die Lookup-Tabelle aus den Standarddateien und liefert (lookup_df, eta_interp).
    """
    base_dir = Path(__file__).resolve().parent[1] / "Lookuptable" / "Ltb_Bus"
    path_T = base_dir / "wirk_T.csv"
    path_n = base_dir / "wirk_n.csv"
    path_Z = base_dir / "wirk_Z.csv"

    lookup = GenLookupTable(path_T, path_n, path_Z)
    eta_interp = make_eta_interpolator(lookup)
    return lookup, eta_interp
