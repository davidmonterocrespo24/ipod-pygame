import pygame
import time
import random

class PlaybackManager:
    def __init__(self, volume_change_callback=None):
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
        pygame.mixer.init()
        self.current_song_path = None
        self.is_playing = False
        self.is_paused = False
        self.position_ms = 0 # Current playback position in milliseconds
        self.duration_s = 0 # Total duration of the song in seconds
        self._volume = 0.7  # Internal volume storage (0.0 to 1.0)
        pygame.mixer.music.set_volume(self._volume)
        self.song_end_event = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.song_end_event)
        self.volume_change_callback = volume_change_callback

    def load_song(self, song_path, duration_s):
        if self.current_song_path == song_path and self.is_playing:
            return # Already playing this song
        try:
            pygame.mixer.music.load(song_path)
            self.current_song_path = song_path
            self.duration_s = duration_s
            self.position_ms = 0
            self.is_playing = False
            self.is_paused = False
            print(f"Canción cargada: {song_path}, Duración: {duration_s}s")
            return True
        except pygame.error as e:
            print(f"Error al cargar la canción {song_path}: {e}")
            self.current_song_path = None
            self.duration_s = 0
            return False

    def play(self):
        if self.current_song_path:
            if self.is_paused:
                pygame.mixer.music.unpause()
                print("Reanudando reproducción.")
            else:
                pygame.mixer.music.play()
                print("Iniciando reproducción.")
            self.is_playing = True
            self.is_paused = False
        else:
            print("No hay canción cargada para reproducir.")

    def pause(self):
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.is_paused = True
            print("Reproducción pausada.")

    def stop(self):
        if self.is_playing or self.is_paused:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.is_paused = False
            self.position_ms = 0
            # self.current_song_path = None # Optionally clear current song
            print("Reproducción detenida.")

    def get_current_position_s(self):
        if self.is_playing and not self.is_paused:
            # pygame.mixer.music.get_pos() returns ms since play started
            # It resets on pause/unpause, so we need to manage it carefully if seeking is added
            return pygame.mixer.music.get_pos() / 1000.0
        elif self.is_paused:
            # This is tricky as get_pos() might be -1 or unreliable when paused.
            # For now, we return the last known position before pause.
            # A more robust solution would involve tracking elapsed time manually.
            return self.position_ms / 1000.0 
        return 0.0

    def update_position_on_pause(self):
        """Call this when pausing to store the current position."""
        if self.is_playing and not self.is_paused: # Should be called before setting is_paused = True
            self.position_ms = pygame.mixer.music.get_pos()

    def get_duration_s(self):
        return self.duration_s

    def set_volume(self, volume_level):
        """Set volume between 0.0 and 1.0."""
        self._volume = max(0.0, min(1.0, volume_level))
        pygame.mixer.music.set_volume(self._volume)
        if self.volume_change_callback:
            self.volume_change_callback(self._volume)
        print(f"Volumen ajustado a: {int(self._volume * 100)}%")

    def get_volume(self):
        return self._volume

    def is_busy(self):
        """Check if music is currently playing or paused (i.e., loaded and not stopped)."""
        return pygame.mixer.music.get_busy() or self.is_paused
    
    def check_song_ended(self, event):
        """Checks if the given Pygame event is the song end event."""
        if event.type == self.song_end_event:
            print("La canción ha terminado (detectado por evento).")
            self.is_playing = False
            self.is_paused = False
            self.position_ms = 0 # Reset position
            return True
        return False

    def seek(self, time_s):
        """Seek to a specific time in the song (in seconds)."""
        if self.current_song_path and self.duration_s > 0:
            seek_pos_s = max(0, min(time_s, self.duration_s))
            try:
                # Stop, then play from the start, then set position
                # This is a common way to handle seeking with pygame.mixer.music
                # as direct seeking can be unreliable or not supported for all formats.
                current_volume = self.get_volume()
                was_playing = self.is_playing
                was_paused = self.is_paused

                pygame.mixer.music.stop() # Stop playback
                pygame.mixer.music.play(start=seek_pos_s) # Play from new position
                
                # If it was paused, pause it again. If it wasn't playing, stop it.
                if was_paused:
                    pygame.mixer.music.pause()
                    self.is_playing = False
                    self.is_paused = True
                elif not was_playing:
                    pygame.mixer.music.stop()
                    self.is_playing = False
                    self.is_paused = False
                else: # was playing
                    self.is_playing = True
                    self.is_paused = False
                
                self.position_ms = seek_pos_s * 1000
                pygame.mixer.music.set_volume(current_volume) # Restore volume
                print(f"Seek a {seek_pos_s:.2f}s")

            except pygame.error as e:
                print(f"Error al buscar en la canción: {e}")
        else:
            print("No se puede buscar: no hay canción cargada o duración desconocida.")


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((300, 200))
    pygame.display.set_caption("Playback Test")
    
    # Create a dummy MP3 file for testing
    # You'll need a real MP3 file here. `mutagen` can create one, or use an existing file.
    # For simplicity, this example assumes 'dummy_song.mp3' exists and has some duration.
    # Example: create a tiny silent mp3 if you have ffmpeg
    # import os
    # os.system("ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 10 -q:a 9 dummy_song.mp3 -y")

    # Changed to test a song from a hypothetical "Album Motion"
    # For this test to work:
    # 1. Create a file named "motion_album_test_song.mp3" (or your actual song file).
    # 2. Place it where this script can find it (e.g., in the 'src' folder or provide a full path).
    # 3. Ensure it's a valid MP3 file.
    # The main application (main.py) will find and list "Album Motion" 
    # by scanning your music library directories and reading metadata.
    test_song_path = "motion_album_test_song.mp3" # REPLACE WITH A VALID MP3 PATH from "Album Motion"
    
    # Check if test_song_path exists, if not, skip playback test portion
    try:
        with open(test_song_path, 'rb') as f:
            pass # File exists
        song_available = True
        print(f"Attempting to test playback with: {test_song_path}")
    except FileNotFoundError:
        print(f"Test song '{test_song_path}' not found. Please create this file or update the path.")
        print("Skipping playback tests that require a song file.")
        song_available = False

    playback = PlaybackManager()
    clock = pygame.time.Clock()
    running = True

    if song_available:
        # Assume duration is 10 seconds for the test song. 
        # For a real song, this duration would ideally come from its metadata.
        playback.load_song(test_song_path, 10.0) 
        playback.play()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if playback.check_song_ended(event):
                print("Evento de fin de canción recibido en el bucle principal.")
                # playback.play() # Example: play again
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and song_available:
                    if playback.is_playing:
                        playback.pause()
                    else:
                        playback.play()
                if event.key == pygame.K_s and song_available:
                    playback.stop()
                if event.key == pygame.K_UP:
                    new_vol = min(1.0, playback.get_volume() + 0.1)
                    playback.set_volume(new_vol)
                if event.key == pygame.K_DOWN:
                    new_vol = max(0.0, playback.get_volume() - 0.1)
                    playback.set_volume(new_vol)
                if event.key == pygame.K_RIGHT and song_available:
                    current_pos = playback.get_current_position_s()
                    playback.seek(current_pos + 5) # Seek forward 5s
                if event.key == pygame.K_LEFT and song_available:
                    current_pos = playback.get_current_position_s()
                    playback.seek(current_pos - 5) # Seek backward 5s

        # Update screen
        screen.fill((30, 30, 30))
        if song_available and playback.current_song_path:
            pos_s = playback.get_current_position_s()
            dur_s = playback.get_duration_s()
            font = pygame.font.Font(None, 36)
            text = font.render(f"{pos_s:.1f}s / {dur_s:.1f}s", True, (200, 200, 200))
            screen.blit(text, (50, 50))
            
            vol_text = font.render(f"Vol: {int(playback.get_volume()*100)}%", True, (200, 200, 200))
            screen.blit(vol_text, (50, 100))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
