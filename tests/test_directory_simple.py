#!/usr/bin/env python3
"""
Simple test script to verify directory default logic
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from infini_converter.config import Config

def test_directory_defaults():
    """Test the directory default logic"""
    print("Testing directory default logic...")
    
    # Create a config instance
    config = Config()
    
    # Test 1: Check main.py directory calculation
    main_py_dir = os.path.dirname(os.path.abspath(__file__))
    main_py_dir = os.path.dirname(main_py_dir)  # Go up one level to the project directory
    
    print(f"Main.py directory: {main_py_dir}")
    print(f"Config input directory: {config.get_input_directory()}")
    print(f"Config output directory: {config.get_output_directory()}")
    
    # Test 2: Simulate GUI logic for setting defaults
    input_dir = config.get_input_directory()
    if not input_dir:
        input_dir = main_py_dir
        print(f"✅ Input directory defaults to: {input_dir}")
    else:
        print(f"ℹ️ Input directory from config: {input_dir}")
    
    output_dir = config.get_output_directory()
    if not output_dir:
        output_dir = input_dir
        print(f"✅ Output directory defaults to: {output_dir}")
    else:
        print(f"ℹ️ Output directory from config: {output_dir}")
    
    # Test 3: Test the logic when directories are explicitly set
    config.set_input_directory("/custom/input/path")
    config.set_output_directory("/custom/output/path")
    
    input_dir = config.get_input_directory()
    output_dir = config.get_output_directory()
    
    if input_dir == "/custom/input/path" and output_dir == "/custom/output/path":
        print("✅ Custom directory paths work correctly")
    else:
        print("❌ Custom directory paths don't work correctly")
    
    print("\nDirectory default logic test completed!")

if __name__ == "__main__":
    test_directory_defaults()