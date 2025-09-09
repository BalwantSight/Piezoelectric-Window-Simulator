import numpy as np
from scipy.integrate import odeint
from collections import deque # For power history

class PhysicsModel:
    """
    Models the physics of the glass panel's vibration more rigorously.
    """
    def __init__(self, mass=10.0, damping=10.0, stiffness=100000.0, area=0.5, max_elec_damping=5.0):
        self.m = mass          # Panel mass (kg)
        self.c1 = damping      # Linear damping coefficient (N·s/m)
        self.c2 = 0.5          # Quadratic damping coefficient for added realism
        self.max_c_elec = max_elec_damping # Maximum electrical damping coefficient (N·s/m)
        self.c_elec = 0.0      # Dynamic electrical damping
        self.k = stiffness     # Stiffness constant (N/m)
        self.A = area          # Window area (m^2)
        
        self.state = [0.0, 0.0]  # [displacement, velocity]
        self.time = 0.0
        self.wind_speed = 0.0
        self.displacement = 0.0 # Initialize
        self.velocity = 0.0     # Initialize

        # New: Physical limit for displacement
        self.max_displacement = 0.01 # 10 mm as a fail-safe limit
        self.failed = False # State variable for system failure
        
        self.damping_ratio = self._calculate_damping_ratio()
        self.resonant_frequency = self._calculate_resonant_frequency() # Calculate resonant frequency

        self.power_history = deque(maxlen=200) # History for the graph
        self.avg_power_window = deque(maxlen=60 * 5) # 5-second window for average power (60 FPS * 5s)
        self.average_power = 0.0

    def _calculate_damping_ratio(self):
        """
        Calculates the damping ratio of the system.
        ζ = c / (2 * sqrt(k*m))
        """
        if self.k > 0 and self.m > 0:
            return self.c1 / (2 * np.sqrt(self.k * self.m))
        return 0.0
    
    def _calculate_resonant_frequency(self):
        """
        Calculates the natural resonant frequency of the system, including damping.
        """
        damping_ratio = self._calculate_damping_ratio()
        if damping_ratio >= 1:
            return 0.0 # Overdamped system, no resonance
        
        if self.m > 0 and self.k > 0:
            omega_n = np.sqrt(self.k / self.m)
            omega_d = omega_n * np.sqrt(1 - damping_ratio**2)
            return omega_d / (2 * np.pi)
        return 0.0

    def _vibration_equation(self, state, t):
        y, v = state
        
        # New: If the system has failed, there is no more vibration
        if self.failed:
            return [0, 0]

        if self.wind_speed <= 0:
            return [0, 0]

        # Wind force model with random fluctuations (turbulence)
        # Note: This is a simplified model. A more advanced version could include
        # a vortex shedding model for more realistic resonance at certain speeds.
        force_amplitude = 0.5 * 1.225 * self.wind_speed**2 * self.A * 0.1
        
        wind_excitation_frequency = self.wind_speed * 0.3 + self.resonant_frequency * 0.1
        noise = (np.random.rand() - 0.5) * force_amplitude * 0.2
        
        F_external = force_amplitude * np.sin(2 * np.pi * wind_excitation_frequency * self.time) + noise

        # More realistic damping: linear + quadratic (air resistance)
        F_damping = self.c1 * v + self.c2 * v**2 * np.sign(v)

        # Force from electrical generation (electrical damping)
        F_elec = self.c_elec * v

        F_stiffness = self.k * y
        
        dy_dt = v
        dv_dt = (F_external - F_damping - F_elec - F_stiffness) / self.m
        
        return [dy_dt, dv_dt]

    def update(self, wind_speed, dt, energy_storage=None):
        """
        Updates the physical state (displacement and velocity) of the model.
        Also dynamically adjusts electrical damping.
        """
        if self.failed:
            self.wind_speed = 0.0
            self.displacement = 0.0
            self.velocity = 0.0
            return
            
        self.wind_speed = wind_speed
        
        # Dynamically adjust electrical damping based on battery charge (gradual model)
        if energy_storage:
            charge_level = energy_storage.state_of_charge
            # Smoothly transition from max_c_elec (empty) to min_c_elec (full)
            min_c_elec = 0.5
            self.c_elec = self.max_c_elec * (1 - charge_level / 100.0) + min_c_elec
        
        # Recalculate frequency if parameters change
        self.damping_ratio = self._calculate_damping_ratio()
        self.resonant_frequency = self._calculate_resonant_frequency()
            
        if self.wind_speed > 0:
            time_span = [0, dt]
            self.state = odeint(self._vibration_equation, self.state, time_span)[-1]
        else:
            self.state = [0.0, 0.0]

        self.time += dt
        
        self.displacement, self.velocity = self.state

        # New: Check for physical failure
        if abs(self.displacement) > self.max_displacement:
            self.failed = True

    def update_power_metrics(self, current_power):
        """
        Updates the history and average of the generated power.
        """
        # Update power history for the graph
        self.power_history.append(current_power * 1000) # In mW
        
        # Update average power
        self.avg_power_window.append(current_power * 1000)
        self.average_power = sum(self.avg_power_window) / len(self.avg_power_window) if len(self.avg_power_window) > 0 else 0.0