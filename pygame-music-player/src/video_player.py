"""
Video playback module for iPod Classic interface.
Handles video file management and playback using ffpyplayer.
"""
import pygame
import os
import time
from pathlib import Path

try:
    from ffpyplayer.player import MediaPlayer
    FFPYPLAYER_AVAILABLE = True
except ImportError:
    FFPYPLAYER_AVAILABLE = False
    print("Warning: ffpyplayer not available. Video playback will be disabled.")


class VideoPlayer:
    """Handles video playback functionality"""
    
    def __init__(self, config):
        self.config = config
        
        # Video playback state
        self.current_video_data = None  # (path, filename)
        self.video_playing = False
        self.video_paused = False
        self.video_files = []  # List of available video files
        self.video_player = None  # ffpyplayer MediaPlayer instance
        self.video_surface = None  # pygame surface for video frames
        self.video_start_time = 0  # Time when video started playing
        self.video_pause_time = 0  # Time when video was paused

    def scan_video_files(self):
        """Scan for video files in the videos directory"""
        # Define video directories to scan
        project_video_dir = Path(__file__).parent.parent / "videos"
        project_video_dir.mkdir(exist_ok=True)  # Create it if it doesn't exist

        self.video_files = []
        
        # Supported video formats
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        #imprimir la ruta del directorio de videos
        print(f"Scanning for videos in: {project_video_dir}")

        if project_video_dir.exists():
            for file_path in project_video_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in video_extensions:
                    self.video_files.append(str(file_path))
        
        # Sort video files alphabetically
        self.video_files.sort()
        #imprimir la lista de archivos de video encontrados
        print(f"Found {len(self.video_files)} video files: {self.video_files}")
        return self.video_files

    def play_video(self, video_path):
        """Start video playback using ffpyplayer"""
        if not FFPYPLAYER_AVAILABLE:
            return False
            
        try:
            # Stop any current video
            self.stop_video()
            
            # Create new video player
            self.video_player = MediaPlayer(video_path)
            self.current_video_data = (video_path, Path(video_path).name)
            self.video_playing = True
            self.video_paused = False
            self.video_start_time = time.time()
            
            return True
            
        except Exception as e:
            print(f"Error starting video playback: {e}")
            self.stop_video()
            return False

    def pause_video(self):
        """Pause/unpause video playback"""
        if not self.video_player:
            return
            
        if self.video_paused:
            # Resume video
            if hasattr(self, 'video_pause_time'):
                # Adjust start time to account for pause duration
                pause_duration = time.time() - self.video_pause_time
                self.video_start_time += pause_duration
            self.video_paused = False
        else:
            # Pause video
            self.video_pause_time = time.time()
            self.video_paused = True

    def stop_video(self):
        """Stop video playback and cleanup"""
        if self.video_player:
            self.video_player.close_player()
            self.video_player = None
        
        self.video_playing = False
        self.video_paused = False
        self.current_video_data = None
        self.video_surface = None

    def get_video_frame(self):
        """Get current video frame for rendering"""
        if not self.video_player or not FFPYPLAYER_AVAILABLE:
            return None, None
            
        try:
            # Get video frame
            frame, val = self.video_player.get_frame()
            return frame, val
        except Exception as e:
            print(f"Error getting video frame: {e}")
            return None, None

    def draw_video_playing(self, screen, renderer):
        """Draw the video playback screen"""
        if not self.video_player or not FFPYPLAYER_AVAILABLE:
            # Fallback display
            renderer.draw_background()
            title = "Video" if FFPYPLAYER_AVAILABLE else "Video Error"
            renderer.draw_header(title)
            
            # Display error or loading message
            if not FFPYPLAYER_AVAILABLE:
                text = "Video playback unavailable"
            else:
                text = "Loading video..."
            
            renderer.draw_message_screen(text)
            return
            
        try:
            # Get video frame
            frame, val = self.get_video_frame()
            
            if frame is not None:
                try:
                    # Extract the actual frame from tuple if needed
                    actual_frame = frame[0] if isinstance(frame, tuple) else frame
                    
                    # Convert frame to pygame surface
                    w, h = actual_frame.get_size()
                    frame_data = actual_frame.to_bytearray()[0]
                    
                    # Create pygame surface from frame data
                    frame_surface = pygame.image.frombuffer(frame_data, (w, h), 'RGB')
                    
                    # Scale frame to fit iPod screen while maintaining aspect ratio
                    video_area_height = self.config.DISPLAY_HEIGHT - self.config.header_height
                    video_area_width = self.config.SCREEN_WIDTH
                    
                    # Calculate scaled dimensions
                    aspect_ratio = w / h
                    if w > h:
                        # Landscape video
                        scaled_width = min(video_area_width, w)
                        scaled_height = int(scaled_width / aspect_ratio)
                        if scaled_height > video_area_height:
                            scaled_height = video_area_height
                            scaled_width = int(scaled_height * aspect_ratio)
                    else:
                        # Portrait video
                        scaled_height = min(video_area_height, h)
                        scaled_width = int(scaled_height * aspect_ratio)
                        if scaled_width > video_area_width:
                            scaled_width = video_area_width
                            scaled_height = int(scaled_width / aspect_ratio)
                    
                    # Scale the frame
                    scaled_frame = pygame.transform.scale(frame_surface, (scaled_width, scaled_height))
                    
                    # Clear screen with black
                    screen.fill((0, 0, 0))
                    
                    # Draw header
                    renderer.draw_header("Video")
                    
                    # Center the video frame
                    frame_x = (self.config.SCREEN_WIDTH - scaled_width) // 2
                    frame_y = self.config.header_height + (video_area_height - scaled_height) // 2
                    
                    screen.blit(scaled_frame, (frame_x, frame_y))
                    
                    # Draw video controls overlay (bottom of screen)
                    self.draw_video_controls(screen)
                    
                except Exception as e:
                    print(f"Error processing frame: {e}")
                    renderer.draw_background()
                    renderer.draw_header("Video")
                    text = f"Frame error: {str(e)[:20]}..."
                    renderer.draw_message_screen(text)
            else:
                # No frame available, show loading or ended message
                renderer.draw_background()
                renderer.draw_header("Video")
                
                if isinstance(val, (int, float)) and val < 0:  # Negative val indicates EOF
                    text = "Video ended"
                    renderer.draw_message_screen(text)
                    # Auto-return to video menu after video ends
                    pygame.time.wait(1000)
                    self.stop_video()
                    return "ended"
                else:
                    text = "Loading video..."
                    renderer.draw_message_screen(text)
                
        except Exception as e:
            print(f"Error in video playback: {e}")
            renderer.draw_background()
            renderer.draw_header("Video")
            renderer.draw_message_screen("Video playback error")
            # Auto-return to video menu after error
            pygame.time.wait(2000)
            self.stop_video()
            return "error"

    def draw_video_controls(self, screen):
        """Draw video playback controls with progress bar at the bottom of the screen"""
        controls_height = 50
        controls_y = self.config.DISPLAY_HEIGHT - controls_height
        
        # Semi-transparent background for controls
        controls_surface = pygame.Surface((self.config.SCREEN_WIDTH, controls_height))
        controls_surface.set_alpha(200)
        controls_surface.fill((0, 0, 0))
        screen.blit(controls_surface, (0, controls_y))
        
        # Get video duration and current position
        current_time = 0.0
        duration = 60.0  # Default duration if unknown
        
        if self.video_player:
            try:
                # Get current playback position
                current_time = time.time() - self.video_start_time
                if self.video_paused and hasattr(self, 'video_pause_time'):
                    current_time = self.video_pause_time - self.video_start_time
                
                # Try to get duration from video metadata
                duration = getattr(self.video_player, 'duration', None) or 60.0
                
                # Ensure current_time doesn't exceed duration
                current_time = min(current_time, duration)
                
            except Exception:
                current_time = 0.0
                duration = 60.0
        
        # Progress bar
        progress_bar_width = self.config.SCREEN_WIDTH - 40
        progress_bar_height = 4
        progress_bar_x = 20
        progress_bar_y = controls_y + 8
        
        # Background of progress bar
        pygame.draw.rect(screen, (60, 60, 60), 
                        (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height), 
                        border_radius=2)
        
        # Progress fill
        if duration > 0:
            progress_width = int((current_time / duration) * progress_bar_width)
            if progress_width > 0:
                pygame.draw.rect(screen, (255, 255, 255), 
                                (progress_bar_x, progress_bar_y, progress_width, progress_bar_height), 
                                border_radius=2)
        
        # Time display
        current_time_str = self.config.format_time(current_time)
        duration_str = self.config.format_time(duration)
        time_text = f"{current_time_str} / {duration_str}"
        
        time_surf = self.config.font_small.render(time_text, True, (255, 255, 255))
        time_x = progress_bar_x
        time_y = progress_bar_y + progress_bar_height + 5
        screen.blit(time_surf, (time_x, time_y))
        
        # Play/Pause indicator and controls
        if self.video_paused:
            status_text = "▶ PAUSED"
            controls_text = "Space: Play, Esc: Exit"
        else:
            status_text = "❚❚ PLAYING"
            controls_text = "Space: Pause, Esc: Exit"
        
        # Status indicator (play/pause)
        status_surf = self.config.font_small.render(status_text, True, (255, 255, 255))
        status_x = self.config.SCREEN_WIDTH - status_surf.get_width() - 20
        status_y = time_y
        screen.blit(status_surf, (status_x, status_y))
        
        # Control instructions
        controls_surf = self.config.font_small.render(controls_text, True, (200, 200, 200))
        controls_x = (self.config.SCREEN_WIDTH - controls_surf.get_width()) // 2
        controls_y_pos = controls_y + controls_height - 15
        screen.blit(controls_surf, (controls_x, controls_y_pos))
