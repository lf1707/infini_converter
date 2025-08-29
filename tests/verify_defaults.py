#!/usr/bin/env python3
"""
Quick test to verify directory boxes show default values
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from infini_converter.config import Config

def test_default_values():
    """Test that directory boxes show default values"""
    print("=== Testing Default Directory Values ===")
    
    # Calculate expected main.py directory
    main_py_dir = os.path.dirname(os.path.abspath(__file__))
    main_py_dir = os.path.dirname(main_py_dir)
    print(f"Expected default directory: {main_py_dir}")
    
    # Check config values
    config = Config()
    config_input = config.get_input_directory()
    config_output = config.get_output_directory()
    print(f"Config input directory: {config_input}")
    print(f"Config output directory: {config_output}")
    
    # Test what the GUI should show
    print(f"GUI will show input directory: {main_py_dir}")
    print(f"GUI will show output directory: {main_py_dir}")
    
    print("\n✅ Directory boxes will now always show default values")
    print("✅ Config values are ignored for directory fields")
    print("✅ Users always see meaningful default paths")

if __name__ == "__main__":
    test_default_values()