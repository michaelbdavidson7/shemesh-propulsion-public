import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc


# Constants (assumed based on available data)# Given values in kg per square meter
ACS3_BOOM_WEIGHT_PER_M2 = 0.0082  # kg/m²
SMA_BOOM_WEIGHT_PER_M2 = 0.0005662499999999999  # kg/m²

# Conversion factor: 1 kg = 1000 grams
CONVERSION_FACTOR = 1000  

# Convert to grams per square meter
acs3_boom_weight_g_per_m2 = ACS3_BOOM_WEIGHT_PER_M2 * CONVERSION_FACTOR
sma_boom_weight_g_per_m2 = SMA_BOOM_WEIGHT_PER_M2 * CONVERSION_FACTOR

#ACS3 raw parameters
acs3_mission_sailboomsubsystem_mass_kg = 7.7
acs3_mission_sailboomsubsystem_mass_g = 7700
acs3_mission_full_sail_size_m2 = 80
acs3_mission_booms_weight_g = 656
acs3_mission_sail_weight_g = 340
acs3_mission_sailboomsubsystem_mass_without_sails_booms_g = acs3_mission_sailboomsubsystem_mass_g - acs3_mission_booms_weight_g - acs3_mission_sail_weight_g
SALL_E_estimated_subsystem_weight_g=acs3_mission_sailboomsubsystem_mass_without_sails_booms_g/2
# Create a small table of removed components from ACS3 as a DataFrame
sall_e_required_acs3_components_data = {
    "Name": ["Boom Hub Release Pin-Puller (1)", "Tape Spool Drive Gears (4)", "Motor Drive Gear", "Bus/Drive Train Plate", "Sail Plate", "Metal Tapes (4)", "Tape-Driven Boom Hub (4)", "Tape Drive Spools (4)", "Sail Spools (4)", "End Plate"],
    "Keep?": ["✔️", "❌",  "❌", "❌", "✔️", "❌", "✔️", "✔️", "❌","✔️" ]
}

sall_e_required_acs3_components_df = pd.DataFrame(sall_e_required_acs3_components_data)
# Create a DataTable using the loaded DataFrame
sall_e_required_acs3_components = dash_table.DataTable(
    columns=[{"name": col, "id": col} for col in sall_e_required_acs3_components_df.columns],
    data=sall_e_required_acs3_components_df.to_dict("records"),
    style_cell={'textAlign': 'center', 'fontSize': 16},
    style_header={'fontWeight': 'bold'},
    style_table={'width': '200px', 'margin-left': '50px', 'margin-top':'50px', 'margin-bottom': '50px'}
)

# Summary data
sall_e_vs_acs3_summary_data = {
    "Feature": ["Massive weight reduction", "Removes many components", "Simplifies complexity at large scale", "Reduces man-hours required to build"],
    "Status":["✔️","✔️","✔️","✔️",]
}
sall_e_vs_acs3_summary_df = pd.DataFrame(sall_e_vs_acs3_summary_data)
sall_e_vs_acs3_summary_table = dash_table.DataTable(
    columns=[{"name": col, "id": col} for col in sall_e_vs_acs3_summary_df.columns],
    data=sall_e_vs_acs3_summary_df.to_dict("records"),
    style_cell={'textAlign': 'center', 'fontSize': 16},
    style_header={'fontWeight': 'bold'},
    style_table={'width': '200px', 'margin-left': '50px', 'margin-top':'50px', 'margin-bottom': '50px'}
)


# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.ZEPHYR])

app.layout = html.Div([
    html.H1("ACS3 vs. SALL-E Weight Comparison"),
    html.H3("\"SALL-E\" is a new solar sail spacecraft that has solar sails actuated by Shape Memory Alloys, which is a solid state actuation. This allows a boom-less mission profile that saves a lot of weight!"),
    
    html.Label("Select Sail Area (m²):"),
    dcc.Slider(
        id='sail-area-slider',
        min=10, max=200, step=5, value=80,  # Adjust range as needed
        marks={i: str(i) for i in range(10, 210, 20)}
    ),
    
    html.Div(id='weight-output'),
    
    dcc.Graph(id='boom-weight-graph'),
    html.Div(style={'height': '200px'}),
    html.H1("Massive weight savings when comparing booms vs boom-less architecture: "),
    dcc.Graph(id='comparison-graph'),
    html.Div(style={'height': '200px'}),
    html.H2("How does the rest of the ACS3 booms subsystem compare? Is there weight to save there too?"),
    html.P(f"Sail size: {acs3_mission_full_sail_size_m2} (m²)"),
    html.P(f"Total mass: {acs3_mission_sailboomsubsystem_mass_kg}kg - 656g (All four booms weight) - 340g (All four quadrants sail weight) = {acs3_mission_sailboomsubsystem_mass_without_sails_booms_g} grams. "),
    html.H3("ACS3 Booms Subsystem without the booms and sail weights is 6704 grams."),
    html.Div(style={'height': '200px'}),
    html.Img(src="/assets/ACS3_booms_subsystem_pic.jpg"),
    html.Div([
        html.Div([
            html.H4("Approximated required components for the SALL-E Solid State SMA-Driven Unit vs ACS3's mission components:", className="card-title"),
            html.H6("Comparing the components needed to the components we can remove", className="card-subtitle mb-2 text-muted"),
            sall_e_required_acs3_components,
        ], className="card-body"),
    ], className="card"),
    html.Div(style={'height': '20px'}),
    
    html.H4(f"Estimated weight savings of 50%, SALL-E boom subsystem estimated at {(SALL_E_estimated_subsystem_weight_g)} grams vs {acs3_mission_sailboomsubsystem_mass_without_sails_booms_g} grams on ACS3."),
    html.Br(),
    html.Div(style={'height': '200px'}),
    html.Div(style={'height': '20px'}),
    dcc.Graph(id='comparison-graph2'),
    html.Div([
        html.Div([
            html.H4("Summary table", className="card-title"),
            html.H6("Final comparison between ACS3 and SALL-E", className="card-subtitle mb-2 text-muted"),
            sall_e_vs_acs3_summary_table,
        ], className="card-body"),
    ], className="card"),
    
    
    html.Div(style={'height': '20px'}),
    html.Div(style={'height': '20px'})
], className="container-fluid", )

