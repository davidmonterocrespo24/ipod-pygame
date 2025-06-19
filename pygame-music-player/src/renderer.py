"""
Rendering module for iPod Classic interface.
Handles all drawing operations and visual rendering.
"""
import pygame
import os
from pathlib import Path
import random


class iPodRenderer:
    """Handles all rendering operations for the iPod Classic UI"""
    
    def __init__(self, screen, config):
        self.screen = screen
        self.config = config
        
    def draw_background(self):
        """Draw iPod Classic white background"""
        self.screen.fill(self.config.BG_COLOR)

    def draw_header(self, title, is_playing=False, is_paused=False):
        """Draw iPod Classic header with status bar"""
        # Header background
        pygame.draw.rect(self.screen, self.config.HEADER_BG, 
                        (0, 0, self.config.SCREEN_WIDTH, self.config.header_height))
        
        # Bottom border line
        pygame.draw.line(self.screen, self.config.HEADER_DIVIDER, 
                        (0, self.config.header_height-1), 
                        (self.config.SCREEN_WIDTH, self.config.header_height-1))
        
        # Title text - centered
        text_surface = self.config.font_header.render(title, True, self.config.HEADER_TEXT)
        text_rect = text_surface.get_rect(centerx=self.config.SCREEN_WIDTH / 2, 
                                        centery=self.config.header_height / 2)
        self.screen.blit(text_surface, text_rect)

        # iPod Classic status indicators
        # Battery indicator (right side)
        batt_width, batt_height = 15, 8
        batt_x = self.config.SCREEN_WIDTH - batt_width - 5
        batt_y = (self.config.header_height - batt_height) // 2
        
        # Battery outline
        pygame.draw.rect(self.screen, self.config.BATTERY_BORDER, 
                        (batt_x, batt_y, batt_width, batt_height), 1)
        # Battery fill (simulate full battery)
        pygame.draw.rect(self.screen, self.config.BATTERY_COLOR, 
                        (batt_x + 1, batt_y + 1, batt_width - 2, batt_height - 2))
        # Battery terminal
        pygame.draw.rect(self.screen, self.config.BATTERY_BORDER, 
                        (batt_x + batt_width, batt_y + 2, 2, batt_height - 4))
        
        # Play indicator (left side) - show if music is playing
        if is_playing and not is_paused:
            play_icon = self.config.font_header.render("▶", True, self.config.HEADER_TEXT)
            self.screen.blit(play_icon, (5, (self.config.header_height - play_icon.get_height()) // 2))

    def draw_menu(self, menu_items, selected_index, scroll_offset, list_type=""):
        """Draw iPod Classic menu with proper styling"""
        y_offset = self.config.header_height + 3  # Start closer to header like real iPod
        
        for i in range(self.config.visible_items_limit):
            current_item_index = scroll_offset + i
            if current_item_index >= len(menu_items):
                break

            item = menu_items[current_item_index]
            item_y_pos = y_offset + (i * self.config.item_height)
            
            is_selected = (current_item_index == selected_index)
            
            # iPod Classic selection highlight
            if is_selected:
                # Draw rounded selection rectangle like iPod
                selection_rect = pygame.Rect(3, item_y_pos, self.config.SCREEN_WIDTH - 6, self.config.item_height)
                pygame.draw.rect(self.screen, self.config.MENU_ITEM_SELECTED_BG, selection_rect, border_radius=6)
                text_color = self.config.MENU_ITEM_SELECTED_TEXT
                sub_text_color = self.config.MENU_ITEM_SELECTED_TEXT
            else:
                text_color = self.config.MENU_ITEM_TEXT
                sub_text_color = self.config.GRAY

            # Main menu item text with iPod spacing
            label_text = item.get("label", "")
            if len(label_text) > 30: 
                label_text = label_text[:27] + "..."
            text_surf = self.config.font_menu_item.render(label_text, True, text_color)
            self.screen.blit(text_surf, (12, item_y_pos + (self.config.item_height - text_surf.get_height()) // 2))

            # Sublabel for songs (artist name)
            if "sublabel" in item and list_type == "songs":
                sub_label_text = item.get("sublabel", "")
                if len(sub_label_text) > 25:
                    sub_label_text = sub_label_text[:22] + "..."
                sub_text_surf = self.config.font_menu_item_small.render(sub_label_text, True, sub_text_color)
                # Position sublabel below main label
                sub_y = item_y_pos + (self.config.item_height // 2) + 4
                self.screen.blit(sub_text_surf, (15, sub_y))
            
            # iPod Classic navigation arrow
            if is_selected and item.get("action") != "none":
                arrow_surf = self.config.font_menu_item.render("›", True, text_color)
                arrow_x = self.config.SCREEN_WIDTH - arrow_surf.get_width() - 12
                arrow_y = item_y_pos + (self.config.item_height - arrow_surf.get_height()) // 2
                self.screen.blit(arrow_surf, (arrow_x, arrow_y))

        # iPod Classic scrollbar
        if len(menu_items) > self.config.visible_items_limit:
            self.draw_scrollbar(menu_items, scroll_offset)

    def draw_scrollbar(self, menu_items, scroll_offset):
        """Draw iPod Classic style scrollbar"""
        list_height_pixels = self.config.visible_items_limit * self.config.item_height
        scrollbar_width = 4
        scrollbar_x = self.config.SCREEN_WIDTH - scrollbar_width - 2
        scrollbar_y = self.config.header_height + 3
        
        # Background
        scrollbar_bg_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, list_height_pixels)
        pygame.draw.rect(self.screen, self.config.SCROLL_BAR_BG, scrollbar_bg_rect, border_radius=2)
        
        # Thumb
        thumb_height = max(8, (self.config.visible_items_limit / len(menu_items)) * list_height_pixels)
        thumb_y_offset = (scroll_offset / len(menu_items)) * list_height_pixels
        thumb_y = scrollbar_y + thumb_y_offset
        scrollbar_fg_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
        pygame.draw.rect(self.screen, self.config.SCROLL_BAR_FG, scrollbar_fg_rect, border_radius=2)

    def draw_now_playing(self, song_data, current_position, is_playing, is_paused, 
                        playlist_info=None):
        """Draw the Now Playing screen (estilo iPod Classic real)"""
        # --- HEADER ---
        header_height = 24
        pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, self.config.SCREEN_WIDTH, header_height))
        font_header = self.config.font_header
        header_text = font_header.render("Now Playing", True, (255, 255, 255))
        self.screen.blit(header_text, (8, 4))
        # Flecha azul a la derecha
        arrow_font = pygame.font.SysFont(None, 22, bold=True)
        arrow = arrow_font.render("▶", True, (0, 120, 255))
        self.screen.blit(arrow, (self.config.SCREEN_WIDTH - 22, 4))

        # --- CARÁTULA ---
        album_art_size = 90
        album_art_x = 12
        album_art_y = header_height + 10
        # Mostrar carátula desde metadatos si es posible
        cover_flow = getattr(self, 'cover_flow', None)
        song_cover = None
        if song_data and cover_flow:
            _id, path, title, artist, album, duration_s = song_data
            song_cover = cover_flow.get_album_art(album, None, (album_art_size, album_art_size), path)
        if song_cover:
            self.screen.blit(song_cover, (album_art_x, album_art_y))
        else:
            pygame.draw.rect(self.screen, (230, 230, 230), (album_art_x, album_art_y, album_art_size, album_art_size))
            pygame.draw.rect(self.screen, (180, 180, 180), (album_art_x, album_art_y, album_art_size, album_art_size), 1)
            # Placeholder de texto
            art_font = pygame.font.SysFont(None, 18)
            art_text_surf = art_font.render("Album Art", True, (180, 180, 180))
            art_text_rect = art_text_surf.get_rect(center=(album_art_x + album_art_size // 2, album_art_y + album_art_size // 2))
            self.screen.blit(art_text_surf, art_text_rect)

        # --- INFO DE LA CANCIÓN ---
        if not song_data:
            no_song_text = self.config.font_now_playing_title.render("No hay canción", True, (0, 0, 0))
            text_rect = no_song_text.get_rect(left=album_art_x + album_art_size + 15, top=album_art_y)
            self.screen.blit(no_song_text, text_rect)
            return
        _id, path, title, artist, album, duration_s = song_data
        text_x = album_art_x + album_art_size + 15
        text_y = album_art_y
        # Título
        title_font = pygame.font.SysFont(None, 20, bold=True)
        title_str = title[:32] + ("..." if len(title) > 32 else "")
        title_surf = title_font.render(title_str, True, (0, 0, 0))
        self.screen.blit(title_surf, (text_x, text_y))
        text_y += title_surf.get_height() + 2
        # Artista
        artist_font = pygame.font.SysFont(None, 16)
        artist_str = artist[:32] + ("..." if len(artist) > 32 else "")
        artist_surf = artist_font.render(artist_str, True, (80, 80, 80))
        self.screen.blit(artist_surf, (text_x, text_y))
        text_y += artist_surf.get_height() + 1
        # Álbum
        album_font = pygame.font.SysFont(None, 14)
        album_str = album[:32] + ("..." if len(album) > 32 else "")
        album_surf = album_font.render(album_str, True, (120, 120, 120))
        self.screen.blit(album_surf, (text_x, text_y))

        # --- BARRA DE PROGRESO Y TIEMPOS ---
        progress_bar_width = self.config.SCREEN_WIDTH - 40
        progress_bar_x = 20
        progress_bar_height = 6
        progress_bar_y = self.config.DISPLAY_HEIGHT - 32
        # Barra de fondo
        pygame.draw.rect(self.screen, (220, 220, 220), (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height), border_radius=3)
        # Barra de progreso azul
        if duration_s > 0:
            progress = max(0.0, min(1.0, current_position / duration_s))
            filled_width = int(progress * progress_bar_width)
            pygame.draw.rect(self.screen, (0, 153, 255), (progress_bar_x, progress_bar_y, filled_width, progress_bar_height), border_radius=3)
        # Tiempo actual (izquierda)
        time_font = pygame.font.SysFont(None, 16)
        time_current_str = self.config.format_time(current_position)
        current_time_surf = time_font.render(time_current_str, True, (0, 0, 0))
        self.screen.blit(current_time_surf, (progress_bar_x, progress_bar_y + progress_bar_height + 4))
        # Tiempo restante (derecha)
        if duration_s > 0:
            remaining_s = duration_s - current_position
            time_remaining_str = f"-{self.config.format_time(remaining_s)}"
        else:
            time_remaining_str = "-00:00"
        remaining_time_surf = time_font.render(time_remaining_str, True, (0, 0, 0))
        remaining_time_rect = remaining_time_surf.get_rect(right=progress_bar_x + progress_bar_width, top=progress_bar_y + progress_bar_height + 4)
        self.screen.blit(remaining_time_surf, remaining_time_rect)

    def draw_mini_player(self, song_data, current_position, duration, is_playing, is_paused):
        """Draw mini player at bottom of screen"""
        if not song_data:
            return
        
        mini_player_rect = pygame.Rect(0, self.config.DISPLAY_HEIGHT - self.config.mini_player_height, 
                                      self.config.SCREEN_WIDTH, self.config.mini_player_height)
        # Create a surface for transparency
        s = pygame.Surface((self.config.SCREEN_WIDTH, self.config.mini_player_height), pygame.SRCALPHA)
        s.fill(self.config.MINI_PLAYER_BG)
        self.screen.blit(s, (0, self.config.DISPLAY_HEIGHT - self.config.mini_player_height))

        _id, _path, title, artist, _album, duration_s = song_data
        
        display_text = title[:25] + "..." if len(title) > 25 else title
        if is_playing and not is_paused: 
            icon = "▶ "
        elif is_paused: 
            icon = "❚❚ "
        else: 
            icon = ""
        
        text_surf = self.config.font_mini_player.render(icon + display_text, True, self.config.MINI_PLAYER_TEXT)
        self.screen.blit(text_surf, (5, self.config.DISPLAY_HEIGHT - self.config.mini_player_height + 
                                   (self.config.mini_player_height - text_surf.get_height()) // 2))

        # Mini progress bar
        if duration_s > 0:
            progress_width = 80
            progress_x = self.config.SCREEN_WIDTH - progress_width - 5
            progress_y = self.config.DISPLAY_HEIGHT - self.config.mini_player_height + (self.config.mini_player_height - 2) // 2
            pygame.draw.rect(self.screen, self.config.GRAY, (progress_x, progress_y, progress_width, 2))
            
            progress = current_position / duration_s
            filled = int(progress * progress_width)
            pygame.draw.rect(self.screen, self.config.MINI_PLAYER_TEXT, (progress_x, progress_y, filled, 2))

    def draw_message_screen(self, line1, line2=""):
        """Draw a message screen with one or two lines of text"""
        font_large = self.config.font_menu_item
        font_small = self.config.font_menu_item_small

        line1_surf = font_large.render(line1, True, self.config.MENU_ITEM_TEXT)
        line1_rect = line1_surf.get_rect(centerx=self.config.SCREEN_WIDTH/2, 
                                        centery=self.config.DISPLAY_HEIGHT/2 - 15)
        self.screen.blit(line1_surf, line1_rect)

        if line2:
            line2_surf = font_small.render(line2, True, self.config.GRAY)
            line2_rect = line2_surf.get_rect(centerx=self.config.SCREEN_WIDTH/2, 
                                           centery=self.config.DISPLAY_HEIGHT/2 + 15)
            self.screen.blit(line2_surf, line2_rect)

    def draw_settings_menu(self, menu_items, selected_index, scroll_offset):
        """Draw settings menu with special formatting"""
        y_offset = self.config.header_height + 5
        
        for i in range(self.config.visible_items_limit):
            current_item_index = scroll_offset + i
            if current_item_index >= len(menu_items):
                break

            item = menu_items[current_item_index]
            item_y_pos = y_offset + (i * self.config.item_height)
            
            is_selected = (current_item_index == selected_index)
            
            if is_selected:
                pygame.draw.rect(self.screen, self.config.MENU_ITEM_SELECTED_BG, 
                               (0, item_y_pos, self.config.SCREEN_WIDTH, self.config.item_height))
                text_color = self.config.MENU_ITEM_SELECTED_TEXT
            else:
                text_color = self.config.MENU_ITEM_TEXT
                
            label_text = item.get("label", "")
            if len(label_text) > 35: 
                label_text = label_text[:32] + "..."
            text_surf = self.config.font_menu_item.render(label_text, True, text_color)
            self.screen.blit(text_surf, (10, item_y_pos + (self.config.item_height - text_surf.get_height()) // 2))

            if is_selected:
                arrow_surf = self.config.font_menu_item.render("›", True, text_color)
                self.screen.blit(arrow_surf, (self.config.SCREEN_WIDTH - 20, 
                                            item_y_pos + (self.config.item_height - arrow_surf.get_height()) // 2))

    def draw_menu_with_album_art(self, menu_items, selected_index, scroll_offset, list_type, cover_flow=None, albums=None):
        """Dibuja el menú clásico a la izquierda y un carrusel de portadas de álbumes a la derecha con animación aleatoria de desplazamiento"""
        menu_width = self.config.SCREEN_WIDTH // 2
        art_width = self.config.SCREEN_WIDTH - menu_width
        menu_area = pygame.Rect(0, 0, menu_width, self.config.DISPLAY_HEIGHT)
        art_area = pygame.Rect(menu_width, 0, art_width, self.config.DISPLAY_HEIGHT)
        self.screen.fill(self.config.BG_COLOR)
        self.draw_header("iPod", False, False)
        menu_surface = pygame.Surface((menu_width, self.config.DISPLAY_HEIGHT), pygame.SRCALPHA)
        y_offset = self.config.header_height + 3
        for i in range(self.config.visible_items_limit):
            current_item_index = scroll_offset + i
            if current_item_index >= len(menu_items):
                break
            item = menu_items[current_item_index]
            item_y_pos = y_offset + (i * self.config.item_height)
            is_selected = (current_item_index == selected_index)
            if is_selected:
                selection_rect = pygame.Rect(3, item_y_pos, menu_width - 6, self.config.item_height)
                pygame.draw.rect(menu_surface, self.config.MENU_ITEM_SELECTED_BG, selection_rect, border_radius=6)
                text_color = self.config.MENU_ITEM_SELECTED_TEXT
                sub_text_color = self.config.MENU_ITEM_SELECTED_TEXT
            else:
                text_color = self.config.MENU_ITEM_TEXT
                sub_text_color = self.config.GRAY
            label_text = item.get("label", "")
            if len(label_text) > 18:
                label_text = label_text[:15] + "..."
            text_surf = self.config.font_menu_item.render(label_text, True, text_color)
            menu_surface.blit(text_surf, (12, item_y_pos + (self.config.item_height - text_surf.get_height()) // 2))
            if "sublabel" in item and list_type == "songs":
                sub_label_text = item.get("sublabel", "")
                if len(sub_label_text) > 15:
                    sub_label_text = sub_label_text[:12] + "..."
                sub_text_surf = self.config.font_menu_item_small.render(sub_label_text, True, sub_text_color)
                sub_y = item_y_pos + (self.config.item_height // 2) + 4
                menu_surface.blit(sub_text_surf, (15, sub_y))
            if is_selected and item.get("action") != "none":
                arrow_surf = self.config.font_menu_item.render("›", True, text_color)
                arrow_x = menu_width - arrow_surf.get_width() - 12
                arrow_y = item_y_pos + (self.config.item_height - arrow_surf.get_height()) // 2
                menu_surface.blit(arrow_surf, (arrow_x, arrow_y))
        if len(menu_items) > self.config.visible_items_limit:
            list_height_pixels = self.config.visible_items_limit * self.config.item_height
            scrollbar_width = 4
            scrollbar_x = menu_width - scrollbar_width - 2
            scrollbar_y = self.config.header_height + 3
            scrollbar_bg_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, list_height_pixels)
            pygame.draw.rect(menu_surface, self.config.SCROLL_BAR_BG, scrollbar_bg_rect, border_radius=2)
            thumb_height = max(8, (self.config.visible_items_limit / len(menu_items)) * list_height_pixels)
            thumb_y_offset = (scroll_offset / len(menu_items)) * list_height_pixels
            thumb_y = scrollbar_y + thumb_y_offset
            scrollbar_fg_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
            pygame.draw.rect(menu_surface, self.config.SCROLL_BAR_FG, scrollbar_fg_rect, border_radius=2)
        self.screen.blit(menu_surface, (0, 0))

        # --- PORTADAS DERECHA CON ANIMACIÓN ALEATORIA ---
        art_surface = pygame.Surface((art_width, self.config.DISPLAY_HEIGHT), pygame.SRCALPHA)
        center_x = art_width // 2
        center_y = self.config.DISPLAY_HEIGHT // 2
        cover_size = (min(art_width - 40, 120), min(self.config.DISPLAY_HEIGHT - 80, 120))

        # Animación: mantener estado entre frames
        if not hasattr(self, '_album_anim_state'):
            self._album_anim_state = {
                'last_idx': -1,
                'direction': (0, 1),
                'progress': 1.0,
                'start_time': 0,
                'duration': 0.7,
                'next_idx': 0
            }
        anim = self._album_anim_state
        # Determinar lista de álbumes
        album_list = []
        if list_type == "albums" and albums:
            album_list = albums
        elif cover_flow and hasattr(cover_flow, "cover_flow_albums") and cover_flow.cover_flow_albums:
            album_list = cover_flow.cover_flow_albums
        # Si no hay álbumes, placeholder
        if not album_list:
            art = pygame.Surface(cover_size)
            art.fill(self.config.NOW_PLAYING_ALBUM_ART_BG)
            pygame.draw.rect(art, self.config.ALBUM_ART_BORDER_COLOR, art.get_rect(), 1)
            font = pygame.font.SysFont(None, 18)
            text = font.render("Sin portada", True, self.config.ALBUM_ART_BORDER_COLOR)
            text_rect = text.get_rect(center=(cover_size[0]//2, cover_size[1]//2))
            art.blit(text, text_rect)
            art_rect = art.get_rect(center=(center_x, center_y))
            art_surface.blit(art, art_rect)
            self.screen.blit(art_surface, (menu_width, 0))
            return
        # Selección de índice
        idx = 0
        if list_type == "albums" and albums:
            idx = selected_index if 0 <= selected_index < len(album_list) else 0
        else:
            # Carrusel automático
            idx = (pygame.time.get_ticks() // 2500) % len(album_list)
        # Si cambió el álbum, elegir nueva dirección aleatoria
        if anim['last_idx'] != idx:
            directions = [
                (0, -1),  # arriba
                (0, 1),   # abajo
                (1, 0),   # derecha
                (-1, 0),  # izquierda
                (1, 1),   # diagonal abajo derecha
                (-1, 1),  # diagonal abajo izquierda
                (1, -1),  # diagonal arriba derecha
                (-1, -1)  # diagonal arriba izquierda
            ]
            anim['direction'] = random.choice(directions)
            anim['progress'] = 0.0
            anim['start_time'] = pygame.time.get_ticks() / 1000.0
            anim['duration'] = 0.7 + random.random() * 0.5
            anim['next_idx'] = idx
        # Progreso de animación
        now = pygame.time.get_ticks() / 1000.0
        t = min(1.0, (now - anim['start_time']) / anim['duration'])
        anim['progress'] = t
        # Interpolación
        prev_idx = anim['last_idx'] if anim['last_idx'] >= 0 else idx
        next_idx = anim['next_idx']
        # Obtener nombres y paths
        def get_album_info(album):
            if isinstance(album, dict):
                return album.get("name") or album.get("label"), album.get("art_path"), album.get("song_path")
            return str(album), None, None
        prev_name, prev_path, prev_song_path = get_album_info(album_list[prev_idx])
        next_name, next_path, next_song_path = get_album_info(album_list[next_idx])
        # Obtener portadas
        if cover_flow:
            prev_art = cover_flow.get_album_art(prev_name, prev_path, cover_size, prev_song_path)
            next_art = cover_flow.get_album_art(next_name, next_path, cover_size, next_song_path)
        else:
            prev_art = pygame.Surface(cover_size)
            prev_art.fill(self.config.NOW_PLAYING_ALBUM_ART_BG)
            next_art = prev_art.copy()
        # Calcular desplazamiento
        # Animación lenta y cambio de dirección cada 3 segundos
        if not hasattr(self, '_album_anim_last_change'):
            self._album_anim_last_change = 0
        ticks = pygame.time.get_ticks()
        now_sec = ticks / 1000.0
        if now_sec - self._album_anim_last_change > 3.0:
            directions = [
                (0, -1),  # arriba
                (0, 1),   # abajo
                (1, 0),   # derecha
                (-1, 0),  # izquierda
                (1, 1),   # diagonal abajo derecha
                (-1, 1),  # diagonal abajo izquierda
                (1, -1),  # diagonal arriba derecha
                (-1, -1)  # diagonal arriba izquierda
            ]
            anim['direction'] = random.choice(directions)
            anim['start_time'] = now_sec
            anim['duration'] = 2.5 + random.random() * 1.0  # 2.5-3.5s
            self._album_anim_last_change = now_sec
        dx, dy = anim['direction']
        t = anim['progress']
        offset_x = int((1-t) * dx * art_width * 0.7)
        offset_y = int((1-t) * dy * self.config.DISPLAY_HEIGHT * 0.7)
        # Dibuja portada anterior desplazándose fuera
        if anim['last_idx'] != -1 and t < 1.0:
            prev_rect = prev_art.get_rect(center=(center_x - offset_x, center_y - offset_y))
            art_surface.blit(prev_art, prev_rect)
        # Dibuja portada nueva entrando
        next_rect = next_art.get_rect(center=(center_x + (art_width * dx * (1-t)), center_y + (self.config.DISPLAY_HEIGHT * dy * (1-t))))
        art_surface.blit(next_art, next_rect)
        self.screen.blit(art_surface, (menu_width, 0))
        # Si terminó la animación, actualizar last_idx
        if t >= 1.0:
            anim['last_idx'] = next_idx
