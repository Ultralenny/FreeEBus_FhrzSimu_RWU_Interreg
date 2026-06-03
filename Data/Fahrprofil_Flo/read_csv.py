import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

CSV_PATH = Path(__file__).parent / "route_profile_fhv_flo.csv"


def load_profile(path: Path = CSV_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


def plot_speed_profile(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

    axes[0].plot(df["t_s"], df["v_kmh"])
    axes[0].set_ylabel("Speed (km/h)")
    axes[0].grid(True)

    axes[1].plot(df["t_s"], df["s_m"])
    axes[1].set_ylabel("Distance (m)")
    axes[1].grid(True)

    axes[2].plot(df["t_s"], df["slope_rad"])
    axes[2].set_ylabel("Slope (rad)")
    axes[2].set_xlabel("Time (s)")
    axes[2].grid(True)

    fig.suptitle("Speed Profile FHV Flo")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    df = load_profile()
    print(f"Loaded {len(df)} rows")
    print(df.head())
    print(df.describe())
    plot_speed_profile(df)
