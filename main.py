import pygame
import sys
from visualizer import Visualizer
from physics_model import PhysicsModel
from generator import VibrationGenerator
from energy_storage import EnergyStorage

def main():
    visualizer = Visualizer()
    physics_model = None
    generator = None
    energy_storage = None
    
    wind_speed = 0.0
    
    NUM_WINDOWS = 100 # Number of windows contributing to the battery charge
    total_energy_single_window = 0.0
    
    running = True
    while running:
        dt = visualizer.get_delta_time()
        
        for event in visualizer.get_events():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    action = visualizer.handle_mouse_click(event.pos)
                    if action == 'start':
                        params = visualizer.get_params()
                        physics_model = PhysicsModel(
                            mass=params['mass'],
                            damping=params['damping'],
                            stiffness=params['stiffness'],
                            area=params['area'],
                            max_elec_damping=params['max_elec_damping']
                        )
                        # The efficiency from the visualizer is passed to the generator
                        generator = VibrationGenerator(
                            piezo_const=params['piezo_const'],
                            resistance=params['resistance'],
                            efficiency=params['efficiency']
                        )
                        # Correction: The slider's value is already in Watts.
                        discharge_rate_in_watts = params['discharge_rate'] 
                        energy_storage = EnergyStorage(discharge_rate_watts=discharge_rate_in_watts)
                        wind_speed = 0.0
                        total_energy_single_window = 0.0
                    elif action == 'stop':
                        physics_model = None
                        generator = None
                        energy_storage = None
                        wind_speed = 0.0
                        total_energy_single_window = 0.0
                    elif action == 'wind_up' and visualizer.simulation_running:
                        wind_speed += 0.5
                        if wind_speed > 30: wind_speed = 30
                    elif action == 'wind_down' and visualizer.simulation_running:
                        wind_speed -= 1.0
                        if wind_speed < 0: wind_speed = 0
            elif event.type == pygame.MOUSEBUTTONUP:
                visualizer.handle_mouse_release()
            elif event.type == pygame.MOUSEMOTION:
                visualizer.handle_mouse_drag(event.pos)
        
        # Simulation logic
        if visualizer.simulation_running and physics_model and generator and energy_storage:
            # First, update the physical model, passing the energy storage for dynamic damping
            physics_model.update(wind_speed, dt, energy_storage)
            
            # Check for failure before calculating power
            if physics_model.failed:
                visualizer.simulation_running = False
                wind_speed = 0.0
                print("Simulation failed: Displacement limit exceeded.") # For console debugging
            
            # Now, calculate power using the newly updated attributes
            current_power = generator.calculate_power(physics_model.displacement, physics_model.velocity) 
            
            # And now, pass the power to the physical model's update function
            physics_model.update_power_metrics(current_power)

            # Calculate energy for a single window for this cycle and scale it to the total number of windows for the battery
            joules_this_cycle_single_window = generator.calculate_energy_this_cycle(dt)
            total_joules_generated_this_cycle = joules_this_cycle_single_window * NUM_WINDOWS

            energy_storage.update(dt, total_joules_generated_this_cycle)

            # Accumulate energy for the SINGLE window display
            total_energy_single_window += joules_this_cycle_single_window
            
        visualizer.draw_elements(wind_speed, physics_model, generator, energy_storage, total_energy_single_window)
        
    visualizer.quit()
    sys.exit()

if __name__ == "__main__":
    main()