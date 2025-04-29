import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# Atmospheric density table (simplified) for different altitudes in km
density_table = {
    100: 5.6e-7,
    150: 2.07e-9,
    200: 2e-9,
    250: 3e-10,
    300: 2e-10,
    400: 3e-11,
    500: 1e-11,
    600: 5e-12,
    700: 1.5e-12,
    800: 6e-13,
    900: 3e-13,
    1000: 1e-13
}
density_altitudes = np.array([100, 150, 200, 250, 300, 400, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000])
density_values = np.array([5.6e-7, 2.07e-9, 2e-9, 3e-10, 2e-10, 3e-11, 1e-11, 5e-12, 
                           1.5e-12, 6e-13, 3e-13, 1e-13, 3e-14, 1e-14, 3e-15, 1e-15, 5e-16])

def get_density(altitude):
    # Linear interpolation between known points
    return np.interp(altitude, density_altitudes, density_values)

# Constants
solar_pressure = 4.5e-6  # N/m²
solar_thrust_per_m2 = solar_pressure * 2  # for perfect reflector

# Initialize the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Solar Sail Mission Planner: Drag, Thrust, and Orbit Raising"),
    
    html.Label("Sail Area (m²):"),
    dcc.Slider(
        id="area-slider", min=1, max=10000, step=10, value=4000,
        marks={i: str(i) for i in range(0, 11000, 2000)}
    ),
    html.Br(),

    html.Label("Orbit Altitude (km):"),
    dcc.Slider(
        id="altitude-slider", min=100, max=max(density_altitudes), step=10, value=600,
        marks={i: str(i) for i in range(100, max(density_altitudes) + 100, 100)}
    ),
    html.Br(),

    html.Label("Orbital Velocity (m/s):"),
    dcc.Slider(
        id="velocity-slider", min=6000, max=8500, step=50, value=7800,
        marks={i: str(i) for i in range(6000, 9000, 500)}
    ),
    html.Br(),

    html.Label("Drag Coefficient (Cd):"),
    dcc.Slider(
        id="cd-slider", min=0.5, max=3.0, step=0.1, value=2.2,
        marks={i/10: f"{i/10}" for i in range(5, 31, 5)}
    ),
    html.Br(),

    html.Label("Spacecraft Mass (kg):"),
    dcc.Slider(
        id="mass-slider", min=0.1, max=1000, step=0.1, value=20,
        marks={i: str(i) for i in range(0, 1100, 200)}
    ),
    html.Br(),

    html.Label("Duty Cycle (% useful thrust time):"),
    dcc.Slider(
        id="duty-slider", min=0, max=100, step=1, value=20,
        marks={i: f"{i}%" for i in range(0, 110, 20)}
    ),
    html.Br(),

    dcc.Graph(id="drag-vs-altitude-graph"),
    dcc.Graph(id="solar-vs-drag-graph"),
    dcc.Graph(id="orbit-raise-graph"),
    html.Div(id="mission-output", style={"marginTop": 20, "fontSize": 20}),
    dcc.Graph(id="summary-table"),

])

@app.callback(
    [Output("drag-vs-altitude-graph", "figure"),
     Output("solar-vs-drag-graph", "figure"),
     Output("mission-output", "children"),
     Output("orbit-raise-graph", "figure"),
     Output("summary-table", "figure"),
     ],
    [Input("area-slider", "value"),
     Input("altitude-slider", "value"),
     Input("velocity-slider", "value"),
     Input("cd-slider", "value"),
     Input("mass-slider", "value"),
     Input("duty-slider", "value")]
)
def update_graphs(area, altitude, velocity, Cd, mass, duty_cycle):
    rho = get_density(altitude)

    # Forces
    solar_thrust = solar_thrust_per_m2 * area
    drag_force = 0.5 * Cd * rho * velocity**2 * area

    # Correct force timing
    effective_solar_thrust = solar_thrust * (duty_cycle / 100.0)  # Solar thrust only during duty cycle
    effective_drag_force = drag_force * 1.0  # Drag always active

    # Net Force and Acceleration
    net_force = effective_solar_thrust - effective_drag_force
    net_acceleration = net_force / mass  # m/s²

    # Delta-V per day
    delta_v_per_day = net_acceleration * 86400  # seconds/day

    # Time to gain 100 m/s
    if delta_v_per_day > 0:
        time_days_to_100ms = 100 / delta_v_per_day
    else:
        time_days_to_100ms = float('inf')
        
    # Simulate orbit raising for 180 days
    times, altitudes_sim, delta_vs = simulate_orbit_raise(
        initial_altitude_km=altitude,
        initial_velocity=velocity,
        net_acceleration=net_acceleration,
        days=180
    )

    # Create orbit raise graph
    orbit_fig = go.Figure()
    orbit_fig.add_trace(go.Scatter(
        x=times,
        y=altitudes_sim,
        mode='lines+markers',
        name="Altitude over Time"
    ))
    orbit_fig.update_layout(
        title="Simulated Orbit Raise Over Time",
        xaxis_title="Days",
        yaxis_title="Altitude (km)",
        height=500
    )

    # Drag vs Altitude
    altitude_range = np.linspace(100, max(density_altitudes), 100)
    densities = np.array([get_density(a) for a in altitude_range])
    drags = 0.5 * Cd * densities * velocity**2 * area

    drag_fig = go.Figure()
    drag_fig.add_trace(go.Scatter(
        x=altitude_range,
        y=drags,
        mode="lines+markers",
        name="Drag vs Altitude"
    ))
    drag_fig.update_layout(
        xaxis_title="Altitude (km)",
        yaxis_title="Drag Force (N)",
        title="Drag Force vs Altitude",
        height=500
    )

    # Solar vs Drag bar chart
    solar_vs_drag_fig = go.Figure(data=[
        go.Bar(name="Effective Solar Thrust", x=["Solar Thrust"], y=[effective_solar_thrust]),
        go.Bar(name="Drag Force", x=["Drag"], y=[effective_drag_force])
    ])
    solar_vs_drag_fig.update_layout(
        barmode='group',
        title="Solar Thrust vs Drag Force",
        yaxis_title="Force (N)",
        height=400
    )

    # Output text
    output_text = (f"Solar Thrust (raw): {solar_thrust:.6f} N\n"
                   f"Effective Solar Thrust (Duty Cycle {duty_cycle}%): {effective_solar_thrust:.6f} N\n"
                   f"Drag Force: {effective_drag_force:.6f} N\n"
                   f"Net Force: {net_force:.6f} N\n"
                   f"Net Acceleration: {net_acceleration:.8f} m/s²\n"
                   f"Delta-V Gain per Day: {delta_v_per_day:.4f} m/s/day\n"
                   f"Estimated Days to Gain +100 m/s: {time_days_to_100ms:.2f} days")
    
    
    summary_df = generate_summary_table(area, velocity, Cd, mass, duty_cycle)
    summary_table = dash_table.DataTable(
        columns=[{"name": col, "id": col} for col in summary_df.columns],
        data=summary_df.to_dict('records'),
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center', 'padding': '5px'},
        style_header={'fontWeight': 'bold'}
    )
    summary_graph_fig, escape_altitude = generate_summary_graph(area, velocity, Cd, mass, duty_cycle)

    return drag_fig, solar_vs_drag_fig, output_text, orbit_fig, summary_graph_fig

