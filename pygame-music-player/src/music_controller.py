"""
Music control module for iPod Classic interface.
Handles music playback logic, playlists, and song management.
"""
import random
from pathlib import Path


class MusicController:
    """Handles music playback logic and song management"""
    
    def __init__(self, db, playback_manager):
        self.db = db
        self.playback = playback_manager
        
        # Playback state
        self.current_song_data = None  # (id, path, title, artist, album, duration)
        self.playlist_for_playback = []  # Current list of songs for play, next, prev
        self.current_playlist_index = -1
        
        # Settings
        self.repeat_mode = "off"  # off, one, all
        self.shuffle_mode = False

    def play_song_from_data(self, song_data):
        """Play a song from song data tuple"""
        # song_data = (id, path, title, artist, album, duration)
        if song_data and Path(song_data[1]).exists():
            self.current_song_data = song_data
            success = self.playback.load_song(song_data[1], song_data[5])
            if success:
                self.playback.play()
                return True
            else:
                self.current_song_data = None
                return False
        else:
            self.current_song_data = None
            return False

    def play_song_from_list(self, song_data, song_list):
        """Play a song and set up the playlist context"""
        # When a song is selected from a list, that list becomes the current playlist
        self.playlist_for_playback = [item["data"] for item in song_list if item["action"] == "play_song"]
        try:
            self.current_playlist_index = self.playlist_for_playback.index(song_data)
        except ValueError:
            # Should not happen if data came from current_list_items
            self.current_playlist_index = 0 
            self.playlist_for_playback = [song_data] 

        return self.play_song_from_data(song_data)

    def play_all_shuffle(self):
        """Play all songs in shuffle mode"""
        all_songs = self.db.get_all_songs()
        if all_songs:
            self.playlist_for_playback = random.sample(all_songs, len(all_songs))
            self.current_playlist_index = 0
            self.shuffle_mode = True
            return self.play_song_from_data(self.playlist_for_playback[0])
        return False

    def handle_song_end(self):
        """Handle when a song ends - advance according to repeat/shuffle settings"""
        if not self.playlist_for_playback or self.current_playlist_index == -1:
            self.playback.stop()
            self.current_song_data = None
            return "stopped"

        if self.repeat_mode == "one":
            # Repeat current song
            self.play_song_from_data(self.playlist_for_playback[self.current_playlist_index])
            return "repeated"
        elif self.shuffle_mode and self.repeat_mode != "one":
            # Shuffle to next song
            if len(self.playlist_for_playback) > 1:
                new_index = self.current_playlist_index
                while new_index == self.current_playlist_index:
                    new_index = random.randrange(len(self.playlist_for_playback))
                self.current_playlist_index = new_index
            else:
                self.current_playlist_index = 0
            self.play_song_from_data(self.playlist_for_playback[self.current_playlist_index])
            return "shuffled"
        elif self.repeat_mode == "all":
            # Advance to next song, wrap around
            self.current_playlist_index = (self.current_playlist_index + 1) % len(self.playlist_for_playback)
            self.play_song_from_data(self.playlist_for_playback[self.current_playlist_index])
            return "advanced"
        else:
            # Repeat mode is off, advance if possible
            if self.current_playlist_index < len(self.playlist_for_playback) - 1:
                self.current_playlist_index += 1
                self.play_song_from_data(self.playlist_for_playback[self.current_playlist_index])
                return "advanced"
            else:
                # End of playlist, stop
                self.playback.stop()
                self.current_song_data = None
                return "ended"

    def next_song(self):
        """Skip to next song"""
        if not self.playlist_for_playback or self.current_playlist_index == -1:
            return False
        
        if self.shuffle_mode:
            if len(self.playlist_for_playback) > 1:
                new_index = self.current_playlist_index
                while new_index == self.current_playlist_index:
                    new_index = random.randrange(len(self.playlist_for_playback))
                self.current_playlist_index = new_index
            else:
                self.current_playlist_index = 0
        else:
            self.current_playlist_index = (self.current_playlist_index + 1) % len(self.playlist_for_playback)
        
        return self.play_song_from_data(self.playlist_for_playback[self.current_playlist_index])

    def previous_song(self):
        """Go to previous song or restart current if >3 seconds played"""
        if not self.playlist_for_playback or self.current_playlist_index == -1:
            return False

        # If current song has played for more than ~3 seconds, restart it
        if self.playback.get_current_position_s() > 3.0:
            return self.play_song_from_data(self.playlist_for_playback[self.current_playlist_index])

        if self.shuffle_mode:
            # In shuffle, previous could also be random
            if len(self.playlist_for_playback) > 1:
                new_index = self.current_playlist_index
                while new_index == self.current_playlist_index:
                    new_index = random.randrange(len(self.playlist_for_playback))
                self.current_playlist_index = new_index
            else:
                self.current_playlist_index = 0
        else:
            if self.current_playlist_index > 0:
                self.current_playlist_index -= 1
            else:
                # Wrap around to the end
                self.current_playlist_index = len(self.playlist_for_playback) - 1
        
        return self.play_song_from_data(self.playlist_for_playback[self.current_playlist_index])

    def toggle_playback(self):
        """Toggle play/pause"""
        if self.playback.is_playing:
            if self.playback.is_paused:
                self.playback.unpause()
            else:
                self.playback.pause()
        elif self.current_song_data:
            # Resume if song is loaded but not playing
            self.playback.play()
        else:
            # No song loaded, try to play first available song
            return self.play_first_available_song()
        return True

    def play_first_available_song(self):
        """Play the first available song if no song is currently loaded"""
        if not self.current_song_data:
            all_songs = self.db.get_all_songs()
            if all_songs:
                self.playlist_for_playback = all_songs
                self.current_playlist_index = 0
                return self.play_song_from_data(all_songs[0])
        return False

    def toggle_repeat_mode(self):
        """Cycle through repeat modes: off -> one -> all -> off"""
        if self.repeat_mode == "off":
            self.repeat_mode = "one"
        elif self.repeat_mode == "one":
            self.repeat_mode = "all"
        else:
            self.repeat_mode = "off"

    def toggle_shuffle_mode(self):
        """Toggle shuffle mode on/off"""
        self.shuffle_mode = not self.shuffle_mode

    def get_current_song_info(self):
        """Get current song information"""
        return self.current_song_data

    def get_playlist_info(self):
        """Get current playlist information (current index, total count)"""
        if self.playlist_for_playback and self.current_playlist_index >= 0:
            return (self.current_playlist_index, len(self.playlist_for_playback))
        return None

    def get_playback_state(self):
        """Get current playback state"""
        return {
            "is_playing": self.playback.is_playing,
            "is_paused": self.playback.is_paused,
            "current_position": self.playback.get_current_position_s(),
            "volume": self.playback.get_volume(),
            "repeat_mode": self.repeat_mode,
            "shuffle_mode": self.shuffle_mode
        }

    def get_repeat_mode(self):
        """Get current repeat mode"""
        return self.repeat_mode

    def get_shuffle_mode(self):
        """Get current shuffle mode"""
        return self.shuffle_mode

    def set_volume(self, volume):
        """Set playback volume (0.0 to 1.0)"""
        self.playback.set_volume(max(0.0, min(1.0, volume)))

    def adjust_volume(self, delta):
        """Adjust volume by delta amount"""
        current_volume = self.playback.get_volume()
        new_volume = max(0.0, min(1.0, current_volume + delta))
        self.set_volume(new_volume)

    def stop(self):
        """Stop playback and clear current song"""
        self.playback.stop()
        self.current_song_data = None

    def get_current_playlist_index(self):
        """Get current playlist index"""
        return self.current_playlist_index

    def get_playlist_length(self):
        """Get length of current playlist"""
        return len(self.playlist_for_playback) if self.playlist_for_playback else 0