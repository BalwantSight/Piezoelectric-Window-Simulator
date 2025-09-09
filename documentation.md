# Technical Documentation: Piezoelectric Window Simulator

## 1. Project Overview

This document provides a detailed technical explanation of the Piezoelectric Window Simulator. The project's goal is to model the physical phenomena involved in harvesting wind energy through the vibrations of a window panel using piezoelectric materials. This simulation serves as a conceptual prototype to evaluate the feasibility and potential energy output of such a system in an urban environment.

The model is built upon fundamental principles of mechanical vibrations, fluid dynamics, and electrical engineering, solved numerically using Python libraries like SciPy and NumPy.

---

## 2. Physical and Mathematical Model

The simulation is based on a second-order ordinary differential equation (ODE) that describes the motion of a damped harmonic oscillator under an external force.

### 2.1. The Governing Equation of Motion

The core of the physics engine solves the following equation, which represents the vertical or horizontal displacement ($y$) of the center of mass of the panel over time:

$$
m\frac{d^2y}{dt^2} + c_{total}\frac{dy}{dt} + ky = F_{wind}(t)
$$

Where:
-   $m$: **Mass** of the vibrating panel (kg).
-   $k$: **Stiffness** of the panel's supports (N/m).
-   $y$: **Displacement** from the equilibrium position (m).
-   $c_{total}$: **Total Damping Coefficient** (N·s/m), which is a composite of several effects described below.
-   $F_{wind}(t)$: **External Force** exerted by the wind as a function of time (N).

This differential equation is solved at each time step using the `scipy.integrate.odeint` function, which provides a robust and accurate numerical solution.

### 2.2. Wind Force Model ($F_{wind}$)

The force of the wind is the primary driver of the system. In this simulation, it's modeled as a sinusoidal force with added stochastic noise to represent turbulence.

-   **Amplitude:** The force's amplitude is based on the standard fluid dynamics pressure equation: $F_{amp} \propto \frac{1}{2}\rho A v^2$, where $\rho$ is air density, $A$ is the panel area, and $v$ is the wind speed.
-   **Frequency:** The excitation frequency is heuristically linked to the wind speed and the panel's natural resonant frequency. This ensures that higher wind speeds can induce vibrations closer to the resonance point, maximizing displacement.
-   **Turbulence:** A random noise component is added to the force to simulate the chaotic nature of urban wind, preventing the system from reaching an unrealistic, perfect steady-state oscillation.

### 2.3. Damping Model ($c_{total}$)

Damping is a critical factor that opposes motion and stabilizes the system. Our model uses a sophisticated composite damping coefficient to achieve higher realism:

$$
F_{damping} = c_{total}\dot{y} = (c_1 + c_2|\dot{y}| + c_{elec})\dot{y}
$$

1.  **Linear Mechanical Damping ($c_1$):** Represents internal friction and viscous losses in the material. It is a constant coefficient proportional to velocity ($\dot{y}$).
2.  **Quadratic Damping ($c_2$):** Represents aerodynamic drag, which becomes significant at higher vibration velocities. This force is proportional to the square of the velocity ($c_2\dot{y}^2$).
3.  **Dynamic Electrical Damping ($c_{elec}$):** This is the most innovative part of the model. When the piezoelectric material generates electricity, it extracts kinetic energy from the system, which manifests as a damping force. This damping is modeled as being **dynamic**:
    -   When the connected battery is empty (low state of charge), the electrical load on the generator is high, resulting in a **larger** electrical damping force ($c_{elec} \rightarrow c_{max}$).
    -   When the battery is full, the load is minimal, and the damping effect is **reduced** ($c_{elec} \rightarrow c_{min}$).
    This correctly models the physical principle that energy generation creates mechanical opposition.

### 2.4. Piezoelectric Generation Model

The conversion of mechanical vibration to electrical power is modeled as follows:

1.  **Voltage Generation:** The voltage ($V$) produced by the piezoelectric material is proportional to the rate of mechanical strain, which is directly related to the velocity of vibration ($\dot{y}$).
    $$ V \propto |\dot{y}| $$
2.  **Power Output:** The instantaneous electrical power ($P$) is calculated using Ohm's law, considering an electrical load resistance ($R$) and a generator efficiency factor ($\eta$).
    $$ P_{out} = \eta \frac{V^2}{R} $$
The model also includes realistic caps on the maximum voltage and power to prevent physical impossibilities at extreme velocities.

### 2.5. Energy Storage Model

The generated energy is stored in a central battery. The model uses a simple numerical integration:
$$ E_{new} = E_{old} + (P_{generated} - P_{discharge}) \cdot \Delta t $$
-   $P_{generated}$ is the sum of power from all windows in the system.
-   $P_{discharge}$ is a constant rate representing self-discharge or the consumption of a connected device.

---

## 3. Realism of the Model & Assumptions

This simulator is designed to be a realistic approximation of the physical phenomena, but it relies on certain assumptions and simplifications.

-   **Strengths in Realism:**
    -   **ODE Foundation:** The use of a second-order ODE is the standard, validated approach for modeling mechanical vibrations.
    -   **Composite Damping:** The inclusion of linear, quadratic, and dynamic electrical damping provides a much more nuanced and realistic model of the forces opposing motion than a simple linear damper.
    -   **Energy Conservation:** The link between energy generation and increased damping correctly reflects the principle of energy conservation.

-   **Assumptions and Simplifications:**
    -   **Single Degree of Freedom (SDOF):** The model simplifies the panel to a single point mass, ignoring complex vibrational modes (e.g., twisting, higher-order bending) that would occur in a real-world panel.
    -   **Simplified Wind Model:** The current wind force model is a heuristic approximation. Real-world wind interaction is a complex fluid dynamics problem that this model simplifies for computational efficiency.

---

## 4. Future Improvements for Enhanced Realism

To further increase the simulator's fidelity, the following advancements could be implemented:

1.  **Advanced Aerodynamic Modeling:**
    -   Replace the current wind model with a more sophisticated one that can simulate **Vortex-Induced Vibrations (VIV)**. This would involve calculating the Strouhal number to predict when the frequency of vortex shedding matches the panel's natural frequency, a primary cause of large-amplitude vibrations in structures.
    -   Incorporate models for other aeroelastic phenomena like **flutter**, which can occur at high wind speeds.

2.  **Control System Implementation:**
    -   Integrate a **PID (Proportional-Integral-Derivative) controller** to dynamically manage the system. For instance, the controller could adjust the electrical load resistance ($R$) in real-time to achieve **impedance matching**, maximizing the power transfer from the mechanical system to the electrical system.
    -   The PID could also serve as a safety mechanism, drastically increasing electrical damping if vibrations approach the material's physical failure limit.

3.  **Environmental Parameterization:**
    -   Allow the user to adjust environmental parameters like **air temperature and pressure (altitude)**. These factors affect air density ($\rho$), which is a key variable in the wind force calculation, making the simulation adaptable to different geographical locations.

4.  **Finite Element Method (FEM) Integration:**
    -   For ultimate realism, the SDOF model could be replaced with a **Finite Element Model** of the window panel. This would allow the simulation to capture multiple, complex modes of vibration and provide a much more accurate picture of mechanical stress and power generation across the panel's surface.