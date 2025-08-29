"""
Logging system for Infini Converter
"""

import logging
import os
from datetime import datetime
from typing import Optional

class Logger:
    def __init__(self, log_file: str = "infini_converter.log", enabled: bool = True):
        self.enabled = enabled
        self.log_file = log_file
        self.logger = None
        self.setup_logger()
    
    def setup_logger(self) -> None:
        if not self.enabled:
            return
        
        self.logger = logging.getLogger("infini_converter")
        self.logger.setLevel(logging.DEBUG)
        
        if not self.logger.handlers:
            os.makedirs(os.path.dirname(self.log_file) if os.path.dirname(self.log_file) else ".", exist_ok=True)
            
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def debug(self, message: str) -> None:
        if self.enabled and self.logger:
            self.logger.debug(message)
    
    def info(self, message: str) -> None:
        if self.enabled and self.logger:
            self.logger.info(message)
    
    def warning(self, message: str) -> None:
        if self.enabled and self.logger:
            self.logger.warning(message)
    
    def error(self, message: str) -> None:
        if self.enabled and self.logger:
            self.logger.error(message)
    
    def critical(self, message: str) -> None:
        if self.enabled and self.logger:
            self.logger.critical(message)
    
    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled
        if enabled and not self.logger:
            self.setup_logger()
        elif not enabled and self.logger:
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)
            self.logger = None