# iPod Classic Music Player

Un reproductor de música en Python que emula la interfaz clásica del iPod usando Pygame, diseñado especialmente para Raspberry Pi Zero pero compatible con cualquier sistema.

## 🎵 Características

### Interfaz iPod Classic Auténtica
- **UI iPod Classic 6ta Generación**: Interfaz fiel al diseño original con colores y fuentes auténticas
- **Click Wheel Funcional**: Rueda táctil simulada con botones Menu, Play/Pause, Forward, Backward y botón central
- **Pantalla 2.8"**: Resolución 358x269 simulando la pantalla original del iPod
- **Animaciones Suaves**: Transiciones y animaciones como el iPod real

### Funcionalidades de Música
- **Biblioteca Musical**: Escaneo automático de archivos MP3, WAV, OGG, FLAC, M4A, AAC
- **Navegación por Artista/Álbum/Canciones**: Organización completa de la música
- **Cover Flow**: Vista de álbumes con navegación visual (como iPod Classic real)
- **Controles de Reproducción**: Play, pausa, siguiente, anterior, shuffle, repetir
- **Control de Volumen**: Ajuste de volumen integrado
- **Now Playing**: Pantalla de reproducción actual con barra de progreso

### Funcionalidades Multimedia
- **Reproductor de Video**: Soporte para archivos de video locales
- **YouTube Player**: 
  - Búsqueda de videos con teclado virtual iPod
  - Videos trending de música
  - Reproducción de videos de YouTube
- **Listas de Reproducción**: Soporte básico para listas

### Conectividad
- **WiFi Manager**: Conexión y gestión de redes WiFi
- **Base de Datos SQLite**: Almacenamiento eficiente de metadatos musicales

### Optimizado para Raspberry Pi
- **Arranque Automático**: Se ejecuta automáticamente al encender
- **Modo Consola**: Funciona sin entorno de escritorio
- **Bajo Consumo**: Optimizado para Raspberry Pi Zero
- **Framebuffer**: Salida directa a pantalla sin X11

## 📦 Instalación

### Instalación Rápida en Raspberry Pi

```bash
# Clona el repositorio
git clone https://github.com/tu-usuario/pygame-music-player.git
cd pygame-music-player

# Ejecuta el instalador automático
chmod +x quick_install_pi.sh
./quick_install_pi.sh

# Reinicia para aplicar cambios
sudo reboot
```

### Instalación Completa en Raspberry Pi

```bash
# Para instalación completa con todas las optimizaciones
chmod +x install_pi.sh
./install_pi.sh
sudo reboot
```

### Instalación Manual

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/pygame-music-player.git
   cd pygame-music-player
   ```

2. **Crear entorno virtual:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Agregar música:**
   - Crea una carpeta `music` en el directorio del proyecto
   - O coloca música en `~/Music`
   - Formatos soportados: MP3, WAV, OGG, FLAC, M4A, AAC

5. **Ejecutar:**
   ```bash
   python src/main.py
   ```

## 🎮 Controles

### Teclado (Desarrollo/PC)
- **Flechas ↑↓ o W/S**: Navegar menús
- **Enter/Espacio**: Seleccionar elemento
- **Escape/Backspace**: Volver/Menú anterior
- **En Now Playing:**
  - A/← : Canción anterior
  - D/→ : Canción siguiente  
  - P: Play/Pausa
  - V: Control de volumen

### Click Wheel (Mouse/Táctil)
- **Rueda externa**: Deslizar para navegar
- **Botón central**: Seleccionar
- **Botón superior (Menu)**: Volver
- **Botón inferior (Play)**: Play/Pausa
- **Botones laterales**: Anterior/Siguiente

## 📁 Estructura del Proyecto

```
pygame-music-player/
├── src/
│   ├── main.py              # Aplicación principal
│   ├── database.py          # Gestión de base de datos SQLite
│   ├── playback.py          # Control de reproducción
│   ├── renderer.py          # Motor de renderizado iPod
│   ├── ui_config.py         # Configuración visual iPod Classic
│   ├── menu_manager.py      # Gestión de menús y navegación
│   ├── music_controller.py  # Controlador de música
│   ├── click_wheel.py       # Implementación Click Wheel
│   ├── cover_flow.py        # Vista Cover Flow
│   ├── video_player.py      # Reproductor de video
│   ├── youtube_manager.py   # Gestión de YouTube
│   ├── youtube_player.py    # Reproductor YouTube
│   ├── wifi_manager.py      # Gestión WiFi
│   └── input_handler.py     # Manejo de entrada
├── music/                   # Directorio de música local
├── videos/                  # Directorio de videos locales
├── assets/                  # Recursos (fuentes, imágenes)
├── install_pi.sh           # Instalador completo para Pi
├── quick_install_pi.sh     # Instalador rápido para Pi
├── requirements.txt        # Dependencias Python
└── README.md              # Este archivo
```

## 🛠️ Dependencias

### Python
- `pygame-ce>=2.1.0` - Motor gráfico mejorado
- `mutagen>=1.45.0` - Metadatos de audio
- `ffpyplayer>=4.3.0` - Reproducción de video
- `yt-dlp>=2023.11.16` - Soporte YouTube
- `requests>=2.31.0` - Peticiones HTTP

### Sistema (Raspberry Pi)
- `python3-pygame` - Pygame del sistema
- `alsa-utils` - Audio ALSA
- `libsdl2-dev` - Desarrollo SDL2
- `python3-dev` - Headers de Python

## 🎛️ Gestión del Servicio (Raspberry Pi)

Una vez instalado, puedes controlar el iPod con estos comandos:

```bash
# Controlar el servicio
ipod-control.sh start     # Iniciar
ipod-control.sh stop      # Detener  
ipod-control.sh restart   # Reiniciar
ipod-control.sh status    # Estado
ipod-control.sh logs      # Ver logs

# Comandos systemd directos
sudo systemctl status ipod-player
sudo journalctl -u ipod-player -f
```

## 🔧 Configuración

### Directorios de Música
El reproductor escanea automáticamente:
- `./music/` (directorio del proyecto)
- `~/Music/` (directorio de usuario)

### Resolución de Pantalla
- **Pantalla iPod**: 358x269 píxeles (2.8")
- **Ventana total**: 358x431 píxeles (3.5" diagonal)
- **Click Wheel**: 358x162 píxeles

### Base de Datos
- Archivo: `ipod_music_library.db`
- Auto-escaneo al inicio
- Actualización incremental de metadatos

## 🐛 Solución de Problemas

### Audio no funciona
```bash
# Verificar dispositivos de audio
aplay -l

# Configurar salida de audio (Pi)
sudo raspi-config # Advanced Options > Audio > Force 3.5mm
```

### Sin video en Raspberry Pi
```bash
# Verificar framebuffer
ls -la /dev/fb0

# Agregar usuario al grupo video
sudo usermod -a -G video pi
```

### Problemas de permisos
```bash
# Corregir permisos de la aplicación
sudo chown -R pi:pi /home/pi/ipod-music-player
```

## 🤝 Contribuir

1. Hacer fork del repositorio
2. Crear rama para tu característica (`git checkout -b feature/nueva-caracteristica`)
3. Commit de cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

## 📜 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🎵 Agradecimientos

Inspirado en el diseño clásico del iPod de Apple y construido con amor para la comunidad de Raspberry Pi.

---

**¡Disfruta tu experiencia iPod Classic en Raspberry Pi!** 🎧