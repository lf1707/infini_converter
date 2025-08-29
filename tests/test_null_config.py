#!/usr/bin/env python3
"""
Test directory behavior with null config values
"""

import sys
import os
import tkinter as tk

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from infini_converter.config import Config

def test_null_config_values():
    """Test directory behavior when config values are null"""
    print("=== Testing with Null Config Values ===")
    
    # Calculate expected main.py directory
    main_py_dir = os.path.dirname(os.path.abspath(__file__))
    main_py_dir = os.path.dirname(main_py_dir)  # Go up one level to the project directory
    print(f"Expected main.py directory: {main_py_dir}")
    
    # Create fresh config and clear the values
    config = Config()
    config.set_input_directory("")
    config.set_output_directory("")
    
    config_input = config.get_input_directory()
    config_output = config.get_output_directory()
    print(f"Config input directory after clear: '{config_input}'")
    print(f"Config output directory after clear: '{config_output}'")
    
    # Test if values are considered null/empty
    print(f"Config input is null/empty: {not config_input}")
    print(f"Config output is null/empty: {not config_output}")
    
    # Test the logic that should be used in GUI
    input_dir = config.get_input_directory()
    if not input_dir:
        input_dir = main_py_dir
        print(f"✅ Input directory would show default: '{input_dir}'")
    else:
        print(f"❌ Input directory shows config value: '{input_dir}'")
    
    output_dir = config.get_output_directory()
    if not output_dir:
        output_dir = input_dir
        print(f"✅ Output directory would show default: '{output_dir}'")
    else:
        print(f"❌ Output directory shows config value: '{output_dir}'")
    
    # Test with GUI
    print("\n=== Testing GUI with Null Config ===")
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    try:
        # Temporarily replace the config
        from infini_converter.gui import InfiniConverterGUI
        
        # Create app with cleared config
        app = InfiniConverterGUI(root)
        
        # Override the config to use our cleared values
        app.config = config
        
        # Reload the directory settings using the same logic as __init__
        main_py_dir = os.path.dirname(os.path.abspath(__file__))
        main_py_dir = os.path.dirname(main_py_dir)
        
        input_dir = app.config.get_input_directory()
        if not input_dir:
            input_dir = main_py_dir
        
        output_dir = app.config.get_output_directory()
        if not output_dir:
            output_dir = input_dir
        
        # Set the variables
        app.input_directory.set(input_dir)
        app.output_directory.set(output_dir)
        
        print(f"GUI input directory: '{app.input_directory.get()}'")
        print(f"GUI output directory: '{app.output_directory.get()}'")
        
        if app.input_directory.get() == main_py_dir:
            print("✅ Input directory shows default when config is null")
        else:
            print("❌ Input directory does not show default when config is null")
            
        if app.output_directory.get() == main_py_dir:
            print("✅ Output directory shows default when config is null")
        else:
            print("❌ Output directory does not show default when config is null")
            
    except Exception as e:
        print(f"Error during GUI test: {e}")
    
    root.destroy()
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_null_config_values()