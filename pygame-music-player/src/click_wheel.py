"""
Click Wheel module for iPod Classic interface.
Implements the iconic iPod Click Wheel with all its functionalities.
"""
import pygame
import math
import pygame.gfxdraw


class ClickWheel:
    """iPod Classic Click Wheel implementation"""
    
    # Click Wheel area height constant
    CLICK_WHEEL_AREA_HEIGHT = 162  # Height of the click wheel area
    def __init__(self, ui_config):
        self.ui_config = ui_config
        # Click Wheel dimensions and position adaptados a 358x162 (nueva area de Click Wheel)
        self.wheel_radius = 75  # Ajustado para la nueva altura (162px aprox)
        self.center_button_radius = 30 # Ajustado proporcionalmente
        self.wheel_center_x = self.ui_config.SCREEN_WIDTH // 2  # Centro del nuevo ancho (358/2 = 179)
        # Posicionar el Click Wheel en la parte inferior de la pantalla
        self.wheel_center_y = self.CLICK_WHEEL_AREA_HEIGHT // 2  # Centro vertical de la zona del Click Wheel
        
        # Colors
        self.wheel_color = (220, 220, 220)  # Light gray wheel
        self.wheel_border_color = (180, 180, 180)  # Darker gray border
        self.center_button_color = (255, 255, 255)  # White center button
        self.center_button_border = (160, 160, 160)  # Gray border
        self.button_pressed_color = (200, 200, 200)  # Darker when pressed
        self.highlight_color = (100, 150, 255)  # Blue highlight for active areas
        
        # Button areas (in degrees) - Ajustados para Click Wheel clásica
        self.menu_button_area = (60, 120)        # Arriba (Menu)
        self.play_pause_area = (240, 300)        # Abajo (Play/Pause)
        self.backward_area = (160, 200)          # Izquierda (<<) - Ajustado
        self.forward_area = (340, 20)            # Derecha (>>), wraparound - Ajustado
        
        # State tracking
        self.pressed_buttons = set()
        self.mouse_on_wheel = False
        self.last_wheel_angle = 0
        self.scroll_sensitivity = 2.0
        self.wheel_momentum = 0
        self.momentum_decay = 0.9
        
        # Touch tracking for scroll gestures
        self.touching_wheel = False
        self.last_touch_angle = 0
        self.scroll_accumulator = 0
        # Visual feedback
        self.button_highlight = None
        self.center_button_pressed = False
        self.was_center_pressed = False
        
    def handle_mouse_input(self, mouse_pos, event):
        """Handle mouse input for Click Wheel interaction"""
        actions = []
        
        # Check if mouse is over the wheel area
        dx = mouse_pos[0] - self.wheel_center_x
        dy = mouse_pos[1] - self.wheel_center_y
        distance_from_center = math.sqrt(dx * dx + dy * dy)
        
        # Handle center button
        if distance_from_center <= self.center_button_radius:
            # Handle center button press on MOUSEBUTTONDOWN
            if event.type == pygame.MOUSEBUTTONDOWN and not self.was_center_pressed:
                actions.append({"type": "select"})
            # Update state for drawing - check mouse button state directly after event processing
            # Use pygame.mouse.get_pressed() here to get current state for drawing
            self.center_button_pressed = pygame.mouse.get_pressed()[0] # Update state for drawing
            # Update was_center_pressed based on MOUSEBUTTONDOWN/UP
            if event.type == pygame.MOUSEBUTTONDOWN: self.was_center_pressed = True
            if event.type == pygame.MOUSEBUTTONUP: self.was_center_pressed = False

            # If mouse is released outside center button after being pressed inside, do nothing special
            # Only handle 'select' action on press down within the center.
            # This prevents accidental selections from scrolling gestures ending over the center button.
            return actions # Exit early if interaction is with the center button
        # Handle wheel area
        elif distance_from_center <= self.wheel_radius:
            self.mouse_on_wheel = True
            # Calculate angle (only if mouse is pressed on the wheel)
            # We need the angle on press to detect which button was intended
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.touching_wheel = True
                angle = math.atan2(dy, dx) * 180 / math.pi
                if angle < 0:
                    angle += 360
                self.last_touch_angle = angle
                self.button_highlight = self._get_button_area(angle) # Highlight button on press
                self.scroll_accumulator = 0 # Reset scroll on new press

            elif event.type == pygame.MOUSEBUTTONUP and self.touching_wheel:
                # Handle button press on MOUSEBUTTONUP IF it was pressed down on a button area
                # We need to recalculate the angle on release to check if it's still over the intended button area
                # This adds robustness against slight mouse movements between press and release.
                release_dx = mouse_pos[0] - self.wheel_center_x
                release_dy = mouse_pos[1] - self.wheel_center_y
                distance_from_center_release = math.sqrt(release_dx * release_dx + release_dy * release_dy)

                if distance_from_center_release <= self.wheel_radius: # Check if release is still on the wheel
                    release_angle = math.atan2(release_dy, release_dx) * 180 / math.pi
                    if release_angle < 0:
                        release_angle += 360
                    release_button_area = self._get_button_area(release_angle)

                    # Only trigger button action if release is over the SAME button area that was highlighted on press
                    # And if a button was actually highlighted on press (prevent scroll from triggering button)
                    if self.button_highlight is not None and release_button_area == self.button_highlight:
                         actions.append(self._get_button_action(self.button_highlight))

                self.touching_wheel = False
                self.button_highlight = None # Clear highlight on release
                self.scroll_accumulator = 0 # Reset scroll accumulator on release

            elif event.type == pygame.MOUSEMOTION and self.touching_wheel and pygame.mouse.get_pressed()[0]:
                 # Handle wheel scrolling WHILE mouse is pressed
                 # Calculate angle
                 angle = math.atan2(dy, dx) * 180 / math.pi
                 if angle < 0:
                     angle += 360
                 # Calculate angle difference for scrolling
                 angle_diff = angle - self.last_touch_angle
                 # Handle angle wraparound
                 if angle_diff > 180:
                     angle_diff -= 360
                 elif angle_diff < -180:
                     angle_diff += 360
                 # Accumulate scroll
                 self.scroll_accumulator += angle_diff
                 # Generate scroll events (adjust sensitivity)
                 scroll_threshold = 15 # Increased threshold for less sensitive scrolling
                 while abs(self.scroll_accumulator) >= scroll_threshold:
                     if self.scroll_accumulator > 0:
                         actions.append({"type": "scroll_down"})
                         self.scroll_accumulator -= scroll_threshold
                     else:
                         actions.append({"type": "scroll_up"})
                         self.scroll_accumulator += scroll_threshold
                 self.last_touch_angle = angle
                 self.button_highlight = None # Clear button highlight when scrolling starts/happens

        else:
            # Mouse is not on the wheel area
            self.mouse_on_wheel = False
            self.touching_wheel = False # Ensure touch state is reset
            self.button_highlight = None
            self.center_button_pressed = False
            self.scroll_accumulator = 0

        return actions
    
    def handle_keyboard_input(self, event):
        """Handle keyboard input as Click Wheel commands"""
        actions = []
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                actions.append({"type": "scroll_up"})
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                actions.append({"type": "scroll_down"})
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                actions.append({"type": "button_press", "button": "backward"})
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                actions.append({"type": "button_press", "button": "forward"})
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                actions.append({"type": "select"})
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
                actions.append({"type": "button_press", "button": "menu"})
            elif event.key == pygame.K_p:
                actions.append({"type": "button_press", "button": "play_pause"})
        
        return actions
    
    def _get_button_area(self, angle):
        """Determine which button area the angle falls into (acciones invertidas para MENU/PLAY)"""
        if self._angle_in_range(angle, self.menu_button_area):
            return "play_pause"  # Invertido para corregir el error reportado
        elif self._angle_in_range(angle, self.play_pause_area):
            return "menu"      # Invertido para corregir el error reportado
        elif self._angle_in_range(angle, self.forward_area):
            return "forward"
        elif self._angle_in_range(angle, self.backward_area):
            return "backward"
        return None
    
    def _angle_in_range(self, angle, range_tuple):
        """Check if angle is within a range, handling wraparound"""
        start, end = range_tuple
        if start <= end:
            return start <= angle <= end
        else:  # Wraparound case (e.g., 340 to 20 degrees)
            return angle >= start or angle <= end # Check if angle is >= start OR <= end
    
    def _get_button_action(self, button):
        """Get action for button press"""
        return {"type": "button_press", "button": button}
    
    def update(self):
        """Update Click Wheel state (for momentum, animations, etc.)"""
        # Apply momentum decay for smooth scrolling
        if abs(self.wheel_momentum) > 0.1:
            self.wheel_momentum *= self.momentum_decay
        else:
            self.wheel_momentum = 0
    def draw(self, screen):
        """Draw the Click Wheel on the screen"""
        # Draw background for the Click Wheel area
        wheel_bg_rect = pygame.Rect(0, 0, screen.get_width(), screen.get_height())
        pygame.draw.rect(screen, (30, 26, 20), wheel_bg_rect)  # Light gray background
        
        # Draw main wheel circle (antialiasing)
        pygame.gfxdraw.filled_circle(screen, self.wheel_center_x, self.wheel_center_y, self.wheel_radius, self.wheel_color)
        pygame.gfxdraw.aacircle(screen, self.wheel_center_x, self.wheel_center_y, self.wheel_radius, self.wheel_border_color)
        
        # Draw button area highlights
        self._draw_button_areas(screen)
        
        # Draw center button (antialiasing)
        center_color = self.button_pressed_color if self.center_button_pressed else self.center_button_color
        pygame.gfxdraw.filled_circle(screen, self.wheel_center_x, self.wheel_center_y, self.center_button_radius, center_color)
        pygame.gfxdraw.aacircle(screen, self.wheel_center_x, self.wheel_center_y, self.center_button_radius, self.center_button_border)
        
        # Draw center button border (extra thickness)
        pygame.gfxdraw.aacircle(screen, self.wheel_center_x, self.wheel_center_y, self.center_button_radius+1, self.center_button_border)
        
        # Draw button labels
        self._draw_button_labels(screen)
    
    def _draw_button_areas(self, screen):
        """Draw the four button areas around the wheel (resaltado correcto)"""
        if self.button_highlight:
            # Highlight the active button area based on the detected area, not the action name
            highlight_angles = {
                "menu": self.menu_button_area,
                "play_pause": self.play_pause_area, # Aunque la acción se invierta, usamos este rango para dibujar el highlight
                "forward": self.forward_area,
                "backward": self.backward_area
            }
            
            # Use the button_highlight name to find the correct visual angle range
            # Note: button_highlight comes from _get_button_area which might return inverted ACTION names.
            # We need to map the *returned action name* back to the *original visual area name* for highlighting.
            # Or, better, modify _get_button_area to return a visual area identifier.
            # Let's stick to the simpler patch for now: map the potentially inverted action name
            # back to the correct angle ranges for highlighting.

            # Instead of mapping action names to angles directly, let's map the intended button name
            # (which we can derive from the button_highlight string returned by _get_button_area)
            # back to the correct angle ranges for highlighting.
            # This requires knowing the *original* mapping of angles to visual areas.

            # A simpler approach given the current structure: just use the button_highlight string
            # returned by _get_button_area, and map it to the *correct visual angle* for highlighting.
            # Since _get_button_area returns the *action name*, and we inverted menu/play actions,
            # we need to map the *returned action name* to the *visual area angles*.

            # Let's define a mapping from the potentially inverted action names (returned by _get_button_area)
            # to the actual visual area angle ranges.
            visual_area_angles = {
                # If _get_button_area returned "play_pause", it was because the MENU area was clicked.
                "play_pause": self.menu_button_area, # When _get_button_area returns "play_pause", highlight the MENU visual area angles
                # If _get_button_area returned "menu", it was because the PLAY area was clicked.
                "menu": self.play_pause_area,      # When _get_button_area returns "menu", highlight the PLAY visual area angles
                
                # The forward and backward actions are not inverted, so their action name matches the visual area.
                "forward": self.forward_area,
                "backward": self.backward_area
            }

            if self.button_highlight in visual_area_angles:
                start_angle, end_angle = visual_area_angles[self.button_highlight]
                self._draw_arc_segment(screen, start_angle, end_angle, self.highlight_color)
    
    def _draw_arc_segment(self, screen, start_angle, end_angle, color):
        """Draw an arc segment for button highlighting"""
        # Convert angles to radians
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)
        
        # Create points for the arc
        points = []
        inner_radius = self.center_button_radius + 5
        outer_radius = self.wheel_radius - 5
        
        # Generate arc points
        angle_step = math.radians(5)  # 5-degree steps
        current_angle = start_rad
        
        while current_angle <= end_rad:
            # Outer arc point
            x_outer = self.wheel_center_x + outer_radius * math.cos(current_angle)
            y_outer = self.wheel_center_y + outer_radius * math.sin(current_angle)
            points.append((x_outer, y_outer))
            current_angle += angle_step
        
        # Add end point if needed
        if current_angle - angle_step < end_rad:
            x_outer = self.wheel_center_x + outer_radius * math.cos(end_rad)
            y_outer = self.wheel_center_y + outer_radius * math.sin(end_rad)
            points.append((x_outer, y_outer))
        
        # Inner arc points (reverse direction)
        current_angle = end_rad
        while current_angle >= start_rad:
            x_inner = self.wheel_center_x + inner_radius * math.cos(current_angle)
            y_inner = self.wheel_center_y + inner_radius * math.sin(current_angle)
            points.append((x_inner, y_inner))
            current_angle -= angle_step
        
        # Draw the polygon if we have enough points
        if len(points) >= 3:
            pygame.draw.polygon(screen, color, points)
    def _draw_button_labels(self, screen):
        """Draw labels for the four buttons (iPod Classic layout)"""
        # Use a safe font fallback
        try:
            font = self.ui_config.font_small
        except:
            font = pygame.font.Font(None, 14)  # Fallback font
            
        label_distance = self.wheel_radius - 15
        
        # MENU (arriba)
        menu_x = self.wheel_center_x
        menu_y = self.wheel_center_y - label_distance
        menu_text = font.render("MENU", True, (60, 60, 60))
        menu_rect = menu_text.get_rect(center=(menu_x, menu_y))
        screen.blit(menu_text, menu_rect)
        
        # PLAY/PAUSE (abajo)
        play_x = self.wheel_center_x
        play_y = self.wheel_center_y + label_distance
        play_text = font.render("PLAY", True, (60, 60, 60))
        play_rect = play_text.get_rect(center=(play_x, play_y))
        screen.blit(play_text, play_rect)
        
        # ATRÁS (izquierda)
        backward_x = self.wheel_center_x - label_distance
        backward_y = self.wheel_center_y
        backward_text = font.render("<<", True, (60, 60, 60))
        backward_rect = backward_text.get_rect(center=(backward_x, backward_y))
        screen.blit(backward_text, backward_rect)
        
        # ADELANTE (derecha)
        forward_x = self.wheel_center_x + label_distance
        forward_y = self.wheel_center_y
        forward_text = font.render(">>", True, (60, 60, 60))
        forward_rect = forward_text.get_rect(center=(forward_x, forward_y))
        screen.blit(forward_text, forward_rect)
        
        # SELECT (centro)
        center_text = font.render("SELECT", True, (80, 80, 80))
        center_rect = center_text.get_rect(center=(self.wheel_center_x, self.wheel_center_y))
        screen.blit(center_text, center_rect)
    
    def reset_state(self):
        """Reset Click Wheel state"""
        self.pressed_buttons.clear()
        self.touching_wheel = False
        self.button_highlight = None
        self.center_button_pressed = False
        self.scroll_accumulator = 0
        self.wheel_momentum = 0
        self.was_center_pressed = False
