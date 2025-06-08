#!/bin/bash

# Script de instalación rápida para Raspberry Pi Zero
# Versión simplificada para instalación básica

set -e

echo "🎵 Instalación rápida de iPod Music Player"
echo "=========================================="

# Variables
APP_DIR="/home/pi/ipod-music-player"
SERVICE_NAME="ipod-player"

# Actualizar sistema
echo "📦 Actualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar dependencias esenciales
echo "📦 Instalando dependencias..."
sudo apt install -y python3 python3-pip python3-venv python3-pygame git

# Crear directorio y copiar archivos
echo "📁 Preparando aplicación..."
sudo mkdir -p "$APP_DIR"
sudo chown pi:pi "$APP_DIR"

# Copiar archivos del proyecto actual
cp -r ./src "$APP_DIR/"
cp -r ./assets "$APP_DIR/" 2>/dev/null || mkdir -p "$APP_DIR/assets"
cp -r ./music "$APP_DIR/" 2>/dev/null || mkdir -p "$APP_DIR/music"
cp requirements.txt "$APP_DIR/" 2>/dev/null || true

# Configurar entorno virtual
echo "🐍 Configurando Python..."
cd "$APP_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# Instalar dependencias de Python
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install mutagen pygame-ce
fi

# Crear servicio systemd simple
echo "⚙️ Configurando servicio..."
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null << EOF
[Unit]
Description=iPod Music Player
After=multi-user.target

[Service]
Type=simple
User=pi
WorkingDirectory=$APP_DIR
Environment=HOME=/home/pi
Environment=SDL_VIDEODRIVER=fbcon
Environment=SDL_FBDEV=/dev/fb0
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/src/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Configurar inicio automático
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}.service
sudo systemctl set-default multi-user.target

# Configurar permisos
sudo usermod -a -G audio,video pi
sudo chown -R pi:pi "$APP_DIR"

echo ""
echo "✅ ¡Instalación completada!"
echo ""
echo "Para iniciar manualmente: sudo systemctl start $SERVICE_NAME"
echo "Para ver logs: sudo journalctl -u $SERVICE_NAME -f"
echo "Para reiniciar el sistema: sudo reboot"
echo ""
echo "🎵 ¡Tu iPod estará listo después del reinicio!"
