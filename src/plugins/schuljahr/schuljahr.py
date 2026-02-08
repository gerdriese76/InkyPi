from plugins.base_plugin.base_plugin import BasePlugin
from PIL import Image
from datetime import datetime, timezone, timedelta
import logging
import pytz

logger = logging.getLogger(__name__)
class Schuljahr(BasePlugin):
    def generate_settings_template(self):
        template_params = super().generate_settings_template()
        template_params['style_settings'] = True
        return template_params

    def generate_image(self, settings, device_config):
        dimensions = device_config.get_resolution()
        if device_config.get_config("orientation") == "vertical":
            dimensions = dimensions[::-1]
        
        timezone = device_config.get_config("timezone", default="America/New_York")
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)

        # Default to current year if no settings
        target_date = datetime(current_time.year + 1, 1, 1, tzinfo=tz)
        start_date = datetime(current_time.year, 1, 1, tzinfo=tz)

        start_date_str = settings.get('startDate')
        end_date_str = settings.get('endDate')

        try:
            if start_date_str:
                sy, sm, sd = map(int, start_date_str.split('-'))
                start_date = tz.localize(datetime(sy, sm, sd))
            
            if end_date_str:
                ey, em, ed = map(int, end_date_str.split('-'))
                target_date = tz.localize(datetime(ey, em, ed))
        except Exception as e:
            logger.error(f"Error parsing dates: {e}")

        total_days = (target_date - start_date).days
        days_left_seconds = (target_date - current_time).total_seconds()
        days_left = days_left_seconds / (24 * 3600)
        
        elapsed_seconds = (current_time - start_date).total_seconds()
        
        percent = 0
        if total_days > 0:
            percent = (elapsed_seconds / (total_days * 24 * 3600)) * 100
        
        # Clamp values
        percent = max(0, min(100, round(percent)))
        days_left_display = max(0, round(days_left))

        template_params = {
            "year": f"{start_date.year}/{target_date.year}" if start_date.year != target_date.year else target_date.year,
            "year_percent": percent,
            "days_left": days_left_display,
            "plugin_settings": settings
        }
        
        image = self.render_image(dimensions, "schuljahr.html", "schuljahr.css", template_params)
        return image