class EnergyStorage:
    """
    Simulates energy storage in a central battery.
    """
    # The battery capacity has been reduced for a more evident visualization of the charge
    def __init__(self, capacity_joules=50000.0, discharge_rate_watts=5.0): # Equivalent to ~14 Wh
        self.capacity = capacity_joules
        self.stored_energy = 0.0
        self.state_of_charge = 0.0
        self.discharge_rate = discharge_rate_watts

    def update(self, dt, joules_to_add):
        """
        Adds energy and applies discharge for the current time step.
        """
        # First, apply the discharge
        joules_to_discharge = self.discharge_rate * dt
        self.stored_energy -= joules_to_discharge
        
        # Then, store the generated energy
        self.stored_energy += joules_to_add
        
        # Ensures the energy does not fall below zero or exceed capacity
        self.stored_energy = max(0, self.stored_energy)
        self.stored_energy = min(self.stored_energy, self.capacity)
        
        self.update_state_of_charge()

    def update_state_of_charge(self):
        """
        Calculates the battery's state of charge as a percentage.
        """
        self.state_of_charge = (self.stored_energy / self.capacity) * 100.0