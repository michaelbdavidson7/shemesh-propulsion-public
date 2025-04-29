import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import math
import plotly.graph_objs as go

# ========================
# 💡 Constants
# ========================
ACS3_BOOM_MASS_PER_M = 23.43     # g/m, ACS3 boom mass per meter
SMA_MASS_PER_M = 1.66            # g/m, based on 0.50mm SMA wire
SMA_MASS_PER_M = 3            # g/m, REFACTOR BASED ON COATINGS AND ADHESIVES
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

# ========================
# Dash App
# ========================
app = dash.Dash(__name__)
app.title = "Sail Boom Mass Comparator"

app.layout = html.Div([
    html.H1("Sail Boom Mass Comparison", style={"textAlign": "center"}),
    html.P(f"{PRODUCT_NAME} is the next generation solar sail technology deployed by solid state Shape Memory Alloys (SMAs). This advancement allows lighter sails, less parts, less manhours to build, and a self-healing capability."),
    html.H3("Constants"),
    html.Ul([
        html.Li(f"ACS3 boom mass per meter: {ACS3_BOOM_MASS_PER_M} g/m"),
        html.Li(f"{PRODUCT_NAME} SMA wire mass per meter, incl. coatings and adhesives: {SMA_MASS_PER_M} g/m"),
        html.Li(f"ACS3 boom length scales at {ACS3_SCALING_FACTOR} × side length"),
        html.Li(f"Number of radial wires: {NUM_RADIAL_WIRES} (round trip = ×2)"),
        html.Li(f"Solar Sail Material Weight (CP1 with coatings): {ACS3_SAIL_MASS_PER_M2} kg/m²"),
        html.Li(f"Entire Sail/Boom Subsystem of ACS3: {SAIL_BOOM_ENTIRE_SUBSYSTEM} kg"),
        html.Li(f"Approx weight of sail subsystem parts made redundant by {PRODUCT_NAME}'s solid state design: {APPROX_KG_SUBSYSTEM_PARTS_REDUCTION} kg"),
    ], style={"fontFamily": "monospace"}),

    html.Label("Sail Area (m²)", style={"marginTop": "20px"}),
    dcc.Slider(
        id='area-slider',
        min=100,
        max=10000,
        step=50,
        value=2000,
        marks={i: str(i) for i in range(100, 10001, 1000)},
        tooltip={"placement": "bottom", "always_visible": True}
    ),

    html.Div(id='results', style={"marginTop": "30px", "fontFamily": "monospace", "whiteSpace": "pre"}),

    dcc.Graph(id='mass-chart', style={"marginTop": "40px"})
], className="container")


