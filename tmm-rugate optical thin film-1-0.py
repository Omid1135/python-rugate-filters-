import tmm
import math
import numpy as np
import matplotlib.pyplot as plt

# Function to plot refractive index profile
def plot_index_profile(x, n_layer, ax):
    """Plots the refractive index profile of a rugate film."""
    ax.plot(x, n_layer)
    ax.set_xlabel("Distance (nm)")
    ax.set_ylabel("Refractive Index")
    ax.set_title("Refractive Index Profile")
    ax.grid(True)

# Define layer parameters (example)
n_list = [1.0]  # Air (superstrate) - refractive index of air (typically 1.0)
d_list = [float('inf')]  # Prepend infinity for the layer before the film

# Design Parameters (adjust as needed)
target_wavelength = 532  # nm
num_layers = 20
high_index = 2.3  # Refractive index of high-index material (e.g., TiO2)
low_index = 1.45  # Refractive index of low-index material (e.g., SiO2)
substrate_index = 1.5  # Refractive index of substrate (e.g., glass)

# Calculate average refractive index
average_index = (high_index + low_index) / 2

# Calculate modulation amplitude
modulation_amplitude = (high_index - low_index) / 2

# Calculate film thickness for quarter-wave stack (adjust for desired finesse)
film_thickness_case1 = target_wavelength / (4 * np.sqrt(average_index * substrate_index)) * (1 + 0.1)  # Add a small margin
layer_thickness_case1 = film_thickness_case1 / num_layers
x_case1 = np.linspace(0, film_thickness_case1, num_layers)

# Design Case 1: Simple Sinusoidal Profile (reference)
n_layer_case1 = average_index + modulation_amplitude * np.sin(2 * np.pi * x_case1 / film_thickness_case1)

# Design Case 2: Apodized Sinusoidal Profile (improved performance)
film_thickness_case2 = film_thickness_case1  # Same film thickness
layer_thickness_case2 = layer_thickness_case1  # Same layer thickness
x_case2 = np.linspace(0, film_thickness_case2, num_layers)
apodization_width = 0.2 * film_thickness_case2  # Adjust apodization width

def apodize(x, amplitude, period, width):
    return amplitude * np.sin(2 * np.pi * x / period) * np.exp(-(x - period/2)**2 / (2*width**2))

n_layer_case2 = average_index + apodize(x_case2, modulation_amplitude, film_thickness_case2, apodization_width)

# Construct layer structures
n_list_case1 = n_list.copy()  # Create copies to avoid modifying original lists
n_list_case2 = n_list.copy()

n_list_case1.extend(n_layer_case1.tolist())
n_list_case2.extend(n_layer_case2.tolist())

# Create layer thicknesses (assuming equal thicknesses)
layer_thicknesses_case1 = [layer_thickness_case1] * num_layers
layer_thicknesses_case2 = [layer_thickness_case2] * num_layers

# Modify d_list to include infinities for air and substrate
d_list_case1 = [float('inf')] + layer_thicknesses_case1 + [float('inf')]
d_list_case2 = [float('inf')] + layer_thicknesses_case2 + [float('inf')]

# Add substrate refractive index and thickness (implicitly assumed to be infinite)
n_list_case1.append(substrate_index)
n_list_case2.append(substrate_index)

# Simulate and plot reflectance spectra (educational comparison)
wavelengths = np.linspace(300, 800, 500)  # Wavelength range for reflectance calculation (nm)

def plot_reflectance(n_list, d_list, label, ax):
    try:
        reflectances_vec = [tmm.coh_tmm('s', n_list, d_list, th_0=0, lam_vac=wavelength)['R'] for wavelength in wavelengths]
        ax.plot(wavelengths, reflectances_vec, label=label)
    except ValueError as e:
        print(f"Error encountered during TMM calculation for {label}: {e}")
        print("n_list:", n_list)
        print("d_list:", d_list)
        raise  # Re-raise the error for further debugging

# Create subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

# Plot refractive index profiles
plot_index_profile(x_case1, n_layer_case1, ax1)
plot_index_profile(x_case2, n_layer_case2, ax1)
ax1.legend(["Simple Sinusoidal", "Apodized Sinusoidal"])

# Plot reflectance spectra
plot_reflectance(n_list_case1, d_list_case1, "Simple Sinusoidal Profile", ax2)
plot_reflectance(n_list_case2, d_list_case2, "Apodized Sinusoidal Profile", ax2)
ax2.set_xlabel("Wavelength (nm)")
ax2.set_ylabel("Reflectance")
ax2.set_title("Reflectance Spectra of Rugate Filters")
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.show()
