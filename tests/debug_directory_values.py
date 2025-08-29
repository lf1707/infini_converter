#!/usr/bin/env python3
"""
Debug script to check directory values in the GUI
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from infini_converter.config import Config

def debug_directory_values():
    """Debug what directory values are being set"""
    print("=== Debugging Directory Values ===")
    
    # Calculate expected main.py directory
    main_py_dir = os.path.dirname(os.path.abspath(__file__))
    main_py_dir = os.path.dirname(main_py_dir)  # Go up one level to the project directory
    print(f"Expected main.py directory: {main_py_dir}")
    
    # Check config values
    config = Config()
    config_input = config.get_input_directory()
    config_output = config.get_output_directory()
    print(f"Config input directory: '{config_input}'")
    print(f"Config output directory: '{config_output}'")
    
    # Test if values are considered null/empty
    print(f"Config input is null/empty: {not config_input}")
    print(f"Config output is null/empty: {not config_output}")
    
    # Simulate the GUI logic step by step
    input_dir = config.get_input_directory()
    print(f"Step 1 - input_dir from config: '{input_dir}'")
    
    if not input_dir:
        input_dir = main_py_dir
        print(f"Step 2 - input_dir set to default: '{input_dir}'")
    
    output_dir = config.get_output_directory()
    print(f"Step 3 - output_dir from config: '{output_dir}'")
    
    if not output_dir:
        output_dir = input_dir
        print(f"Step 4 - output_dir set to default: '{output_dir}'")
    
    # Test with actual GUI initialization
    print("\n=== Testing GUI Initialization ===")
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    try:
        from infini_converter.gui import InfiniConverterGUI
        app = InfiniConverterGUI(root)
        
        print(f"GUI input directory: '{app.input_directory.get()}'")
        print(f"GUI output directory: '{app.output_directory.get()}'")
        
        # Check if they match expected values
        expected_input = main_py_dir if not config_input else config_input
        expected_output = expected_input if not config_output else config_output
        
        print(f"Expected input: '{expected_input}'")
        print(f"Expected output: '{expected_output}'")
        
        input_match = app.input_directory.get() == expected_input
        output_match = app.output_directory.get() == expected_output
        
        print(f"Input directory match: {input_match}")
        print(f"Output directory match: {output_match}")
        
    except Exception as e:
        print(f"Error during GUI initialization: {e}")
    
    root.destroy()
    print("=== Debug Complete ===")

if __name__ == "__main__":
    debug_directory_values()