import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import numpy as np
import matplotlib.pyplot as plt

from sail_size_calculator_utils import get_planet_mission_card

# Constants
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

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Solar Sail Δv Simulator"
hardcoded_sail_area = 4096
planet_cards = get_planet_mission_card(hardcoded_sail_area=hardcoded_sail_area, ACS3_BOOMS_MASS_PER_M=ACS3_BOOM_MASS_PER_M_KG, SMA_MASS_PER_M2=SMA_MASS_PER_M_KG)

app.layout = dbc.Container([
    html.H1("Solar Sail Propulsion Calculator", className="text-center mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Sail Width (m)"),
            dcc.Input(id="sail-width", type="number", value=44.722, step=.001, className="form-control"),

            dbc.Label("Sail Height (m)", className="mt-3"),
            dcc.Input(id="sail-height", type="number", value=44.721, step=.001, className="form-control"),

            dbc.Label("Spacecraft Mass (kg)", className="mt-3"),
            dcc.Input(id="mass", type="number", value=5, step=1, className="form-control"),
        ], width=4),

    #     dbc.Col([
    #         html.H5("Results", className="mt-2"),
    #         html.Div(id="output-area", className="border p-3 bg-light"),
    #         dcc.Graph(id="dv-graph")
    #     ])
    # ]),
    # dbc.Row([
    #     dbc.Col([
    # dcc.Graph(id="heatmap-graph")
    #     ])dbc.Row([
    dbc.Col([
        html.H5("Results", className="mt-2"),
        html.Div(id="output-area", className="border p-3 bg-light"),
        html.Div(id="dv-card", className="border p-3 bg-light"),
    ], width=8)  # You can change to width=6 or whatever looks good
], justify="center"),
    
dbc.Row([
    dbc.Col([
        html.Hr(),
        html.H5("ACS3 Parameters Expanded vs SMA Version Expanded"),
        dcc.Graph(id="dv-graph"),
    ], width=6),
]),
    
    # ]),
dbc.Row([
    dbc.Col([
        html.Hr(),
        html.H5("Δv at 700 Hours Heatmap - This is static and doesn't change from the inputs"),
        dcc.Graph(id="acs3-heatmap-graph")
    ], width=6),
    dbc.Col([
        html.Hr(),
        html.H5("Δv at 700 Hours Heatmap - This is static and doesn't change from the inputs"),
        dcc.Graph(id="sall-e-heatmap-graph")
    ], width=6),
]),
dbc.Row([
    dbc.Col([
        html.Hr(),
        html.H5("Δv at 700 Hours Heatmap - This is static and doesn't change from the inputs"),
        dcc.Graph(id="diff-fig-graph")
    ], width=6),
    dbc.Col([
        html.Hr(),
    html.H5(f"Mission Time Comparison (Hardcoded: {hardcoded_sail_area} m² sail, 10 kg base mass)"),
    planet_cards,
    ], width=6),
])
], fluid=True)



def compute_solar_sail_stats(width_m, height_m, base_mass_kg, hours_duration=720):
    area = width_m * height_m
    perimeter = 2 * (width_m + height_m)

    # sma_mass = perimeter * SMA_MASS_PER_M_KG
    sail_mass = area * ACS3_SAIL_MASS_PER_M2
    # total_mass = base_mass_kg + sma_mass + sail_mass
    
    radius = width_m / 2
    # how much wire do we need
    basic_sma_length = perimeter + 2 * radius
    basic_sma_mass_g = basic_sma_length * SMA_MASS_PER_M_KG
    basic_sma_mass_kg = basic_sma_mass_g / 1000
    basic_sma_and_sails_mass_kg = basic_sma_mass_kg + sail_mass
    basic_sma_total = sail_mass + basic_sma_mass_kg + OTHER_SUBSECTION_PARTS_THAT_ARE_NEEDED

    thrust = 2 * SOLAR_PRESSURE * area  # N
    acceleration = thrust / basic_sma_total  # m/s²

    time_hours = np.linspace(0, hours_duration, 300)
    time_seconds = time_hours * 3600
    delta_v = acceleration * time_seconds  # m/s

    return {
        "area": area,
        "perimeter": perimeter,
        "sma_mass": basic_sma_total,
        "sail_mass": sail_mass,
        "total_mass": basic_sma_total,
        "thrust": thrust,
        "acceleration": acceleration,
        "dv_per_minute": acceleration * 60,
        "dv_per_hour": acceleration * 3600,
        "time_hours": time_hours,
        "delta_v": delta_v
    }
    
