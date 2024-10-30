from datetime import datetime
import pytz
from utils.config import ConfigManager

config = ConfigManager()
local_tz = pytz.timezone(config.get('ui', 'timezone'))

def format_datetime(dt_str: str) -> str:
    """Convert ISO datetime string to local formatted datetime string"""
    if not dt_str:
        return ""
    
    # Parse ISO format datetime
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except ValueError:
        return dt_str
    
    # If the datetime is naive, assume it's in UTC
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    
    # Convert to local timezone
    local_dt = dt.astimezone(local_tz)
    
    # Format according to config
    return local_dt.strftime(config.get('ui', 'datetime_format'))

def format_date(date_str: str) -> str:
    """Convert ISO date string to local formatted date string"""
    if not date_str:
        return ""
    
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime(config.get('ui', 'date_format'))
    except ValueError:
        return date_str 