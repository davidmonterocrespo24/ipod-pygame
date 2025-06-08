import sqlite3
from pathlib import Path
from mutagen import File
import time

class MusicDatabase:
    def __init__(self, db_path="music_library.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializar base de datos SQLite """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                title TEXT,
                artist TEXT,
                album TEXT,
                duration REAL,
                file_size INTEGER,
                last_modified REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS playlist_songs (
                playlist_id INTEGER,
                song_id INTEGER,
                position INTEGER,
                FOREIGN KEY (playlist_id) REFERENCES playlists (id),
                FOREIGN KEY (song_id) REFERENCES songs (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def scan_music_library(self, music_dirs=None):
        """Escanear y actualizar biblioteca de música """
        if music_dirs is None:
            # Consider common music locations for different OS if possible
            # For now, using the provided defaults and adding user's home directory
            music_dirs_paths = [
                Path.home() / "Music",
                Path("./music")  # Directorio local relativo al script
            ]
            # Add platform-specific paths if needed, e.g., for external drives
            # On Linux/macOS:
            # music_dirs_paths.append(Path("/media"))
            # music_dirs_paths.append(Path("/mnt"))
            # On Windows, drive letters might be more complex to auto-detect robustly
            # For simplicity, we'll rely on user putting music in ~/Music or ./music
        else:
            music_dirs_paths = [Path(d) for d in music_dirs]

        supported_formats = {'.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac'}
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        print("Escaneando biblioteca de música...")
        songs_processed = 0
        songs_added_or_updated = 0
        
        for music_dir_path in music_dirs_paths:
            if not music_dir_path.exists() or not music_dir_path.is_dir():
                print(f"Directorio no encontrado o no es un directorio: {music_dir_path}")
                continue
            
            print(f"Escaneando en: {music_dir_path}")
            for file_path in music_dir_path.rglob("*"):
                if file_path.suffix.lower() in supported_formats and file_path.is_file():
                    songs_processed += 1
                    try:
                        stat = file_path.stat()
                        cursor.execute(
                            "SELECT last_modified FROM songs WHERE path = ?",
                            (str(file_path),)
                        )
                        result = cursor.fetchone()
                        
                        if result and result[0] == stat.st_mtime:
                            continue  # Archivo no modificado
                        
                        metadata = self.extract_metadata(file_path)
                        
                        cursor.execute('''
                            INSERT OR REPLACE INTO songs 
                            (path, title, artist, album, duration, file_size, last_modified)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            str(file_path),
                            metadata['title'],
                            metadata['artist'],
                            metadata['album'],
                            metadata['duration'],
                            stat.st_size,
                            stat.st_mtime
                        ))
                        songs_added_or_updated +=1
                        
                        if songs_processed % 50 == 0:
                            print(f"Procesadas {songs_processed} canciones...")
                            
                    except Exception as e:
                        print(f"Error procesando {file_path}: {e}")
        
        conn.commit()
        conn.close()
        print(f"Escaneo completado. {songs_processed} archivos revisados, {songs_added_or_updated} canciones añadidas/actualizadas.")
        if songs_added_or_updated > 0:
            print("Biblioteca actualizada.")
        else:
            print("La biblioteca ya estaba al día.")

    def extract_metadata(self, file_path_obj):
        """Extraer metadatos de archivo de audio """
        file_path = str(file_path_obj)
        try:
            audio_file = File(file_path)
            if audio_file is None: # Should not happen if File() itself doesn't raise error
                # Fallback for files not recognized by mutagen but having valid extension
                return {
                    'title': file_path_obj.stem,
                    'artist': "Artista Desconocido",
                    'album': "Álbum Desconocido",
                    'duration': 0
                }

            title = file_path_obj.stem # Default to filename stem
            artist = "Artista Desconocido"
            album = "Álbum Desconocido"
            duration = 0

            if audio_file.info:
                duration = getattr(audio_file.info, 'length', 0)

            if audio_file.tags:
                # MP3 (ID3)
                if 'TIT2' in audio_file.tags: title = str(audio_file.tags['TIT2'].text[0])
                if 'TPE1' in audio_file.tags: artist = str(audio_file.tags['TPE1'].text[0])
                if 'TALB' in audio_file.tags: album = str(audio_file.tags['TALB'].text[0])
                # FLAC/OGG (Vorbis Comments)
                elif 'TITLE' in audio_file.tags: title = str(audio_file.tags['TITLE'][0])
                elif 'ARTIST' in audio_file.tags: artist = str(audio_file.tags['ARTIST'][0])
                elif 'ALBUM' in audio_file.tags: album = str(audio_file.tags['ALBUM'][0])
                # M4A/MP4 (iTunes-style metadata)
                elif '\xa9nam' in audio_file.tags: title = str(audio_file.tags['\xa9nam'][0])
                elif '\xa9ART' in audio_file.tags: artist = str(audio_file.tags['\xa9ART'][0])
                elif '\xa9alb' in audio_file.tags: album = str(audio_file.tags['\xa9alb'][0])
            
            return {
                'title': title if title else file_path_obj.stem,
                'artist': artist,
                'album': album,
                'duration': duration if duration else 0
            }
            
        except Exception as e:
            # print(f"Error extrayendo metadatos de {file_path}: {e}")
            return {
                'title': file_path_obj.stem,
                'artist': "Artista Desconocido",
                'album': "Álbum Desconocido",
                'duration': 0
            }
    
    def get_all_songs(self):
        """Obtener todas las canciones """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Return id along with other details
        cursor.execute('''
            SELECT id, path, title, artist, album, duration 
            FROM songs 
            ORDER BY artist, album, title
        ''')
        songs = cursor.fetchall()
        conn.close()
        return songs
    
    def get_artists(self):
        """Obtener lista de artistas """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT artist FROM songs WHERE artist IS NOT NULL AND artist != "" ORDER BY artist')
        artists = [row[0] for row in cursor.fetchall()]
        conn.close()
        return artists
    
    def get_albums(self):
        """Obtener lista de álbumes """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT album FROM songs WHERE album IS NOT NULL AND album != "" ORDER BY album')
        albums = [row[0] for row in cursor.fetchall()]
        conn.close()
        return albums
    
    def get_songs_by_artist(self, artist):
        """Obtener canciones por artista """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, path, title, artist, album, duration 
            FROM songs 
            WHERE artist = ? 
            ORDER BY album, title
        ''', (artist,))
        songs = cursor.fetchall()
        conn.close()
        return songs
    
    def get_songs_by_album(self, album):
        """Obtener canciones por álbum """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, path, title, artist, album, duration 
            FROM songs 
            WHERE album = ? 
            ORDER BY title
        ''', (album,))
        songs = cursor.fetchall()
        conn.close()
        return songs

    def get_song_by_id(self, song_id):
        """Obtener una canción por su ID """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, path, title, artist, album, duration 
            FROM songs 
            WHERE id = ?
        ''', (song_id,))
        song = cursor.fetchone()
        conn.close()
        return song

if __name__ == '__main__':
    # Example Usage:
    db = MusicDatabase(db_path="test_music_library.db")
    
    # Create a dummy music directory for testing
    test_music_dir = Path("test_music")
    test_music_dir.mkdir(exist_ok=True)
    (test_music_dir / "fake_song1.mp3").write_text("dummy mp3 content")
    (test_music_dir / "fake_song2.wav").write_text("dummy wav content")
    
    # Scan library
    db.scan_music_library(music_dirs=[str(test_music_dir)])
    
    print("\\nTodas las canciones:")
    for song in db.get_all_songs():
        print(song)
        
    print("\\nArtistas:")
    for artist in db.get_artists():
        print(artist)
        
    print("\\nÁlbumes:")
    for album in db.get_albums():
        print(album)

    # Clean up dummy directory and db
    # import shutil
    # shutil.rmtree(test_music_dir)
    # Path("test_music_library.db").unlink(missing_ok=True)
