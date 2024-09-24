import numpy as np

# Material database (MPa)
materials = {
    'Steel': 250,
    'Aluminum': 150,
    'Titanium': 900,
    'Cast Iron': 300,
}

# Function to calculate von Mises stress based on diameter
def calculate_stresses(diameter, T, M, F):
    # Convert diameter to meters
    d = diameter / 1000  # Convert mm to meters
    c = d / 2
    
    # Polar Moment of Inertia (J)
    J = (np.pi * d**4) / 32
    
    # Second Moment of Area (I)
    I = (np.pi * d**4) / 64
    
    # Cross-sectional Area (A)
    A = (np.pi * d**2) / 4
    
    # Torsional Shear Stress (τ_t)
    tau_t = (T * c) / J
    
    # Bending Stress (σ_b)
    sigma_b = (M * c) / I
    
    # Axial Stress (σ_a)
    sigma_a = F / A
    
    # Von Mises Stress (σ_vm)
    sigma_vm = np.sqrt(sigma_a**2 + sigma_b**2 + 3 * tau_t**2)
    
    return sigma_vm

# Function to calculate shaft deflection (optional)
def calculate_deflection(L, d, M, E):
    # Moment of Inertia
    I = (np.pi * (d**4)) / 64  # m^4
    # Deflection formula for simply supported shaft with point load
    delta = (M * L**2) / (8 * E * I)  # m
    return delta

# Input Validation Function
def get_positive_input(prompt):
    while True:
        value = float(input(prompt))
        if value > 0:
            return value
        else:
            print("Please enter a positive value.")

# Material Selection
def select_material():
    print("\nAvailable materials:")
    for i, mat in enumerate(materials.keys()):
        print(f"{i+1}. {mat}")
    
    while True:
        choice = int(input("\nSelect the material by entering the number: "))
        if 1 <= choice <= len(materials):
            material = list(materials.keys())[choice - 1]
            return material, materials[material]
        else:
            print("Invalid choice. Please select a valid material.")

# Suggest modifications
def suggest_modifications(T, M, F, Sy, FoS_desired, current_kt):
    print("\nNo valid diameter found.")
    print("Suggested modifications to improve the design:\n")
    
    # Suggest increasing material yield strength
    stronger_materials = {mat: y for mat, y in materials.items() if y > Sy}
    if stronger_materials:
        print("1. Use a stronger material:")
        for mat, strength in stronger_materials.items():
            print(f"   - {mat} with yield strength: {strength} MPa")
    else:
        print("1. No stronger materials available in the current database.")
    
    # Suggest lowering loads or moments
    print("\n2. Reduce applied loads:")
    print(f"   - Reduce torque (T) by at least: {T * 0.8:.2f} Nm (suggest reducing by 20%)")
    print(f"   - Reduce bending moment (M) by at least: {M * 0.8:.2f} Nm (suggest reducing by 20%)")
    print(f"   - Reduce axial load (F) by at least: {F * 0.8:.2f} N (suggest reducing by 20%)")
    
    # Suggest lowering the stress concentration factor
    if current_kt > 1.0:
        print(f"\n3. Use design modifications to reduce stress concentration factor (Kt):")
        print(f"   - Current Kt: {current_kt:.2f}, Suggested Kt: {max(1.0, current_kt * 0.9):.2f} (reduce by 10%)")
    
    # Suggest adjusting factor of safety
    print(f"\n4. Reduce the desired factor of safety (FoS):")
    print(f"   - Current FoS: {FoS_desired}, Suggested FoS: {FoS_desired * 0.9:.2f} (reduce by 10%)")

# User Input
T = get_positive_input("Enter the applied torque (Nm): ")
M = get_positive_input("Enter the bending moment (Nm): ")
F = get_positive_input("Enter the axial load (N): ")
L = get_positive_input("Enter the shaft length (mm): ")
FoS_desired = get_positive_input("Enter the desired factor of safety: ")

material, Sy = select_material()
E = get_positive_input("Enter the material's Young's Modulus (GPa): ") * 1e9  # Convert to Pa

# Optional: Stress Concentration Factor
Kt = get_positive_input("Enter the stress concentration factor (e.g., 1.5 for keyways, 1.0 for no concentration): ")

# Loop to find the minimum required diameter
print("\nCalculating minimum shaft diameter...\n")

for d in np.arange(10, 200, 0.1):  # Diameter range in mm
    sigma_vm = calculate_stresses(d, T, M, F) * Kt  # Adjust for stress concentration
    FoS_actual = Sy / sigma_vm
    
    if FoS_actual >= FoS_desired:
        deflection = calculate_deflection(L / 1000, d / 1000, M, E)  # Length and diameter converted to meters
        print(f"\nMinimum Shaft Diameter: {d:.2f} mm")
        print(f"Von Mises Stress: {sigma_vm:.2f} MPa")
        print(f"Factor of Safety: {FoS_actual:.2f}")
        print(f"Deflection of Shaft: {deflection * 1000:.3f} mm")  # Convert deflection to mm
        print(f"Material: {material} (Yield Strength: {Sy} MPa)")
        break
else:
    # If no valid diameter is found, suggest modifications
    suggest_modifications(T, M, F, Sy, FoS_desired, Kt)