def simulate_orbit_raise(initial_altitude_km, initial_velocity, net_acceleration, days, timestep=1):
    # Constants
    G = 6.67430e-11  # gravitational constant
    M = 5.972e24     # mass of Earth
    R_earth = 6371e3  # Earth radius in meters

    # Initialize
    altitudes = []
    delta_vs = []
    times = []

    # Initial conditions
    v = initial_velocity  # m/s
    t = 0  # days

    for _ in range(0, days, timestep):
        times.append(t)
        
        # Update velocity
        v += net_acceleration * timestep * 86400  # timestep days * seconds/day

        # Calculate new orbit altitude
        r = G * M / v**2  # orbital radius
        altitude = (r - R_earth) / 1000  # in km
        altitudes.append(altitude)
        delta_vs.append(v)

        t += timestep

    return times, altitudes, delta_vs

def generate_summary_table(area, velocity, Cd, mass, duty_cycle):
    rows = []
    step_km = 50  # step size

    for alt in range(100, int(max(density_altitudes)) + 50, step_km):
        rho = get_density(alt)
        drag_force = 0.5 * Cd * rho * velocity**2 * area
        solar_thrust = solar_thrust_per_m2 * area
        effective_solar_thrust = solar_thrust * (duty_cycle / 100.0)

        net_force = effective_solar_thrust - drag_force
        net_acceleration = net_force / mass

        if net_acceleration > 0:
            result = "Climb (Gain)"
        else:
            result = "Decay (Loss)"

        rows.append({
            "Altitude (km)": alt,
            "Net Acceleration (m/s²)": f"{net_acceleration:.8e}",
            "Result": result
        })

    df = pd.DataFrame(rows)
    return df
def generate_summary_graph(area, velocity, Cd, mass, duty_cycle):
    altitudes = []
    net_accelerations = []

    # Finer steps below 800 km
    alt = 100
    while alt <= max(density_altitudes):
        rho = get_density(alt)
        drag_force = 0.5 * Cd * rho * velocity**2 * area
        solar_thrust = solar_thrust_per_m2 * area
        effective_solar_thrust = solar_thrust * (duty_cycle / 100.0)

        net_force = effective_solar_thrust - drag_force
        net_acceleration = net_force / mass

        altitudes.append(alt)
        net_accelerations.append(net_acceleration)

        alt += 25 if alt < 800 else 50

    fig = go.Figure()

    # Color coding: Red = Decay, Green = Climb
    colors = ["red" if acc < 0 else "green" for acc in net_accelerations]

    fig.add_trace(go.Scatter(
        x=altitudes,
        y=net_accelerations,
        mode='markers+lines',
        marker=dict(color=colors, size=6),
        line=dict(color="blue"),
        name="Net Acceleration"
    ))

    # Add zero acceleration line
    fig.add_hline(y=0, line_dash="dash", line_color="black", annotation_text="Zero Net Acceleration", annotation_position="top right")

    fig.update_layout(
        title="Net Acceleration vs Altitude (Colored Climb vs Decay)",
        xaxis_title="Altitude (km)",
        yaxis_title="Net Acceleration (m/s²)",
        yaxis_range=[-0.001, 0.0005],
        height=500
    )
    fig.update_layout(
        xaxis_range=[800, 1600],  # Focus where action happens
        yaxis_range=[-0.001, 0.0005],
        width=800,  # narrower plot
        height=500
    )
    # Find first positive net acceleration
    escape_altitude = None
    escape_net_acc = None
    for a, acc in zip(altitudes, net_accelerations):
        if acc > 0:
            escape_altitude = a
            escape_net_acc = acc
            break

    # Plot special marker at escape point
    if escape_altitude is not None:
        fig.add_trace(go.Scatter(
            x=[escape_altitude],
            y=[escape_net_acc],
            mode="markers+text",
            marker=dict(color="gold", size=14, symbol="star"),
            text=["🚀 Escape!"],
            textposition="top center",
            name="Escape Point"
        ))

    return fig, escape_altitude


if __name__ == "__main__":
    app.run_server(debug=True, port=8051)
