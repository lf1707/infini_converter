#!/usr/bin/env python3
"""
Comprehensive test script for Infini Converter functions
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from infini_converter.config import Config
from infini_converter.logger import Logger
from infini_converter.file_discovery import FileDiscovery
from infini_converter.processor import FileProcessor

def test_config():
    """Test Config class functionality"""
    print("Testing Config class...")
    
    config = Config()
    
    # Test file extensions
    extensions = ['.txt', '.csv', '.json']
    config.set_file_extensions(extensions)
    assert config.get_file_extensions() == extensions
    print("✓ File extensions configuration works")
    
    # Test output directory
    with tempfile.TemporaryDirectory() as temp_dir:
        config.set_output_directory(temp_dir)
        assert config.get_output_directory() == temp_dir
        print("✓ Output directory configuration works")
    
    # Test processing program
    config.set_processing_program("/bin/echo")
    assert config.get_processing_program() == "/bin/echo"
    print("✓ Processing program configuration works")
    
    # Test logging
    config.set_logging_enabled(True)
    assert config.is_logging_enabled() == True
    config.set_logging_enabled(False)
    assert config.is_logging_enabled() == False
    print("✓ Logging configuration works")
    
    # Test save and load
    config.save_config()
    new_config = Config()
    assert new_config.get_file_extensions() == extensions
    print("✓ Configuration save/load works")

def test_logger():
    """Test Logger class functionality"""
    print("\nTesting Logger class...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = os.path.join(temp_dir, "test.log")
        
        # Test logger creation
        logger = Logger(log_file, True)
        logger.info("Test message")
        logger.error("Test error")
        logger.warning("Test warning")
        
        # Verify log file was created and contains content
        assert os.path.exists(log_file)
        with open(log_file, 'r') as f:
            content = f.read()
            assert "Test message" in content
            assert "Test error" in content
            assert "Test warning" in content
        print("✓ Logger creates files and writes messages")
        
        # Test disable logging
        logger.set_enabled(False)
        logger.info("This should not be logged")
        with open(log_file, 'r') as f:
            content = f.read()
            assert "This should not be logged" not in content
        print("✓ Logger can be disabled")

def test_file_discovery():
    """Test FileDiscovery class functionality"""
    print("\nTesting FileDiscovery class...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        test_files = [
            "test1.txt",
            "test2.csv", 
            "test3.json",
            "test4.py",  # Should not be found
            "subdir/test5.txt",  # Should be found
        ]
        
        for file_path in test_files:
            full_path = os.path.join(temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write("test content")
        
        # Test with default extensions
        discovery = FileDiscovery(['.txt', '.csv', '.json'])
        found_files = discovery.find_files(temp_dir)
        
        # Should find 4 files (test1.txt, test2.csv, test3.json, subdir/test5.txt)
        assert len(found_files) == 4
        found_basenames = [os.path.basename(f) for f in found_files]
        assert "test1.txt" in found_basenames
        assert "test2.csv" in found_basenames
        assert "test3.json" in found_basenames
        assert "test5.txt" in found_basenames
        assert "test4.py" not in found_basenames
        print("✓ File discovery works with correct extensions")
        
        # Test extension updates
        discovery.set_extensions(['.py'])
        found_files = discovery.find_files(temp_dir)
        assert len(found_files) == 1
        assert os.path.basename(found_files[0]) == "test4.py"
        print("✓ Extension updates work")

def test_processor():
    """Test FileProcessor class functionality"""
    print("\nTesting FileProcessor class...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test input file
        input_file = os.path.join(temp_dir, "test_input.txt")
        with open(input_file, 'w') as f:
            f.write("test content")
        
        # Create output directory
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(output_dir)
        
        # Test processor setup
        processor = FileProcessor("/bin/echo", output_dir)
        assert processor.processing_program == "/bin/echo"
        assert processor.output_directory == output_dir
        print("✓ Processor setup works")
        
        # Test program validation
        assert processor.validate_program("/bin/echo") == True
        assert processor.validate_program("/nonexistent/path") == False
        print("✓ Program validation works")
        
        # Test file processing (with echo command)
        result = processor.process_file(input_file)
        assert result["success"] == True
        assert result["input_file"] == input_file
        assert result["output_file"] == os.path.join(output_dir, "test_input.txt")
        assert os.path.exists(result["output_file"])
        print("✓ Single file processing works")
        
        # Test batch processing
        processor.clear_results()
        input_files = [input_file]
        results = processor.process_files_batch(input_files, output_dir)
        assert len(results) == 1
        assert results[0]["success"] == True
        assert processor.get_processing_status()["processed_count"] == 1
        print("✓ Batch processing works")
        
        # Test error handling - non-existent file
        result = processor.process_file("/nonexistent/file.txt")
        assert result["success"] == False
        assert "not found" in result["error"]
        print("✓ Error handling works")

def test_gui_functions():
    """Test GUI-related functions"""
    print("\nTesting GUI-related functions...")
    
    # Test that we can import and create the GUI
    try:
        import tkinter as tk
        from src.infini_converter.gui import InfiniConverterGUI
        
        # Create a test root window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create GUI instance
        app = InfiniConverterGUI(root)
        
        # Test that all components are initialized
        assert hasattr(app, 'config')
        assert hasattr(app, 'logger')
        assert hasattr(app, 'file_discovery')
        assert hasattr(app, 'processor')
        assert hasattr(app, 'input_directory')
        assert hasattr(app, 'output_directory')
        assert hasattr(app, 'processing_program')
        assert hasattr(app, 'file_extensions')
        assert hasattr(app, 'logging_enabled')
        
        print("✓ GUI initialization works")
        
        # Test directory browsing functions exist
        assert hasattr(app, 'browse_input_directory')
        assert hasattr(app, 'browse_output_directory')
        assert hasattr(app, 'browse_processing_program')
        print("✓ Directory browsing functions exist")
        
        # Test file processing functions exist
        assert hasattr(app, 'process_selected_files')
        assert hasattr(app, 'process_all_files')
        assert hasattr(app, 'stop_processing')
        assert hasattr(app, 'clear_file_list')
        print("✓ File processing functions exist")
        
        # Test settings functions exist
        assert hasattr(app, 'save_settings')
        assert hasattr(app, 'load_initial_settings')
        print("✓ Settings functions exist")
        
        # Test logging functions exist
        assert hasattr(app, 'toggle_logging')
        assert hasattr(app, 'log_message')
        print("✓ Logging functions exist")
        
        root.destroy()
        
    except ImportError as e:
        print(f"✗ GUI import failed: {e}")
    except Exception as e:
        print(f"✗ GUI test failed: {e}")

def main():
    """Run all tests"""
    print("=== Infini Converter Function Test Suite ===\n")
    
    try:
        test_config()
        test_logger()
        test_file_discovery()
        test_processor()
        test_gui_functions()
        
        print("\n=== All Tests Completed Successfully! ===")
        return 0
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())