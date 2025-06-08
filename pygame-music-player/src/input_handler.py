"""
Input handling module for iPod Classic interface.
Manages keyboard input and user interactions.
"""
import pygame


class InputHandler:
    """Handles all user input for the iPod Classic interface"""
    
    def __init__(self, config):
        self.config = config
        
        # Volume control state
        self.volume_control_active = False

    def handle_input(self, ui_state, callbacks):
        """
        Handle all input events
        
        Args:
            ui_state: Dictionary containing current UI state
            callbacks: Dictionary of callback functions for different actions
        
        Returns:
            Dictionary of actions to perform
        """
        actions = []
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                actions.append({"type": "quit"})
                continue
            
            # Check for song end event from PlaybackManager
            if callbacks.get("check_song_ended") and callbacks["check_song_ended"](event):
                actions.append({"type": "song_ended"})
                continue

            if event.type == pygame.KEYDOWN:
                # Handle volume control input
                if self.volume_control_active:
                    volume_action = self._handle_volume_control(event, callbacks)
                    if volume_action:
                        actions.append(volume_action)
                    continue

                # Handle video playback input
                if ui_state.get("current_menu") == "video_playing":
                    video_action = self._handle_video_input(event, callbacks)
                    if video_action:
                        actions.append(video_action)
                    continue

                # Handle regular navigation input
                nav_action = self._handle_navigation_input(event, ui_state)
                if nav_action:
                    actions.append(nav_action)
                
                # Handle action input
                action_input = self._handle_action_input(event, ui_state, callbacks)
                if action_input:
                    actions.append(action_input)
        
        return actions

    def _handle_volume_control(self, event, callbacks):
        """Handle volume control input"""
        if event.key == pygame.K_UP or event.key == pygame.K_w:
            if callbacks.get("adjust_volume"):
                callbacks["adjust_volume"](0.05)  # Increase volume
                return {"type": "refresh_settings"}
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            if callbacks.get("adjust_volume"):
                callbacks["adjust_volume"](-0.05)  # Decrease volume
                return {"type": "refresh_settings"}
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
            self.volume_control_active = False
            return {"type": "exit_volume_control"}
        return None

    def _handle_video_input(self, event, callbacks):
        """Handle video playback input"""
        if event.key == pygame.K_SPACE:
            # Toggle pause (handled by video player internally)
            return False
        elif event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
            # Stop video and return to menu
            return True
        return False

    def _handle_navigation_input(self, event, ui_state):
        """Handle navigation input (up/down/left/right)"""
        current_menu = ui_state.get("current_menu")
        
        if event.key == pygame.K_UP or event.key == pygame.K_w:
            return {"type": "navigate_up"}
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            return {"type": "navigate_down"}
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
            if current_menu == "cover_flow":
                return {"type": "cover_flow_left"}
            else:
                return {"type": "previous_song"}
        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            if current_menu == "cover_flow":
                return {"type": "cover_flow_right"}
            else:
                return {"type": "next_song"}
        return None

    def _handle_action_input(self, event, ui_state, callbacks):
        """Handle action input (select, back, play/pause)"""
        if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            return {"type": "select"}
        elif event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
            return {"type": "go_back"}
        elif event.key == pygame.K_p:
            # Play/pause toggle for music
            return {"type": "toggle_playback"}
        return None

    def set_volume_control_active(self, active):
        """Set volume control mode"""
        self.volume_control_active = active

    def is_volume_control_active(self):
        """Check if volume control is active"""
        return self.volume_control_active
    
    def handle_navigation(self, event):
        """Handle navigation input and return simple navigation commands"""
        if event.key in [pygame.K_UP, pygame.K_w]:
            return "up"
        elif event.key in [pygame.K_DOWN, pygame.K_s]:
            return "down"
        elif event.key in [pygame.K_LEFT, pygame.K_a]:
            return "left"
        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
            return "right"
        elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
            return "select"
        elif event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
            return "back"
        elif event.key == pygame.K_p:
            return "play_pause"
        return None
    
    def handle_volume_control(self, event, playback):
        """Handle volume control input"""
        if event.key in [pygame.K_UP, pygame.K_w]:
            new_volume = min(1.0, playback.get_volume() + 0.05)
            playback.set_volume(new_volume)
            return True
        elif event.key in [pygame.K_DOWN, pygame.K_s]:
            new_volume = max(0.0, playback.get_volume() - 0.05)
            playback.set_volume(new_volume)
            return True
        return False
    
    def handle_cover_flow_input(self, event):
        """Handle cover flow navigation input"""
        if event.key in [pygame.K_LEFT, pygame.K_a]:
            return "left"
        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
            return "right"
        return None
    
    def handle_video_input(self, event):
        """Handle video playback input and return True if video should be stopped"""
        if event.key == pygame.K_SPACE:
            # Toggle pause (handled by video player internally)
            return False
        elif event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
            # Stop video and return to menu
            return True
        return False
