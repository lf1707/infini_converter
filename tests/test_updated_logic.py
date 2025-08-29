#!/usr/bin/env python3
"""
Test the updated directory logic that always shows defaults
"""

import sys
import os
import tkinter as tk

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from infini_converter.config import Config

def test_updated_directory_logic():
    """Test the updated directory logic that always shows defaults"""
    print("=== Testing Updated Directory Logic ===")
    
    # Calculate expected main.py directory
    main_py_dir = os.path.dirname(os.path.abspath(__file__))
    main_py_dir = os.path.dirname(main_py_dir)  # Go up one level to the project directory
    print(f"Expected main.py directory: {main_py_dir}")
    
    # Test with actual config
    config = Config()
    config_input = config.get_input_directory()
    config_output = config.get_output_directory()
    print(f"Config input directory: '{config_input}'")
    print(f"Config output directory: '{config_output}'")
    
    # Test the new logic
    input_dir = main_py_dir  # Always use main.py directory as default
    
    # Use config value only if it's different from main.py directory
    if config_input and config_input != main_py_dir:
        input_dir = config_input
        print(f"Using config input: '{input_dir}'")
    else:
        print(f"Using default input: '{input_dir}'")
    
    output_dir = input_dir  # Default output to input directory
    
    # Use config value only if it's different from input directory
    if config_output and config_output != input_dir:
        output_dir = config_output
        print(f"Using config output: '{output_dir}'")
    else:
        print(f"Using default output: '{output_dir}'")
    
    # Test with GUI
    print("\n=== Testing GUI with Updated Logic ===")
    root = tk.Tk()
    root.withdraw()
    
    try:
        from infini_converter.gui import InfiniConverterGUI
        app = InfiniConverterGUI(root)
        
        print(f"GUI input directory: '{app.input_directory.get()}'")
        print(f"GUI output directory: '{app.output_directory.get()}'")
        
        # Check if they show defaults
        input_shows_default = app.input_directory.get() == main_py_dir
        output_shows_default = app.output_directory.get() == main_py_dir
        
        print(f"Input shows default: {input_shows_default}")
        print(f"Output shows default: {output_shows_default}")
        
        if input_shows_default:
            print("✅ Input directory shows default value")
        else:
            print("ℹ️ Input directory shows config value (different from default)")
            
        if output_shows_default:
            print("✅ Output directory shows default value")
        else:
            print("ℹ️ Output directory shows config value (different from default)")
        
    except Exception as e:
        print(f"Error during GUI test: {e}")
    
    root.destroy()
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_updated_directory_logic()