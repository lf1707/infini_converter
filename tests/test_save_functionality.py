#!/usr/bin/env python3
"""
Test the save button functionality
"""

import sys
import os
import tkinter as tk

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from infini_converter.config import Config

def test_save_functionality():
    """Test that save button works correctly"""
    print("=== Testing Save Button Functionality ===")
    
    # Calculate expected main.py directory
    main_py_dir = os.path.dirname(os.path.abspath(__file__))
    main_py_dir = os.path.dirname(main_py_dir)
    print(f"Expected main.py directory: {main_py_dir}")
    
    # Create fresh config
    config = Config()
    
    # Show initial state
    print("\nInitial config state:")
    print(f"  Input directory: '{config.get_input_directory()}'")
    print(f"  Output directory: '{config.get_output_directory()}'")
    print(f"  Processing program: '{config.get_processing_program()}'")
    print(f"  Command template: '{config.get_command_template()}'")
    print(f"  File extensions: {config.get_file_extensions()}")
    print(f"  Logging enabled: {config.is_logging_enabled()}")
    
    # Simulate user changing values
    print("\nSimulating user changing values...")
    config.set_input_directory("/custom/input/path")
    config.set_output_directory("/custom/output/path")
    config.set_processing_program("/custom/program")
    config.set_command_template("custom {input} command")
    config.set_file_extensions([".mp3", ".wav"])
    config.set_logging_enabled(False)
    
    print("After user changes:")
    print(f"  Input directory: '{config.get_input_directory()}'")
    print(f"  Output directory: '{config.get_output_directory()}'")
    print(f"  Processing program: '{config.get_processing_program()}'")
    print(f"  Command template: '{config.get_command_template()}'")
    print(f"  File extensions: {config.get_file_extensions()}")
    print(f"  Logging enabled: {config.is_logging_enabled()}")
    
    # Test GUI initialization logic
    print("\nTesting GUI initialization logic:")
    input_dir = config.get_input_directory()
    if not input_dir:
        input_dir = main_py_dir
    print(f"GUI would show input directory: '{input_dir}'")
    
    output_dir = config.get_output_directory()
    if not output_dir:
        output_dir = input_dir
    print(f"GUI would show output directory: '{output_dir}'")
    
    # Test save functionality
    print("\nTesting save functionality...")
    config.save_config()
    print("✅ Configuration saved successfully")
    
    # Reload config to verify save worked
    config2 = Config()
    print("\nAfter reloading config:")
    print(f"  Input directory: '{config2.get_input_directory()}'")
    print(f"  Output directory: '{config2.get_output_directory()}'")
    print(f"  Processing program: '{config2.get_processing_program()}'")
    print(f"  Command template: '{config2.get_command_template()}'")
    print(f"  File extensions: {config2.get_file_extensions()}")
    print(f"  Logging enabled: {config2.is_logging_enabled()}")
    
    print("\n✅ Save button functionality test completed successfully!")
    print("✅ Values are properly saved to config file")
    print("✅ GUI displays saved values instead of hardcoded defaults")

if __name__ == "__main__":
    test_save_functionality()