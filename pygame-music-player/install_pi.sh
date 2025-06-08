#!/bin/bash

# Script de instalación para Raspberry Pi Zero
# Instala la aplicación iPod Music Player y la configura para ejecutarse al inicio

set -e  # Salir si hay algún error

echo "🎵 Instalando iPod Music Player en Raspberry Pi Zero..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables de configuración
APP_NAME="ipod-music-player"
APP_DIR="/home/pi/$APP_NAME"
USER="pi"
SERVICE_NAME="ipod-player"

echo -e "${YELLOW}📋 Configuración:${NC}"
echo "  • Directorio de instalación: $APP_DIR"
echo "  • Usuario: $USER"
echo "  • Servicio: $SERVICE_NAME"
echo ""

# Función para mostrar mensajes
log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Verificar que estamos en Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    log_warning "Este script está diseñado para Raspberry Pi"
    read -p "¿Continuar de todos modos? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 1. Actualizar sistema
echo -e "${YELLOW}📦 Actualizando sistema...${NC}"
sudo apt update && sudo apt upgrade -y
log_info "Sistema actualizado"

# 2. Instalar dependencias del sistema
echo -e "${YELLOW}📦 Instalando dependencias del sistema...${NC}"
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    python3-pygame \
    python3-dev \
    libasound2-dev \
    libportaudio2 \
    libportaudiocpp0 \
    portaudio19-dev \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    python3-setuptools \
    alsa-utils \
    pulseaudio

log_info "Dependencias del sistema instaladas"

# 3. Configurar audio
echo -e "${YELLOW}🔊 Configurando audio...${NC}"
# Asegurar que el usuario pi esté en el grupo audio
sudo usermod -a -G audio pi

# Configurar ALSA
sudo tee /home/pi/.asoundrc > /dev/null << 'EOF'
pcm.!default {
    type hw
    card 0
}
ctl.!default {
    type hw
    card 0
}
EOF

log_info "Audio configurado"

# 4. Crear directorio de aplicación
echo -e "${YELLOW}📁 Preparando directorio de aplicación...${NC}"
sudo mkdir -p "$APP_DIR"
sudo chown pi:pi "$APP_DIR"
log_info "Directorio preparado: $APP_DIR"

# 5. Copiar archivos de la aplicación
echo -e "${YELLOW}📋 Copiando archivos de la aplicación...${NC}"
if [ -d "./src" ]; then
    cp -r ./src "$APP_DIR/"
    cp -r ./assets "$APP_DIR/" 2>/dev/null || mkdir -p "$APP_DIR/assets"
    cp -r ./fonts "$APP_DIR/" 2>/dev/null || mkdir -p "$APP_DIR/fonts"
    cp -r ./images "$APP_DIR/" 2>/dev/null || mkdir -p "$APP_DIR/images"
    cp -r ./music "$APP_DIR/" 2>/dev/null || mkdir -p "$APP_DIR/music"
    cp -r ./videos "$APP_DIR/" 2>/dev/null || mkdir -p "$APP_DIR/videos"
    cp requirements.txt "$APP_DIR/" 2>/dev/null || true
    cp README.md "$APP_DIR/" 2>/dev/null || true
    log_info "Archivos copiados"
else
    log_error "No se encontró el directorio src. Ejecuta este script desde el directorio del proyecto."
    exit 1
fi

# 6. Crear entorno virtual e instalar dependencias de Python
echo -e "${YELLOW}🐍 Configurando entorno virtual de Python...${NC}"
cd "$APP_DIR"
python3 -m venv venv
source venv/bin/activate

# Actualizar pip
pip install --upgrade pip

# Instalar dependencias
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # Instalar dependencias básicas si no existe requirements.txt
    pip install mutagen ffpyplayer pygame-ce
fi

log_info "Entorno virtual configurado"

# 7. Crear script de inicio
echo -e "${YELLOW}🚀 Creando script de inicio...${NC}"
sudo tee /usr/local/bin/start-ipod-player.sh > /dev/null << EOF
#!/bin/bash

# Script de inicio para iPod Music Player
export DISPLAY=:0
export PULSE_RUNTIME_PATH=/run/user/1000/pulse

# Configurar variables de entorno para SDL (Pygame)
export SDL_VIDEODRIVER=fbcon
export SDL_FBDEV=/dev/fb0
export SDL_NOMOUSE=1

# Cambiar al directorio de la aplicación
cd $APP_DIR

# Activar entorno virtual
source venv/bin/activate

# Ejecutar la aplicación
python src/main.py

EOF

