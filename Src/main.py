import datetime as dt
import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from Data.Vehicle_Data import *
from FahrRes import *
from LookupTable import *
from Elektromotor import *
from Fahrprofil import *
from Loop_Config import *
from Debug import write_debug_csv




#####
#--------------------------Debug Settings ---------------------------------------------------
#####
debug_modus = False
if debug_modus == True:
    debug_csv_path = r"Debug\debug_output.csv"
    debug_csv_delimiter = ";"
    debug_csv_decimal_separator = ","
    debug_csv_float_format = ".6f"

def _env_bool(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


#####
###____________________________________MAIN_LOOP______________________________________________________________________####
#####


if __name__ == "__main__":
    #param = build_Volvo_7900E()
    param = build_Mercedes_Actros()
    ###_________________Filepaths___________________________________________#####
    path_T = r"Data\Lookuptable\Ltb_Bus\wirk_T.csv"
    path_n = r"Data\Lookuptable\Ltb_Bus\wirk_n.csv"
    path_Z = r"Data\Lookuptable\Ltb_Bus\wirk_Z.csv"
    
    #default_speed = r"Data\Fahrprofil 410315_6\v_uni_matched_410315_6.csv"
    default_speed = r"Data\Fahrprofil 410315_6\Valdierung_22m_s_1Stunde.csv"
    # default_elevation = r"Data\Fahrprofil 410315_6\inclination_410315_6.csv"
    default_elevation = r"Data\Hoehen-Profil\inclination_flat_0.csv"
    
    path_SpeedVector = os.getenv("FREEEBUS_SPEED_PROFILE", default_speed)
    path_Elevation = os.getenv("FREEEBUS_ELEV_PROFILE", default_elevation)
    show_plots = _env_bool("FREEEBUS_SHOW_PLOTS", True)
    save_plots = _env_bool("FREEEBUS_SAVE_PLOTS", False)
    plot_dir_env = os.getenv("FREEEBUS_PLOT_DIR")
    output_dir = Path(plot_dir_env) if plot_dir_env else (Path(__file__).resolve().parents[1] / "Debug" / "plots")
    ###_____________Function_______LookupTabelle______________________________####
    print("_Functioncall_LookupTable_")
    
    
    EM_LookupTable = GenLookupTable(path_T, path_n, path_Z)
    eta_interp = make_eta_interpolator(EM_LookupTable)
    
    
    ###____________________Range_und_Elevation______________________________####
    print("_Functioncall_Range_to_elevation_")
    Range_Elevation, dist_idx, angles = load_Elevation_profile(path_Elevation)
    
    ###____________________Speed_Vector______________________________####
    print("_Functioncall_Speed_Vector_")
    Speed_Vector = load_speed_profile(path_SpeedVector)
    
    #### Setup for LOOP    # Function State initialisierung
    row_number = 0
    index = 0
    strecke = 0.0
    dt = 1.0  # Zeitschritt zwischen sample werten (anpassen falls Sampling != 1 s)

    t_axis = []
    F_roll_list = []
    F_luft_list = []
    F_steig_list = []
    F_beschl_list = []
    F_ges_list = []
    Steigungswinkel = []
    Drehmoment = []
    soc = []
    Energie_usage = []
    Nebeverbrauch_Gesamt = []
    Distanz = []
    t = np.arange(len(Speed_Vector)) * dt  # time axis
    v = Speed_Vector.iloc[:, 0].to_numpy(float)  # speed column
    debug_rows = []

    # ========== NEBENVERBRAUCH KONFIGURATION ==========
    # Jahreszeit für Nebenverbäuche // 1 = Frühling; 2 = Sommer; 3 = Herbst; 4 = Winter
    Jahreszeit = 1 
    Nebenverbauch_kwh_base = Nebenverbauch(Jahreszeit)  # Basis-Nebenverbrauch pro Sekunde
    print(f"Basis-Nebenverbrauch: {Nebenverbauch_kwh_base} kWh/s")
    
    # ========== STILLSTANDS-TRACKING ==========
    stillstand_counter = 0  # Zähler für Stillstandszeit in Sekunden
    stillstand_threshold = 120  # 2 Minuten = 120 Sekunden
    velocity_threshold = 0.5  # Geschwindigkeit unter 0.5 m/s = Stillstand
    Nebenverbauch_tracking = []  # Zum Debuggen: Nebenverbrauch pro Iteration speichern
    

    #####________________________________________Main_FOR_LOOP_____________________________________________________#####

    for row in Speed_Vector.to_numpy(copy=False):
        velocity = float(row[0])

        if index + 1 >= len(Speed_Vector):
            break  # or set acceleration = 0 and continue

        acceleration = float(
            (Speed_Vector.iloc[index + 1, 0] - Speed_Vector.iloc[index, 0]) / dt
        )
        
        strecke += velocity * dt
        Distanz.append(strecke)
        # lineare Interpolation der Steigung auf die aktuelle Strecke
        steigung = float(np.interp(strecke, dist_idx, angles))
        Steigungswinkel.append(steigung)
        
        F_roll = rollwiderstand(param.m_ges, param.c_r)
        F_luft = luftwiderstand(velocity, param.cw, param.A)
        F_steig = steigungswiderstand(param.m_ges, steigung)
        F_beschl = beschleunigungswiderstand(param.m_Fahrz, acceleration, massenfaktor=1.05)
        F_ges = gesamtfahrwiderstand(F_roll, F_luft, F_steig, F_beschl)

        t_axis.append(index * dt)
        F_roll_list.append(F_roll)
        F_luft_list.append(F_luft)
        F_steig_list.append(F_steig)
        F_beschl_list.append(F_beschl)
        F_ges_list.append(F_ges)

        F_trac = max(F_ges, 0.0)
        
        n_rad = RadDrehzahl(velocity, param.RadDurchmesser)
        n_Motor = MotorDrehzahl(n_rad, param.i)

        trq_rad = Radmoment(F_ges, param.RadDurchmesser)
        trq_motor = Motormoment(trq_rad, param.eta_Antrieb, param.i)
        Drehmoment.append(trq_motor)
        eta_Ltb = eta_interp((trq_motor, n_Motor))  # mit [Torque, RPM]
        

        Fahrleistung_EL = (Fahrleistung(F_trac, velocity, eta_Ltb) / 1000)  # elektrische Leistung in kW
       
        ##          Rekuperation
        P_mech = F_ges * velocity  # W, can be negative
        if P_mech >= 0:
            P_batt_kW = (P_mech / eta_Ltb) / 1000.0  # traction draws from battery
        else:
            P_batt_kW = (P_mech * param.eta_reku) / 1000.0  # regen charges battery (negative)

        # ========== NEBENVERBRAUCH-LOGIK VERBESSERT ==========
        # Prüfe, ob der Bus stillsteht
        if velocity < velocity_threshold:  # Bus steht
            stillstand_counter += dt  # Inkrementiere Stillstandszeit
        else:  # Bus fährt
            stillstand_counter = 0  # Setze Zähler zurück
        
        # Bestimme Nebenverbrauch basierend auf Stillstandsdauer
        if stillstand_counter >= stillstand_threshold:
            # Nach 2 Minuten Stillstand: Nebenverbrauch = 0
            Nebenverbauch_kwh = 0.0
        else:
            # Ansonsten: Normaler Nebenverbrauch (auch während Stillstand, aber < 2 Min)
            Nebenverbauch_kwh = Nebenverbauch_kwh_base * (dt / 3600.0)

        # Energie hinzufügen
        param.Energie_verbrauch = min(
            param.E_Battrie,
            max(0.0, param.Energie_verbrauch + Nebenverbauch_kwh + P_batt_kW * (dt / 3600.0)),
        )
        Energie_usage.append(param.Energie_verbrauch)
        Nebeverbrauch_Gesamt.append(Nebenverbauch_kwh)
        
        
        State_of_Charge = 100.0 * (1.0 - param.Energie_verbrauch / param.E_Battrie)
        State_of_Charge = max(0.0, min(100.0, State_of_Charge))
        soc.append(State_of_Charge)

        if debug_modus == True:
            strecke_km = strecke / 1000.0
            debug_rows.append(
                {
                    "index": index,
                    "strecke_m": float(strecke),
                    "strecke_km": float(strecke_km),
                    "steigung_deg": float(steigung),
                    "velocity_m_s": float(velocity),
                    "acceleration_m_s2": float(acceleration),
                    "f_roll_n": float(F_roll),
                    "f_luft_n": float(F_luft),
                    "f_steig_n": float(F_steig),
                    "f_beschl_n": float(F_beschl),
                    "f_ges_n": float(F_ges),
                    "n_motor_rpm": float(n_Motor),
                    "trq_motor_nm": float(trq_motor),
                    "eta_ltb": float(eta_Ltb),
                    "fahrleistung_el_kw": float(Fahrleistung_EL),
                    "nebenverbauch_kwh": float(Nebenverbauch_kwh),
                    "stillstand_counter_s": float(stillstand_counter),
                    "energie_verbrauch_kwh": float(param.Energie_verbrauch),
                    "state_of_charge_pct": float(State_of_Charge),
                }
            )
            print(f"Indexnummer: {index}")
            print(f"Zurueckgelegte Distanz in m: {strecke:.1f}")
            print(f"Steigunggswinkel bei km {strecke_km:.1f}: {steigung:.1f}")
            
            print(f"Geschwindigkeit:        {velocity:.1f} m/s")
            print(f"Beschleunigung:        {acceleration:.1f} m/s^2")
            print(f"Stillstand Counter:     {stillstand_counter:.1f} s")
            print(f"Nebenverbrauch:         {Nebenverbauch_kwh:.6f} kWh")
            print(f"Rollwiderstand:         {F_roll:.1f} N")
            print(f"Luftwiderstand:         {F_luft:.1f} N")
            print(f"Steigungswiderstand:    {F_steig:.1f} N")
            print(f"Beschleunigungswiderst: {F_beschl:.1f} N")
            print(f"Gesamtfahrwiderstand:   {F_ges:.1f} N")
            print(f"Drehzahl Motor:     {n_Motor:1f} 1/min")
            print(f"Drehmoment Motor:   {trq_motor:.1f} Nm")
            print(f"Wirkungsgrad:       {eta_Ltb:.1f}")

            print(f"Fahrleistung elektrisch: {Fahrleistung_EL:.1f} kW")
            print(f"Energieverbauch: {param.Energie_verbrauch:.1f} kWh")
            print(f"State of Charge: {State_of_Charge:.2f} %")
            print("______                          ____")
            
        index = index + 1

    if debug_modus == True:
        write_debug_csv(
            debug_csv_path,
            debug_rows,
            delimiter=debug_csv_delimiter,
            decimal_separator=debug_csv_decimal_separator,
            float_format=debug_csv_float_format,
        )
        # ______________________________________________________________________________________________________________________#

    print("_Speed_Vector_Loop_finished_")
    print("_Functioncall_Speed_Vector_finished_")
    print("_Plot_all_Resistances")
    
    if debug_modus == True:
        if Distanz:
            total_km = Distanz[-1] / 1000.0
            total_kwh = Energie_usage[-1] if Energie_usage else 0.0
            kwh_per_100km = (total_kwh / total_km * 100.0) if total_km > 0 else 0.0
            print(f"Gesamtdistanz: {total_km:.2f} km")
            print(f"Energieverbrauch: {total_kwh:.2f} kWh")
            print(f"Spezifisch: {kwh_per_100km:.2f} kWh/100km")

    figs = []

    fig = plt.figure(figsize=(10, 4))
    figs.append(fig)
    plt.plot(t_axis, Energie_usage, label="Energieverbauch in kWh")
    plt.xlabel("Zeit [s]")
    plt.ylabel("Energie [kWh]")
    plt.title("Energieverbrauch")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    #plt.show()



    """
    plt.figure(figsize=(10, 4))
    plt.plot(t_axis, soc, label="SOC")
    plt.xlabel("Zeit [s]")
    plt.ylabel("State of Charge [%]")
    plt.title("State of Charge")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    #plt.show()
    """
    v = (Speed_Vector.iloc[:, 0].to_numpy(float)) * 3.6
    t = np.arange(len(v)) * dt
    dist_km = np.array(Distanz) / 1000.0

    fig = plt.figure(figsize=(10, 5))
    figs.append(fig)

    plt.subplot(3, 1, 1)
    plt.plot(t, v, label="Geschwindigkeit")
    plt.xlabel("Zeit [s]")
    plt.ylabel("v [km/s]")
    plt.grid(True)
    plt.legend()

    plt.subplot(3, 1, 2)
    plt.plot(t_axis, Steigungswinkel, label="Steigung", color="green")
    plt.xlabel("Zeit [s]")
    plt.ylabel("Steigungswinkel [°]")
    plt.grid(True)
    plt.legend()

    plt.subplot(3, 1, 3)
    plt.plot(t_axis, dist_km, label="Distanz", color="orange")
    plt.xlabel("Zeit [s]")
    plt.ylabel("Distanz [km]")
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    #plt.show()

    # ______________________________________________________________________________________________________________________#

    fig, axes = plt.subplots(5, 1, figsize=(10, 10), sharex=True)
    figs.append(fig)
    axes[0].plot(t_axis, F_roll_list, color="tab:blue")
    axes[0].set_ylabel("Roll [N]")

    axes[1].plot(t_axis, F_luft_list, color="tab:orange")
    axes[1].set_ylabel("Luft [N]")

    axes[2].plot(t_axis, F_steig_list, color="tab:green")
    axes[2].set_ylabel("Steigung [N]")

    axes[3].plot(t_axis, F_beschl_list, color="tab:red")
    axes[3].set_ylabel("Beschl. [N]")

    axes[4].plot(t_axis, F_ges_list, color="black")
    axes[4].set_ylabel("Gesamt [N]")
    axes[4].set_xlabel("Zeit [s]")

    for ax in axes:
        ax.grid(True)

    plt.tight_layout()

    if save_plots:
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        speed_tag = Path(path_SpeedVector).stem
        elev_tag = Path(path_Elevation).stem
        for idx, fig in enumerate(figs, 1):
            out_path = output_dir / f"sim_{speed_tag}_{elev_tag}_{timestamp}_{idx}.png"
            fig.savefig(out_path, dpi=150)

    if show_plots:
        plt.show()
    else:
        for fig in figs:
            plt.close(fig)

# ______________________________________________________________________________________________________________________#
    print("Main Function: Done")
