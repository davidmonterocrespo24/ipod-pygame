"""
UI Configuration module for iPod Classic interface.
Contains colors, fonts, layout constants and theme configuration.
"""
import pygame
import os


class UIConfig:
    """iPod Classic 6th Generation UI configuration and theming"""
    
    def __init__(self):        # Screen dimensions - iPod Classic 6th Generation with Click Wheel
        # Original iPod Classic 6th Gen had 2.5-inch, 320x240 screen
        # We'll extend height to accommodate the Click Wheel below
        # Dimensiones actualizadas para simular 2.8" pantalla y 3.5" total diagonal
        self.SCREEN_WIDTH = 310
        self.DISPLAY_HEIGHT = 269  # Actual display area height (Pantalla iPod)
        # La altura total de la ventana (SCREEN_HEIGHT) y la altura de la zona de Click Wheel
        # se calculan en main.py para lograr la diagonal de 3.5". Usaremos estos valores
        # para referencia, aunque el renderizado principal usa DISPLAY_HEIGHT.
        self.WINDOW_HEIGHT = 420 # Altura total de la ventana (referencia)
        self.CLICK_WHEEL_AREA_HEIGHT = 162 # Altura de la zona de Click Wheel (referencia)
        self.SCREEN_HEIGHT = self.WINDOW_HEIGHT  # Alias for compatibility
        
        # Colors - Authentic iPod Classic 6th Generation Color Scheme
        # Main background: Pure white like the original iPod interface
        self.BG_COLOR = (255, 255, 255)  # Pure white background
        
        # Header colors (top status bar)
        self.HEADER_BG = (245, 245, 245)  # Very light gray for header
        self.HEADER_TEXT = (0, 0, 0)  # Black text
        self.HEADER_DIVIDER = (180, 180, 180)  # Light gray divider line
        
        # Menu colors
        self.MENU_ITEM_TEXT = (0, 0, 0)  # Black text
        self.MENU_ITEM_SELECTED_BG = (80, 130, 230)  # iPod's signature blue
        self.MENU_ITEM_SELECTED_TEXT = (255, 255, 255)  # White text on blue
        self.MENU_ARROW = (130, 130, 130)  # Gray arrow for navigation
        
        # Scroll bar colors
        self.SCROLL_BAR_BG = (230, 230, 230)  # Light gray background
        self.SCROLL_BAR_FG = (150, 150, 150)  # Darker gray indicator
        
        # Now Playing colors
        self.NOW_PLAYING_TEXT = (0, 0, 0)  # Black text
        self.PROGRESS_BAR_BG = (220, 220, 220)  # Light gray background
        self.PROGRESS_BAR_FG = (0, 0, 0)  # Black progress
        self.PROGRESS_BAR_BORDER = (180, 180, 180)  # Border around progress bar
        
        # Album art colors
        self.ALBUM_ART_BORDER_COLOR = (150, 150, 150)  # Gray border
        self.NOW_PLAYING_ALBUM_ART_BG = (240, 240, 240)  # Light gray placeholder
        self.NOW_PLAYING_TRACK_INFO_COLOR = (0, 0, 0)  # Black track info
        
        # Mini player colors
        self.MINI_PLAYER_BG = (240, 240, 240, 200)  # Light gray semi-transparent
        self.MINI_PLAYER_TEXT = (0, 0, 0)  # Black text
        
        # Status indicators
        self.BATTERY_COLOR = (0, 200, 0)  # Green battery
        self.BATTERY_BORDER = (100, 100, 100)  # Gray battery border
        
        # Additional iPod-specific colors
        self.GRAY = (100, 100, 100)
        self.LIGHT_GRAY = (200, 200, 200)
        self.DARK_GRAY = (80, 80, 80)
        self.DIVIDER_COLOR = (220, 220, 220)  # For separating menu sections
        
        # UI Layout - iPod Classic 6th Generation proportions
        self.visible_items_limit = 8  # iPod showed about 8 menu items
        self.item_height = 24  # Slightly smaller for more compact look
        self.header_height = 20  # Compact header like original iPod
        self.mini_player_height = 22  # Compact mini player
        
        # Cover Flow settings
        self.cover_art_size_focused = (80, 80)
        self.cover_art_size_unfocused = (50, 50)
        self.reflection_height_ratio = 0.4  # How much of the image height is reflected
        
        # Initialize fonts
        self._init_fonts()
    
    def _init_fonts(self):
        """Initialize iPod Classic style fonts"""
        # iPod used clean, simple fonts. We'll use system fonts that are similar
        font_name_main = None
        font_name_bold = None 
        
        try:
            # Check for fonts similar to iPod's font (Helvetica/Arial family)
            if os.name == 'nt':  # Windows
                font_name_main = 'Arial' 
                font_name_bold = 'Arial'
            else:  # Linux, macOS
                available_fonts = pygame.font.get_fonts()
                if 'helvetica' in available_fonts:
                    font_name_main = 'helvetica'
                    font_name_bold = 'helvetica'
                elif 'dejavusans' in available_fonts:
                    font_name_main = 'dejavusans'
                    font_name_bold = 'dejavusans'
                elif 'arial' in available_fonts:
                    font_name_main = 'arial'
                    font_name_bold = 'arial'

            # iPod Classic font sizes (adjusted for clarity)
            self.font_header = pygame.font.SysFont(font_name_main, 12, bold=True)  # Small header text
            self.font_menu_item = pygame.font.SysFont(font_name_main, 16)  # Main menu items
            self.font_menu_item_small = pygame.font.SysFont(font_name_main, 12)  # Secondary info
            self.font_now_playing_title = pygame.font.SysFont(font_name_bold, 14, bold=True)  # Song title
            self.font_now_playing_artist = pygame.font.SysFont(font_name_main, 12)  # Artist name
            self.font_now_playing_album = pygame.font.SysFont(font_name_main, 11)  # Album name
            self.font_time = pygame.font.SysFont(font_name_main, 11)  # Time display
            self.font_mini_player = pygame.font.SysFont(font_name_main, 11)  # Mini player
            self.font_status = pygame.font.SysFont(font_name_main, 12)  # Status icons
            self.font_track_title = pygame.font.SysFont(font_name_bold, 16)  # Track title in video
            self.font_small = pygame.font.SysFont(font_name_main, 10)  # Small font for settings, etc.
            
        except Exception as e:
            print(f"Error loading system fonts: {e}. Using Pygame default font.")
            # Fallback to default fonts with iPod-appropriate sizes
            self.font_header = pygame.font.Font(None, 16)
            self.font_menu_item = pygame.font.Font(None, 20)
            self.font_menu_item_small = pygame.font.Font(None, 16)
            self.font_now_playing_title = pygame.font.Font(None, 18)
            self.font_now_playing_artist = pygame.font.Font(None, 16)
            self.font_now_playing_album = pygame.font.Font(None, 14)
            self.font_time = pygame.font.Font(None, 14)
            self.font_mini_player = pygame.font.Font(None, 14)
            self.font_status = pygame.font.Font(None, 16)
            self.font_track_title = pygame.font.Font(None, 22)
            self.font_small = pygame.font.Font(None, 12)
    
    def format_time(self, seconds):
        """Format time in MM:SS format"""
        if seconds is None or not isinstance(seconds, (int, float)) or seconds < 0:
            return "00:00"
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
