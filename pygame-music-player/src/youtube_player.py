"""
YouTube Player for iPod Classic interface.
Handles YouTube video playback using existing VideoPlayer infrastructure.
"""

import pygame
import threading
import os
import tempfile
from pathlib import Path
from video_player import VideoPlayer

try:
    from ffpyplayer.player import MediaPlayer
    FFPYPLAYER_AVAILABLE = True
except ImportError:
    FFPYPLAYER_AVAILABLE = False
    print("Warning: ffpyplayer not available. YouTube video playback will be disabled.")


class YouTubePlayer:
    """YouTube video player using existing VideoPlayer infrastructure"""
    
    def __init__(self, ui_config):
        self.ui_config = ui_config
        self.current_video = None
        self.video_player = VideoPlayer(ui_config)
        self.download_thread = None
        self.temp_file_path = None    
    def play_youtube_video(self, video_data):
        """Play a YouTube video using the VideoPlayer"""
        if not FFPYPLAYER_AVAILABLE:
            print("Error: ffpyplayer no está disponible para reproducir videos")
            return False
            
        self.current_video = video_data
        
        # Get stream URL
        from youtube_manager import YouTubeManager
        youtube_manager = YouTubeManager()
        
        try:
            # Get the stream URL from YouTube
            stream_url = youtube_manager.get_video_stream_url(video_data['url'])
            if not stream_url:
                print("No se pudo obtener la URL del video")
                return False
            
            print(f"Reproduciendo: {video_data['title']} by {video_data['uploader']}")
              # Use the existing VideoPlayer to play the stream URL directly
            success = self.video_player.play_video(stream_url)
            
            return success
            
        except Exception as e:
            print(f"Error playing YouTube video: {e}")
            return False
    
    def pause_video(self):
        """Pause video playback"""
        self.video_player.pause_video()
        print("Video pausado")
    
    def resume_video(self):
        """Resume video playback"""
        self.video_player.pause_video()  # VideoPlayer's pause_video toggles pause/resume
        print("Video reanudado")
    
    def stop_video(self):
        """Stop video playback"""
        self.video_player.stop_video()
        self.current_video = None
        print("Video detenido")
    
    def is_playing(self):
        """Check if video is currently playing"""
        return self.video_player.video_playing
    
    def is_paused(self):
        """Check if video is paused"""
        return self.video_player.video_paused
    
    def draw_youtube_video_playing(self, surface, renderer):
        """Draw YouTube video playing screen using VideoPlayer"""
        if not self.current_video:
            renderer.draw_background()
            renderer.draw_header("YouTube")
            renderer.draw_message_screen("No hay video seleccionado")
            return
        
        # Use VideoPlayer's drawing method but with YouTube header and custom overlays
        result = self.video_player.draw_video_playing(surface, renderer)
        
        # Override the header to show "YouTube" instead of "Video"
        renderer.draw_header("YouTube")
          # Add YouTube-specific video info overlay
        if self.video_player.video_playing and not result:
            self._draw_youtube_video_info(surface, renderer)
        
        return result
    
    def _draw_youtube_video_info(self, surface, renderer):
        """Draw YouTube-specific video information overlay"""
        # Calculate position for video info
        info_y = self.ui_config.DISPLAY_HEIGHT - 100
        
        # Create semi-transparent background for video info
        info_height = 70
        info_surface = pygame.Surface((self.ui_config.SCREEN_WIDTH, info_height))
        info_surface.set_alpha(180)
        info_surface.fill((0, 0, 0))
        surface.blit(info_surface, (0, info_y))
        
        # Video title - using font_now_playing_title and white text
        title_text = self.current_video['title']
        if len(title_text) > 35:
            title_text = title_text[:35] + "..."
        title_surface = self.ui_config.font_now_playing_title.render(title_text, True, (255, 255, 255))
        surface.blit(title_surface, (10, info_y + 5))
        
        # Channel name - using font_now_playing_artist and light gray text
        channel_text = f"Por: {self.current_video['uploader']}"
        if len(channel_text) > 40:
            channel_text = channel_text[:40] + "..."
        channel_surface = self.ui_config.font_now_playing_artist.render(channel_text, True, (200, 200, 200))
        surface.blit(channel_surface, (10, info_y + 25))
        
        # Duration and views - using font_small and light gray text
        duration_str = self.current_video.get('duration', '0:00')
        view_count = self._format_view_count(self.current_video.get('view_count', 0))
        info_text = f"{duration_str} • {view_count}"
        info_surface_text = self.ui_config.font_small.render(info_text, True, (200, 200, 200))
        surface.blit(info_surface_text, (10, info_y + 45))
    
    def _format_view_count(self, count):
        """Format view count to readable format"""
        if not count:
            return "0 visualizaciones"
            
        if count >= 1000000:
            return f"{count/1000000:.1f}M visualizaciones"
        elif count >= 1000:
            return f"{count/1000:.1f}K visualizaciones"
        else:
            return f"{count} visualizaciones"
    
    def update_playback_position(self, dt):
        """Update video playback position (compatibility method)"""
        # The VideoPlayer handles its own timing internally
        pass
    
    def seek_forward(self, seconds=10):
        """Seek forward in video (placeholder - VideoPlayer doesn't have seek support)"""
        print(f"Adelantando {seconds}s (función no implementada en VideoPlayer)")
    
    def seek_backward(self, seconds=10):
        """Seek backward in video (placeholder - VideoPlayer doesn't have seek support)"""
        print(f"Retrocediendo {seconds}s (función no implementada en VideoPlayer)")
