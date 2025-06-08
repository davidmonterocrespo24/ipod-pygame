# 🥧 Instalación en Raspberry Pi Zero

Este documento explica cómo instalar y configurar tu iPod Music Player en Raspberry Pi Zero para que se ejecute automáticamente al inicio sin necesidad del escritorio.

## 📋 Requisitos

- Raspberry Pi Zero (W recomendado)
- Tarjeta microSD (16GB mínimo)
- Raspberry Pi OS Lite instalado
- Acceso SSH o teclado/monitor para configuración inicial

## 🚀 Instalación Automática

### Opción 1: Instalación Completa (Recomendada)

```bash
# Copiar archivos a tu Pi Zero
scp -r pygame-music-player/ pi@tu-pi-ip:~/

# Conectar por SSH
ssh pi@tu-pi-ip

# Ir al directorio del proyecto
cd pygame-music-player

# Hacer ejecutable el script
chmod +x install_pi.sh

# Ejecutar instalación completa
./install_pi.sh
```

### Opción 2: Instalación Rápida

```bash
# Para una instalación más rápida y básica
chmod +x quick_install_pi.sh
./quick_install_pi.sh
```

## 🔧 ¿Qué hace la instalación?

### 1. **Actualización del Sistema**
- Actualiza todos los paquetes del sistema
- Instala dependencias necesarias

### 2. **Dependencias Instaladas**
- Python 3 y pip
- Pygame y SDL2
- Bibliotecas de audio (ALSA, PulseAudio)
- Herramientas de desarrollo

### 3. **Configuración de la Aplicación**
- Crea directorio en `/home/pi/ipod-music-player`
- Configura entorno virtual de Python
- Instala dependencias específicas del proyecto

### 4. **Configuración del Sistema**
- **Modo sin escritorio**: Configura el sistema para arrancar en modo consola
- **Servicio systemd**: Crea servicio para inicio automático
- **Optimizaciones**: Configuraciones específicas para Pi Zero

### 5. **Configuración de Hardware**
- Audio ALSA configurado
- Permisos de framebuffer para video
- Optimizaciones de GPU y CPU

## 🎛️ Control del Servicio

Después de la instalación, puedes controlar tu iPod con estos comandos:

```bash
# Controlar el servicio
ipod-control.sh start    # Iniciar
ipod-control.sh stop     # Detener
ipod-control.sh restart  # Reiniciar
ipod-control.sh status   # Ver estado
ipod-control.sh logs     # Ver logs en tiempo real

# O usar systemctl directamente
sudo systemctl start ipod-player
sudo systemctl stop ipod-player
sudo systemctl status ipod-player
```

## 📊 Verificar el Estado

```bash
# Ver si el servicio está ejecutándose
sudo systemctl status ipod-player

# Ver logs del servicio
sudo journalctl -u ipod-player -f

# Ver procesos relacionados
ps aux | grep python
```

## 🎵 Agregar Música

```bash
# Copiar música a tu Pi Zero
scp *.mp3 pi@tu-pi-ip:~/ipod-music-player/music/

# O montar USB/dispositivo externo
sudo mount /dev/sda1 /mnt
cp /mnt/*.mp3 ~/ipod-music-player/music/
sudo umount /mnt
```

## ⚡ Optimizaciones para Pi Zero

El script automáticamente detecta si se ejecuta en Pi Zero y aplica:

- **Resolución reducida**: 240x320 para mejor rendimiento
- **FPS limitado**: 15 FPS en lugar de 30
- **Configuración de memoria**: GPU con 64MB, optimizaciones de swap
- **Servicios deshabilitados**: Bluetooth y otros servicios innecesarios
- **Variables SDL**: Configuración optimizada para framebuffer

## 🔧 Configuración Manual (Avanzada)

Si necesitas personalizar la configuración:

### Editar configuración del servicio:
```bash
sudo nano /etc/systemd/system/ipod-player.service
sudo systemctl daemon-reload
sudo systemctl restart ipod-player
```

### Editar configuración de boot:
```bash
sudo nano /boot/config.txt
# Reiniciar después de cambios
sudo reboot
```

### Configurar audio manualmente:
```bash
# Probar salida de audio
speaker-test -t wav -c 2

# Configurar volumen
alsamixer
```

## 🐛 Solución de Problemas

### El servicio no inicia:
```bash
# Revisar logs de error
sudo journalctl -u ipod-player --no-pager

# Verificar permisos
ls -la /home/pi/ipod-music-player/

# Probar manualmente
cd /home/pi/ipod-music-player
source venv/bin/activate
python src/main.py
```

### Sin sonido:
```bash
# Verificar dispositivos de audio
aplay -l

# Configurar como predeterminado
sudo raspi-config
# Advanced Options > Audio > Force 3.5mm jack
```

### Pantalla en negro:
```bash
# Verificar framebuffer
ls -la /dev/fb*

# Verificar configuración de video
vcgencmd get_mem gpu
```

### Alto uso de CPU:
```bash
# Monitorear uso de recursos
top
htop

# Reducir calidad en pi_zero_config.py
nano /home/pi/ipod-music-player/pi_zero_config.py
```

## 📱 Uso de la Interfaz

Una vez iniciado, tu iPod funcionará así:

- **Sin mouse/teclado necesario**: Usa controles táctiles o botones configurados
- **Navegación**: Menús tipo iPod Classic
- **Música**: Reproducción automática desde la carpeta `music/`
- **Controles**: Play/Pause, Siguiente, Anterior, Volumen

## 🔄 Actualizar la Aplicación

```bash
# Parar el servicio
sudo systemctl stop ipod-player

# Actualizar código
cd /home/pi/ipod-music-player
# Copiar nuevos archivos aquí

# Reiniciar servicio
sudo systemctl start ipod-player
```

## 📋 Archivos Importantes

- **Aplicación**: `/home/pi/ipod-music-player/`
- **Servicio**: `/etc/systemd/system/ipod-player.service`
- **Script inicio**: `/usr/local/bin/start-ipod-player.sh`
- **Control**: `/usr/local/bin/ipod-control.sh`
- **Config boot**: `/boot/config.txt`
- **Logs**: `sudo journalctl -u ipod-player`

## 🎉 ¡Listo!

Después de ejecutar la instalación y reiniciar tu Pi Zero:

```bash
sudo reboot
```

Tu iPod Music Player se iniciará automáticamente y estará listo para usar. 

**¡Disfruta tu reproductor de música estilo iPod Classic en Raspberry Pi Zero!** 🎵🥧
