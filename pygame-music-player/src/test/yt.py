import os
from pathlib import Path
from yt_dlp import YoutubeDL

# Configuración
canal_url = 'https://www.youtube.com/channel/UC5OrDvL9DscpcAstz7JnQGA'
output_dir = Path("musica_descargada")

# Opciones para yt-dlp
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': str(output_dir / '%(album,playlist,uploader)s/%(title)s.%(ext)s'),  # Fallback: álbum, playlist o uploader
    'postprocessors': [
        {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
        {'key': 'EmbedThumbnail'},
        {'key': 'FFmpegMetadata'}
    ],
    'writethumbnail': True,
    'writeinfojson': True,
    'quiet': False,
    'ignoreerrors': True,  # Para que no se detenga si hay errores en algún video
}

# Descargar todo el canal
with YoutubeDL(ydl_opts) as ydl:
    ydl.download([canal_url])

print("Descarga completada. Los archivos están organizados por álbum/playlist/uploader.")

# Si quieres forzar la carátula manualmente, puedes recorrer los archivos y usar mutagen,
# pero normalmente yt-dlp ya lo hace bien con EmbedThumbnail.
