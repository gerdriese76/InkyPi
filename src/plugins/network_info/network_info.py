import logging
import socket
import subprocess
import re
from datetime import datetime
import pytz
from plugins.base_plugin.base_plugin import BasePlugin
from utils.app_utils import get_font

logger = logging.getLogger(__name__)

class NetworkInfo(BasePlugin):
    def __init__(self, config, **dependencies):
        super().__init__(config, **dependencies)

    def generate_image(self, settings, device_config):
        dimensions = device_config.get_resolution()
        
        # Get Timezone
        timezone_name = device_config.get_config("timezone") or "UTC"
        try:
            tz = pytz.timezone(timezone_name)
            now = datetime.now(tz)
        except Exception as e:
            logger.error(f"Invalid timezone {timezone_name}, falling back to local: {e}")
            now = datetime.now()

        # Gather Data
        data = {
            "ssid": self.get_ssid(),
            "ip_address": self.get_ip_address(),
            "gateway": self.get_default_gateway(),
            "current_time": now.strftime("%H:%M:%S"),
            "current_date": now.strftime("%Y-%m-%d"),
            "ping_1_1_1_1": self.get_ping_time("1.1.1.1"),
            "ping_8_8_8_8": self.get_ping_time("8.8.8.8")
        }

        # Render
        return self.render_image(dimensions, "network_info.html", "style.css", data)

    def get_ssid(self):
        try:
            # Linux (iwgetid)
            result = subprocess.run(["iwgetid", "-r"], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            
            # Fallback nmcli (often used on Raspberry Pi OS)
            result = subprocess.run(["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"], capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if line.startswith("yes:"):
                        return line.split(":", 1)[1]
        except Exception as e:
            logger.error(f"Failed to get SSID: {e}")
        return "Unknown"

    def get_ip_address(self):
        try:
            # Connect to a public DNS server to determine the outgoing interface IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.1)
            # Doesn't actually connect, just determines route
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "Unknown"

    def get_default_gateway(self):
        try:
            # Linux specific
            with open("/proc/net/route") as f:
                for line in f:
                    fields = line.strip().split()
                    if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                        continue
                    return socket.inet_ntoa(bytes.fromhex(fields[2])[::-1])
        except Exception as e:
            logger.error(f"Failed to get gateway: {e}")
        return "Unknown"

    def get_ping_time(self, host):
        try:
            # Linux: -c 1 (count), -W 1 (timeout in seconds)
            command = ['ping', '-c', '1', '-W', '1', host]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = result.stdout
            
            # Parse time=X.X ms
            match = re.search(r"time=([\d\.]+)", output)
            if match:
                return f"{match.group(1)} ms"
            return "Timeout"
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            return "Error"
