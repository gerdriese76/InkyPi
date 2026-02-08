from plugins.base_plugin.base_plugin import BasePlugin
from datetime import datetime
import logging
import pytz

logger = logging.getLogger(__name__)

class Ferien(BasePlugin):
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
        
        names = settings.get('holidayName[]', [])
        dates = settings.get('holidayDate[]', [])
        
        holidays = []
        
        # Ensure lists
        if names and not isinstance(names, list): names = [names]
        if dates and not isinstance(dates, list): dates = [dates]
        
        if names and dates:
            for name, date_str in zip(names, dates):
                if not name or not date_str: continue
                try:
                    y, m, d = map(int, date_str.split('-'))
                    # Create timezone-aware target date at midnight
                    holiday_date = tz.localize(datetime(y, m, d))
                    
                    # Compare dates
                    days_diff = (holiday_date.date() - current_time.date()).days
                    
                    if days_diff >= 0:
                        holidays.append({
                            'name': name,
                            'date': date_str,
                            'days_left': days_diff
                        })
                except Exception as e:
                    logger.error(f"Error parsing holiday {name} {date_str}: {e}")
        
        # Sort by days left
        holidays.sort(key=lambda x: x['days_left'])
        
        template_params = {
            "holidays": holidays,
            "plugin_settings": settings
        }
        
        return self.render_image(dimensions, "ferien.html", "ferien.css", template_params)
