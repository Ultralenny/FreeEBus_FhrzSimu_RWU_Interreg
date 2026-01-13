from dataclasses import dataclass

@dataclass
class Loop_Config:
   
    row_number : int
    index :int
    dt :int 
    strecke :float
    Energie_verbrauch: float
    
    t_axis : list
    F_roll_list : list
    F_luft_list : list
    F_steig_list : list
    F_beschl_list : list
    F_ges_list : list
    Steigungswinkel : list
    Drehmoment : list
    soc : list


def Loop_config() -> Loop_Config:
    row_number = 0
    index = 0
    strecke = 0.0
    dt = 1.0  
    Energie_verbrauch = 0
    t_axis = []
    F_roll_list = []
    F_luft_list = []
    F_steig_list = []
    F_beschl_list = []
    F_ges_list = []
    Steigungswinkel = []
    Drehmoment = []
    soc = []

    return Loop_Config(
    row_number,
    index,
    strecke,
    dt,
    Energie_verbrauch,  
    t_axis,
    F_roll_list,
    F_luft_list,
    F_steig_list,
    F_beschl_list,
    F_ges_list,
    Steigungswinkel,
    Drehmoment,
    soc,
    )
