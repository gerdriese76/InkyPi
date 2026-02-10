import sys
import os
import logging
from unittest.mock import MagicMock, patch
from PIL import Image

# Add src to sys.path
sys.path.append(os.path.join(os.getcwd(), 'src'))

# Setup minimal logging
logging.basicConfig(level=logging.DEBUG)

from plugins.network_info.network_info import NetworkInfo

# Mock take_screenshot_html to avoid dependency on chrome
with patch('plugins.base_plugin.base_plugin.take_screenshot_html') as mock_screenshot:
    # Create a dummy image to return
    dummy_img = Image.new('RGB', (800, 480), color='white')
    mock_screenshot.return_value = dummy_img

    # Mock configuration
    plugin_config = {
        "display_name": "Network Info",
        "id": "network_info",
        "class": "NetworkInfo"
    }

    # Settings
    settings = {}

    # Mock device config
    class MockDeviceConfig:
        def get_resolution(self):
            return (800, 480) # Example resolution

    device_config = MockDeviceConfig()

    # Instantiate Plugin
    plugin = NetworkInfo(plugin_config)

    # Generate Image
    try:
        print("Generating image...")
        img = plugin.generate_image(settings, device_config)
        print("Image generated successfully.")
        
        # Save for verification
        output_path = "network_info_test.png"
        img.save(output_path)
        print(f"Saved test image to {output_path}")

    except Exception as e:
        print(f"Error generating image: {e}")
        import traceback
        traceback.print_exc()
