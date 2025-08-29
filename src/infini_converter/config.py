"""
Configuration manager for Infini Converter
"""

import json
import os
from typing import Dict, List

class Config:
    def __init__(self, config_file: str = None):
        self.config_file = config_file or os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.json')
        self.config = self._load_default_config()
        self.load_config()
    
    def _load_default_config(self) -> Dict:
        return {
            "file_extensions": [".txt", ".csv", ".json", ".xml", ".log"],
            "output_directory": "",
            "processing_program": "",
            "command_template": "",
            "logging_enabled": True,
            "log_file": "infini_converter.log",
            "show_command_confirm": False,
            "gui": {
                "window_size": [800, 600],
                "window_title": "Infini Converter"
            }
        }
    
    def load_config(self) -> None:
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}")
    
    def save_config(self) -> None:
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default=None):
        return self.config.get(key, default)
    
    def set(self, key: str, value) -> None:
        self.config[key] = value
    
    def get_file_extensions(self) -> List[str]:
        return self.get("file_extensions", [])
    
    def set_file_extensions(self, extensions: List[str]) -> None:
        self.set("file_extensions", extensions)
    
    def get_output_directory(self) -> str:
        return self.get("output_directory", "")
    
    def set_output_directory(self, directory: str) -> None:
        self.set("output_directory", directory)
    
    def get_processing_program(self) -> str:
        return self.get("processing_program", "")
    
    def set_processing_program(self, program: str) -> None:
        self.set("processing_program", program)
    
    def get_command_template(self) -> str:
        return self.get("command_template", "")
    
    def set_command_template(self, template: str) -> None:
        self.set("command_template", template)
    
    def get_input_directory(self) -> str:
        return self.get("input_directory", "")
    
    def set_input_directory(self, directory: str) -> None:
        self.set("input_directory", directory)
    
    def is_logging_enabled(self) -> bool:
        return self.get("logging_enabled", True)
    
    def set_logging_enabled(self, enabled: bool) -> None:
        self.set("logging_enabled", enabled)
    
    def get_log_file(self) -> str:
        return self.get("log_file", "infini_converter.log")
    
    def is_command_confirm_enabled(self) -> bool:
        return self.get("show_command_confirm", False)
    
    def set_command_confirm_enabled(self, enabled: bool) -> None:
        self.set("show_command_confirm", enabled)
    
    def load_defaults(self) -> None:
        """Load the default configuration values."""
        default_config = self._load_default_config()
        # Preserve input_directory if it exists in current config
        if "input_directory" in self.config:
            default_config["input_directory"] = self.config["input_directory"]
        self.config = default_config
    
    def save_config_as(self, config_name: str) -> str:
        """Save current configuration with a custom name.
        
        Args:
            config_name: Name for the configuration file
            
        Returns:
            Path to the saved config file
        """
        if not config_name:
            raise ValueError("Config name cannot be empty")
        
        # Sanitize config name
        safe_name = "".join(c for c in config_name if c.isalnum() or c in ('-', '_', ' ')).strip()
        if not safe_name:
            raise ValueError("Invalid config name")
        
        # Replace spaces with underscores and ensure .json extension
        filename = safe_name.replace(' ', '_') + '.json'
        config_path = os.path.join(os.path.dirname(self.config_file), filename)
        
        # Save the current config to the new file
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            return config_path
        except IOError as e:
            raise IOError(f"Failed to save config to {config_path}: {e}")
    
    def load_config_from(self, config_path: str) -> None:
        """Load configuration from a specific file.
        
        Args:
            config_path: Path to the configuration file to load
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        if not os.path.exists(config_path):
            return False
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                self.config.update(loaded_config)
            return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config from {config_path}: {e}")
            return False
    
    def list_saved_configs(self) -> List[str]:
        """List all saved configuration files.
        
        Returns:
            List of config file names (without .json extension)
        """
        config_dir = os.path.dirname(self.config_file)
        if not os.path.exists(config_dir):
            return []
        
        configs = []
        for filename in os.listdir(config_dir):
            if filename.endswith('.json'):
                config_name = filename[:-5]  # Remove .json extension
                configs.append(config_name)
        
        return sorted(configs)
    
    def get_config_path(self, config_name: str) -> str:
        """Get the full path for a named configuration.
        
        Args:
            config_name: Name of the configuration
            
        Returns:
            Full path to the config file
        """
        # Sanitize and format the name
        safe_name = "".join(c for c in config_name if c.isalnum() or c in ('-', '_', ' ')).strip()
        filename = safe_name.replace(' ', '_') + '.json'
        return os.path.join(os.path.dirname(self.config_file), filename)