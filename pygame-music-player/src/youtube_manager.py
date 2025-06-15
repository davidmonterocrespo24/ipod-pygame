"""
YouTube Manager for iPod Classic interface.
Handles YouTube video search, trending videos, and video information.
"""

import yt_dlp
import requests
import json
from pathlib import Path
import threading
import time
from urllib.parse import quote_plus


class YouTubeManager:
    """Manager for YouTube video search, trending, and playback"""
    
    def __init__(self):
        self.ydl_opts = {
            'format': 'best[height<=480][ext=mp4]/best[height<=480]/best',  # Simplificar formato
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'merge_output_format': 'mp4',
            'socket_timeout': 30,  # Aumentar timeout
            'retries': 10,  # Aumentar reintentos
            'fragment_retries': 10,  # Reintentos para fragmentos
            'skip_unavailable_fragments': True,  # Saltar fragmentos no disponibles
            'http_chunk_size': 10485760,  # Tamaño de chunk más grande
            'buffersize': 1024,  # Buffer más grande
        }
        self.search_results = []
        self.trending_videos = []
        self.is_searching = False
        self.is_loading_trending = False
        self.search_error = None
        
    def search_videos(self, query, max_results=20):
        """Search for YouTube videos"""
        if not query.strip():
            return []
            
        self.is_searching = True
        self.search_results = []
        self.search_error = None
        
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Search for videos
                search_query = f"ytsearch{max_results}:{query}"
                info = ydl.extract_info(search_query, download=False)
                
                if 'entries' in info:
                    for entry in info['entries']:
                        if entry:
                            video_data = {
                                'id': entry.get('id', ''),
                                'title': entry.get('title', 'Unknown Title'),
                                'uploader': entry.get('uploader', 'Unknown Channel'),
                                'duration': self._format_duration(entry.get('duration', 0)),
                                'duration_raw': entry.get('duration', 0),
                                'view_count': entry.get('view_count', 0),
                                'url': entry.get('webpage_url', ''),
                                'thumbnail': entry.get('thumbnail', ''),
                                'description': entry.get('description', '')[:200] + '...' if entry.get('description') else ''
                            }
                            self.search_results.append(video_data)
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            self.search_error = str(e)
        finally:
            self.is_searching = False
            
        return self.search_results
    
    def get_trending_music_videos(self, max_results=25):
        """Get trending music videos"""
        self.is_loading_trending = True
        self.trending_videos = []
        
        try:
            print("Intentando obtener videos trending de YouTube...")
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Try different trending URLs
                trending_urls = [
                    "https://www.youtube.com/feed/trending?bp=4gINGgt5dG1hX2NoYXJ0cw%3D%3D",  # Music category
                    "https://www.youtube.com/feed/trending?bp=4gINGgt5dG1hX2NoYXJ0cw%3D%3D&gl=US",  # US region
                    "https://www.youtube.com/feed/trending?bp=4gINGgt5dG1hX2NoYXJ0cw%3D%3D&gl=ES"   # Spain region
                ]
                
                for url in trending_urls:
                    try:
                        print(f"Intentando URL: {url}")
                        info = ydl.extract_info(url, download=False)
                        
                        if 'entries' in info and info['entries']:
                            print(f"Encontrados {len(info['entries'])} videos en {url}")
                            for entry in info['entries']:
                                if entry and len(self.trending_videos) < max_results:
                                    try:
                                        # Get detailed info for each video
                                        video_info = ydl.extract_info(entry['id'], download=False)
                                        
                                        if video_info:
                                            video_data = {
                                                'id': video_info.get('id', ''),
                                                'title': video_info.get('title', 'Unknown Title'),
                                                'uploader': video_info.get('uploader', 'Unknown Channel'),
                                                'duration': self._format_duration(video_info.get('duration', 0)),
                                                'duration_raw': video_info.get('duration', 0),
                                                'view_count': video_info.get('view_count', 0),
                                                'url': video_info.get('webpage_url', ''),
                                                'thumbnail': video_info.get('thumbnail', ''),
                                                'description': video_info.get('description', '')[:200] + '...' if video_info.get('description') else ''
                                            }
                                            # Avoid duplicates
                                            if not any(v['id'] == video_data['id'] for v in self.trending_videos):
                                                self.trending_videos.append(video_data)
                                                print(f"Añadido video: {video_data['title']}")
                                    except Exception as e:
                                        print(f"Error obteniendo info del video {entry.get('id', 'unknown')}: {e}")
                                        continue
                            
                            # If we got some videos, break the loop
                            if self.trending_videos:
                                break
                    except Exception as e:
                        print(f"Error con URL {url}: {e}")
                        continue
                
                # If no videos found through trending, try fallback
                if not self.trending_videos:
                    print("No se encontraron videos trending, intentando fallback...")
                    self._try_fallback_trending(ydl, max_results)
                    
        except Exception as e:
            print(f"Error general cargando videos trending: {e}")
            # Try fallback if main method fails
            try:
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    self._try_fallback_trending(ydl, max_results)
            except Exception as e:
                print(f"Error en fallback: {e}")
        finally:
            self.is_loading_trending = False
            print(f"Total de videos trending encontrados: {len(self.trending_videos)}")
            
        return self.trending_videos
    
    def _try_fallback_trending(self, ydl, max_results):
        """Try alternative methods to get trending videos"""
        trending_queries = [
            "music trending",
            "viral music videos",
            "top hits",
            "new music videos",
            "popular music",
            "music hits"
        ]
        
        for query in trending_queries:
            try:
                print(f"Intentando búsqueda fallback: {query}")
                search_query = f"ytsearch{max_results//2}:{query}"
                info = ydl.extract_info(search_query, download=False)
                
                if 'entries' in info:
                    for entry in info['entries']:
                        if entry and len(self.trending_videos) < max_results:
                            video_data = {
                                'id': entry.get('id', ''),
                                'title': entry.get('title', 'Unknown Title'),
                                'uploader': entry.get('uploader', 'Unknown Channel'),
                                'duration': self._format_duration(entry.get('duration', 0)),
                                'duration_raw': entry.get('duration', 0),
                                'view_count': entry.get('view_count', 0),
                                'url': entry.get('webpage_url', ''),
                                'thumbnail': entry.get('thumbnail', ''),
                                'description': entry.get('description', '')[:200] + '...' if entry.get('description') else ''
                            }
                            # Avoid duplicates
                            if not any(v['id'] == video_data['id'] for v in self.trending_videos):
                                self.trending_videos.append(video_data)
                                print(f"Añadido video fallback: {video_data['title']}")
            except Exception as e:
                print(f"Error en búsqueda fallback '{query}': {e}")
                continue
    
    def get_video_stream_url(self, video_url):
        """Get direct stream URL for video playback"""
        try:
            print(f"Obteniendo URL del stream para: {video_url}")
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                if not info:
                    print("No se pudo obtener información del video")
                    return None
                
                # Intentar obtener el formato que incluya video y audio
                formats = info.get('formats', [])
                best_format = None
                
                # Primero intentar encontrar un formato que incluya video y audio
                for f in formats:
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        if f.get('height', 0) <= 480:
                            best_format = f
                            break
                
                # Si no se encuentra, usar el formato por defecto
                if not best_format:
                    best_format = info.get('url', '')
                
                print(f"Formato seleccionado: {best_format.get('format_id', 'default')}")
                stream_url = best_format.get('url', '')
                
                # Verificar que la URL sea válida
                if not stream_url:
                    print("URL del stream no válida")
                    return None
                    
                print(f"URL del stream obtenida: {stream_url[:100]}...")
                return stream_url
                
        except Exception as e:
            print(f"Error obteniendo URL del stream: {e}")
            return None
    
    def _format_duration(self, seconds):
        """Format duration from seconds to MM:SS or HH:MM:SS"""
        if not seconds:
            return "0:00"
            
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def _format_view_count(self, count):
        """Format view count to readable format"""
        if not count:
            return "0 views"
            
        if count >= 1000000:
            return f"{count/1000000:.1f}M views"
        elif count >= 1000:
            return f"{count/1000:.1f}K views"
        else:
            return f"{count} views"
