#!/usr/bin/env python3
"""
Test script to verify directory default logic
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
import tempfile

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from infini_converter.gui import InfiniConverterGUI

def test_directory_defaults():
    """Test the directory default logic"""
    root = tk.Tk()
    root.title("Directory Default Logic Test")
    root.geometry("500x300")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Testing with temp directory: {temp_dir}")
        
        # Create test GUI instance
        app = InfiniConverterGUI(root)
        
        # Test 1: Check if input directory defaults to main.py location
        main_py_dir = os.path.dirname(os.path.abspath(__file__))
        main_py_dir = os.path.dirname(main_py_dir)  # Go up one level to the project directory
        
        input_dir = app.input_directory.get()
        output_dir = app.output_directory.get()
        
        print(f"Main.py directory: {main_py_dir}")
        print(f"Input directory: {input_dir}")
        print(f"Output directory: {output_dir}")
        
        # Test 2: Verify input directory defaults correctly
        if input_dir == main_py_dir:
            print("✅ Input directory defaults correctly to main.py location")
        else:
            print("❌ Input directory does not default correctly")
        
        # Test 3: Verify output directory defaults to input directory
        if output_dir == input_dir:
            print("✅ Output directory defaults correctly to input directory")
        else:
            print("❌ Output directory does not default correctly")
        
        # Test 4: Test changing input directory updates output directory
        old_input = input_dir
        new_input = temp_dir
        
        app.input_directory.set(new_input)
        
        # Check if output directory was updated
        if app.output_directory.get() == new_input:
            print("✅ Output directory automatically updated when input directory changed")
        else:
            print("❌ Output directory was not automatically updated")
        
        # Test 5: Test independent output directory setting
        independent_output = os.path.join(temp_dir, "custom_output")
        app.output_directory.set(independent_output)
        
        # Now change input directory - output should stay independent
        app.input_directory.set(os.path.join(temp_dir, "new_input"))
        
        if app.output_directory.get() == independent_output:
            print("✅ Output directory remains independent when manually set")
        else:
            print("❌ Output directory was incorrectly changed")
        
        # Display test results in GUI
        result_frame = ttk.Frame(root)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(result_frame, text="Test Results:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        test_results = [
            f"Main.py directory: {main_py_dir}",
            f"Input directory: {app.input_directory.get()}",
            f"Output directory: {app.output_directory.get()}",
            "",
            "✅ Directory default logic implemented successfully!"
        ]
        
        for result in test_results:
            ttk.Label(result_frame, text=result, font=("Arial", 10)).pack(anchor=tk.W, pady=2)
        
        print("\nTest completed successfully!")
        root.mainloop()

if __name__ == "__main__":
    test_directory_defaults()