stats = compute_solar_sail_stats(width_m=44.72, height_m=44.72, base_mass_kg=10, hours_duration=720)
print(f"Sail Area: {stats['area']} m²")
print(f"SMA Mass: {stats['sma_mass']:.4f} kg")
print(f"Sail Mass (ACS3): {stats['sail_mass']:.4f} kg")
print(f"Total System Mass: {stats['total_mass']:.4f} kg")
print(f"Thrust: {stats['thrust']:.6e} N")
print(f"Acceleration: {stats['acceleration']:.6e} m/s²")
print(f"Δv per minute: {stats['dv_per_minute']:.4f} m/s")
print(f"Δv per hour: {stats['dv_per_hour']:.4f} m/s")
plt.figure(figsize=(10, 6))
plt.plot(stats["time_hours"], stats["delta_v"])
plt.title("Δv Over Time (Solar Sail)")
plt.xlabel("Time (hours)")
plt.ylabel("Δv (m/s)")
plt.grid(True)
plt.tight_layout()
# plt.show()


# Ranges
sail_areas = np.linspace(10, 20000, 100)  # m²
base_masses = np.linspace(1, 100, 100)    # kg

A, M = np.meshgrid(sail_areas, base_masses)  # meshgrid: area vs base mass

# Derived parameters
width = height = np.sqrt(A)  # assume square sails
perimeter = 2 * (width + height)
radius = width / 2
basic_sma_length = perimeter + width * radius
basic_sma_mass_g = basic_sma_length * SMA_MASS_PER_M_KG
basic_sma_mass_kg = basic_sma_mass_g / 1000
sail_mass = A * ACS3_SAIL_MASS_PER_M2
total_mass = M + basic_sma_mass_kg + sail_mass + OTHER_SUBSECTION_PARTS_THAT_ARE_NEEDED
thrust = 2 * SOLAR_PRESSURE * A
acceleration = thrust / total_mass
delta_v = acceleration * SECONDS  # m/s at 700 hours

# Plotting
plt.figure(figsize=(10, 6))
contour = plt.contourf(A, M, delta_v, levels=50, cmap="viridis")
cbar = plt.colorbar(contour)
cbar.set_label("Δv at 700 hours (m/s)")

plt.xlabel("Sail Area (m²)")
plt.ylabel("Base Mass (kg)")
plt.title("Δv vs Sail Area and Mass at 700 hours")
plt.tight_layout()
# plt.show()

def get_deltav_heatmap(dv_at_700:np.ndarray, title:str) ->go.Figure:
    heatmap_fig = go.Figure(data=go.Contour(
        z=dv_at_700,
        x=sail_areas,
        y=base_masses,
        colorscale='Viridis',
        zmin=0,
        zmax=5000,
        colorbar=dict(title="Δv (m/s)")
    ))
    heatmap_fig.update_layout(
        title=title,
        xaxis_title="Sail Area (m²)",
        yaxis_title="Base Mass of non-sail components (kg)",
        template="plotly_white",
        height=1000 ,
    )
    return heatmap_fig
# def get_deltav_and_accel_per_hour(area, mass, perimeter, mass_per_m2, figure):

#         sma_weight = perimeter * mass_per_m2
#         sail_weight = area * ACS3_SAIL_MASS_PER_M2
#         total_mass = mass + sma_weight + sail_weight

#         thrust = 2 * SOLAR_PRESSURE * area
#         acceleration = thrust / total_mass

#         accel_per_min = acceleration * 60
#         accel_per_hour = acceleration * 3600
#         # Δv over time
#         hours = np.linspace(0, 24*30, 300)
#         seconds = hours * 3600
#         dv_values = acceleration * seconds
        
#         figure.add_trace(go.Scatter(x=hours, y=dv_values, mode='lines', name='Δv (m/s)'))

