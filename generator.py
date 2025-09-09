import numpy as np

class VibrationGenerator:
    """
    Models the conversion of vibration to electrical energy more rigorously.
    Power is proportional to the VELOCITY of the deformation.
    """
    def __init__(self, piezo_const=15.0, resistance=100.0, max_voltage=100.0, efficiency=0.4):
        self.piezo_const = piezo_const # Material constant
        self.resistance = resistance   # Load resistance
        self.max_voltage = max_voltage # Maximum output voltage (V)
        self.power_output = 0.0
        self.efficiency = efficiency

    def calculate_power(self, displacement, velocity):
        """
        Calculates the simulated output power in Watts.
        The piezoelectric voltage is proportional to the rate of strain (velocity).
        Power = (Efficiency * Voltage^2) / Resistance.
        """
        # Limit the voltage for a more realistic model
        voltage = min(self.piezo_const * abs(velocity), self.max_voltage)
        
        # Apply a power limit to avoid extreme values
        power_unlimited = (voltage**2) / self.resistance
        self.power_output = min(power_unlimited, 10) * self.efficiency
        
        return self.power_output

    def calculate_energy_this_cycle(self, dt):
        """
        Calculates the energy generated in the current time step.
        """
        return self.power_output * dt