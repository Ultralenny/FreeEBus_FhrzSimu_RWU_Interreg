import datetime as dt
import os
import subprocess
import sys
from pathlib import Path
from tkinter import Tk, StringVar, BooleanVar, messagebox, W, E, N, S
from tkinter import ttk

import pandas as pd
import matplotlib.pyplot as plt


DATA_ROOT = Path(__file__).resolve().parents[1] / "Data"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "Debug" / "plots"


def _list_profile_files():
    files = []
    allowed_ext = {".csv", ".xlsx", ".xls", ".xlsm"}
    for path in DATA_ROOT.rglob("*"):
        if path.suffix.lower() not in allowed_ext:
            continue
        parts_lower = [p.lower() for p in path.parts]
        if "lookuptable" in parts_lower or "ltb_bus" in parts_lower or "matlab" in parts_lower:
            continue
        files.append(path)
    return files


def _split_profiles(files):
    speed = []
    elevation = []
    for path in files:
        rel = path.relative_to(DATA_ROOT)
        name = rel.name.lower()
        parts_lower = [p.lower() for p in rel.parts]
        if (
            "hoehen-profil" in parts_lower
            or "hoehenprofil" in parts_lower
            or "elevation" in parts_lower
            or "inclination" in name
            or "steigung" in name
        ):
            elevation.append(rel)
        else:
            speed.append(rel)
    return sorted(speed), sorted(elevation)


def _read_table_raw(path, header):
    suffix = Path(path).suffix.lower()
    if suffix in {".xlsx", ".xls", ".xlsm"}:
        return pd.read_excel(path, header=header)
    return pd.read_csv(path, delimiter=",", decimal=".", header=header)


def _read_table_auto(path):
    df = _read_table_raw(path, header=None)
    if df.empty:
        return df
    header_row = [str(x).strip() for x in df.iloc[0].tolist()]
    known_headers = {"time_s", "speed_kph", "distance_m", "cum_distance_m", "cycle", "velocity_ms"}
    has_alpha = any(any(c.isalpha() for c in h) for h in header_row if h)
    if any(h in known_headers for h in header_row) or has_alpha:
        df = _read_table_raw(path, header=0)
    return df


def load_speed_profile(path):
    path = Path(path)
    if not path.is_absolute():
        path = DATA_ROOT / path
    df = _read_table_auto(path)
    if df.empty:
        return df

    if "velocity_ms" in df.columns:
        v_ms = df["velocity_ms"].astype(float)
    elif "speed_kph" in df.columns:
        v_ms = df["speed_kph"].astype(float) / 3.6
    else:
        first_col = df.columns[0]
        v_ms = df[first_col].astype(float)
    return v_ms.to_frame(name="velocity_ms")


def load_elevation_profile(path):
    path = Path(path)
    if not path.is_absolute():
        path = DATA_ROOT / path
    df = _read_table_auto(path)
    if df.empty:
        return df

    if "strecke" in df.columns and "steigung_deg" in df.columns:
        elev = df[["strecke", "steigung_deg"]].copy()
    else:
        elev = df.iloc[:, :2].copy()
        elev.columns = ["strecke", "steigung_deg"]
    elev = elev.astype(float)
    elev.set_index("strecke", inplace=True)
    return elev


def _sanitize_filename(text):
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in text)


def plot_profiles(speed_df, elevation_df, show_plots, save_plots, speed_name, elevation_name):
    if speed_df.empty or elevation_df.empty:
        return

    fig, axes = plt.subplots(2, 1, figsize=(10, 6))
    v_kmh = speed_df.iloc[:, 0].to_numpy(float) * 3.6
    t = range(len(v_kmh))
    axes[0].plot(t, v_kmh, label="Geschwindigkeit")
    axes[0].set_xlabel("Zeit [s]")
    axes[0].set_ylabel("v [km/h]")
    axes[0].grid(True)
    axes[0].legend()

    dist = elevation_df.index.to_numpy(float) / 1000.0
    elev = elevation_df.iloc[:, 0].to_numpy(float)
    axes[1].plot(dist, elev, label="Steigung", color="green")
    axes[1].set_xlabel("Distanz [km]")
    axes[1].set_ylabel("Steigung [deg]")
    axes[1].grid(True)
    axes[1].legend()

    plt.tight_layout()

    if save_plots:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        speed_tag = _sanitize_filename(Path(speed_name).stem)
        elev_tag = _sanitize_filename(Path(elevation_name).stem)
        out_path = OUTPUT_DIR / f"profiles_{speed_tag}_{elev_tag}_{timestamp}.png"
        fig.savefig(out_path, dpi=150)

    if show_plots:
        plt.show()
    else:
        plt.close(fig)


class ProfileGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Reichweiten berechnung FreeE-Bus")

        self.speed_var = StringVar()
        self.elev_var = StringVar()
        self.plot_now_var = BooleanVar(value=True)
        self.save_plots_var = BooleanVar(value=False)
        self.status_var = StringVar(value="Bereit.")

        mainframe = ttk.Frame(root, padding=(12, 12, 12, 12))
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        ttk.Label(mainframe, text="Fahrprofil (Geschwindigkeit)").grid(column=0, row=0, sticky=W)
        self.speed_combo = ttk.Combobox(mainframe, textvariable=self.speed_var, state="readonly", width=60)
        self.speed_combo.grid(column=0, row=1, sticky=(W, E))

        ttk.Label(mainframe, text="Hoehenprofil (Steigung)").grid(column=0, row=2, sticky=W, pady=(8, 0))
        self.elev_combo = ttk.Combobox(mainframe, textvariable=self.elev_var, state="readonly", width=60)
        self.elev_combo.grid(column=0, row=3, sticky=(W, E))

        checks_frame = ttk.Frame(mainframe)
        checks_frame.grid(column=0, row=4, sticky=W, pady=(8, 0))
        ttk.Checkbutton(checks_frame, text="Plots sofort anzeigen", variable=self.plot_now_var).grid(column=0, row=0, sticky=W)
        ttk.Checkbutton(checks_frame, text="Plots speichern", variable=self.save_plots_var).grid(column=1, row=0, sticky=W, padx=(12, 0))

        buttons_frame = ttk.Frame(mainframe)
        buttons_frame.grid(column=0, row=5, sticky=W, pady=(8, 0))
        ttk.Button(buttons_frame, text="Aktualisieren", command=self.refresh_lists).grid(column=0, row=0, sticky=W)
        ttk.Button(buttons_frame, text="Laden", command=self.on_load).grid(column=1, row=0, sticky=W, padx=(8, 0))

        ttk.Label(mainframe, textvariable=self.status_var).grid(column=0, row=6, sticky=W, pady=(8, 0))

        run_frame = ttk.Frame(mainframe)
        run_frame.grid(column=0, row=7, sticky=E, pady=(8, 0))
        ttk.Button(run_frame, text="RUN", command=self.on_run).grid(column=0, row=0, sticky=E)

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        mainframe.columnconfigure(0, weight=1)

        self.refresh_lists()

    def refresh_lists(self):
        files = _list_profile_files()
        speed, elevation = _split_profiles(files)
        speed_values = [str(p) for p in speed]
        elev_values = [str(p) for p in elevation]

        current_speed = self.speed_var.get()
        current_elev = self.elev_var.get()

        self.speed_combo["values"] = speed_values
        self.elev_combo["values"] = elev_values

        if current_speed in speed_values:
            self.speed_var.set(current_speed)
        elif speed_values:
            self.speed_var.set(speed_values[0])

        if current_elev in elev_values:
            self.elev_var.set(current_elev)
        elif elev_values:
            self.elev_var.set(elev_values[0])

    def on_load(self):
        speed_name = self.speed_var.get()
        elev_name = self.elev_var.get()
        if not speed_name or not elev_name:
            messagebox.showerror("Fehler", "Bitte Fahrprofil und Hoehenprofil auswaehlen.")
            return

        try:
            speed_df = load_speed_profile(speed_name)
            elevation_df = load_elevation_profile(elev_name)
        except Exception as exc:
            messagebox.showerror("Fehler beim Laden", str(exc))
            return

        self.status_var.set(
            f"Geladen: {speed_name} ({len(speed_df)} Zeilen), {elev_name} ({len(elevation_df)} Zeilen)"
        )

        plot_profiles(
            speed_df,
            elevation_df,
            show_plots=self.plot_now_var.get(),
            save_plots=self.save_plots_var.get(),
            speed_name=speed_name,
            elevation_name=elev_name,
        )

    def on_run(self):
        speed_name = self.speed_var.get()
        elev_name = self.elev_var.get()
        if not speed_name or not elev_name:
            messagebox.showerror("Fehler", "Bitte Fahrprofil und Hoehenprofil auswaehlen.")
            return

        env = os.environ.copy()
        env["FREEEBUS_SPEED_PROFILE"] = speed_name
        env["FREEEBUS_ELEV_PROFILE"] = elev_name
        env["FREEEBUS_SHOW_PLOTS"] = "1" if self.plot_now_var.get() else "0"
        env["FREEEBUS_SAVE_PLOTS"] = "1" if self.save_plots_var.get() else "0"
        env["FREEEBUS_PLOT_DIR"] = str(OUTPUT_DIR)

        main_path = Path(__file__).resolve().parent / "Main.py"
        repo_root = DATA_ROOT.parent
        try:
            subprocess.Popen([sys.executable, str(main_path)], env=env, cwd=repo_root)
            self.status_var.set("Simulation gestartet.")
        except Exception as exc:
            messagebox.showerror("Fehler", f"Simulation konnte nicht gestartet werden: {exc}")

if __name__ == "__main__":
    root = Tk()
    app = ProfileGUI(root)
    root.mainloop()
