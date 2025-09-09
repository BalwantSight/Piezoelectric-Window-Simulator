import pygame
import numpy as np
from collections import deque

class Visualizer:
    """
    Handles the simulation's visualization with an interactive and reorganized interface.
    """
    def __init__(self, screen_size=(1400, 900)):
        pygame.init()
        self.screen_size = screen_size
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Piezoelectric Window Generator - Simulation")
        
        # Fonts
        self.font_title = pygame.font.Font(None, 40)
        self.font_subtitle = pygame.font.Font(None, 30)
        self.font_label = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)

        self.clock = pygame.time.Clock()
        self.simulation_running = False
        self.timer_started = False
        
        # Default parameters for sliders (now in SI units)
        self.params = {
            'mass': 10.0,
            'damping': 10.0,
            'stiffness': 100000.0,
            'area': 0.5,
            'max_elec_damping': 5.0,
            'efficiency': 0.4, # Corrected value to 0.4
            # New value for the discharge rate, more appropriate for low-power systems
            'discharge_rate': 0.003, # 3 mW
            # More realistic default values
            'piezo_const': 25.0,
            'resistance': 10000.0
        }
        
        # Slider definition and positioning (bottom left)
        # Grouped into a single box
        self.sliders = {
            'mass': Slider(80, 610, 250, 10, (1, 50), self.params['mass'], "Mass (kg)"),
            'damping': Slider(80, 680, 250, 10, (1, 50), self.params['damping'], "Damping (N·s/m)"),
            'stiffness': Slider(80, 750, 250, 10, (10000, 500000), self.params['stiffness'], "Stiffness (N/m)"),
            'area': Slider(80, 820, 250, 10, (0.05, 1.0), self.params['area'], "Area (m²)"),
            # Control sliders relocated to a single box
            'max_elec_damping': Slider(self.screen_size[0] - 420, 380, 250, 10, (0.5, 20.0), self.params['max_elec_damping'], "Max Elec. Damping (N·s/m)"),
            'efficiency': Slider(self.screen_size[0] - 420, 450, 250, 10, (0.01, 1.0), self.params['efficiency'], "Generator Efficiency"),
            'discharge_rate': Slider(self.screen_size[0] - 420, 520, 250, 10, (0.0, 0.07), self.params['discharge_rate'], "Battery Discharge (mW)"),
            'piezo_const': Slider(self.screen_size[0] - 420, 590, 250, 10, (1, 30), self.params['piezo_const'], "Piezo. Constant (V/m/s)"),
            'resistance': Slider(self.screen_size[0] - 420, 660, 250, 10, (1, 50000), self.params['resistance'], "Load Resistance (Ω)")
        }
        
        # Buttons (bottom right)
        self.start_button = Button(self.screen_size[0] // 2 - 150, self.screen_size[1] // 2 - 350, 300, 70, "Start Simulation", (50,205,50))
        self.stop_button = Button(self.screen_size[0] - 350, self.screen_size[1] - 150, 300, 70, "Stop Simulation", (220,20,60))
        
        # Wind controls - Relocated to the bottom center
        self.wind_buttons_x = self.screen_size[0] // 2 - 55
        self.wind_buttons_y = self.screen_size[1] // 2 + 320
        self.wind_up_button = Button(self.wind_buttons_x + 60, self.wind_buttons_y, 50, 50, "+", (100, 150, 200))
        self.wind_down_button = Button(self.wind_buttons_x, self.wind_buttons_y, 50, 50, "-", (100, 150, 200))

        # Power graph configuration
        self.graph_rect = pygame.Rect(self.screen_size[0] - 450, 70, 400, 200)
        self.graph_max_y = 10
        self.power_history_display_length = 200
        
        # New variable for visual scaling of displacement
        self.max_visual_displacement_pixels = 60 # pixels, a reasonable limit for window movement

    def get_beaufort_scale(self, wind_speed):
        """
        Determines the description of wind speed on the Beaufort scale.
        """
        if wind_speed < 0.3: return "Calm (0 BF)"
        elif wind_speed < 1.6: return "Light Air (1 BF)"
        elif wind_speed < 3.4: return "Light Breeze (2 BF)"
        elif wind_speed < 5.5: return "Gentle Breeze (3 BF)"
        elif wind_speed < 8.0: return "Moderate Breeze (4 BF)"
        elif wind_speed < 10.8: return "Fresh Breeze (5 BF)"
        elif wind_speed < 13.9: return "Strong Breeze (6 BF)"
        elif wind_speed < 17.2: return "Near Gale (7 BF)"
        elif wind_speed < 20.8: return "Gale (8 BF)"
        elif wind_speed < 24.5: return "Strong Gale (9 BF)"
        elif wind_speed < 28.5: return "Storm (10 BF)"
        elif wind_speed < 32.7: return "Violent Storm (11 BF)"
        else: return "Hurricane (12 BF)"

    def draw_elements(self, wind_speed, physics_model, generator, energy_storage, total_energy_single_window):
        # Dark background
        self.screen.fill((30, 30, 30))
        
        title = self.font_title.render("Piezoelectric Window Generator Simulation", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_size[0] // 2, 50))
        self.screen.blit(title, title_rect)

        # Always draw the parameter boxes
        self.draw_sliders()

        # Draw the simulation part only if it is active
        if self.simulation_running:
            self.draw_window_simulation(physics_model)
            self.draw_data_panel(wind_speed, physics_model, generator, energy_storage, total_energy_single_window)
            self.draw_power_graph(physics_model.power_history)
            self.draw_wind_controls(wind_speed)
            self.stop_button.draw(self.screen)
            # New: Draw a warning if the system has failed
            if physics_model and physics_model.failed:
                warning_text = self.font_title.render("SYSTEM FAILURE: DISPLACEMENT LIMIT EXCEEDED", True, (255, 0, 0))
                warning_rect = warning_text.get_rect(center=(self.screen_size[0] // 2, self.screen_size[1] // 2))
                self.screen.blit(warning_text, warning_rect)
        else:
            # In configuration mode, the start button is displayed
            self.start_button.draw(self.screen)
            # And the dynamic elements of the simulation are hidden, although the static boxes are kept.
            # You can optionally "draw" static elements to maintain visual consistency
            # For example, a static window without animation and empty data panels.
            self.draw_static_elements()
        
        pygame.display.flip()

    def draw_static_elements(self):
        # Draws the window and panels with initial values
        # This prevents the "AttributeError: 'NoneType' object has no attribute 'displacement'" error
        # when the simulation has not yet started.
        
        # Static window
        window_width = 400
        window_height = 500
        window_x = self.screen_size[0] // 2 - window_width // 2
        window_y = self.screen_size[1] // 2 - window_height // 2
        pygame.draw.rect(self.screen, (180, 200, 220, 150), (window_x, window_y, window_width, window_height), border_radius=10)
        pygame.draw.rect(self.screen, (50, 50, 50), (window_x, window_y, window_width, window_height), 5, border_radius=10)
        
        # Static data panels
        self.draw_data_panel(0, None, None, None, 0)
        
        # Static graph
        self.draw_power_graph(deque(maxlen=200))

        # Static wind controls
        self.draw_wind_controls(0)
    
    def draw_sliders(self):
        # Draw box for physical parameters
        # Width modified from 300 to 350
        physics_panel = pygame.Rect(50, 540, 350, 320)
        pygame.draw.rect(self.screen, (50, 50, 50), physics_panel, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 100), physics_panel, 2, border_radius=10)
        
        # Modified label
        subtitle_physics = self.font_subtitle.render("Piezoelectric Panel Parameters", True, (255, 255, 255))
        self.screen.blit(subtitle_physics, (physics_panel.x + 10, physics_panel.y + 10))
        
        # Passes the simulation state so the slider can decide whether to draw in active or inactive mode
        self.sliders['mass'].draw(self.screen, self.simulation_running)
        self.sliders['damping'].draw(self.screen, self.simulation_running)
        self.sliders['stiffness'].draw(self.screen, self.simulation_running)
        self.sliders['area'].draw(self.screen, self.simulation_running)

        # Draw box for the control parameter
        control_panel = pygame.Rect(self.screen_size[0] - 450, 310, 400, 420) # Height modified for new sliders
        pygame.draw.rect(self.screen, (50, 50, 50), control_panel, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 100), control_panel, 2, border_radius=10)

        subtitle_control = self.font_subtitle.render("Control Parameters", True, (255, 255, 255))
        self.screen.blit(subtitle_control, (control_panel.x + 10, control_panel.y + 10))

        self.sliders['max_elec_damping'].draw(self.screen, self.simulation_running)
        self.sliders['efficiency'].draw(self.screen, self.simulation_running)
        self.sliders['discharge_rate'].draw(self.screen, self.simulation_running)
        self.sliders['piezo_const'].draw(self.screen, self.simulation_running)
        self.sliders['resistance'].draw(self.screen, self.simulation_running)

    def draw_wind_controls(self, wind_speed):
        # Draw wind controls
        self.wind_up_button.draw(self.screen)
        self.wind_down_button.draw(self.screen)
        
        wind_title = self.font_label.render("Configure Wind Speed", True, (200, 200, 200))
        wind_title_rect = wind_title.get_rect(center=(self.screen_size[0] // 2, self.wind_buttons_y + 70))
        self.screen.blit(wind_title, wind_title_rect)

    def draw_window_simulation(self, physics_model):
        window_width = 400
        window_height = 500
        window_x = self.screen_size[0] // 2 - window_width // 2
        window_y = self.screen_size[1] // 2 - window_height // 2
        
        # New robust visual scaling
        # Clamp the displacement to a reasonable range for visual stability
        clamped_displacement = np.clip(physics_model.displacement, -0.005, 0.005)
        # Map the clamped physical displacement (in meters) to pixels
        displacement_factor = int(clamped_displacement / 0.005 * self.max_visual_displacement_pixels)
        
        outer_panel_rect = pygame.Rect(window_x + displacement_factor, window_y, window_width, window_height)
        pygame.draw.rect(self.screen, (100, 150, 200), outer_panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, (50, 50, 50), outer_panel_rect, 5, border_radius=10)
        
        inner_panel_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
        pygame.draw.rect(inner_panel_surface, (180, 200, 220, 150), inner_panel_surface.get_rect(), border_radius=10)
        pygame.draw.rect(inner_panel_surface, (50, 50, 50), inner_panel_surface.get_rect(), 5, border_radius=10)
        self.screen.blit(inner_panel_surface, (window_x, window_y))

        panel_text = self.font_label.render("Outer Piezoelectric Panel", True, (200, 200, 200))
        text_rect = panel_text.get_rect(center=(outer_panel_rect.centerx, outer_panel_rect.top - 30))
        self.screen.blit(panel_text, text_rect)
        
        panel_text_inner = self.font_label.render("Inner Panel (Structural)", True, (200, 200, 200))
        text_rect_inner = panel_text_inner.get_rect(center=(window_x + window_width // 2, window_y + window_height + 30))
        self.screen.blit(panel_text_inner, text_rect_inner)

    def draw_data_panel(self, wind_speed, physics_model, generator, energy_storage, total_energy_single_window):
        panel_x = 50
        panel_y = 75
        panel_width = 420
        panel_height = 380 
        
        pygame.draw.rect(self.screen, (50, 50, 50), (panel_x, panel_y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 100), (panel_x, panel_y, panel_width, panel_height), 2, border_radius=10)

        # Center the title
        title_surf = self.font_subtitle.render("SIMULATION DATA", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(panel_x + panel_width / 2, panel_y + 35))
        self.screen.blit(title_surf, title_rect)
        
        data_y_start = panel_y + 20
        
        # Checks are added to avoid errors
        if physics_model and generator and energy_storage:
            self.draw_info_value(f"Time Elapsed: {physics_model.time:.2f} s", (panel_x + 20, data_y_start + 40))
            self.draw_info_value(f"Wind Speed: {wind_speed:.2f} m/s", (panel_x + 20, data_y_start + 70))
            beaufort_desc = self.get_beaufort_scale(wind_speed)
            self.draw_info_value(f"({beaufort_desc})", (panel_x + 20, data_y_start + 95))
            self.draw_info_value(f"Resonant Frequency: {physics_model.resonant_frequency:.2f} Hz", (panel_x + 20, data_y_start + 130))
            self.draw_info_value(f"Displacement: {physics_model.displacement * 1000:.4f} mm", (panel_x + 20, data_y_start + 160))
            self.draw_info_value(f"Instantaneous Power: {generator.power_output * 1000:.4f} mW", (panel_x + 20, data_y_start + 190))
            self.draw_info_value(f"Average Power (5s): {physics_model.average_power:.4f} mW", (panel_x + 20, data_y_start + 220))
            self.draw_info_value(f"Accumulated Energy (one window): {total_energy_single_window:.4f} Joules", (panel_x + 20, data_y_start + 250))
            
            # Centered battery section
            battery_y_start = data_y_start + 280
            pygame.draw.line(self.screen, (150, 150, 150), (panel_x, battery_y_start), (panel_x + panel_width, battery_y_start), 1)

            battery_label_text = "Battery Energy"
            system_text = "(System of 100 double-panel piezoelectric windows)"
            energy_value_text = f"{energy_storage.stored_energy / 1000:.4f} kJ ({energy_storage.capacity / 1000:.0f} kJ)"

            battery_label_surf = self.font_label.render(battery_label_text, True, (255, 255, 255))
            system_surf = self.font_small.render(system_text, True, (200, 200, 200))

            # Logic to change the battery energy color
            battery_color = (0, 255, 0) if energy_storage.stored_energy > 0 else (255, 0, 0)
            energy_value_surf = self.font_label.render(energy_value_text, True, battery_color)
            
            battery_label_rect = battery_label_surf.get_rect(center=(panel_x + panel_width / 2, battery_y_start + 20))
            system_rect = system_surf.get_rect(center=(panel_x + panel_width / 2, battery_y_start + 45))
            energy_value_rect = energy_value_surf.get_rect(center=(panel_x + panel_width / 2, battery_y_start + 70))

            self.screen.blit(battery_label_surf, battery_label_rect)
            self.screen.blit(system_surf, system_rect)
            self.screen.blit(energy_value_surf, energy_value_rect)

            # Added new practical energy equivalences
            num_phone_charges = energy_storage.stored_energy / 5000.0 # 5000 Joules per charge
            num_led_hours = energy_storage.stored_energy / 36000.0 # 36000 Joules per hour for a 10W LED
            # New example: Wireless IoT Sensor
            num_sensor_sends = energy_storage.stored_energy / 1.944 # 1.944 Joules per send
            
            # Logic to change the color to red or green depending on the value
            # Now the condition uses round(value, 3) to match the display format.
            led_color = (0, 255, 0) if round(num_led_hours, 3) > 0 else (255, 0, 0)
            phone_color = (0, 255, 0) if round(num_phone_charges, 3) > 0 else (255, 0, 0)
            sensor_color = (0, 255, 0) if round(num_sensor_sends, 3) > 0 else (255, 0, 0)

            # Display order: LED Hours -> Phone Charges -> IoT Sensor Sends
            self.draw_info_value(f"~{num_led_hours:.3f} LED Hours", (panel_x + 20, battery_y_start + 95), color=led_color)
            self.draw_info_value(f"~{num_phone_charges:.3f} Phone Charges", (panel_x + 20, battery_y_start + 120), color=phone_color)
            self.draw_info_value(f"~{num_sensor_sends:.3f} IoT Sensor Sends", (panel_x + 20, battery_y_start + 145), color=sensor_color)
        else:
            # Draws static/empty data in configuration mode
            self.draw_info_value("Time Elapsed: --", (panel_x + 20, data_y_start + 40))
            self.draw_info_value("Wind Speed: --", (panel_x + 20, data_y_start + 70))
            self.draw_info_value("(--)", (panel_x + 20, data_y_start + 95))
            self.draw_info_value(f"Resonant Frequency: --", (panel_x + 20, data_y_start + 130))
            self.draw_info_value(f"Displacement: --", (panel_x + 20, data_y_start + 160))
            self.draw_info_value(f"Instantaneous Power: --", (panel_x + 20, data_y_start + 190))
            self.draw_info_value(f"Average Power (5s): --", (panel_x + 20, data_y_start + 220))
            self.draw_info_value(f"Accumulated Energy: --", (panel_x + 20, data_y_start + 250))
            
            # The equivalences are drawn outside the conditional so they always appear
            battery_y_start = data_y_start + 280
            pygame.draw.line(self.screen, (150, 150, 150), (panel_x, battery_y_start), (panel_x + panel_width, battery_y_start), 1)
            
            # "Battery Energy" text
            battery_label_text = "Battery Energy"
            battery_label_surf = self.font_label.render(battery_label_text, True, (255, 255, 255))
            battery_label_rect = battery_label_surf.get_rect(center=(panel_x + panel_width / 2, battery_y_start + 20))
            self.screen.blit(battery_label_surf, battery_label_rect)

            # "(--) kJ" text adjusted on the Y position
            self.draw_info_value("(--.0000) kJ (1000 kJ)", (panel_x + 20, battery_y_start + 45))

            self.draw_info_value("~ -- LED Hours", (panel_x + 20, battery_y_start + 95))
            self.draw_info_value("~ -- Phone Charges", (panel_x + 20, battery_y_start + 120))
            self.draw_info_value("~ -- IoT Sensor Sends", (panel_x + 20, battery_y_start + 145))


    def draw_power_graph(self, power_history):
        pygame.draw.rect(self.screen, (50, 50, 50), self.graph_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 100), self.graph_rect, 2, border_radius=10)

        graph_title = self.font_subtitle.render("Instantaneous Power (mW)", True, (255, 255, 255))
        self.screen.blit(graph_title, (self.graph_rect.x + 10, self.graph_rect.y + 10))

        if len(power_history) < 2:
            return

        points = []
        max_power_val = max(power_history) if len(power_history) > 0 else self.graph_max_y
        
        for i, val in enumerate(power_history):
            x = self.graph_rect.x + (i / (self.power_history_display_length - 1)) * self.graph_rect.width
            y_scaled = (val / (max_power_val if max_power_val > 0 else self.graph_max_y)) * self.graph_rect.height * 0.8
            y = self.graph_rect.y + self.graph_rect.height - y_scaled - 10
            points.append((x, y))
        
        if len(points) > 1:
            pygame.draw.lines(self.screen, (0, 120, 255), False, points, 2)

        max_val_label = self.font_small.render(f"{max_power_val:.3f} mW", True, (200, 200, 200))
        self.screen.blit(max_val_label, (self.graph_rect.x + self.graph_rect.width - max_val_label.get_width() - 5, self.graph_rect.y + 20))

    def draw_info_title(self, text, position):
        surface = self.font_subtitle.render(text, True, (255, 255, 255))
        self.screen.blit(surface, position)

    def draw_info_value(self, text, position, color=(200, 200, 200)):
        # Adds the color parameter for control
        surface = self.font_label.render(text, True, color)
        self.screen.blit(surface, position)

    def get_delta_time(self):
        if self.timer_started:
            return self.clock.tick(60) / 1000.0
        return 0

    def get_events(self):
        return pygame.event.get()

    def handle_mouse_click(self, pos):
        if not self.simulation_running:
            if self.start_button.is_clicked(pos):
                self.simulation_running = True
                return 'start'
        else:
            if self.stop_button.is_clicked(pos):
                self.simulation_running = False
                self.timer_started = False
                return 'stop'
            elif self.wind_up_button.is_clicked(pos):
                self.timer_started = True
                return 'wind_up'
            elif self.wind_down_button.is_clicked(pos):
                self.timer_started = True
                return 'wind_down'
        
        # This loop now only runs if the simulation is not in progress
        if not self.simulation_running:
            for slider in self.sliders.values():
                if slider.rect.collidepoint(pos):
                    slider.is_held = True

    def handle_mouse_release(self):
        for slider in self.sliders.values():
            slider.is_held = False

    def handle_mouse_drag(self, pos):
        for name, slider in self.sliders.items():
            if slider.is_held:
                new_value = slider.update(pos)
                self.params[name] = new_value
                return 'update_params'
        return None

    def get_params(self):
        return self.params
        
    def quit(self):
        pygame.quit()

class Slider:
    def __init__(self, x, y, width, height, val_range, default_val, label_text):
        self.rect = pygame.Rect(x, y, width, height)
        self.val_range = val_range
        self.value = default_val
        self.label_text = label_text
        self.is_held = False
        self.font = pygame.font.Font(None, 24)
        
        # Initial slider position
        # Correction: Ensures the default value is within the slider's range to avoid errors
        default_val = max(self.val_range[0], min(self.val_range[1], default_val))
        self.slider_pos = x + int(width * (default_val - val_range[0]) / (val_range[1] - val_range[0]))

    def draw(self, screen, is_locked):
        # Selects the color of the text and the knob according to the locked state
        if is_locked:
            text_color = (120, 120, 120)
            knob_color = (80, 80, 80)
            track_color = (150, 150, 150)
        else:
            text_color = (255, 255, 255)
            knob_color = (100, 100, 100)
            track_color = (200, 200, 200)

        pygame.draw.rect(screen, track_color, self.rect, border_radius=5)
        pygame.draw.circle(screen, knob_color, (self.slider_pos, self.rect.centery), 8)
        
        if "Efficiency" in self.label_text:
            label = self.font.render(f"{self.label_text}: {self.value * 100:.0f}%", True, text_color)
        elif "mW" in self.label_text:
            label = self.font.render(f"{self.label_text}: {self.value * 1000:.1f}", True, text_color)
        else:
            label = self.font.render(f"{self.label_text}: {self.value:.2f}", True, text_color)
        
        screen.blit(label, (self.rect.x, self.rect.y - 25))

    def update(self, pos):
        self.slider_pos = max(self.rect.left, min(pos[0], self.rect.right))
        self.value = self.val_range[0] + (self.slider_pos - self.rect.left) / self.rect.width * (self.val_range[1] - self.val_range[0])
        return self.value

class Button:
    def __init__(self, x, y, width, height, text, color=(150, 150, 150)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, 36)
        self.color = color
        self.hover_color = tuple(min(255, c + 30) for c in color)

    def draw(self, screen):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            current_color = self.hover_color
        else:
            current_color = self.color
        pygame.draw.rect(screen, current_color, self.rect, border_radius=5)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)