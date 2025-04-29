import math
import matplotlib.pyplot as plt
import numpy as np

import pandas as pd
# ========================
# Constants
# ========================
ACS3_BOOM_MASS_PER_M = 23.43     # g/m
SMA_MASS_PER_M = 1.66            # g/m
SMA_MASS_PER_M = 3            # g/m, REFACTOR BASED ON COATINGS AND ADHESIVES
ACS3_SCALING_FACTOR = 3.13       # dimensionless
NUM_RADIAL_WIRES = 8
ACS3_SAIL_MASS_PER_M2 = 0.00425  # kg/m²
SAIL_BOOM_ENTIRE_MISSION_SUBSYSTEM_MINUS_BOOMS_AND_SAILS = 6.704
OTHER_SUBSECTION_PARTS_THAT_ARE_NEEDED = 3.704  # (6.704 - 3)

# 🎨 Colors
COLOR_SAIL = '#4169E1'          # Royal Blue
COLOR_SMA_OR_BOOMS = '#DC143C'  # Crimson Red
COLOR_SUBSYSTEMS = '#2F4F4F'    # Dark Slate Gray

# ========================
# Sail Areas to Analyze
# ========================
sail_areas = [80, 500, 1000, 2000, 4000, 6000, 8000]  # in m²

# ========================
# Mass Computation
# ========================
acs3_masses = []
basic_masses = []
radial_masses = []

for area in sail_areas:
    side = math.sqrt(area)
    perimeter = 4 * side
    radius = side / 2

    # Sail mass
    sail_mass = area * ACS3_SAIL_MASS_PER_M2  # kg

    # ACS3 booms mass
    boom_length = ACS3_SCALING_FACTOR * side
    acs3_booms_mass_kg = (boom_length * ACS3_BOOM_MASS_PER_M) / 1000

    # SMA basic perimeter wires
    basic_sma_length = perimeter + 2 * radius
    basic_sma_mass_kg = (basic_sma_length * SMA_MASS_PER_M) / 1000

    # SMA radial perimeter wires
    radial_length = NUM_RADIAL_WIRES * 2 * radius
    total_radial_length = radial_length + perimeter
    radial_sma_mass_kg = (total_radial_length * SMA_MASS_PER_M) / 1000

    # Final mass breakdowns
    acs3_total = [sail_mass, acs3_booms_mass_kg, SAIL_BOOM_ENTIRE_MISSION_SUBSYSTEM_MINUS_BOOMS_AND_SAILS]
    basic_total = [sail_mass, basic_sma_mass_kg, OTHER_SUBSECTION_PARTS_THAT_ARE_NEEDED]
    radial_total = [sail_mass, radial_sma_mass_kg, OTHER_SUBSECTION_PARTS_THAT_ARE_NEEDED]

    acs3_masses.append(acs3_total)
    basic_masses.append(basic_total)
    radial_masses.append(radial_total)

# ========================
# Static Stacked Bar Chart
# ========================
x = np.arange(len(sail_areas))  # x locations for groups
width = 0.25  # width of bars

fig, ax = plt.subplots(figsize=(14, 8))

def stack_bars(masses, offset, label_prefix):
    sails = [m[0] for m in masses]
    booms = [m[1] for m in masses]
    subsys = [m[2] for m in masses]

    ax.bar(x + offset, sails, width, label=f'{label_prefix} - Sail', color=COLOR_SAIL)
    ax.bar(x + offset, booms, width, bottom=sails, label=f'{label_prefix} - Booms/SMA', color=COLOR_SMA_OR_BOOMS)
    ax.bar(x + offset, subsys, width, bottom=np.array(sails) + np.array(booms), label=f'{label_prefix} - Subsystems', color=COLOR_SUBSYSTEMS)

stack_bars(acs3_masses, -width, "ACS3")
stack_bars(basic_masses, 0, "SSP-1 Basic")
stack_bars(radial_masses, width, "SSP-1 Radial")

# Labels and formatting
ax.set_ylabel('Mass (kg)')
ax.set_xlabel('Sail Area (m²)')
ax.set_title('Mass Breakdown vs Sail Area')
ax.set_xticks(x)
ax.set_xticklabels(sail_areas)
ax.legend(ncol=2)
ax.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()

# Save static bar graph
plt.savefig('mass_breakdown_stacked.png', dpi=300)
plt.show()

# ========================
# Mass Savings Calculation
# ========================

acs3_totals = [sum(m) for m in acs3_masses]
basic_totals = [sum(m) for m in basic_masses]
radial_totals = [sum(m) for m in radial_masses]

basic_savings_pct = [100 * (1 - b/a) for a, b in zip(acs3_totals, basic_totals)]
radial_savings_pct = [100 * (1 - r/a) for a, r in zip(acs3_totals, radial_totals)]

# ========================
# Plot Mass Savings
# ========================

fig2, ax2 = plt.subplots(figsize=(12, 6))

ax2.plot(sail_areas, basic_savings_pct, marker='o', label='SSP-1 Basic Savings', color=COLOR_SMA_OR_BOOMS)
ax2.plot(sail_areas, radial_savings_pct, marker='s', label='SSP-1 Radial Savings', color=COLOR_SAIL)

ax2.set_xlabel('Sail Area (m²)')
ax2.set_ylabel('Mass Savings (%)')
ax2.set_title('Mass Savings Compared to ACS3')
ax2.grid(True, linestyle='--', alpha=0.5)
ax2.legend()
plt.tight_layout()

# Save mass savings line graph
plt.savefig('mass_savings_vs_area.png', dpi=300)
plt.show()

# ========================
# CSV Export
# ========================

# Build a DataFrame
df = pd.DataFrame({
    'Sail Area (m²)': sail_areas,
    'ACS3 Total Mass (kg)': acs3_totals,
    'SSP-1 Basic Total Mass (kg)': basic_totals,
    'SSP-1 Radial Total Mass (kg)': radial_totals,
    'SSP-1 Basic Savings (%)': basic_savings_pct,
    'SSP-1 Radial Savings (%)': radial_savings_pct,
})

# Save to CSV
df.to_csv('mass_savings_summary.csv', index=False)

print("✅ Saved CSV: mass_savings_summary.csv")
