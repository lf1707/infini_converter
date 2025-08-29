#!/usr/bin/env python3
"""
Test subprocess execution directly
"""

import sys
import os
import tempfile
import subprocess

# Add src to path
sys.path.insert(0, 'src')

from infini_converter.processor import FileProcessor

def test_subprocess_execution():
    """Test subprocess execution directly."""
    print("Testing subprocess execution...")
    
    # Create a temporary directory and file
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test file
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # Create output directory
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Create processor instance
        processor = FileProcessor()
        processor.processing_program = "echo"
        processor.output_directory = output_dir
        
        print(f"Test file: {test_file}")
        print(f"Output directory: {output_dir}")
        
        # Test command building
        cmd_list = processor.build_command(test_file)
        cmd_string = processor.build_command_string(test_file)
        
        print(f"Command list: {cmd_list}")
        print(f"Command string: {cmd_string}")
        
        # Test subprocess execution
        try:
            print("Executing subprocess...")
            result = subprocess.run(
                cmd_list,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            print(f"Return code: {result.returncode}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            
            if result.returncode == 0:
                print("✓ Subprocess execution successful!")
            else:
                print("✗ Subprocess execution failed!")
                
        except Exception as e:
            print(f"✗ Exception during subprocess execution: {e}")
        
        # Test with a simple command that should work
        print("\n--- Testing with simple command ---")
        simple_cmd = ["echo", "hello"]
        try:
            result = subprocess.run(
                simple_cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            print(f"Simple command result: {result.stdout}")
        except Exception as e:
            print(f"Simple command failed: {e}")

if __name__ == "__main__":
    test_subprocess_execution()