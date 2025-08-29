#!/usr/bin/env python3
"""
Test script to verify directory boxes show default values
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
import tempfile

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from infini_converter.gui import InfiniConverterGUI
from infini_converter.config import Config

def test_directory_display():
    """Test that directory boxes show default values"""
    root = tk.Tk()
    root.title("Directory Display Test")
    root.geometry("600x400")
    
    # Create a test with a fresh config (simulating null values)
    test_config = Config()
    
    # Clear the config to test default behavior
    test_config.set_input_directory("")
    test_config.set_output_directory("")
    
    # Create GUI with the test config
    app = InfiniConverterGUI(root)
    
    # Override the config to use our test config
    app.config = test_config
    
    # Get the expected default values
    main_py_dir = os.path.dirname(os.path.abspath(__file__))
    main_py_dir = os.path.dirname(main_py_dir)  # Go up one level to the project directory
    
    # Check what values are displayed
    input_display = app.input_directory.get()
    output_display = app.output_directory.get()
    
    print(f"Expected input directory: {main_py_dir}")
    print(f"Display input directory: {input_display}")
    print(f"Display output directory: {output_display}")
    
    # Test results
    test_frame = ttk.Frame(root)
    test_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    ttk.Label(test_frame, text="Directory Display Test Results:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
    
    # Check if input directory shows default
    input_test = "✅ PASS" if input_display == main_py_dir else "❌ FAIL"
    input_msg = f"Input directory shows default: {input_test}"
    ttk.Label(test_frame, text=input_msg, font=("Arial", 10)).pack(anchor=tk.W, pady=2)
    
    # Check if output directory shows default
    output_test = "✅ PASS" if output_display == main_py_dir else "❌ FAIL"
    output_msg = f"Output directory shows default: {output_test}"
    ttk.Label(test_frame, text=output_msg, font=("Arial", 10)).pack(anchor=tk.W, pady=2)
    
    # Show current directory values
    ttk.Label(test_frame, text="", font=("Arial", 8)).pack(anchor=tk.W, pady=5)
    ttk.Label(test_frame, text="Current values in GUI:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
    ttk.Label(test_frame, text=f"Input: {input_display}", font=("Arial", 9)).pack(anchor=tk.W, pady=1)
    ttk.Label(test_frame, text=f"Output: {output_display}", font=("Arial", 9)).pack(anchor=tk.W, pady=1)
    
    # Test with actual saved config values
    ttk.Label(test_frame, text="", font=("Arial", 8)).pack(anchor=tk.W, pady=5)
    ttk.Label(test_frame, text="With saved config values:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
    
    # Create another instance with real config
    app2 = InfiniConverterGUI(root)
    real_input = app2.input_directory.get()
    real_output = app2.output_directory.get()
    
    ttk.Label(test_frame, text=f"Input: {real_input}", font=("Arial", 9)).pack(anchor=tk.W, pady=1)
    ttk.Label(test_frame, text=f"Output: {real_output}", font=("Arial", 9)).pack(anchor=tk.W, pady=1)
    
    root.mainloop()

if __name__ == "__main__":
    test_directory_display()