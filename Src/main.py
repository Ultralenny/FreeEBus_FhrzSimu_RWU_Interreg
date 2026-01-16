import numpy as np
import matplotlib.pyplot as plt
from FahrRes import *
from LookupTable import *
from Elektromotor import *
from Fahrprofil import *
from Config_Data import *
from Loop_Config import *

#####
#--------------------------Debug Settings ---------------------------------------------------
#####
debug_modus = False


#####
###____________________________________MAIN_LOOP______________________________________________________________________####
#####


if __name__ == "__main__":
    param = build_config()
    
    ###_____________Function_______LookupTabelle______________________________####
    print("_Functioncall_LookupTable_")
    path_T = r"Data\Lookuptable\Ltb_Bus\wirk_T.csv"
    path_n = r"Data\Lookuptable\Ltb_Bus\wirk_n.csv"
    path_Z = r"Data\Lookuptable\Ltb_Bus\wirk_Z.csv"
    
    EM_LookupTable = GenLookupTable(path_T, path_n, path_Z)
    eta_interp = make_eta_interpolator(EM_LookupTable)
    
    
    ###____________________Range_und_Elevation______________________________####
    print("_Functioncall_Range_to_elevation_")
    Range_Elevation = Datafield_range_to_elevation()
    dist_idx = Range_Elevation.index.to_numpy(float)  # strecke
    angles = Range_Elevation.iloc[:, 0].to_numpy(float)  # elevation angle

    ###____________________Speed_Vector______________________________####
    print("_Functioncall_Speed_Vector_")
    Speed_Vector = Datafield_Speed_Vector()

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

    t = np.arange(len(Speed_Vector)) * dt  # time axis
    v = Speed_Vector.iloc[:, 0].to_numpy(float)  # speed column

    #####________________________________________Main_FOR_LOOP_____________________________________________________#####

    for row in Speed_Vector.to_numpy(copy=False):
        velocity = float(row[0])

        if index + 1 >= len(Speed_Vector):
            break  # or set acceleration = 0 and continue

        acceleration = float(
            (Speed_Vector.iloc[index + 1, 0] - Speed_Vector.iloc[index, 0]) / dt
        )

        strecke += velocity * dt
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

        Fahrleistung_EL = (
            Fahrleistung(F_trac, velocity, eta_Ltb) / 1000
        )  # elektrische Leistung in kW
       
        ##          Rekuperation
        P_mech = F_ges * velocity  # W, can be negative
        if P_mech >= 0:
            P_batt_kW = (P_mech / eta_Ltb) / 1000.0  # traction draws from battery
        else:
            P_batt_kW = (P_mech * param.eta_reku) / 1000.0  # regen charges battery (negative)

        param.Energie_verbrauch = min(
            param.E_Battrie,
            max(0.0, param.Energie_verbrauch + P_batt_kW * (dt / 3600.0)),
        )

        State_of_Charge = 100.0 * (1.0 - param.Energie_verbrauch / param.E_Battrie)
        State_of_Charge = max(0.0, min(100.0, State_of_Charge))
        soc.append(State_of_Charge)

        if debug_modus == True:
            print(f"Indexnummer: {index}")
            print(f"Zurueckgelegte Distanz in m: {strecke:.1f}")
            print(f"Steigunggswinkel bei km {(strecke / 1000):.1f}: {steigung:.1f}")
            
            print(f"Geschwindigkeit:        {velocity:.1f} m/s")
            print(f"Beschleunigung:        {acceleration:.1f} m/s^2")
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
        
    # ______________________________________________________________________________________________________________________#

    print("_Speed_Vector_Loop_finished_")
    print("_Functioncall_Speed_Vector_finished_")
    print("_Plot_all_Resistances")

    plt.figure(figsize=(10, 4))
    plt.plot(t_axis, soc, label="SOC")
    plt.xlabel("Zeit [s]")
    plt.ylabel("State of Charge [%]")
    plt.title("State of Charge")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    #plt.show()

    v = (Speed_Vector.iloc[:, 0].to_numpy(float)) * 3.6
    t = np.arange(len(v)) * dt
    dist = np.cumsum(v * dt)  # meters

    plt.figure(figsize=(10, 5))

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
    plt.plot(t, dist / 1000.0, label="Distanz", color="orange")
    plt.xlabel("Zeit [s]")
    plt.ylabel("Distanz [km]")
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    #plt.show()

    # ______________________________________________________________________________________________________________________#

    fig, axes = plt.subplots(6, 1, figsize=(10, 10), sharex=True)
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

    axes[5].plot(t_axis, Drehmoment, color="cyan")
    axes[5].set_ylabel("Drehmoment [Nm]")
    axes[5].set_xlabel("Zeit [s]")

    for ax in axes:
        ax.grid(True)

    plt.tight_layout()
    plt.show()

# ______________________________________________________________________________________________________________________#
print("Main Function: Done")