#         return (figure, accel_per_min, accel_per_hour, sma_weight, sail_weight, total_mass, thrust, acceleration)
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
                            width:int,
                            height:int):
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
        
        return acceleration, output
        accel_per_min = acceleration * 60
        accel_per_hour = acceleration * 3600
        dv_values = acceleration * seconds
# def get_mission_speeds(sma_total_mass, accel_sma, accel_acs3 ):
#     missions = {
#     "Moon": 3100,
#     "Venus": 3500,
#     "Mars": 4000
# }

#     # Store the central row (or a few select values) from your mass range
#     row_idx = sma_total_mass.shape[0] // 2  # pick a mid-mass slice
#     area_vals = A[row_idx, :]
#     sma_accel_vals = accel_sma[row_idx, :]
#     acs3_accel_vals = accel_acs3[row_idx, :]

#     for mission, target_dv in missions.items():
#         sma_times = target_dv / sma_accel_vals / 3600  # hours
#         acs3_times = target_dv / acs3_accel_vals / 3600

#         # Now you can plot these, or display:
#         print(f"Mission to {mission}:")
#         for i in range(len(area_vals)):
#             print(f"  Sail Area: {area_vals[i]:.0f} m² — SMA: {sma_times[i]:.1f} hr, ACS3: {acs3_times[i]:.1f} hr")

