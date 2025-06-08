"""
Menu management module for iPod Classic interface.
Handles loading and navigating between different menus.
"""

from pathlib import Path
import random


class MenuManager:
    """Manages all menu states and navigation for iPod Classic UI"""

    def __init__(self, db, scan_video_files_callback=None):
        self.db = db
        self.scan_video_files_callback = scan_video_files_callback

        # UI State
        self.current_menu = "main"
        self.menu_stack = []  # For navigating back
        self.current_list_items = []  # Items currently displayed in a list menu
        self.current_list_type = ""  # e.g., 'artists', 'albums', 'songs'
        self.selected_index = 0  # Index of the selected item in the current list
        self.scroll_offset = 0  # For scrolling long lists

        # Filter context for sub-menus
        self.current_artist_filter = ""
        self.current_album_filter = ""

        # Video files list
        self.video_files = []

    def load_main_menu(self):
        """Load iPod Classic main menu"""
        self.current_menu = "main"
        # iPod Classic 6th Gen main menu structure
        self.current_list_items = [
            {"label": "Music", "action": "music"},
            {"label": "Videos", "action": "videos"},
            {"label": "Photos", "action": "photos"},
            {"label": "Podcasts", "action": "podcasts"},
            {"label": "Extras", "action": "extras"},
            {"label": "Settings", "action": "settings"},
            {"label": "Shuffle Songs", "action": "play_all_shuffle"},
            {"label": "Now Playing", "action": "now_playing"},
        ]
        self.selected_index = 0
        self.scroll_offset = 0

    def load_music_menu(self):
        """Load music submenu"""
        self.current_menu = "music"
        # iPod Classic Music menu structure
        self.current_list_items = [
            {"label": "Cover Flow", "action": "view_cover_flow"},
            {"label": "Artists", "action": "view_artists"},
            {"label": "Albums", "action": "view_albums"},
            {"label": "Songs", "action": "view_all_songs"},
            {"label": "Playlists", "action": "playlists"},
            {"label": "Genres", "action": "genres"},
            {"label": "Composers", "action": "composers"},
            {"label": "Audiobooks", "action": "audiobooks"},
        ]
        self.selected_index = 0
        self.scroll_offset = 0

    def load_videos_menu(self):
        """Load video files and display video menu"""
        self.current_menu = "videos"
        if self.scan_video_files_callback:
            self.video_files =self.scan_video_files_callback()

        if not self.video_files:
            self.current_list_items = [
                {"label": "No videos found", "action": "none"},
                {"label": "Place MP4 files in 'videos' folder", "action": "none"},
                {"label": "", "action": "none"},
                {"label": "Go back to main menu", "action": "go_back_to_main"},
            ]
        else:
            self.current_list_items = []
            for video_file in self.video_files:
                filename = Path(video_file).stem
                self.current_list_items.append(
                    {
                        "label": (
                            filename[:30] + "..." if len(filename) > 30 else filename
                        ),
                        "action": "play_video",
                        "data": video_file,
                    }
                )
            self.current_list_items.append({"label": "", "action": "none"})
            self.current_list_items.append(
                {"label": "Go back to main menu", "action": "go_back_to_main"}
            )

        self.selected_index = 0
        self.scroll_offset = 0

    def load_photos_menu(self):
        """Placeholder for Photos menu - not implemented yet"""
        self.current_menu = "photos"
        self.current_list_items = [
            {"label": "Feature not available", "action": "none"},
            {"label": "Photos coming soon...", "action": "none"},
            {"label": "", "action": "none"},
            {"label": "Go back to main menu", "action": "go_back_to_main"},
        ]
        self.selected_index = 0
        self.scroll_offset = 0

    def load_podcasts_menu(self):
        """Placeholder for Podcasts menu - not implemented yet"""
        self.current_menu = "podcasts"
        self.current_list_items = [
            {"label": "Feature not available", "action": "none"},
            {"label": "Podcasts coming soon...", "action": "none"},
            {"label": "", "action": "none"},
            {"label": "Go back to main menu", "action": "go_back_to_main"},
        ]
        self.selected_index = 0
        self.scroll_offset = 0

    def load_extras_menu(self):
        """Placeholder for Extras menu - not implemented yet"""
        self.current_menu = "extras"
        self.current_list_items = [
            {"label": "Feature not available", "action": "none"},
            {"label": "Games coming soon...", "action": "none"},
            {"label": "Clock coming soon...", "action": "none"},
            {"label": "Contacts coming soon...", "action": "none"},
            {"label": "Calendar coming soon...", "action": "none"},
            {"label": "", "action": "none"},
            {"label": "Go back to main menu", "action": "go_back_to_main"},
        ]
        self.selected_index = 0
        self.scroll_offset = 0

    def load_playlists_menu(self):
        """Placeholder for Playlists menu - not implemented yet"""
        self.current_menu = "playlists"
        self.current_list_items = [
            {"label": "Feature not available", "action": "none"},
            {"label": "Playlists coming soon...", "action": "none"},
            {"label": "", "action": "none"},
            {"label": "Go back to music menu", "action": "go_back_to_music"},
        ]
        self.selected_index = 0
        self.scroll_offset = 0

    def load_genres_menu(self):
        """Placeholder for Genres menu - not implemented yet"""
        self.current_menu = "genres"
        self.current_list_items = [
            {"label": "Feature not available", "action": "none"},
            {"label": "Genres coming soon...", "action": "none"},
            {"label": "", "action": "none"},
            {"label": "Go back to music menu", "action": "go_back_to_music"},
        ]
        self.selected_index = 0
        self.scroll_offset = 0

    def load_composers_menu(self):
        """Placeholder for Composers menu - not implemented yet"""
        self.current_menu = "composers"
        self.current_list_items = [
            {"label": "Feature not available", "action": "none"},
            {"label": "Composers coming soon...", "action": "none"},
            {"label": "", "action": "none"},
            {"label": "Go back to music menu", "action": "go_back_to_music"},
        ]
        self.selected_index = 0
        self.scroll_offset = 0

    def load_audiobooks_menu(self):
        """Placeholder for Audiobooks menu - not implemented yet"""
        self.current_menu = "audiobooks"
        self.current_list_items = [
            {"label": "Feature not available", "action": "none"},
            {"label": "Audiobooks coming soon...", "action": "none"},
            {"label": "", "action": "none"},
            {"label": "Go back to music menu", "action": "go_back_to_music"},
        ]
        self.selected_index = 0
        self.scroll_offset = 0

    def load_artists_list(self):
        """Load list of artists from database"""
        self.current_menu = "artists"
        artists = self.db.get_artists()
        self.current_list_items = [
            {"label": artist, "action": "view_songs_by_artist", "data": artist}
            for artist in artists
        ]
        if not artists:
            self.current_list_items.append(
                {"label": "No hay artistas", "action": "none"}
            )
        self.current_list_type = "artists"
        self.selected_index = 0
        self.scroll_offset = 0

    def load_albums_list(self):
        """Load list of albums from database"""
        self.current_menu = "albums"
        albums = self.db.get_albums()
        self.current_list_items = [
            {"label": album, "action": "view_songs_by_album", "data": album}
            for album in albums
        ]
        if not albums:
            self.current_list_items.append(
                {"label": "No hay álbumes", "action": "none"}
            )
        self.current_list_type = "albums"
        self.selected_index = 0
        self.scroll_offset = 0

    def load_songs_by_artist(self, artist_name):
        """Load songs by specific artist"""
        self.current_menu = "songs_by_artist"
        self.current_list_type = "songs"
        
        # Ensure artist_name is a string
        if isinstance(artist_name, tuple):
            artist_name = artist_name[0]
        elif not isinstance(artist_name, str):
            artist_name = str(artist_name)
            
        songs = self.db.get_songs_by_artist(artist_name)
        
        if not songs:
            self.current_list_items = [{"label": "No songs found", "action": "none"}]
        else:
            self.current_list_items = []
            for song in songs:
                self.current_list_items.append({
                    "label": f"{song[2]} - {song[3]}",  # Title - Artist
                    "action": "play_song",
                    "data": song
                })
        
        self.selected_index = 0
        self.scroll_offset = 0
        self.current_artist_filter = artist_name  # For header display

    def load_songs_by_album(self, album_name):
        """Load songs for a specific album"""
        self.current_menu = "songs_by_album"
        self.current_album_filter = album_name
        
        # Ensure album_name is a string
        if isinstance(album_name, tuple):
            album_name = album_name[0]
        elif not isinstance(album_name, str):
            album_name = str(album_name)
            
        songs = self.db.get_songs_by_album(album_name)
        
        if not songs:
            self.current_list_items = [{"label": "No songs found", "action": "none"}]
        else:
            self.current_list_items = []
            for song in songs:
                self.current_list_items.append({
                    "label": f"{song[1]} - {song[2]}",  # Title - Artist
                    "action": "play_song",
                    "data": song
                })
        
        self.selected_index = 0
        self.scroll_offset = 0

    def load_all_songs(self):
        """Load all songs from database"""
        self.current_menu = "all_songs"
        self.current_list_type = "songs"
        songs = self.db.get_all_songs()
        self.current_list_items = [
            {"label": s[2], "sublabel": s[3], "action": "play_song", "data": s}
            for s in songs
        ]
        if not songs:
            self.current_list_items.append(
                {"label": "No hay canciones", "action": "none"}
            )
        self.selected_index = 0
        self.scroll_offset = 0    

    def load_settings_menu(self, repeat_mode, shuffle_mode, volume):
        """Load settings menu with current values"""
        self.current_menu = "settings"
        self.current_list_items = [
            {"label": f"Volumen: {int(volume * 100)}%", "action": "set_volume"},
            {
                "label": f"Repetir: {repeat_mode.capitalize()}",
                "action": "toggle_repeat",
            },
            {
                "label": f"Aleatorio: {'Activado' if shuffle_mode else 'Desactivado'}",
                "action": "toggle_shuffle",
            },
            {"label": "WiFi", "action": "wifi_menu"},
        ]
        self.selected_index = 0
        self.scroll_offset = 0
    
    def load_wifi_menu(self, current_network=None, wifi_enabled=True):
        """Load WiFi menu"""
        self.current_menu = "wifi_menu"
        status_text = f"Conectado a: {current_network}" if current_network else "No conectado"
        
        self.current_list_items = [
            {"label": status_text, "action": "none"},
            {"label": "", "action": "none"},
            {"label": "Buscar redes", "action": "scan_networks"},
            {"label": "Desconectar" if current_network else "Conectar", "action": "toggle_connection"},
            {"label": "Estado de conexión", "action": "connection_status"},
        ]
        self.selected_index = 2  # Default to "Buscar redes"
        self.scroll_offset = 0
    
    def load_wifi_networks(self, networks, scanning=False):
        """Load available WiFi networks"""
        self.current_menu = "wifi_networks"
        
        if scanning:
            self.current_list_items = [
                {"label": "Buscando redes WiFi...", "action": "none"},
                {"label": "Por favor espere", "action": "none"},
            ]
        elif not networks:
            self.current_list_items = [
                {"label": "No se encontraron redes", "action": "none"},
                {"label": "Verifique que WiFi esté activado", "action": "none"},
                {"label": "", "action": "none"},
                {"label": "Reintentar", "action": "scan_networks"},
            ]
        else:
            self.current_list_items = []
            for i, network in enumerate(networks):
                signal_bars = "●●●●●" if network.signal_strength > 80 else \
                             "●●●●○" if network.signal_strength > 60 else \
                             "●●●○○" if network.signal_strength > 40 else \
                             "●●○○○" if network.signal_strength > 20 else "●○○○○"
                
                security_icon = "🔒" if network.security and "WPA" in network.security.upper() else ""
                connected_icon = "✓" if network.is_connected else ""
                
                label = f"{network.ssid[:20]} {signal_bars} {security_icon} {connected_icon}"
                action = "connect_to_network" if not network.is_connected else "disconnect_network"
                
                self.current_list_items.append({
                    "label": label.strip(),
                    "action": action,
                    "data": network
                })
            
            # Add refresh option
            self.current_list_items.append({"label": "", "action": "none"})
            self.current_list_items.append({"label": "Actualizar lista", "action": "scan_networks"})
        
        self.selected_index = 0
        self.scroll_offset = 0
    
    def load_wifi_password_input(self, ssid):
        """Load WiFi password input screen"""
        self.current_menu = "wifi_password"
        self.current_list_items = [
            {"label": f"Red: {ssid}", "action": "none"},
            {"label": "", "action": "none"},
            {"label": "Ingrese la contraseña:", "action": "none"},
            {"label": "Password: ", "action": "password_input"},
            {"label": "", "action": "none"},
            {"label": "Conectar", "action": "connect_with_password"},
            {"label": "Cancelar", "action": "back_to_networks"},
        ]
        self.selected_index = 3  # Focus on password input
        self.scroll_offset = 0
    
    def load_wifi_connecting(self, ssid):
        """Load WiFi connecting screen"""
        self.current_menu = "wifi_connecting"
        self.current_list_items = [
            {"label": f"Conectando a: {ssid}", "action": "none"},
            {"label": "", "action": "none"},
            {"label": "Por favor espere...", "action": "none"},
            {"label": "", "action": "none"},
            {"label": "Cancelar", "action": "cancel_connection"},        ]
        self.selected_index = 4
        self.scroll_offset = 0

    def get_menu_title(self):
        """Get the title for the current menu"""
        title_map = {
            "main": "iPod",
            "music": "Music",
            "videos": "Videos",
            "photos": "Photos",
            "podcasts": "Podcasts",
            "extras": "Extras",
            "playlists": "Playlists",
            "genres": "Genres",
            "composers": "Composers",
            "audiobooks": "Audiobooks",
            "artists": "Artists",
            "albums": "Albums",
            "all_songs": "Songs",
            "songs_by_artist": getattr(self, "current_artist_filter", "Artist")[:15],
            "songs_by_album": getattr(self, "current_album_filter", "Album")[:15],
            "now_playing": "Now Playing",
            "settings": "Settings",
            "cover_flow": "Cover Flow",
            "video_playing": "Video",
            "wifi_menu": "WiFi",
            "wifi_networks": "WiFi Networks",
            "wifi_password": "WiFi Password",
            "wifi_connecting": "Connecting",
        }

        title = title_map.get(self.current_menu, "iPod")
        if len(title) > 20:  # Truncate if too long for header
            title = title[:18] + "..."
        return title

    def can_go_back(self):
        """Check if back navigation is possible"""
        return len(self.menu_stack) > 0 or self.current_menu == "now_playing"

    def go_back(self):
        """Navigate back to previous menu"""
        if self.current_menu == "now_playing":
            # If in now_playing, always go back to the last actual menu, or main if stack is empty
            if self.menu_stack:
                self.current_menu = self.menu_stack.pop()
            else:
                self.load_main_menu()
                return "main"
        elif self.menu_stack:
            self.current_menu = self.menu_stack.pop()
            # Reset selection for the new (old) menu
            self.selected_index = 0
            self.scroll_offset = 0
            return self.current_menu
        else:
            # If at main menu or no stack, perhaps exit or do nothing
            return None

    def push_menu(self, menu_name):
        """Push current menu to stack before navigation"""
        if self.current_menu not in ["now_playing"]:  # Don't push now_playing itself
            self.menu_stack.append(self.current_menu)

    def adjust_scroll_for_selection(self, visible_items_limit):
        """Adjust scroll offset to keep selected item visible"""
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + visible_items_limit:
            self.scroll_offset = self.selected_index - visible_items_limit + 1

    def get_current_items(self):
        """Get the current list of menu items"""
        return self.current_list_items

    def get_current_list_type(self):
        """Get the current list type (e.g., 'artists', 'albums', 'songs')"""
        return getattr(self, "current_list_type", "")
