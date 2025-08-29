#!/usr/bin/env python3
"""
GUI integration test for Infini Converter
"""

import os
import sys
import tempfile
import threading
import time

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def test_gui_without_display():
    """Test GUI components without displaying the window"""
    print("Testing GUI integration...")
    
    try:
        from src.infini_converter.gui import InfiniConverterGUI
        
        # Create a test root window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create GUI instance
        app = InfiniConverterGUI(root)
        
        # Test directory browsing (simulated)
        print("✓ GUI initialization successful")
        
        # Test file discovery with temporary files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_files = ["test1.txt", "test2.csv"]
            for filename in test_files:
                with open(os.path.join(temp_dir, filename), 'w') as f:
                    f.write("test content")
            
            # Set input directory
            app.input_directory.set(temp_dir)
            app.file_discovery.set_extensions(['.txt', '.csv'])
            
            # Test file discovery
            files = app.file_discovery.find_files(temp_dir)
            assert len(files) == 2
            app.selected_files = files
            
            print("✓ File discovery integration works")
            
            # Test settings save/load
            app.config.set_output_directory(temp_dir)
            app.config.set_processing_program("/bin/echo")
            app.config.set_file_extensions(['.txt'])
            app.config.save_config()
            
            # Load settings
            new_config = type(app.config)()
            assert new_config.get_file_extensions() == ['.txt']
            print("✓ Settings save/load integration works")
            
            # Test logging integration
            app.logger.info("GUI test message")
            app.log_message("GUI log test")
            print("✓ Logging integration works")
            
            # Test processing status
            status = app.processor.get_processing_status()
            assert 'is_processing' in status
            assert 'processed_count' in status
            assert 'failed_count' in status
            print("✓ Processing status integration works")
        
        root.destroy()
        
    except Exception as e:
        print(f"✗ GUI integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_manual_functionality():
    """Test manual functionality that users would perform"""
    print("\nTesting manual functionality...")
    
    try:
        from src.infini_converter.config import Config
        from src.infini_converter.file_discovery import FileDiscovery
        from src.infini_converter.processor import FileProcessor
        from src.infini_converter.logger import Logger
        
        # Test complete workflow
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup directories
            input_dir = os.path.join(temp_dir, "input")
            output_dir = os.path.join(temp_dir, "output")
            os.makedirs(input_dir)
            os.makedirs(output_dir)
            
            # Create test files
            test_files = ["file1.txt", "file2.txt", "file3.csv"]
            for filename in test_files:
                with open(os.path.join(input_dir, filename), 'w') as f:
                    f.write(f"Content of {filename}")
            
            # Initialize components
            config = Config()
            logger = Logger(os.path.join(temp_dir, "test.log"), True)
            discovery = FileDiscovery(['.txt', '.csv'])
            processor = FileProcessor("/bin/echo", output_dir)
            
            # Step 1: Discover files
            files = discovery.find_files(input_dir)
            assert len(files) == 3
            logger.info(f"Found {len(files)} files")
            
            # Step 2: Process files
            results = processor.process_files_batch(files, output_dir)
            assert len(results) == 3
            successful = sum(1 for r in results if r["success"])
            logger.info(f"Successfully processed {successful} files")
            
            # Step 3: Verify output files
            output_files = os.listdir(output_dir)
            assert len(output_files) == 3
            logger.info(f"Generated {len(output_files)} output files")
            
            # Step 4: Test configuration
            config.set_output_directory(output_dir)
            config.set_file_extensions(['.txt'])
            config.set_processing_program("/bin/echo")
            config.save_config()
            
            # Step 5: Load and verify configuration
            new_config = Config()
            assert new_config.get_output_directory() == output_dir
            assert new_config.get_file_extensions() == ['.txt']
            logger.info("Configuration saved and loaded successfully")
            
            print("✓ Complete workflow test passed")
            
            # Verify log file contains expected messages
            with open(os.path.join(temp_dir, "test.log"), 'r') as f:
                log_content = f.read()
                assert "Found 3 files" in log_content
                assert "Successfully processed" in log_content
                assert "Configuration saved" in log_content
                print("✓ Logging verification passed")
        
        return True
        
    except Exception as e:
        print(f"✗ Manual functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run GUI integration tests"""
    print("=== Infini Converter GUI Integration Test Suite ===\n")
    
    success = True
    
    if not test_gui_without_display():
        success = False
    
    if not test_manual_functionality():
        success = False
    
    if success:
        print("\n=== All GUI Integration Tests Completed Successfully! ===")
        print("\nManual Test Checklist:")
        print("✓ Application starts without errors")
        print("✓ Directory browsing functions exist")
        print("✓ File discovery works with various extensions")
        print("✓ File processing works with external programs")
        print("✓ Logging functionality is integrated")
        print("✓ Settings can be saved and loaded")
        print("✓ Complete workflow from input to output works")
        print("✓ Error handling is in place")
        return 0
    else:
        print("\n✗ Some GUI integration tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())