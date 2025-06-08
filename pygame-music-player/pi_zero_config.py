# Configuración específica para Raspberry Pi Zero
# Este archivo contiene configuraciones optimizadas para el rendimiento limitado del Pi Zero

# Configuración de Pygame para Pi Zero
import os

# Variables de entorno para optimizar SDL/Pygame en Pi Zero
PI_ZERO_CONFIG = {
    # Driver de video para framebuffer (sin X11)
    'SDL_VIDEODRIVER': 'fbcon',
    'SDL_FBDEV': '/dev/fb0',
    'SDL_NOMOUSE': '1',
    
    # Optimizaciones de audio
    'SDL_AUDIODRIVER': 'alsa',
    'ALSA_PCM_CARD': '0',
    'ALSA_DEVICE': '0',
    
    # Desactivar características no necesarias para ahorrar memoria
    'SDL_VIDEO_CENTERED': '1',
    'SDL_DISABLE_LOCK_KEYS': '1',
}

# Configuración de UI optimizada para Pi Zero
PI_ZERO_UI_CONFIG = {
    # Resolución reducida para mejor rendimiento
    'SCREEN_WIDTH': 240,
    'SCREEN_HEIGHT': 320,
    
    # FPS reducido para ahorrar CPU
    'TARGET_FPS': 15,  # Reducido de 30 a 15
    
    # Configuraciones de renderizado optimizadas
    'ENABLE_ANTIALIASING': False,  # Desactivar para ahorrar CPU
    'RENDER_QUALITY': 'low',  # Baja calidad para mejor rendimiento
    
    # Configuraciones de memoria
    'MAX_CACHED_COVERS': 5,  # Reducir caché de carátulas
    'BUFFER_SIZE': 1024,  # Buffer de audio más pequeño
    
    # Configuraciones de la base de datos
    'DB_CACHE_SIZE': 100,  # Caché de DB más pequeño
    'LAZY_LOADING': True,  # Carga perezosa de elementos
}

def apply_pi_zero_config():
    """Aplica la configuración optimizada para Raspberry Pi Zero"""
    
    # Aplicar variables de entorno de SDL
    for key, value in PI_ZERO_CONFIG.items():
        os.environ[key] = value
    
    print("✓ Configuración de Pi Zero aplicada")
    
    return PI_ZERO_UI_CONFIG

def is_raspberry_pi_zero():
    """Detecta si estamos ejecutando en Raspberry Pi Zero"""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            # Pi Zero tiene ARM6 y menciona "Zero" en el modelo
            if 'ARMv6' in cpuinfo and ('Zero' in cpuinfo or 'BCM2835' in cpuinfo):
                return True
    except:
        pass
    return False

# Configuración de systemd service optimizada para Pi Zero
SYSTEMD_SERVICE_TEMPLATE = """[Unit]
Description=iPod Music Player - Optimizado para Pi Zero
After=multi-user.target sound.target
Wants=sound.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory={app_dir}

# Variables de entorno optimizadas para Pi Zero
Environment=HOME=/home/pi
Environment=XDG_RUNTIME_DIR=/run/user/1000
Environment=SDL_VIDEODRIVER=fbcon
Environment=SDL_FBDEV=/dev/fb0
Environment=SDL_NOMOUSE=1
Environment=SDL_AUDIODRIVER=alsa
Environment=PYGAME_HIDE_SUPPORT_PROMPT=1

# Configuración de CPU y memoria
Nice=0
CPUSchedulingPolicy=1
IOSchedulingClass=1
IOSchedulingPriority=4

# Comando de ejecución
ExecStart={app_dir}/venv/bin/python {app_dir}/src/main.py

# Configuración de reinicio
Restart=always
RestartSec=5
StartLimitInterval=60
StartLimitBurst=3

# Configuración de recursos
MemoryMax=256M
CPUQuota=80%

[Install]
WantedBy=multi-user.target
"""

# Script de optimización post-instalación
OPTIMIZATION_SCRIPT = """#!/bin/bash

# Script de optimización para Raspberry Pi Zero
echo "🔧 Aplicando optimizaciones para Pi Zero..."

# Configurar swappiness para mejor rendimiento con poca RAM
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf

# Optimizar configuración de GPU
sudo tee -a /boot/config.txt << 'EOF'

# Optimizaciones específicas para Pi Zero con iPod Player
gpu_mem=64
disable_overscan=1
hdmi_force_hotplug=1

# Configuración de audio
dtparam=audio=on
audio_pwm_mode=2

# Optimizaciones de CPU
arm_freq=1000
core_freq=500
sdram_freq=500
over_voltage=2

EOF

# Deshabilitar servicios innecesarios para ahorrar memoria
sudo systemctl disable bluetooth
sudo systemctl disable hciuart
sudo systemctl disable triggerhappy
sudo systemctl disable dphys-swapfile

echo "✓ Optimizaciones aplicadas. Se recomienda reiniciar."
"""
