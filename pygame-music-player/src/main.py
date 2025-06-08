import pygame
# Import our modular components
from database import MusicDatabase
from playback import PlaybackManager
from ui_config import UIConfig
from menu_manager import MenuManager
from renderer import iPodRenderer
from video_player import VideoPlayer
from cover_flow import CoverFlow
from input_handler import InputHandler
from music_controller import MusicController
from wifi_manager import WiFiManager
from click_wheel import ClickWheel
from pathlib import Path

# Importar configuración de Pi Zero si está disponible
try:
    import sys
    import os
    # Agregar el directorio padre al path para importar pi_zero_config
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from pi_zero_config import is_raspberry_pi_zero, apply_pi_zero_config
    PI_ZERO_AVAILABLE = True
except ImportError:
    PI_ZERO_AVAILABLE = False
    print("ℹ️  Configuración de Pi Zero no disponible")

class iPodClassicUI:
    """Main iPod Classic UI application using modular components"""
    
    def __init__(self):
        # Aplicar configuración de Pi Zero si está disponible
        if PI_ZERO_AVAILABLE and is_raspberry_pi_zero():
            print("🥧 Raspberry Pi Zero detectado - Aplicando optimizaciones...")
            pi_config = apply_pi_zero_config()
            # Aplicar configuración optimizada a UIConfig
            os.environ['PI_ZERO_MODE'] = '1'
        
        pygame.init()
          # Initialize UI configuration
        self.ui_config = UIConfig()
        
        # Set up display
        self.screen = pygame.display.set_mode((self.ui_config.SCREEN_WIDTH, self.ui_config.SCREEN_HEIGHT))
        pygame.display.set_caption("iPod Classic")
        
        # Initialize core components
        self.db = MusicDatabase(db_path="./ipod_music_library.db")
        self.playback = PlaybackManager(volume_change_callback=self.on_volume_changed)
          # Initialize modular components
        self.renderer = iPodRenderer(self.screen, self.ui_config)
        self.video_player = VideoPlayer(self.ui_config)
        self.cover_flow = CoverFlow(self.ui_config, self.db)
        self.input_handler = InputHandler(self.ui_config)
        self.music_controller = MusicController(self.db, self.playback)
        self.wifi_manager = WiFiManager()
        self.click_wheel = ClickWheel(self.ui_config)
        self.menu_manager = MenuManager(self.db,
                                        scan_video_files_callback=self.video_player.scan_video_files)
        
        # Application state
        self.running = True        
        self.clock = pygame.time.Clock()
        
        # Current state
        self.current_menu = "main"
        self.menu_stack = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.current_song_data = None
        
        # Settings state
        self.volume_control_active = False
          # WiFi state
        self.wifi_networks = []
        self.wifi_connecting = False
        self.wifi_selected_network = None
        self.wifi_scan_in_progress = False
        self.wifi_password_input = ""
        self.wifi_password_hidden = True
        
        # Click Wheel state
        self.click_wheel_enabled = True
        
        # Initialize the application
        self.initialize_app()
    
    def initialize_app(self):
        """Initialize the application with initial data"""
        # Initial library scan
        self.refresh_music_library(show_message=False)
        
        # Load main menu
        self.menu_manager.load_main_menu()
        self.current_menu = "main"
        self.selected_index = 0
        self.scroll_offset = 0
    
    def on_volume_changed(self, new_volume):
        """Callback for volume changes"""
        if self.current_menu == "settings":
            # Refresh settings menu to show new volume
            self._load_current_menu()
    
    def refresh_music_library(self, show_message=True):
        """Refresh the music library"""
        if show_message:
            self.renderer.draw_message_screen("Actualizando biblioteca...", "Por favor espere.")
            pygame.display.flip()
            pygame.time.wait(100)
        
        # Define music directories to scan
        project_music_dir = Path(__file__).parent.parent / "music"
        project_music_dir.mkdir(exist_ok=True)
        
        music_dirs_to_scan = [
            str(project_music_dir), 
            str(Path.home() / "Music")
        ]
        
        self.db.scan_music_library(music_dirs=music_dirs_to_scan)
        
        if show_message:
            self.renderer.draw_message_screen("Biblioteca actualizada", "Presione cualquier tecla.", delay=1500)
            # Return to previous menu or main menu
            if self.menu_stack:
                self.current_menu = self.menu_stack.pop()
            else:
                self.current_menu = "main"
            self._load_current_menu()
    
    def _load_current_menu(self):
        """Load the current menu based on state"""
        if self.current_menu == "main":
            self.menu_manager.load_main_menu()
        elif self.current_menu == "music":
            self.menu_manager.load_music_menu()
        elif self.current_menu == "videos":
            self.menu_manager.load_videos_menu()
        elif self.current_menu == "artists":
            self.menu_manager.load_artists_list()
        elif self.current_menu == "albums":
            self.menu_manager.load_albums_list()        
        elif self.current_menu == "all_songs":
            self.menu_manager.load_all_songs()
        elif self.current_menu == "settings":
            self.menu_manager.load_settings_menu(
                self.music_controller.get_repeat_mode(),
                self.music_controller.get_shuffle_mode(),
                self.playback.get_volume()
            )
        elif self.current_menu == "cover_flow":
            self.cover_flow.load_cover_flow_data()
        elif self.current_menu == "wifi_menu":
            current_network = self.wifi_manager.get_current_connection()
            self.menu_manager.load_wifi_menu(current_network)
        elif self.current_menu == "wifi_networks":
            self.menu_manager.load_wifi_networks(self.wifi_networks, self.wifi_scan_in_progress)
        elif self.current_menu == "wifi_password":
            if self.wifi_selected_network:
                self.menu_manager.load_wifi_password_input(self.wifi_selected_network.ssid)
        elif self.current_menu == "wifi_connecting":
            if self.wifi_selected_network:
                self.menu_manager.load_wifi_connecting(self.wifi_selected_network.ssid)
        # Reset selection
        self.selected_index = 0
        self.scroll_offset = 0
    
    def handle_input(self):
        """Handle all user input"""
        # Get mouse state for Click Wheel
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        # Handle Click Wheel input (mouse and keyboard)
        wheel_actions = []
        
        # Process all events
        events = pygame.event.get()
          # Handle Click Wheel mouse input
        if self.click_wheel_enabled:
            # Process each event for mouse input
            for event in events:
                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
                    wheel_actions.extend(self.click_wheel.handle_mouse_input(mouse_pos, event))
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            # Check for song end event
            if self.playback.check_song_ended(event):
                self.music_controller.handle_song_end()
                continue
            
            # Handle Click Wheel keyboard input
            if self.click_wheel_enabled and event.type == pygame.KEYDOWN:
                wheel_actions.extend(self.click_wheel.handle_keyboard_input(event))
            
            if event.type == pygame.KEYDOWN:
                # Handle volume control
                if self.volume_control_active:
                    if self.input_handler.handle_volume_control(event, self.playback):
                        self._load_current_menu()  # Refresh menu
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE]:
                        self.volume_control_active = False
                    return
                
                # Handle video playback
                if self.current_menu == "video_playing":
                    if self.input_handler.handle_video_input(event):
                        # Video was stopped, return to videos menu
                        self.current_menu = "videos"
                        self._load_current_menu()
                    return
                
                # Handle Cover Flow                
                if self.current_menu == "cover_flow":
                    print("Handling Cover Flow input")
                    direction = self.input_handler.handle_cover_flow_input(event)
                    if direction:
                        self.cover_flow.start_cover_flow_animation(direction)
                    elif event.key == pygame.K_RETURN:
                        # Enter Cover Flow album
                        album_name = self.cover_flow.get_current_album()
                        if album_name:
                            self.menu_stack.append(self.current_menu)
                            self.current_menu = "songs_by_album"
                            self.menu_manager.load_songs_by_album(album_name)
                            self.selected_index = 0
                            self.scroll_offset = 0
                    elif event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                        self.go_back()
                    return
                
                # Handle regular navigation (fallback if Click Wheel is disabled)
                if not self.click_wheel_enabled:
                    navigation = self.input_handler.handle_navigation(event)
                    
                    if navigation == "up":
                        self.move_selection(-1)
                    elif navigation == "down":
                        self.move_selection(1)
                    elif navigation == "left":
                        if self.current_menu == "now_playing":
                            self.music_controller.previous_song()
                        elif self.current_menu == "settings" and self._is_volume_setting():
                            self.volume_control_active = True
                            self.playback.set_volume(max(0.0, self.playback.get_volume() - 0.05))
                            self._load_current_menu()
                    elif navigation == "right":
                        if self.current_menu == "now_playing":
                            self.music_controller.next_song()
                        elif self.current_menu == "settings" and self._is_volume_setting():
                            self.volume_control_active = True
                            self.playback.set_volume(min(1.0, self.playback.get_volume() + 0.05))
                            self._load_current_menu()
                    elif navigation == "select":
                        self.select_item()
                    elif navigation == "back":
                        self.go_back()
                    elif navigation == "play_pause":
                        if self.playback.is_playing and not self.playback.is_paused:
                            self.playback.pause()
                        elif self.current_song_data:
                            self.playback.play()
        
        # Process Click Wheel actions
        self._handle_click_wheel_actions(wheel_actions)
    
    def move_selection(self, direction):
        """Move selection up or down with wrapping"""
        items = self.menu_manager.get_current_items()
        if not items:
            return
            
        if direction == -1:  # Up
            if self.selected_index > 0:
                self.selected_index -= 1
            else:
                self.selected_index = len(items) - 1
        elif direction == 1:  # Down
            if self.selected_index < len(items) - 1:
                self.selected_index += 1
            else:
                self.selected_index = 0
        
        # Adjust scroll offset
        visible_items = self.ui_config.visible_items_limit
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + visible_items:
            self.scroll_offset = self.selected_index - visible_items + 1
    
    def select_item(self):
        """Handle item selection"""
        items = self.menu_manager.get_current_items()
        if not items or self.selected_index >= len(items):
            return
        
        selected = items[self.selected_index]
        action = selected.get("action")
        data = selected.get("data")
        
        if action == "none":
            return
        
        # Push current menu to stack for navigation history
        if action not in ["refresh_library", "quit", "play_all_shuffle", "toggle_repeat", "toggle_shuffle", "set_volume"]:
            if self.current_menu not in ["now_playing"]:
                self.menu_stack.append(self.current_menu)
        
        # Handle different actions
        if action in ["music", "videos", "photos", "podcasts", "extras", "settings"]:
            self.current_menu = action
            self._load_current_menu()
        
        elif action == "view_artists":
            self.current_menu = "artists"
            self._load_current_menu()
        
        elif action == "view_albums":
            self.current_menu = "albums"
            self._load_current_menu()
        
        elif action == "view_all_songs":
            self.current_menu = "all_songs"
            self._load_current_menu()
        
        elif action == "view_cover_flow":
            self.current_menu = "cover_flow"
            self.cover_flow.load_cover_flow_data()
        
        elif action == "view_songs_by_artist":
            self.current_menu = "songs_by_artist"
            self.menu_manager.load_songs_by_artist(data)
            self.selected_index = 0
            self.scroll_offset = 0
        
        elif action == "view_songs_by_album":
            self.current_menu = "songs_by_album"
            self.menu_manager.load_songs_by_album(data)
            self.selected_index = 0
            self.scroll_offset = 0
        
        elif action == "play_video":
            if self.video_player.play_video(data):
                self.current_menu = "video_playing"
        
        elif action == "play_song":
            # Play selected song: pass song data and the full items list for playlist context
            if self.music_controller.play_song_from_list(data, items):
                self.current_song_data = data
                self.current_menu = "now_playing"
        
        elif action == "play_all_shuffle":
            if self.music_controller.play_all_shuffle():
                self.current_song_data = self.music_controller.get_current_song_info()
                self.current_menu = "now_playing"
        
        elif action == "now_playing":
            if not self.current_song_data:
                if self.music_controller.play_first_available_song():
                    self.current_song_data = self.music_controller.get_current_song_info()
            self.current_menu = "now_playing"

        
        elif action == "toggle_repeat":
            self.music_controller.toggle_repeat()
            self._load_current_menu()
        
        elif action == "toggle_shuffle":
            self.music_controller.toggle_shuffle()
            self._load_current_menu()
        
        elif action == "set_volume":
            self.volume_control_active = True
        
        elif action == "refresh_library":
            self.refresh_music_library(show_message=True)
        
        elif action in ["go_back_to_main", "go_back_to_music"]:
            if action == "go_back_to_main":
                self.menu_stack.clear()
                self.current_menu = "main"
            else:
                self.current_menu = "music"
            self._load_current_menu()
    
    def go_back(self):
        """Navigate back to previous menu"""
        if self.volume_control_active:
            self.volume_control_active = False
            self._load_current_menu()
            return
        
        if self.current_menu == "now_playing":
            if self.menu_stack:
                self.current_menu = self.menu_stack.pop()
            else:
                self.current_menu = "main"
            self._load_current_menu()
        elif self.menu_stack:
            self.current_menu = self.menu_stack.pop()
            self._load_current_menu()
    
    def _is_volume_setting(self):
        """Check if current selection is volume setting"""
        items = self.menu_manager.get_current_items()
        if items and self.selected_index < len(items):
            return items[self.selected_index].get("action") == "set_volume"
        return False
    
    def run(self):
        """Main application loop"""
        while self.running:
            # Handle input
            self.handle_input()
              # Update animations
            dt = self.clock.get_time() / 1000.0
            if self.current_menu == "cover_flow":
                self.cover_flow.update_cover_flow_animation(dt)
            
            # Update Click Wheel
            if self.click_wheel_enabled:
                self.click_wheel.update()
            
            # Update current song data
            if self.music_controller.get_current_song_info():
                self.current_song_data = self.music_controller.get_current_song_info()
                    
            # Render the current screen
            self.renderer.draw_background()
            self.renderer.draw_header(self.current_menu, self.playback.is_playing and not self.playback.is_paused)
            if self.current_menu == "now_playing":
                #draw_now_playing(self, song_data, current_position, is_playing, is_paused,  playlist_info=None):
                self.renderer.draw_now_playing(self.current_song_data,
                                                  self.playback.get_current_position_s(),
                                                  self.playback.is_playing,
                                                  self.playback.is_paused,
                                                  self.music_controller.get_playlist_info())
            elif self.current_menu == "video_playing":
                self.video_player.draw_video_playing(self.screen,self.renderer)
            elif self.current_menu == "settings":
                items = self.menu_manager.get_current_items()
                self.renderer.draw_settings_menu(items, self.selected_index, self.scroll_offset)
            elif self.current_menu == "cover_flow":
                self.cover_flow.draw_cover_flow(self.screen)
            else:
                # Draw regular menu
                items = self.menu_manager.get_current_items()
                menu_type = self.menu_manager.get_current_list_type()
                self.renderer.draw_menu(items, self.selected_index, self.scroll_offset, menu_type)
              # Draw mini player if not in now playing screen
            if self.current_menu != "now_playing" and self.current_song_data:
                #draw_mini_player(self, song_data, current_position, duration, is_playing, is_paused):
                self.renderer.draw_mini_player(self.current_song_data,
                                                self.playback.get_current_position_s(),
                                                self.current_song_data[5],
                                                self.playback.is_playing,
                                                self.playback.is_paused)
            
            # Draw Click Wheel
            if self.click_wheel_enabled:
                self.click_wheel.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(30)  # 30 FPS
        
        # Cleanup
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources before exit"""
        if hasattr(self.video_player, 'stop_video'):
            self.video_player.stop_video()
        pygame.quit()
    
    def _handle_click_wheel_actions(self, actions):
        """Handle actions from the Click Wheel"""
        for action in actions:
            action_type = action.get("type")
            
            if action_type == "scroll_up":
                self.move_selection(-1)
            elif action_type == "scroll_down":
                self.move_selection(1)
            elif action_type == "select":
                self.select_item()
            elif action_type == "button_press":
                button = action.get("button")
                if button == "menu":
                    self.go_back()
                elif button == "play_pause":
                    self._handle_play_pause()
                elif button == "forward":
                    self._handle_forward()
                elif button == "backward":
                    self._handle_backward()
    
    def _handle_play_pause(self):
        """Handle play/pause button from Click Wheel"""
        if self.current_menu == "now_playing" or self.current_song_data:
            if self.playback.is_playing and not self.playback.is_paused:
                self.playback.pause()
            elif self.playback.is_paused:
                self.playback.unpause()
            elif self.current_song_data:
                self.playback.play()
            else:
                # Try to play first available song
                self.music_controller.play_first_available_song()
                self.current_song_data = self.music_controller.get_current_song_info()
                if self.current_song_data:
                    self.current_menu = "now_playing"
    
    def _handle_forward(self):
        """Handle forward button from Click Wheel"""
        if self.current_menu == "now_playing":
            self.music_controller.next_song()
        elif self.current_menu == "cover_flow":
            self.cover_flow.start_cover_flow_animation("right")
        else:
            # In other menus, forward could mean "go right" or "fast forward"
            if self.current_menu == "settings" and self._is_volume_setting():
                self.volume_control_active = True
                self.playback.set_volume(min(1.0, self.playback.get_volume() + 0.05))
                self._load_current_menu()
    
    def _handle_backward(self):
        """Handle backward button from Click Wheel"""
        if self.current_menu == "now_playing":
            self.music_controller.previous_song()
        elif self.current_menu == "cover_flow":
            self.cover_flow.start_cover_flow_animation("left")
        else:
            # In other menus, backward could mean "go left" or "rewind"
            if self.current_menu == "settings" and self._is_volume_setting():
                self.volume_control_active = True
                self.playback.set_volume(max(0.0, self.playback.get_volume() - 0.05))
                self._load_current_menu()
