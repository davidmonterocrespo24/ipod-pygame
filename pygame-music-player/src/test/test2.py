import os
import requests
from pathlib import Path
from yt_dlp import YoutubeDL
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

# URL de la playlist (álbum)
playlist_url = 'https://www.youtube.com/watch?v=Zi_XLOBDo_Y&list=PL135553AD7F1D0ABF'  # Cambia por la playlist deseada
output_dir = Path("musica_descargada")

# 1. Obtener información de la playlist para el nombre y la miniatura
with YoutubeDL({'quiet': True}) as ydl:
    info = ydl.extract_info(playlist_url, download=False)
    album_title = info.get('title', 'album')
    cover_url = info.get('thumbnails', [{}])[-1].get('url', None)

album_dir = output_dir / album_title
album_dir.mkdir(parents=True, exist_ok=True)

# 2. Descargar la miniatura (cover)
cover_path = album_dir / "cover.jpg"
if cover_url:
    r = requests.get(cover_url)
    with open(cover_path, "wb") as f:
        f.write(r.content)
else:
    cover_path = None

# 3. Descargar las canciones de la playlist
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': str(album_dir / '%(title)s.%(ext)s'),
    'postprocessors': [
        {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
        {'key': 'EmbedThumbnail'},
        {'key': 'FFmpegMetadata'}
    ],
    'writethumbnail': True,
    'writeinfojson': True,
    'quiet': False,
    'ignoreerrors': True,
}

with YoutubeDL(ydl_opts) as ydl:
    ydl.download([playlist_url])

# 4. Insertar la carátula en cada MP3 (por si yt-dlp falla)
if cover_path and cover_path.exists():
    for mp3_file in album_dir.glob("*.mp3"):
        audio = MP3(mp3_file, ID3=ID3)
        if not audio.tags.getall('APIC'):
            with open(cover_path, 'rb') as img:
                audio.tags.add(APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc=u'Cover',
                    data=img.read()
                ))
            audio.save()
            print(f"Carátula añadida a {mp3_file.name}")

print(f"Álbum '{album_title}' descargado en '{album_dir}'.")