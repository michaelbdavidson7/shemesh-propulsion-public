from dash import html
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import numpy as np
import matplotlib.pyplot as plt
import math

SOLAR_PRESSURE = 4.56e-6  # N/m²
C = 3e8  # Speed of light, m/s
# Constants
SOLAR_PRESSURE = 4.56e-6  # N/m²
SMA_MASS_PER_M2 = 0.002  # kg/m
SMA_MASS_PER_M2 = 0.0005662499999999999  # kg/m
# ACS3_BOOMS_MASS_PER_M = 0.0082
ACS3_SAIL_MASS_PER_M2 = 0.00425  # kg/m²
HOURS = 700 # for the delta v at 700 hours , sail area vs kg mass chart
SECONDS = HOURS * 3600

ACS3_BOOM_MASS_PER_M_G = 23.43     # g/m, ACS3 boom mass per meter
ACS3_BOOM_MASS_PER_M_KG = 0.02343     # kg/m, ACS3 boom mass per meter
# SMA_MASS_PER_M = 1.66            # g/m, based on 0.50mm SMA wire
SMA_MASS_PER_M = 3            # g/m, REFACTOR BASED ON COATINGS AND ADHESIVES
SMA_MASS_PER_M_KG = 3            # kg/m, REFACTOR BASED ON COATINGS AND ADHESIVES
SMA_MASS_1_MM_DIAMETER_PER_M = 7.06 # g/m this is the less optimal scenario but very rigid
ACS3_SCALING_FACTOR = 3.13       # ACS3 boom length per meter of sail side length
NUM_RADIAL_WIRES = 8             # radial SMA wires, each has 2 paths (out and back)
ACS3_SAIL_MASS_PER_M2 = 0.00425  # kg/m²
APPROX_KG_SUBSYSTEM_PARTS_REDUCTION = 3 # kg saved from using solid state
PRODUCT_NAME = "SSP-1"
SAIL_BOOM_ENTIRE_SUBSYSTEM = 7.7 #kg
# (85g * 4 = 340g for sails) + (164g * 4 = 646g for booms) = 996g. 7.7 - 0.996
SAIL_BOOM_ENTIRE_MISSION_SUBSYSTEM_MINUS_BOOMS_AND_SAILS =  6.704
OTHER_SUBSECTION_PARTS_THAT_ARE_NEEDED = SAIL_BOOM_ENTIRE_MISSION_SUBSYSTEM_MINUS_BOOMS_AND_SAILS - APPROX_KG_SUBSYSTEM_PARTS_REDUCTION
def smart_format(x):
    if abs(x) < 1e-3 or abs(x) > 1e5:
        return f"{x:.5e}"  # scientific notation with 5 digits
    elif abs(x) < 1:
        return f"{x:.5f}".rstrip('0').rstrip('.')  # trim trailing zeros
    else:
        return f"{x:.3g}"  # general format, 3 significant digits
def get_deltav_arr(is_sma:bool, mass_per_m_len:float, other_subsystem_mass:float):
    sail_areas = np.linspace(10, 20000, 150)
    base_masses = np.linspace(1, 100, 150)
    A, M = np.meshgrid(sail_areas, base_masses)

    W = H = np.sqrt(A)
    P = 2 * (W + H)
    if is_sma:
        booms_or_sma_len_m = 5*W
    else:
        booms_or_sma_len_m = W*ACS3_SCALING_FACTOR
    component_mass =  (booms_or_sma_len_m * mass_per_m_len) + other_subsystem_mass
    sail_mass = A * ACS3_SAIL_MASS_PER_M2
    total_masses = M + component_mass + sail_mass
    thrusts = 2 * SOLAR_PRESSURE * A
    accelerations = thrusts / total_masses
    return accelerations

def get_deltav_at_700(is_sma:bool, mass_per_m_len:float, other_subsystem_mass:float):
        # Δv heatmap at 700 hours
        HOURS = 700
        SECONDS = HOURS * 3600
        accelerations = get_deltav_arr(is_sma, mass_per_m_len, other_subsystem_mass)
        dv_at_700 = accelerations * SECONDS
        return dv_at_700

