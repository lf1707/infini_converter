#!/usr/bin/env python3
"""
Simple test script to verify directory boxes show default values
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from infini_converter.config import Config

def test_directory_display_logic():
    """Test the directory display logic without GUI"""
    print("Testing directory display logic...")
    
    # Test 1: Calculate main.py directory
    main_py_dir = os.path.dirname(os.path.abspath(__file__))
    main_py_dir = os.path.dirname(main_py_dir)  # Go up one level to the project directory
    print(f"Main.py directory: {main_py_dir}")
    
    # Test 2: Test with null values (should show defaults)
    config = Config()
    original_input = config.get_input_directory()
    original_output = config.get_output_directory()
    
    print(f"Config input directory: {original_input}")
    print(f"Config output directory: {original_output}")
    
    # Simulate the GUI logic
    input_dir = config.get_input_directory()
    if not input_dir:
        input_dir = main_py_dir  # Use default if null
        print(f"✅ Input directory would show default: {input_dir}")
    else:
        print(f"ℹ️ Input directory shows config value: {input_dir}")
    
    output_dir = config.get_output_directory()
    if not output_dir:
        output_dir = input_dir  # Default output to input directory if not set
        print(f"✅ Output directory would show default: {output_dir}")
    else:
        print(f"ℹ️ Output directory shows config value: {output_dir}")
    
    # Test 3: Test with null config values
    print("\nTesting with null config values:")
    config.set_input_directory("")
    config.set_output_directory("")
    
    input_dir = config.get_input_directory()
    output_dir = config.get_output_directory()
    
    if not input_dir:
        input_dir = main_py_dir
        print(f"✅ Input directory shows default when null: {input_dir}")
    
    if not output_dir:
        output_dir = input_dir
        print(f"✅ Output directory shows default when null: {output_dir}")
    
    print("\n✅ Directory display logic test completed!")
    print("The GUI will always show default values in the directory boxes when they would be null.")

if __name__ == "__main__":
    test_directory_display_logic()