import json
from pathlib import Path
from typing import Dict, Any

DEFAULT_CONFIG = {
    "database": {
        "path": "insurance_crm.db",
        "backup_dir": "backups"
    },
    "ui": {
        "theme": "default",
        "date_format": "%m-%d-%Y",
        "time_format": "%I:%M %p",
        "datetime_format": "%m-%d-%Y %I:%M %p",
        "timezone": "US/Central"
    },
    "business": {
        "company_name": "Insurance CRM",
        "currency_symbol": "$"
    }
}

class ConfigManager:
    def __init__(self):
        self.config_path = Path("config.json")
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("Warning: Invalid config file, using defaults")
                return DEFAULT_CONFIG
        else:
            self._save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=4)
    
    def get(self, section: str, key: str) -> Any:
        return self.config.get(section, {}).get(key)
    
    def set(self, section: str, key: str, value: Any) -> None:
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self._save_config(self.config) 