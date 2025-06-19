"""
Cover Flow module for iPod Classic interface.
Handles album art display and Cover Flow navigation with animations.
"""
import pygame
import os
from pathlib import Path
import io
try:
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, APIC
except ImportError:
    MP3 = None
    ID3 = None
    APIC = None
try:
    from PIL import Image
except ImportError:
    Image = None


class CoverFlow:
    """Handles Cover Flow functionality and album art management"""
    
    def __init__(self, config, db):
        self.config = config
        self.db = db
        
        # Cover Flow specific state
        self.cover_flow_albums = []  # List of album data with art paths
        self.current_cover_flow_index = 0
        self.cover_art_cache = {}  # Cache for loaded album art
        
        # Cover Flow animation variables
        self.cover_flow_animation_active = False
        self.cover_flow_animation_direction = "none"  # "left", "right", "none"
        self.cover_flow_animation_progress = 0.0  # 0.0 to 1.0
        self.cover_flow_animation_speed = 8.0  # Higher = faster animation
        self.cover_flow_target_index = 0

    def load_cover_flow_data(self):
        """Load album data for Cover Flow display"""
        # Get albums from database
        albums_from_db = self.db.get_albums()
        self.cover_flow_albums = []
        for album_name in albums_from_db:
            # Buscar una canción de este álbum para extraer la carátula
            songs = self.db.get_songs_by_album(album_name)
            song_path = None
            if songs and len(songs[0]) > 1:
                song_path = songs[0][1]  # path es el segundo campo
            self.cover_flow_albums.append({
                "name": album_name,
                "art_path": None,  # Se puede mejorar si tienes carátulas externas
                "song_path": song_path
            })
        if not self.cover_flow_albums:
            # Handle case with no albums
            print("No albums found for Cover Flow.")
            self.cover_flow_albums = [{"name": "No Albums Found", "art_path": None, "song_path": None}]
        self.current_cover_flow_index = 0

    def get_album_art(self, album_name, art_path=None, size=(80, 80), song_path=None):
        """Get album art surface, with caching. Tries to extract from audio file metadata if possible."""
        cache_key = (album_name, art_path, song_path)
        if cache_key in self.cover_art_cache and size in self.cover_art_cache[cache_key]:
            return self.cover_art_cache[cache_key][size]

        raw_image = None
        # 1. Intentar extraer carátula de metadatos si hay song_path
        if song_path and MP3 and ID3 and APIC:
            try:
                audio = MP3(song_path, ID3=ID3)
                found_valid_image = False
                for tag in audio.tags.values():
                    if isinstance(tag, APIC):
                        mime = getattr(tag, 'mime', '').lower()
                        if mime in ('image/jpeg', 'image/jpg', 'image/png'):
                            img_data = tag.data
                            if Image is not None:
                                img_stream = io.BytesIO(img_data)
                                try:
                                    pil_img = Image.open(img_stream).convert('RGBA')
                                    mode = pil_img.mode
                                    size = pil_img.size
                                    data = pil_img.tobytes()
                                    raw_image = pygame.image.fromstring(data, size, mode)
                                    found_valid_image = True
                                    break
                                except Exception as e:
                                    print(f"Error abriendo imagen APIC válida: {e}")
                            else:
                                img_stream = io.BytesIO(img_data)
                                try:
                                    raw_image = pygame.image.load(img_stream)
                                    found_valid_image = True
                                    break
                                except Exception as e:
                                    print(f"Error abriendo imagen APIC con pygame: {e}")
                        else:
                            print(f"Tipo MIME de carátula no soportado: {mime}")
                if not found_valid_image:
                    print(f"No se encontró ninguna carátula válida en metadatos para {song_path}")
            except Exception as e:
                print(f"Error extrayendo carátula de metadatos: {e}")
        # 2. Si no se pudo, intentar cargar desde art_path
        if raw_image is None and art_path and os.path.exists(art_path):
            try:
                raw_image = pygame.image.load(art_path).convert_alpha()
            except Exception as e:
                print(f"Error cargando imagen de {art_path}: {e}")
                raw_image = None
        # 3. Si no hay imagen, crear placeholder
        if raw_image is None:
            raw_image = pygame.Surface((200, 200), pygame.SRCALPHA)
            raw_image.fill(self.config.NOW_PLAYING_ALBUM_ART_BG)
            pygame.draw.rect(raw_image, self.config.ALBUM_ART_BORDER_COLOR, raw_image.get_rect(), 1)
            placeholder_font = pygame.font.SysFont(None, 24)
            art_text_surf = placeholder_font.render(album_name[:15], True, self.config.ALBUM_ART_BORDER_COLOR)
            art_text_rect = art_text_surf.get_rect(center=(raw_image.get_width() // 2, raw_image.get_height() // 2))
            raw_image.blit(art_text_surf, art_text_rect)
        # Escalar
        scaled_image = pygame.transform.smoothscale(raw_image, size)
        # Cachear
        if cache_key not in self.cover_art_cache:
            self.cover_art_cache[cache_key] = {}
        self.cover_art_cache[cache_key][size] = scaled_image
        self.cover_art_cache[cache_key]['raw'] = raw_image
        return scaled_image

    def draw_cover_flow(self, screen):
        """Draw iPod Classic 6th generation Cover Flow interface"""
        # Black background for Cover Flow
        screen.fill((0, 0, 0))
        
        content_y_start = self.config.header_height + 10
        center_x = self.config.SCREEN_WIDTH // 2
        center_y = content_y_start + (self.config.DISPLAY_HEIGHT - self.config.header_height - self.config.mini_player_height - 20) // 2

        if not self.cover_flow_albums:
            no_albums_text = self.config.font_menu_item.render("No hay álbumes para Cover Flow", True, (255, 255, 255))
            text_rect = no_albums_text.get_rect(center=(self.config.SCREEN_WIDTH / 2, self.config.DISPLAY_HEIGHT / 2))
            screen.blit(no_albums_text, text_rect)
            return

        # Cover Flow parameters
        focused_size = (90, 90)    # Size of the center album
        side_size = (60, 60)       # Size of side albums
        num_side_covers = 2        # Number of covers on each side

        # Calculate animation offset if animation is active
        animation_offset = 0.0
        if self.cover_flow_animation_active:
            # Use easing function for smooth animation
            eased_progress = self.ease_in_out_cubic(self.cover_flow_animation_progress)
            if self.cover_flow_animation_direction == "left":
                animation_offset = eased_progress * 120  # Spacing between covers
            elif self.cover_flow_animation_direction == "right":
                animation_offset = -eased_progress * 120

        # Draw covers with 3D perspective effect
        for i in range(-num_side_covers, num_side_covers + 1):
            album_index = self.current_cover_flow_index + i
            
            # During animation, show transitioning covers
            if self.cover_flow_animation_active:
                if self.cover_flow_animation_direction == "left":
                    album_index = self.current_cover_flow_index + i + (1 if self.cover_flow_animation_progress > 0.5 else 0)
                elif self.cover_flow_animation_direction == "right":
                    album_index = self.current_cover_flow_index + i - (1 if self.cover_flow_animation_progress > 0.5 else 0)
            
            if 0 <= album_index < len(self.cover_flow_albums):
                album_data = self.cover_flow_albums[album_index]
                album_name = album_data["name"]
                
                is_focused = (i == 0)
                
                # Determine cover size and position
                if is_focused:
                    cover_size = focused_size
                    scale_factor = 1.0
                    rotation_angle = 0
                    cover_y = center_y - cover_size[1] // 2
                    alpha = 255
                else:
                    cover_size = side_size
                    scale_factor = 0.7 + 0.3 * (1 - abs(i) * 0.2)  # Gradually smaller
                    rotation_angle = i * 25  # Angle for 3D effect
                    cover_y = center_y - cover_size[1] // 2 + 10  # Slightly lower
                    alpha = max(80, 255 - abs(i) * 60)  # Fade out side covers

                # Calculate X position with animation offset
                base_spacing = 70
                cover_x = center_x + (i * base_spacing) + animation_offset - cover_size[0] // 2

                # Get album art
                art_surface = self.get_album_art(album_name, album_data.get("art_path"), cover_size, album_data.get("song_path"))
                
                # Apply 3D perspective transformations
                if not is_focused:
                    # Scale the cover for perspective
                    scaled_size = (int(cover_size[0] * scale_factor), int(cover_size[1] * scale_factor))
                    if scaled_size[0] > 0 and scaled_size[1] > 0:
                        art_surface = pygame.transform.smoothscale(art_surface, scaled_size)

                    # Apply rotation for 3D effect
                    if abs(rotation_angle) > 0:
                        try:
                            # Apply more pronounced rotation for iPod Classic effect
                            rotated_surface = pygame.transform.rotate(art_surface, rotation_angle)
                            art_surface = rotated_surface
                        except:
                            pass  # Fallback to non-rotated if rotation fails

                    # Apply alpha for depth
                    if alpha < 255:
                        alpha_surface = pygame.Surface(art_surface.get_size(), pygame.SRCALPHA)
                        alpha_surface.set_alpha(alpha)
                        alpha_surface.blit(art_surface, (0, 0))
                        art_surface = alpha_surface

                # Final position adjustment for rotated/scaled surfaces
                art_rect = art_surface.get_rect()
                final_x = cover_x - (art_rect.width - cover_size[0]) // 2
                final_y = cover_y - (art_rect.height - cover_size[1]) // 2

                # Draw the cover
                screen.blit(art_surface, (final_x, final_y))
                
                # Draw reflection for focused cover
                if is_focused and not self.cover_flow_animation_active:
                    self._draw_cover_reflection(screen, art_surface, final_x, final_y + art_rect.height)

        # Draw album name for focused cover
        if not self.cover_flow_animation_active and self.cover_flow_albums:
            current_album = self.cover_flow_albums[self.current_cover_flow_index]
            album_name = current_album["name"]
            name_surface = self.config.font_menu_item.render(album_name[:25], True, (255, 255, 255))
            name_rect = name_surface.get_rect(centerx=center_x, y=center_y + focused_size[1] // 2 + 60)
            screen.blit(name_surface, name_rect)

        # Draw navigation arrows
        if len(self.cover_flow_albums) > 1:
            # Left arrow
            if self.current_cover_flow_index > 0:
                left_arrow = self.config.font_header.render("◀", True, (150, 150, 150))
                screen.blit(left_arrow, (15, center_y - left_arrow.get_height()//2))
            
            # Right arrow  
            if self.current_cover_flow_index < len(self.cover_flow_albums) - 1:
                right_arrow = self.config.font_header.render("▶", True, (150, 150, 150))
                screen.blit(right_arrow, (self.config.SCREEN_WIDTH - 25, center_y - right_arrow.get_height()//2))

        # Album counter
        if self.cover_flow_albums:
            counter_text = f"{self.current_cover_flow_index + 1} of {len(self.cover_flow_albums)}"
            counter_surface = self.config.font_menu_item_small.render(counter_text, True, (150, 150, 150))
            counter_rect = counter_surface.get_rect(centerx=center_x, y=self.config.DISPLAY_HEIGHT - 35)
            screen.blit(counter_surface, counter_rect)

    def _draw_cover_reflection(self, screen, surface, x, y):
        """Draw a reflection effect for cover art"""
        try:
            reflection_height = int(surface.get_height() * 0.4)
            if reflection_height > 0:
                # Create flipped version
                flipped = pygame.transform.flip(surface, False, True)
                reflection = flipped.subsurface((0, 0, surface.get_width(), reflection_height))
                
                # Apply gradient alpha
                alpha_surface = pygame.Surface(reflection.get_size(), pygame.SRCALPHA)
                for y_alpha in range(reflection_height):
                    alpha_value = max(10, 80 - int((y_alpha / reflection_height) * 70))
                    pygame.draw.line(alpha_surface, (255, 255, 255, alpha_value), 
                                   (0, y_alpha), (reflection.get_width(), y_alpha))
                
                reflection.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(reflection, (x, y + 2))  # Small gap
        except:
            pass  # Skip reflection if any error occurs

    def start_cover_flow_animation(self, direction):
        """Start smooth animation for cover flow navigation"""
        if self.cover_flow_animation_active:
            return  # Don't start new animation while one is running
        
        self.cover_flow_animation_active = True
        self.cover_flow_animation_direction = direction
        self.cover_flow_animation_progress = 0.0
        
        # Set target index
        if direction == "left" and self.current_cover_flow_index > 0:
            self.cover_flow_target_index = self.current_cover_flow_index - 1
        elif direction == "right" and self.current_cover_flow_index < len(self.cover_flow_albums) - 1:
            self.cover_flow_target_index = self.current_cover_flow_index + 1
        else:
            self.cover_flow_animation_active = False

    def update_cover_flow_animation(self, dt):
        """Update cover flow animation progress"""
        if not self.cover_flow_animation_active:
            return
        
        # Update animation progress
        self.cover_flow_animation_progress += self.cover_flow_animation_speed * dt
        
        if self.cover_flow_animation_progress >= 1.0:
            # Animation complete
            self.cover_flow_animation_progress = 1.0
            self.cover_flow_animation_active = False
            self.current_cover_flow_index = self.cover_flow_target_index
            self.cover_flow_animation_direction = "none"

    def ease_in_out_cubic(self, t):
        """Smooth easing function for natural animation"""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2

    def navigate_left(self):
        """Navigate left in Cover Flow"""
        if self.current_cover_flow_index > 0:
            self.start_cover_flow_animation("left")
            return True
        return False

    def navigate_right(self):
        """Navigate right in Cover Flow"""
        if self.current_cover_flow_index < len(self.cover_flow_albums) - 1:
            self.start_cover_flow_animation("right")
            return True
        return False

    def get_current_album(self):
        """Get the currently selected album name"""
        if self.cover_flow_albums and 0 <= self.current_cover_flow_index < len(self.cover_flow_albums):
            return self.cover_flow_albums[self.current_cover_flow_index]["name"]
        return None