def get_scalar_acceleration(is_sma:bool, 
                            mass_per_m_len:float, 
                            other_subsystem_mass:float, 
                            additional_spacecraft_mass:float, 
                            width:int|float,
                            height:int|float):
        area = width * height
        perimeter = 2 * (width + height)
        if is_sma:
            booms_or_sma_len_m = 5*width
        else:
            booms_or_sma_len_m = width*ACS3_SCALING_FACTOR
        component_mass_g =  (booms_or_sma_len_m * mass_per_m_len) 
        component_mass_kg =  component_mass_g / 1000
        component_mass_kg = component_mass_kg+ other_subsystem_mass
        sail_mass = area * ACS3_SAIL_MASS_PER_M2
        total_mass = additional_spacecraft_mass + component_mass_kg + sail_mass

        thrust = 2 * SOLAR_PRESSURE * area
        acceleration = thrust / total_mass
        
        accel_per_min = acceleration * 60
        accel_per_hour = acceleration * 3600
        accel_per_day = accel_per_hour * 24
        accel_per_month = smart_format(accel_per_day * 0.20 * 30.44)
        days_to_moon = 3100 / (accel_per_day * 0.20)
        
        output = html.Div([
            html.P(f"Sail Area: {area:.2f} m²"),
            html.P(f"Perimeter: {perimeter:.2f} m"),
            html.P(f"SMA Wire Needed: {booms_or_sma_len_m:.2f} m"),
            html.P(f"SMA Weight (perimeter): {component_mass_g/1000:.4f} kg"),
            html.P(f"Sail Weight (ACS3): {sail_mass:.4f} kg"),
            html.P(f"Other Subsystem Mass: {other_subsystem_mass:.4f} kg"),
            html.P(f"SMA Total Mass (SMA + sail + other subsystem mass + spacecraft mass): {total_mass:.4f} kg"),
            html.P(f"Estimated Thrust: {smart_format(thrust)} N"),
            html.P(f"Acceleration per second of propulsion: {smart_format(acceleration)} m/s"),
            html.P(f"Δv per minute of propulsion: {smart_format(accel_per_min)} m/s"),
            html.P(f"Δv per hour of propulsion: {smart_format(accel_per_hour)} m/s"),
            html.P(f"Duty cycle (time spent in solar propulsion): 20%"),
            html.P(f"Δv per day, with duty cycle reduction: {smart_format(accel_per_day * 0.20) } m/s"),
            html.P(f"Δv per month, with duty cycle reduction: {accel_per_month} m/s"),
            html.H5(f"Time to Moon, incl. duty cycle reduction: {days_to_moon:.2f} days or {days_to_moon/30.44:.2f} months"),
        ])
        
        return acceleration, output, component_mass_kg
    

def get_planet_mission_card(hardcoded_sail_area, SMA_MASS_PER_M2, ACS3_BOOMS_MASS_PER_M):
    sail_area = hardcoded_sail_area  # m²
    width = math.sqrt(hardcoded_sail_area)  # m²
    height = math.sqrt(hardcoded_sail_area)  # m²
    base_mass = 10  # kg
    

    # Acceleration
    a_sma, output, component_mass_kg = get_scalar_acceleration(is_sma=True, 
                                                    mass_per_m_len=SMA_MASS_PER_M, 
                                                    other_subsystem_mass=OTHER_SUBSECTION_PARTS_THAT_ARE_NEEDED, 
                                                    additional_spacecraft_mass=base_mass, 
                                                    width=width,
                                                    height=height)

    a_acs3, acs3_output, acs3_component_mass_kg = get_scalar_acceleration(is_sma=False, 
                                                    mass_per_m_len=ACS3_BOOM_MASS_PER_M_KG * 1000, 
                                                    other_subsystem_mass=SAIL_BOOM_ENTIRE_MISSION_SUBSYSTEM_MINUS_BOOMS_AND_SAILS, 
                                                    additional_spacecraft_mass=base_mass, 
                                                    width=width,
                                                    height=height)

    # Target Δv per mission
    missions = {
        "Moon": 3100,
        "Venus": 3500,
        "Mars": 4000
    }

    cards = []

    for planet, dv in missions.items():
        t_sma = dv / (a_sma * 3600)  # convert to hours
        t_acs3 = dv / (a_acs3 * 3600)
        percent_faster = ((t_acs3 - t_sma) / t_acs3) * 100
        duty_cycle = 0.20
        t_sma_days = dv / ((a_sma * 3600)  * 24 * duty_cycle)
        t_acs3_days = dv / ((a_acs3 * 3600) * 24 * duty_cycle)

        cards.append(
            dbc.Card(
                dbc.CardBody([
                    html.H5(f"{planet} Transfer", className="card-title"),
                    html.P(f"Target Δv: {dv:.0f} m/s"),
                    html.P(f"ACS3 Time to {planet}: {t_acs3_days:.0f} days or {t_acs3_days / 30.44:.2f} months"),
                    html.P(f"SMA Time to {planet}: {t_sma_days:.0f} days or {t_sma_days / 30.44:.2f} months"),
                    html.P(f"ACS3 component weight: {acs3_component_mass_kg:.2f} kg, SMA component weight: {component_mass_kg:.2f} kg, sail weight: {hardcoded_sail_area * ACS3_SAIL_MASS_PER_M2:.2f} kg"), 
                    # html.P(f"SMA Solar Propulsion Hours: {t_sma:.1f}"),
                    # html.P(f"ACS3 Solar Propulsion Hours: {t_acs3:.1f}"),
                    html.P(f"SMA is {percent_faster:.1f}% faster")
                ]),
                className="mb-3 shadow-sm"
            )
        )

    return dbc.Row([dbc.Col(card, width=4) for card in cards])