def get_comparison_graph(show_full_trace=False) -> go.Figure:
    # Comparison for fixed sail areas
    fixed_sail_areas = [80, 200, 1500, 10000]
    acs3_fixed_weights = [area * acs3_boom_weight_g_per_m2 for area in fixed_sail_areas]
    sma_fixed_weights = [area * sma_boom_weight_g_per_m2 for area in fixed_sail_areas]

    # Format values to 3 decimal places
    formatted_acs_fixed_weights = [f"{v:.3f}g" for v in acs3_fixed_weights]

    # Calculate percentage difference and format text for SMA Booms
    formatted_sma_fixed_weights = [
    f"{sma:.3f}g <b>({abs((sma - acs) / acs * 100):.1f}% smaller)</b>" 
        if acs != 0 else f"{sma:.3f}"  # Avoid division by zero
        for acs, sma in zip(acs3_fixed_weights, sma_fixed_weights)
    ]

    # Format sail areas for display
    fixed_sail_areas = [f"{area:.3f}" for area in fixed_sail_areas]

    # Create Figure
    comparison_fig = go.Figure()
    if not show_full_trace:
        title = "Boom Weight Comparison at Specific Sail Areas"
        comparison_fig.add_trace(go.Bar(
            x=fixed_sail_areas,
            y=acs3_fixed_weights,
            name='ACS3 Booms',
            text=formatted_acs_fixed_weights,
            textposition='outside'
        ))
        comparison_fig.add_trace(go.Bar(
            x=fixed_sail_areas,
            y=sma_fixed_weights,
            name='SMA Booms',
            text=formatted_sma_fixed_weights,  # Updated text with % difference
            textposition='outside'
        ))
    if show_full_trace:
        title = "ACS3 vs SALL-E Full Sails Subsystem Comparison at Different Scales"
        acs3_full_sails_subsystem = [(x + acs3_mission_sailboomsubsystem_mass_without_sails_booms_g) for x in acs3_fixed_weights]
        sall_e_full_sails_subsystem = [(x + SALL_E_estimated_subsystem_weight_g) for x in sma_fixed_weights]
        formatted_acs3_full_sails_subsystem = [f"{v:.3f}g" for v in acs3_full_sails_subsystem]
        formatted_sma_fixed_weights2 = [
        f"{sma:.3f}g <b>({abs((sma - acs) / acs * 100):.1f}% smaller)</b>" 
            if acs != 0 else f"{sma:.3f}"  # Avoid division by zero
            for acs, sma in zip(acs3_full_sails_subsystem, sall_e_full_sails_subsystem)
        ]
        comparison_fig.add_trace(go.Bar(
            x=fixed_sail_areas,
            y=acs3_full_sails_subsystem,
            name='ACS3 Estimated Full Sails Subsystem',
            text=formatted_acs3_full_sails_subsystem,
            textposition='outside'
        ))
        comparison_fig.add_trace(go.Bar(
            x=fixed_sail_areas,
            y=sall_e_full_sails_subsystem,
            name='SALL-E Estimated Full Sails Subsystem',
            text=formatted_sma_fixed_weights2,  # Updated text with % difference
            textposition='outside'
        ))
    # Update Layout
    comparison_fig.update_layout(
        title=title,
        xaxis_title="Sail Area (m²)",
        yaxis_title="Boom Weight (g)",
        barmode='group',
        height=800,
        legend_title="Boom Type",
        bargap=0.000001,  # Reduce space between bars
        bargroupgap=0.05  # Reduce space between groups
    )
    return comparison_fig

@app.callback(
    [Output('weight-output', 'children'),
     Output('boom-weight-graph', 'figure'),
     Output('comparison-graph', 'figure'),
     Output('comparison-graph2', 'figure')
     ],
    [Input('sail-area-slider', 'value')]
)
def update_output(sail_area):
    acs3_weight = sail_area * acs3_boom_weight_g_per_m2
    sma_weight = sail_area * sma_boom_weight_g_per_m2
    
    weight_text = f"ACS3 Boom Weight: {acs3_weight:.2f} g | SMA Boom Weight: {sma_weight:.2f} g"
    
    sail_areas = np.linspace(10, 200, 50)
    acs3_weights = sail_areas * acs3_boom_weight_g_per_m2
    sma_weights = sail_areas * sma_boom_weight_g_per_m2
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sail_areas, y=acs3_weights, mode='lines', name='ACS3 Booms'))
    fig.add_trace(go.Scatter(x=sail_areas, y=sma_weights, mode='lines', name='SMA Booms'))
    
    fig.update_layout(title="Boom Weight vs. Sail Area",
                      xaxis_title="Sail Area (m²)",
                      yaxis_title="Boom Weight (g)",
                      legend_title="Boom Type")
    
    comparison_fig:go.Figure = get_comparison_graph(show_full_trace=False)
    comparison_fig2:go.Figure = get_comparison_graph(show_full_trace=True)
    return weight_text, fig, comparison_fig, comparison_fig2



if __name__ == '__main__':
    app.run_server(debug=True)
