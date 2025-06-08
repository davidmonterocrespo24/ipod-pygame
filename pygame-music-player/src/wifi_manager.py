"""
WiFi management module for iPod Classic interface.
Cross-platform WiFi management for Windows and Linux.
"""

import subprocess
import platform
import re
import time
from typing import List, Dict, Optional, Tuple

class WiFiNetwork:
    def __init__(self, ssid: str, signal_strength: int = 0, security: str = ""):
        self.ssid = ssid
        self.signal_strength = signal_strength
        self.security = security
        self.is_connected = False

class WiFiManager:
    """Cross-platform WiFi management for Windows and Linux"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.current_password = ""
        self.password_input_mode = False
        
    def scan_networks(self) -> List[WiFiNetwork]:
        """Scan for available WiFi networks"""
        if self.system == "windows":
            return self._scan_networks_windows()
        elif self.system == "linux":
            return self._scan_networks_linux()
        else:
            return []
    
    def _scan_networks_windows(self) -> List[WiFiNetwork]:
        """Scan networks on Windows using netsh"""
        networks = []
        try:
            # Scan for networks
            result = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'All User Profile' in line:
                        ssid = line.split(':')[1].strip()
                        if ssid:
                            networks.append(WiFiNetwork(ssid))
            
            # Get available networks with signal strength
            result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], 
                                  capture_output=True, text=True, timeout=10)
            
            # Also try to get nearby networks
            result2 = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], 
                                   capture_output=True, text=True, timeout=10)
            
        except Exception as e:
            print(f"Error scanning Windows networks: {e}")
        
        return networks[:10]  # Limit to 10 networks
    
    def _scan_networks_linux(self) -> List[WiFiNetwork]:
        """Scan networks on Linux using nmcli or iwlist"""
        networks = []
        try:
            # Try nmcli first (NetworkManager)
            result = subprocess.run(['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY', 'dev', 'wifi'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line and ':' in line:
                        parts = line.split(':')
                        if len(parts) >= 3 and parts[0]:
                            ssid = parts[0]
                            try:
                                signal = int(parts[1]) if parts[1] else 0
                            except:
                                signal = 0
                            security = parts[2] if len(parts) > 2 else ""
                            networks.append(WiFiNetwork(ssid, signal, security))
            else:
                # Fallback to iwlist
                result = subprocess.run(['sudo', 'iwlist', 'scan'], 
                                      capture_output=True, text=True, timeout=15)
                if result.returncode == 0:
                    ssid_pattern = r'ESSID:"([^"]*)"'
                    matches = re.findall(ssid_pattern, result.stdout)
                    for ssid in matches:
                        if ssid:
                            networks.append(WiFiNetwork(ssid))
                            
        except Exception as e:
            print(f"Error scanning Linux networks: {e}")
        
        # Remove duplicates and sort by signal strength
        unique_networks = {}
        for network in networks:
            if network.ssid not in unique_networks:
                unique_networks[network.ssid] = network
            elif network.signal_strength > unique_networks[network.ssid].signal_strength:
                unique_networks[network.ssid] = network
        
        return sorted(list(unique_networks.values()), key=lambda x: x.signal_strength, reverse=True)[:10]
    
    def get_current_connection(self) -> Optional[str]:
        """Get currently connected network"""
        if self.system == "windows":
            return self._get_current_connection_windows()
        elif self.system == "linux":
            return self._get_current_connection_linux()
        return None
    
    def _get_current_connection_windows(self) -> Optional[str]:
        """Get current connection on Windows"""
        try:
            result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'SSID' in line and ':' in line:
                        ssid = line.split(':')[1].strip()
                        if ssid:
                            return ssid
        except Exception as e:
            print(f"Error getting Windows connection: {e}")
        return None
    
    def _get_current_connection_linux(self) -> Optional[str]:
        """Get current connection on Linux"""
        try:
            result = subprocess.run(['nmcli', '-t', '-f', 'ACTIVE,SSID', 'dev', 'wifi'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.startswith('yes:'):
                        return line.split(':')[1]
        except Exception as e:
            print(f"Error getting Linux connection: {e}")
        return None
    
    def connect_to_network(self, ssid: str, password: str = "") -> Tuple[bool, str]:
        """Connect to a WiFi network"""
        if self.system == "windows":
            return self._connect_windows(ssid, password)
        elif self.system == "linux":
            return self._connect_linux(ssid, password)
        return False, "Unsupported system"
    
    def _connect_windows(self, ssid: str, password: str = "") -> Tuple[bool, str]:
        """Connect to network on Windows"""
        try:
            if password:
                # Create a temporary profile
                profile_xml = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
                
                # Save profile to temp file
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
                    f.write(profile_xml)
                    profile_path = f.name
                
                # Add profile
                result = subprocess.run(['netsh', 'wlan', 'add', 'profile', f'filename={profile_path}'], 
                                      capture_output=True, text=True, timeout=10)
                
                import os
                os.unlink(profile_path)  # Clean up temp file
                
                if result.returncode != 0:
                    return False, "Failed to add profile"
            
            # Connect to network
            result = subprocess.run(['netsh', 'wlan', 'connect', f'name={ssid}'], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                return True, "Connected successfully"
            else:
                return False, "Connection failed"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def _connect_linux(self, ssid: str, password: str = "") -> Tuple[bool, str]:
        """Connect to network on Linux"""
        try:
            if password:
                result = subprocess.run(['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password], 
                                      capture_output=True, text=True, timeout=20)
            else:
                result = subprocess.run(['nmcli', 'dev', 'wifi', 'connect', ssid], 
                                      capture_output=True, text=True, timeout=20)
            
            if result.returncode == 0:
                return True, "Connected successfully"
            else:
                error_msg = result.stderr.strip() if result.stderr else "Connection failed"
                return False, error_msg
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def disconnect(self) -> bool:
        """Disconnect from current network"""
        try:
            if self.system == "windows":
                result = subprocess.run(['netsh', 'wlan', 'disconnect'], 
                                      capture_output=True, text=True, timeout=5)
                return result.returncode == 0
            elif self.system == "linux":
                result = subprocess.run(['nmcli', 'dev', 'disconnect', 'wifi'], 
                                      capture_output=True, text=True, timeout=5)
                return result.returncode == 0
        except Exception:
            pass
        return False
    
    def handle_password_input(self, key_event) -> bool:
        """Handle password input, returns True if password is complete"""
        import pygame
        
        if key_event.key == pygame.K_RETURN:
            return True
        elif key_event.key == pygame.K_BACKSPACE:
            self.current_password = self.current_password[:-1]
        elif key_event.key == pygame.K_ESCAPE:
            self.current_password = ""
            self.password_input_mode = False
            return True
        elif len(self.current_password) < 63:  # WiFi password max length
            if key_event.unicode.isprintable():
                self.current_password += key_event.unicode
        
        return False
    
    def start_password_input(self):
        """Start password input mode"""
        self.current_password = ""
        self.password_input_mode = True
    
    def get_current_password(self) -> str:
        """Get current password being typed"""
        return self.current_password
    
    def clear_password(self):
        """Clear current password"""
        self.current_password = ""
        self.password_input_mode = False
