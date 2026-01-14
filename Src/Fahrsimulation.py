import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Callable, Tuple

from Config_Data import Config
from FahrRes import (
    rollwiderstand,
    luftwiderstand,
    steigungswiderstand,
    beschleunigungswiderstand,
    gesamtfahrwiderstand,
)
from Fahrprofil import Datafield_range_to_elevation, Datafield_Speed_Vector
from Lookuptable import GenLookupTable, make_eta_interpolator
from Elektromotor import RadDrehzahl, MotorDrehzahl, Radmoment, Motormoment


@dataclass
class SimulationResult:
    t_axis: list
    F_roll: list
    F_luft: list
    F_steig: list
    F_beschl: list
    F_ges: list
    steigung: list
    drehmoment: list
    soc: list
    energie_verbrauch: float


def load_eta_interpolator(path_T: str, path_n: str, path_Z: str) -> Callable:
    """Laedt die Lookup-Tabelle und gibt den Interpolator zurueck."""
    em_lookup = GenLookupTable(path_T, path_n, path_Z)
    return make_eta_interpolator(em_lookup)


def load_profile():
    """Laedt Hoehen- und Geschwindigkeitsprofil."""
    range_elevation = Datafield_range_to_elevation()
    dist_idx = range_elevation.index.to_numpy(float)
    angles = range_elevation.iloc[:, 0].to_numpy(float)
    speed_vector = Datafield_Speed_Vector()
    return range_elevation, speed_vector, dist_idx, angles


def init_state():
    """Initialisiert alle Listen fuer die Simulation."""
    return {
        "t_axis": [],
        "F_roll": [],
        "F_luft": [],
        "F_steig": [],
        "F_beschl": [],
        "F_ges": [],
        "steigung": [],
        "drehmoment": [],
        "soc": [],
    }


def compute_resistances(
    cfg: Config, velocity: float, acceleration: float, steigung_grad: float
) -> Tuple[float, float, float, float, float]:
    F_roll = rollwiderstand(cfg.m_ges, cfg.c_r)
    F_luft = luftwiderstand(velocity, cfg.cw, cfg.A)
    F_steig = steigungswiderstand(cfg.m_ges, steigung_grad)
    F_beschl = beschleunigungswiderstand(
        cfg.m_Fahrz, acceleration, massenfaktor=1.05
    )
    F_ges = gesamtfahrwiderstand(F_roll, F_luft, F_steig, F_beschl)
    return F_roll, F_luft, F_steig, F_beschl, F_ges


def drivetrain(cfg: Config, F_ges: float, velocity: float, gear_ratio: float):
    n_rad = RadDrehzahl(velocity, cfg.RadDurchmesser)
    n_motor = MotorDrehzahl(n_rad, gear_ratio)
    trq_rad = Radmoment(F_ges, cfg.RadDurchmesser)
    trq_motor = Motormoment(trq_rad, cfg.eta_Antrieb, gear_ratio)
    return n_rad, n_motor, trq_rad, trq_motor


def update_energy(
    cfg: Config,
    F_ges: float,
    velocity: float,
    eta_Ltb: float,
    energie_verbrauch: float,
    dt: float,
) -> Tuple[float, float]:
    """Aktualisiert Batterieverbrauch und SOC."""
    P_mech = F_ges * velocity  # W, kann negativ sein
    eta_safe = max(eta_Ltb, 1e-3)  # vor Division durch 0 schuetzen

    if P_mech >= 0:
        P_batt_kW = (P_mech / eta_safe) / 1000.0
    else:
        P_batt_kW = (P_mech * cfg.eta_reku) / 1000.0

    energie_verbrauch = min(
        cfg.E_Battrie,
        max(0.0, energie_verbrauch  P_batt_kW * (dt / 3600.0)),
    )

    soc = 100.0 * (1.0 - energie_verbrauch / cfg.E_Battrie)
    soc = max(0.0, min(100.0, soc))
    return energie_verbrauch, soc


