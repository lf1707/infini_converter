"""
Unit tests for Infini Converter
"""

import unittest
import tempfile
import os
import json
from unittest.mock import Mock, patch

from infini_converter.config import Config
from infini_converter.logger import Logger
from infini_converter.file_discovery import FileDiscovery
from infini_converter.processor import FileProcessor


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        self.config = Config(self.config_file)
    
    def tearDown(self):
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        os.rmdir(self.temp_dir)
    
    def test_default_config(self):
        """Test that default configuration is loaded correctly."""
        self.assertIsInstance(self.config.get_file_extensions(), list)
        self.assertTrue(self.config.is_logging_enabled())
        self.assertEqual(self.config.get("window_title"), "Infini Converter")
    
    def test_set_get_config(self):
        """Test setting and getting configuration values."""
        self.config.set_file_extensions([".txt", ".csv"])
        self.assertEqual(self.config.get_file_extensions(), [".txt", ".csv"])
        
        self.config.set_output_directory("/tmp/test")
        self.assertEqual(self.config.get_output_directory(), "/tmp/test")
    
    def test_save_load_config(self):
        """Test saving and loading configuration."""
        self.config.set_file_extensions([".py", ".js"])
        self.config.set_logging_enabled(False)
        self.config.save_config()
        
        # Load new config instance
        new_config = Config(self.config_file)
        self.assertEqual(new_config.get_file_extensions(), [".py", ".js"])
        self.assertFalse(new_config.is_logging_enabled())


class TestLogger(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")
        self.logger = Logger(self.log_file, enabled=True)
    
    def tearDown(self):
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        os.rmdir(self.temp_dir)
    
    def test_logger_enabled(self):
        """Test that logging works when enabled."""
        self.logger.info("Test message")
        self.logger.error("Error message")
        
        # Check if log file was created
        self.assertTrue(os.path.exists(self.log_file))
        
        # Check log content
        with open(self.log_file, 'r') as f:
            content = f.read()
            self.assertIn("Test message", content)
            self.assertIn("Error message", content)
    
    def test_logger_disabled(self):
        """Test that logging is disabled when configured."""
        disabled_logger = Logger(self.log_file, enabled=False)
        disabled_logger.info("This should not be logged")
        
        # Log file should not be created for disabled logger
        self.assertFalse(os.path.exists(self.log_file))
    
    def test_toggle_logging(self):
        """Test toggling logging on and off."""
        self.logger.set_enabled(False)
        self.logger.info("This should not be logged")
        
        # Enable logging
        self.logger.set_enabled(True)
        self.logger.info("This should be logged")
        
        self.assertTrue(os.path.exists(self.log_file))
        with open(self.log_file, 'r') as f:
            content = f.read()
            self.assertIn("This should be logged", content)


class TestFileDiscovery(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.discovery = FileDiscovery([".txt", ".csv"])
        
        # Create test files
        self.test_files = [
            "test1.txt",
            "test2.csv",
            "test3.json",  # Should not be found
            "subdir/test4.txt"
        ]
        
        os.makedirs(os.path.join(self.temp_dir, "subdir"))
        
        for file_path in self.test_files:
            full_path = os.path.join(self.temp_dir, file_path)
            with open(full_path, 'w') as f:
                f.write("test content")
    
    def tearDown(self):
        # Clean up test files
        for file_path in self.test_files:
            full_path = os.path.join(self.temp_dir, file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
        
        if os.path.exists(os.path.join(self.temp_dir, "subdir")):
            os.rmdir(os.path.join(self.temp_dir, "subdir"))
        os.rmdir(self.temp_dir)
    
    def test_find_files(self):
        """Test finding files with specified extensions."""
        files = self.discovery.find_files(self.temp_dir)
        
        # Should find .txt and .csv files, but not .json
        found_basenames = [os.path.basename(f) for f in files]
        self.assertIn("test1.txt", found_basenames)
        self.assertIn("test2.csv", found_basenames)
        self.assertNotIn("test3.json", found_basenames)
    
    def test_find_files_recursive(self):
        """Test recursive file discovery."""
        files = self.discovery.find_files(self.temp_dir, recursive=True)
        
        # Should find files in subdirectories
        found_basenames = [os.path.basename(f) for f in files]
        self.assertIn("test4.txt", found_basenames)
    
    def test_get_file_info(self):
        """Test getting file information."""
        test_file = os.path.join(self.temp_dir, "test1.txt")
        info = self.discovery.get_file_info(test_file)
        
        self.assertEqual(info["name"], "test1.txt")
        self.assertEqual(info["extension"], ".txt")
        self.assertTrue(info["size"] > 0)
        self.assertIn("modified", info)


class TestFileProcessor(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.output_dir)
        
        self.processor = FileProcessor("", self.output_dir)
        
        # Create test input file
        self.test_file = os.path.join(self.temp_dir, "test.txt")
        with open(self.test_file, 'w') as f:
            f.write("test content")
    
    def tearDown(self):
        # Clean up
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        
        if os.path.exists(self.output_dir):
            for file in os.listdir(self.output_dir):
                os.remove(os.path.join(self.output_dir, file))
            os.rmdir(self.output_dir)
        
        os.rmdir(self.temp_dir)
    
    def test_set_output_directory(self):
        """Test setting output directory."""
        new_output_dir = os.path.join(self.temp_dir, "new_output")
        self.processor.set_output_directory(new_output_dir)
        
        self.assertTrue(os.path.exists(new_output_dir))
        self.assertEqual(self.processor.output_directory, new_output_dir)
    
    def test_process_file_no_program(self):
        """Test processing file without a program set."""
        result = self.processor.process_file(self.test_file)
        
        self.assertFalse(result["success"])
        self.assertIn("No processing program specified", result["error"])
    
    def test_process_file_nonexistent(self):
        """Test processing a non-existent file."""
        self.processor.set_processing_program("echo")
        result = self.processor.process_file("/nonexistent/file.txt")
        
        self.assertFalse(result["success"])
        self.assertIn("Input file not found", result["error"])
    
    @patch('subprocess.run')
    def test_process_file_success(self, mock_run):
        """Test successful file processing."""
        # Mock successful subprocess execution
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "processed content"
        mock_run.return_value.stderr = ""
        
        self.processor.set_processing_program("echo")
        result = self.processor.process_file(self.test_file)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["return_code"], 0)
    
    def test_validate_program(self):
        """Test program validation."""
        # Test with non-existent program
        self.assertFalse(self.processor.validate_program("/nonexistent/program"))
        
        # Test with existent but non-executable file
        non_executable = os.path.join(self.temp_dir, "non_executable.txt")
        with open(non_executable, 'w') as f:
            f.write("not executable")
        
        self.assertFalse(self.processor.validate_program(non_executable))


if __name__ == '__main__':
    unittest.main()