@app.callback(
    [Output('results', 'children'),
     Output('mass-chart', 'figure')],
    Input('area-slider', 'value')
)
def update_masses(area):
    # 🔢 Geometry
    side = math.sqrt(area)
    perimeter = 4 * side
    radius = side / 2
    
    # sail weight in kg
    sail_weight = area * ACS3_SAIL_MASS_PER_M2 

    # 🚀 ACS3 Booms
    boom_length = ACS3_SCALING_FACTOR * side
    acs3_mass_g = boom_length * ACS3_BOOM_MASS_PER_M
    acs3_booms_mass_kg = acs3_mass_g / 1000
    acs3_booms_and_sails_mass_kg = acs3_booms_mass_kg + sail_weight
    acs3_total = sail_weight + acs3_booms_mass_kg + SAIL_BOOM_ENTIRE_MISSION_SUBSYSTEM_MINUS_BOOMS_AND_SAILS
    acs3_booms_and_sails_and_redundant_parts_mass_kg = acs3_booms_and_sails_mass_kg + SAIL_BOOM_ENTIRE_MISSION_SUBSYSTEM_MINUS_BOOMS_AND_SAILS

    
    # 🟢 SALL-E (Perimeter + 2 Radii)
    basic_sma_length = 5 * side 
    basic_sma_mass_g = basic_sma_length * SMA_MASS_PER_M
    basic_sma_mass_kg = basic_sma_mass_g / 1000
    basic_sma_and_sails_mass_kg = basic_sma_mass_kg + sail_weight
    basic_sma_total = sail_weight + basic_sma_mass_kg + OTHER_SUBSECTION_PARTS_THAT_ARE_NEEDED
    basic_improvement = 100 * (1 - (basic_sma_total / acs3_total))


    # 🔴 SALL-E (Radial + Perimeter)
    radial_length = NUM_RADIAL_WIRES * 2 * radius
    total_radial_length = radial_length + perimeter
    radial_sma_mass_g = total_radial_length * SMA_MASS_PER_M
    radial_sma_mass_kg = radial_sma_mass_g / 1000
    radial_sma_and_sails_mass_kg = radial_sma_mass_kg + sail_weight
    radial_total = sail_weight + radial_sma_mass_kg + OTHER_SUBSECTION_PARTS_THAT_ARE_NEEDED
    radial_improvement = 100 * (1 - (radial_total / acs3_total))
    
    # SMA at 1mm diameter scenario
    basic_sma_1mm_diameter_mass_g = basic_sma_length * SMA_MASS_1_MM_DIAMETER_PER_M
    basic_sma_1mm_diameter_mass_kg = basic_sma_1mm_diameter_mass_g / 1000
    basic_sma_1mm_diameter_and_sails_mass_kg = basic_sma_1mm_diameter_mass_kg + sail_weight
    basic_sma_1mm_diameter_total = sail_weight + basic_sma_1mm_diameter_mass_kg + OTHER_SUBSECTION_PARTS_THAT_ARE_NEEDED
    basic_sma_1mm_diameter_improvement = 100 * (1 - (basic_sma_1mm_diameter_total / acs3_total))

    # SMA at 1mm diameter radial scenario
    radial_sma_1mm_diameter_mass_g = total_radial_length * SMA_MASS_1_MM_DIAMETER_PER_M
    radial_sma_1mm_diameter_mass_kg = radial_sma_1mm_diameter_mass_g / 1000
    radial_sma_1mm_diameter_and_sails_mass_kg = radial_sma_1mm_diameter_mass_kg + sail_weight
    radial_sma_1mm_diameter_total = sail_weight + radial_sma_1mm_diameter_mass_kg + OTHER_SUBSECTION_PARTS_THAT_ARE_NEEDED
    radial_sma_1mm_diameter_improvement = 100 * (1 - (radial_sma_1mm_diameter_total / acs3_total))
    # 🧾 Results block
    results_text = f"""
=== Sail Geometry ===
Shape:             Square
Sail Area:         {area:.0f} m²
Sail Weight:       {sail_weight:.2f} kg
Side Length:       {side:.2f} m
Perimeter:         {perimeter:.2f} m
Center-to-Edge:    {radius:.2f} m

=== ACS3 Booms ===
Boom Length:       {boom_length:.2f} m
Mass per meter:    {ACS3_BOOM_MASS_PER_M} g/m
Total Booms Mass:        {acs3_mass_g:.1f} g  = {acs3_booms_mass_kg:.2f} kg
Total Booms + Sails Max:         {acs3_booms_and_sails_mass_kg:.1f} kg
Subsystem w/o Booms and Sails:         {SAIL_BOOM_ENTIRE_MISSION_SUBSYSTEM_MINUS_BOOMS_AND_SAILS:.1f} kg (static)
Total Subsystem Mass (sails + booms + subsystem): {acs3_total:.2f} kg

=== {PRODUCT_NAME} (Perimeter + 2 Radii) ===
Wire Length:       {basic_sma_length:.2f} m (4 sides + 2 radii)
Mass per meter:    {SMA_MASS_PER_M} g/m
Total Wire Mass:        {basic_sma_mass_g:.1f} g  = {basic_sma_mass_kg:.2f} kg
Total Wire + Sails Mass:        {basic_sma_and_sails_mass_kg:.2f} kg

=== {PRODUCT_NAME} (Radial + Perimeter) ===
Radial Wires:      {NUM_RADIAL_WIRES} × 2 × {radius:.2f} = {radial_length:.2f} m
Total Wire Length: {total_radial_length:.2f} m (radials + perimeter)
Total Wire Mass:        {radial_sma_mass_g:.1f} g  = {radial_sma_mass_kg:.2f} kg
Total Wire + Sails Mass:        {radial_sma_and_sails_mass_kg:.2f} kg
"""

    # ➡️ NEW: Subsection Table
    table_data = [
        {
            "Configuration": "ACS3",
            "Sail Mass (kg)": f"{sail_weight:.2f}",
            "Booms/SMA Wires Mass (kg)": f"{acs3_booms_mass_kg:.2f}",
            "Other Subsystem Mass (kg)": f"{SAIL_BOOM_ENTIRE_MISSION_SUBSYSTEM_MINUS_BOOMS_AND_SAILS:.2f}",
            "Total (kg)": f"{acs3_total:.2f}",
            "Improvement":" -- "
        },
        {
            "Configuration": f"{PRODUCT_NAME} (Basic, 0.50mm diameter, ideal)",
            "Sail Mass (kg)": f"{sail_weight:.2f}",
            "Booms/SMA Wires Mass (kg)": f"{basic_sma_mass_kg:.2f}",
            "Other Subsystem Mass (kg)": f"{OTHER_SUBSECTION_PARTS_THAT_ARE_NEEDED:.2f}",
            "Total (kg)": f"{basic_sma_total:.2f}",
            "Improvement": f"+{basic_improvement:.0f}% subsystem weight savings"
        },
        {
            "Configuration": f"{PRODUCT_NAME} (Radial, 0.50mm diameter)",
            "Sail Mass (kg)": f"{sail_weight:.2f}",
            "Booms/SMA Wires Mass (kg)": f"{radial_sma_mass_kg:.2f}",
            "Other Subsystem Mass (kg)": f"{OTHER_SUBSECTION_PARTS_THAT_ARE_NEEDED:.2f}",
            "Total (kg)": f"{radial_total:.2f}",
            "Improvement": f"+{radial_improvement:.0f}% subsystem weight savings"
        },
        {
            "Configuration": f"{PRODUCT_NAME} (Basic, 1mm diameter)",
            "Sail Mass (kg)": f"{sail_weight:.2f}",
            "Booms/SMA Wires Mass (kg)": f"{basic_sma_1mm_diameter_mass_kg:.2f}",
            "Other Subsystem Mass (kg)": f"{OTHER_SUBSECTION_PARTS_THAT_ARE_NEEDED:.2f}",
            "Total (kg)": f"{basic_sma_1mm_diameter_total:.2f}",
            "Improvement": f"+{basic_sma_1mm_diameter_improvement:.0f}% subsystem weight savings"
        },
        {
            "Configuration": f"{PRODUCT_NAME} (Radial, 1mm diameter)",
            "Sail Mass (kg)": f"{sail_weight:.2f}",
            "Booms/SMA Wires Mass (kg)": f"{radial_sma_1mm_diameter_mass_kg:.2f}",
            "Other Subsystem Mass (kg)": f"{OTHER_SUBSECTION_PARTS_THAT_ARE_NEEDED:.2f}",
            "Total (kg)": f"{radial_sma_1mm_diameter_total:.2f}",
            "Improvement": f"+{radial_sma_1mm_diameter_improvement:.0f}% subsystem weight savings"
        }
    ]

    table = dash_table.DataTable(
        columns=[
            {"name": col, "id": col} for col in ["Configuration", "Sail Mass (kg)", "Booms/SMA Wires Mass (kg)", "Other Subsystem Mass (kg)", "Total (kg)", "Improvement"]
        ],
        data=table_data,
        style_table={'overflowX': 'auto', 'marginTop': '30px', 'marginLeft':'2px'},
        style_cell={'textAlign': 'center', 'fontFamily': 'monospace'},
        style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'}
    )
    # ========================
    # 🎨 Color Palette
    # ========================
    COLOR_SAIL = '#4169E1'          # Royal Blue
    COLOR_SMA_OR_BOOMS = '#DC143C'  # Crimson Red
    COLOR_SUBSYSTEMS = '#2F4F4F'    # Dark Slate Gray
        # 📊 Chart [your same fig unchanged]
    fig = go.Figure(data=[
        # ACS3
        go.Bar(
            name='ACS3 - Sail Mass',
            x=['ACS3'],
            y=[sail_weight],
            marker_color=COLOR_SAIL,
            hovertemplate='Sail Mass: %{y:.2f} kg'
        ),
        go.Bar(
            name='ACS3 - Booms Mass',
            x=['ACS3'],
            y=[acs3_booms_mass_kg],
            marker_color=COLOR_SMA_OR_BOOMS,
            hovertemplate='Booms Mass: %{y:.2f} kg'
        ),
        go.Bar(
            name='ACS3 - Other Subsystems',
            x=['ACS3'],
            y=[SAIL_BOOM_ENTIRE_MISSION_SUBSYSTEM_MINUS_BOOMS_AND_SAILS],
            marker_color=COLOR_SUBSYSTEMS,
            hovertemplate='Other Subsystems Mass: %{y:.2f} kg'
        ),

        # SMA-BOOM Basic
        go.Bar(
            name=f'{PRODUCT_NAME} Basic - Sail Mass',
            x=[f'{PRODUCT_NAME} Basic'],
            y=[sail_weight],
            marker_color=COLOR_SAIL,
            hovertemplate='Sail Mass: %{y:.2f} kg'
        ),
        go.Bar(
            name=f'{PRODUCT_NAME} Basic - SMA Mass',
            x=[f'{PRODUCT_NAME} Basic'],
            y=[basic_sma_mass_kg],
            marker_color=COLOR_SMA_OR_BOOMS,
            hovertemplate='SMA Mass: %{y:.2f} kg'
        ),
        go.Bar(
            name=f'{PRODUCT_NAME} Basic - Other Subsystems',
            x=[f'{PRODUCT_NAME} Basic'],
            y=[OTHER_SUBSECTION_PARTS_THAT_ARE_NEEDED],
            marker_color=COLOR_SUBSYSTEMS,
            hovertemplate='Other Subsystems Mass: %{y:.2f} kg'
        ),

        # SMA-BOOM Radial
        go.Bar(
            name=f'{PRODUCT_NAME} Radial - Sail Mass',
            x=[f'{PRODUCT_NAME} Radial'],
            y=[sail_weight],
            marker_color=COLOR_SAIL,
            hovertemplate='Sail Mass: %{y:.2f} kg'
        ),
        go.Bar(
            name=f'{PRODUCT_NAME} Radial - SMA Mass',
            x=[f'{PRODUCT_NAME} Radial'],
            y=[radial_sma_mass_kg],
            marker_color=COLOR_SMA_OR_BOOMS,
            hovertemplate='SMA Mass: %{y:.2f} kg'
        ),
        go.Bar(
            name=f'{PRODUCT_NAME} Radial - Other Subsystems',
            x=[f'{PRODUCT_NAME} Radial'],
            y=[OTHER_SUBSECTION_PARTS_THAT_ARE_NEEDED],
            marker_color=COLOR_SUBSYSTEMS,
            hovertemplate='Other Subsystems Mass: %{y:.2f} kg'
        )
    ])

    fig.update_layout(
        barmode='stack',
        title='Subsystem Mass Breakdown by Configuration',
        yaxis_title='Mass (kg)',
        xaxis_title='Configuration',
        height=500,
        width=1600,
        legend_title='Subsystem Components',
    )

    return [html.Pre(results_text), html.H3("Subsection Weights"), table], fig


if __name__ == '__main__':
    app.run(debug=True)