def simulate_trip(
    cfg: Config,
    speed_vector,
    dist_idx,
    angles,
    eta_interp: Callable,
    gear_ratio: float,
    dt: float = 1.0,
) -> SimulationResult:
    """Hauptschleife der Simulation."""
    strecke = 0.0
    energie_verbrauch = 0.0
    state = init_state()

    for idx in range(len(speed_vector)):
        velocity = float(speed_vector.iloc[idx, 0])
        if idx + 1 >= len(speed_vector):
            break

        acceleration = float(
            (speed_vector.iloc[idx + 1, 0] - speed_vector.iloc[idx, 0]) / dt
        )

        strecke += velocity * dt
        steigung_grad = float(np.interp(strecke, dist_idx, angles))

        F_roll, F_luft, F_steig, F_beschl, F_ges = compute_resistances(
            cfg, velocity, acceleration, steigung_grad
        )
        state["t_axis"].append(idx * dt)
        state["F_roll"].append(F_roll)
        state["F_luft"].append(F_luft)
        state["F_steig"].append(F_steig)
        state["F_beschl"].append(F_beschl)
        state["F_ges"].append(F_ges)
        state["steigung"].append(steigung_grad)

        _, n_motor, _, trq_motor = drivetrain(cfg, F_ges, velocity, gear_ratio)
        eta_Ltb = float(eta_interp((trq_motor, n_motor)))
        energie_verbrauch, soc_val = update_energy(
            cfg, F_ges, velocity, eta_Ltb, energie_verbrauch, dt
        )
        state["drehmoment"].append(trq_motor)
        state["soc"].append(soc_val)

    return SimulationResult(
        t_axis=state["t_axis"],
        F_roll=state["F_roll"],
        F_luft=state["F_luft"],
        F_steig=state["F_steig"],
        F_beschl=state["F_beschl"],
        F_ges=state["F_ges"],
        steigung=state["steigung"],
        drehmoment=state["drehmoment"],
        soc=state["soc"],
        energie_verbrauch=energie_verbrauch,
    )


def plot_soc(t_axis, soc):
    plt.figure(figsize=(10, 4))
    plt.plot(t_axis, soc, label="SOC")
    plt.xlabel("Zeit [s]")
    plt.ylabel("State of Charge [%]")
    plt.title("State of Charge")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_profile(speed_vector, steigungsliste, dt: float = 1.0):
    v = (speed_vector.iloc[:, 0].to_numpy(float)) * 3.6
    t = np.arange(len(v)) * dt
    dist = np.cumsum(speed_vector.iloc[:, 0].to_numpy(float) * dt)

    plt.figure(figsize=(10, 5))

    plt.subplot(3, 1, 1)
    plt.plot(t, v, label="Geschwindigkeit")
    plt.xlabel("Zeit [s]")
    plt.ylabel("v [km/h]")
    plt.grid(True)
    plt.legend()

    plt.subplot(3, 1, 2)
    plt.plot(t[: len(steigungsliste)], steigungsliste, label="Steigung", color="green")
    plt.xlabel("Zeit [s]")
    plt.ylabel("Steigungswinkel [deg]")
    plt.grid(True)
    plt.legend()

    plt.subplot(3, 1, 3)
    plt.plot(t, dist / 1000.0, label="Distanz", color="orange")
    plt.xlabel("Zeit [s]")
    plt.ylabel("Distanz [km]")
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.show()


def plot_forces(
    t_axis, F_roll, F_luft, F_steig, F_beschl, F_ges, drehmoment
):
    fig, axes = plt.subplots(6, 1, figsize=(10, 10), sharex=True)
    axes[0].plot(t_axis, F_roll, color="tab:blue")
    axes[0].set_ylabel("Roll [N]")

    axes[1].plot(t_axis, F_luft, color="tab:orange")
    axes[1].set_ylabel("Luft [N]")

    axes[2].plot(t_axis, F_steig, color="tab:green")
    axes[2].set_ylabel("Steigung [N]")

    axes[3].plot(t_axis, F_beschl, color="tab:red")
    axes[3].set_ylabel("Beschl. [N]")

    axes[4].plot(t_axis, F_ges, color="black")
    axes[4].set_ylabel("Gesamt [N]")
    axes[4].set_xlabel("Zeit [s]")

    axes[5].plot(t_axis, drehmoment, color="cyan")
    axes[5].set_ylabel("Drehmoment [Nm]")
    axes[5].set_xlabel("Zeit [s]")

    for ax in axes:
        ax.grid(True)

    plt.tight_layout()
    plt.show()
