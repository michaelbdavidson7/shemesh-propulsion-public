from dash import html
import dash_bootstrap_components as dbc


def get_planet_mission_card(hardcoded_sail_area, SMA_MASS_PER_M2, ACS3_BOOMS_MASS_PER_M2):
    sail_area = hardcoded_sail_area  # m²
    base_mass = 10  # kg

    # Mass calculations
    sma_mass = sail_area * SMA_MASS_PER_M2 
    acs3_mass = sail_area * ACS3_BOOMS_MASS_PER_M2 

    sma_total_mass = base_mass + sma_mass
    acs3_total_mass = base_mass + acs3_mass

    # Thrust (same for both)
    thrust = 2 * 4.56e-6 * sail_area  # Newtons

    # Acceleration
    a_sma = thrust / sma_total_mass
    a_acs3 = thrust / acs3_total_mass

    # Target Δv per mission
    missions = {
        "🌕 Moon": 3100,
        "✨Venus": 3500,
        "🔴 Mars": 4000
    }

    cards = []

    for planet, dv in missions.items():
        t_sma = dv / a_sma / 3600  # convert to hours
        t_acs3 = dv / a_acs3 / 3600
        percent_faster = ((t_acs3 - t_sma) / t_acs3) * 100

        cards.append(
            dbc.Card(
                dbc.CardBody([
                    html.H5(f"{planet} Transfer", className="card-title"),
                    html.P(f"Target Δv: {dv:.0f} m/s"),
                    html.P(f"SMA Solar Propulsion Hours: {t_sma:.1f}"),
                    html.P(f"ACS3 Solar Propulsion Hours: {t_acs3:.1f}"),
                    html.P(f"SMA is {percent_faster:.1f}% faster")
                ]),
                className="mb-3 shadow-sm"
            )
        )

    return dbc.Row([dbc.Col(card, width=4) for card in cards])