sudo chmod +x /usr/local/bin/start-ipod-player.sh
log_info "Script de inicio creado"

# 8. Crear servicio systemd
echo -e "${YELLOW}⚙️ Creando servicio systemd...${NC}"
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null << EOF
[Unit]
Description=iPod Music Player
After=graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=$APP_DIR
Environment=HOME=/home/pi
Environment=XDG_RUNTIME_DIR=/run/user/1000
Environment=DISPLAY=:0
ExecStart=/usr/local/bin/start-ipod-player.sh
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

log_info "Servicio systemd creado"

# 9. Configurar inicio automático sin escritorio
echo -e "${YELLOW}🖥️ Configurando inicio automático...${NC}"

# Configurar para arrancar en modo consola (no escritorio)
sudo systemctl set-default multi-user.target

# Habilitar servicio
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}.service

log_info "Inicio automático configurado"

# 10. Configurar permisos de framebuffer
echo -e "${YELLOW}🔧 Configurando permisos de video...${NC}"
sudo usermod -a -G video pi

# Crear regla udev para framebuffer
sudo tee /etc/udev/rules.d/99-framebuffer.rules > /dev/null << 'EOF'
KERNEL=="fb0", GROUP="video", MODE="0664"
EOF

log_info "Permisos de video configurados"

# 11. Configurar config.txt para mejor rendimiento
echo -e "${YELLOW}⚡ Optimizando configuración de Raspberry Pi...${NC}"
sudo tee -a /boot/config.txt > /dev/null << 'EOF'

# Configuración para iPod Music Player
# Habilitar audio
dtparam=audio=on

# Configuración de GPU para mejor rendimiento con Pygame
gpu_mem=128

# Configuración de framebuffer
framebuffer_width=240
framebuffer_height=320
hdmi_force_hotplug=1
hdmi_group=2
hdmi_mode=87
hdmi_cvt=240 320 60 1 0 0 0

EOF

log_info "Configuración de Raspberry Pi optimizada"

# 12. Crear script de control
echo -e "${YELLOW}🎛️ Creando scripts de control...${NC}"
sudo tee /usr/local/bin/ipod-control.sh > /dev/null << 'EOF'
#!/bin/bash

SERVICE_NAME="ipod-player"

case "$1" in
    start)
        echo "Iniciando iPod Music Player..."
        sudo systemctl start $SERVICE_NAME
        ;;
    stop)
        echo "Deteniendo iPod Music Player..."
        sudo systemctl stop $SERVICE_NAME
        ;;
    restart)
        echo "Reiniciando iPod Music Player..."
        sudo systemctl restart $SERVICE_NAME
        ;;
    status)
        sudo systemctl status $SERVICE_NAME
        ;;
    logs)
        sudo journalctl -u $SERVICE_NAME -f
        ;;
    enable)
        echo "Habilitando inicio automático..."
        sudo systemctl enable $SERVICE_NAME
        ;;
    disable)
        echo "Deshabilitando inicio automático..."
        sudo systemctl disable $SERVICE_NAME
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status|logs|enable|disable}"
        exit 1
        ;;
esac
EOF

sudo chmod +x /usr/local/bin/ipod-control.sh
log_info "Script de control creado"

# 13. Configuración final
echo -e "${YELLOW}🔧 Aplicando configuración final...${NC}"
sudo chown -R pi:pi "$APP_DIR"
chmod +x "$APP_DIR/src/main.py" 2>/dev/null || true

log_info "Configuración final aplicada"

echo ""
echo -e "${GREEN}🎉 ¡Instalación completada exitosamente!${NC}"
echo ""
echo -e "${YELLOW}📋 Información importante:${NC}"
echo "  • Aplicación instalada en: $APP_DIR"
echo "  • Servicio: $SERVICE_NAME"
echo "  • La aplicación se ejecutará automáticamente al arrancar"
echo "  • El sistema arrancará en modo consola (sin escritorio)"
echo ""
echo -e "${YELLOW}🎛️ Comandos útiles:${NC}"
echo "  • Controlar servicio: ipod-control.sh {start|stop|restart|status|logs}"
echo "  • Ver logs: sudo journalctl -u $SERVICE_NAME -f"
echo "  • Estado del servicio: sudo systemctl status $SERVICE_NAME"
echo ""
echo -e "${YELLOW}🔄 Para aplicar todos los cambios, reinicia el sistema:${NC}"
echo "  sudo reboot"
echo ""
echo -e "${GREEN}¡Disfruta tu iPod Music Player en Raspberry Pi!${NC} 🎵"