@app.callback(
    Output("output-area", "children"),
    Output("dv-graph", "figure"),
    Output("acs3-heatmap-graph", "figure"),
    Output("sall-e-heatmap-graph", "figure"),
    Output("diff-fig-graph", "figure"),
    Output("dv-card", "children"),
    Input("sail-width", "value"),
    Input("sail-height", "value"),
    Input("mass", "value")
)
def calculate_and_plot(width, height, additional_mass):
    if width and height and additional_mass and width > 0 and height > 0 and additional_mass > 0:
        area = width * height
        perimeter = 2 * (width + height)

        dv_fig = go.Figure()
        # dv_fig, accel_per_min, accel_per_hour, sma_weight, sail_weight, total_mass, thrust, acceleration = get_deltav_and_accel_per_hour(area=area, additional_mass=additional_mass, perimeter=perimeter, mass_per_m2=SMA_MASS_PER_M_KG, figure=dv_fig)
        # dv_fig, acs3_accel_per_min, acs3_accel_per_hour, acs3_booms_weight, acs3_sail_weight, acs3_total_mass, acs3_thrust, acs3_acceleration = get_deltav_and_accel_per_hour(area=area, additional_mass=additional_mass, perimeter=perimeter, mass_per_m2=ACS3_BOOMS_MASS_PER_M, figure=dv_fig)
        
        # Δv over time
        hours = np.linspace(0, 24*30, 300)
        seconds = hours * 3600
        sail_weight = area * ACS3_SAIL_MASS_PER_M2
        
        acceleration, output = get_scalar_acceleration(is_sma=True, 
                                                       mass_per_m_len=SMA_MASS_PER_M, 
                                                       other_subsystem_mass=OTHER_SUBSECTION_PARTS_THAT_ARE_NEEDED, 
                                                       additional_spacecraft_mass=additional_mass, 
                                                       width=width,
                                                       height=height)
        
        dv_values = acceleration * seconds

        acs3_acceleration, acs3_output = get_scalar_acceleration(is_sma=False, 
                                                       mass_per_m_len=ACS3_BOOM_MASS_PER_M_KG * 1000, 
                                                       other_subsystem_mass=SAIL_BOOM_ENTIRE_MISSION_SUBSYSTEM_MINUS_BOOMS_AND_SAILS, 
                                                       additional_spacecraft_mass=additional_mass, 
                                                       width=width,
                                                       height=height)
        acs3_dv_values = acs3_acceleration * seconds
        
        # side note, accel by type
        # accel_sma = sma_thrust / sma_total_mass
        # accel_acs3 = acs3_thrust / acs3_total_mass
        # get_mission_speeds(sma_total_mass=sma_total_mass, accel_sma=accel_sma, accel_acs3=accel_acs3)
        # add the lines
        dv_fig.add_trace(go.Scatter(x=hours, y=dv_values, mode='lines', name='Shape Memory Alloy-based Subsystem Δv (m/s)'))
        dv_fig.add_trace(go.Scatter(x=hours, y=acs3_dv_values, mode='lines', name='ACS3 Flight Profile Extended Δv (m/s)'))
        
        dv_fig.update_layout(
            title=f"Δv Over Time With {area:.0f}m² Sail Size and {additional_mass} kg Other Weight",
            xaxis_title="Time (hours)",
            yaxis_title="Δv (m/s)",
            template="plotly_white"
        )
        
        dv_at_700_acs3 = get_deltav_at_700(is_sma=False, mass_per_m_len=ACS3_BOOM_MASS_PER_M_KG, other_subsystem_mass=SAIL_BOOM_ENTIRE_MISSION_SUBSYSTEM_MINUS_BOOMS_AND_SAILS)
        dv_at_700_sma = get_deltav_at_700(is_sma=True, mass_per_m_len=SMA_MASS_PER_M, other_subsystem_mass=OTHER_SUBSECTION_PARTS_THAT_ARE_NEEDED)

        acs3_heatmap_fig = get_deltav_heatmap(dv_at_700_acs3, title="ACS3 EXPANDED - Δv at 700 Hours vs Sail Area and Base Mass")
        salle_heatmap_fig = get_deltav_heatmap(dv_at_700_sma, title="SMA VERSION - Δv at 700 Hours vs Sail Area and Base Mass")
        
        percent_diff = ((dv_at_700_sma - dv_at_700_acs3) / dv_at_700_acs3) * 100
        avg_percent_improvement = np.mean(percent_diff)
        print("Maximum Improvement: {:.2f}%".format(np.max(percent_diff)))
        print("Maximum Loss: {:.2f}%".format(np.min(percent_diff)))
        print("Avg Percent Improvement: {:.2f}%".format(avg_percent_improvement))
        acs3_dv_range_str = f"ACS3 Δv range: {dv_at_700_acs3.min():.2f}–{dv_at_700_acs3.max():.2f} m/s"
        print(acs3_dv_range_str)
        sma_dv_range_str = f"SMA  Δv range: {dv_at_700_sma.min():.2f}–{dv_at_700_sma.max():.2f} m/s"
        print(sma_dv_range_str)
        
        dv_acs3_min = np.min(dv_at_700_acs3)
        dv_acs3_max = np.max(dv_at_700_acs3)
        dv_sma_min = np.min(dv_at_700_sma)
        dv_sma_max = np.max(dv_at_700_sma)

        dv_card = dbc.Card(
            dbc.CardBody([
                html.H5("Δv Performance Summary for like configurations at 700 propulsion hours", className="card-title"),
                html.P(f"ACS3 Δv range: {dv_acs3_min:.2f} – {dv_acs3_max:.2f} m/s"),
                html.P(f"SMA  Δv range: {dv_sma_min:.2f} – {dv_sma_max:.2f} m/s"),
                html.H4(f"At 700 hours of continuous thrust, the SMA sail can yield {dv_sma_max / dv_acs3_max:.2f}x more Δv than ACS3, and {avg_percent_improvement:.2f}% average improvement.")
            ]),
            className="mb-4 shadow-sm"
        )
        zmin = np.min(percent_diff)
        zmax = np.max(percent_diff)
        tickvals = np.linspace(zmin, zmax, 10)  
        ticktext = [f"{val:.1f}%" for val in tickvals]
        diff_fig = go.Figure(data=go.Contour(
            z=percent_diff,
            x=sail_areas,
            y=base_masses,
            zmin=zmin,
            zmax=zmax,
            colorscale="YlGnBu",  # or "YlGnBu", "Cividis", "Turbo"
            colorbar=dict(
            title="Δv Improvement (%)",
            tickvals=tickvals.tolist(),
            ticktext=ticktext
            ),
            contours=dict(showlines=False)
        ))
        diff_fig.update_layout(
            title="Δv Improvement (SMA vs ACS3)",
            xaxis_title="Sail Area (m²)",
            yaxis_title="Base Mass (kg)",
            template="plotly_white",
            height=600
        )
        
        return output, dv_fig, acs3_heatmap_fig, salle_heatmap_fig, diff_fig, dv_card

    return "Please enter valid inputs.", go.Figure(), go.Figure()
if __name__ == "__main__":
    app.run(debug=True)
