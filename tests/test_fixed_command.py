#!/usr/bin/env python3
"""
Test the fixed command structure
"""

import os
import tempfile
import shutil
from src.infini_converter.config import Config
from src.infini_converter.file_discovery import FileDiscovery
from src.infini_converter.processor import FileProcessor

def test_fixed_command_structure():
    """Test the fixed command structure"""
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = os.path.join(temp_dir, "input")
        output_dir = os.path.join(temp_dir, "output")
        
        os.makedirs(input_dir)
        os.makedirs(output_dir)
        
        # Create a test file
        test_file = "test.ape"
        with open(os.path.join(input_dir, test_file), 'w') as f:
            f.write("dummy audio content")
        
        print(f"Input directory: {input_dir}")
        print(f"Output directory: {output_dir}")
        print(f"Test file: {test_file}")
        
        # Load the updated config
        config = Config()
        print(f"\nConfig settings:")
        print(f"  Processing program: {config.get_processing_program()}")
        print(f"  Command template: {config.get_command_template()}")
        print(f"  Output directory: {config.get_output_directory()}")
        
        # Initialize processor with the updated config
        processor = FileProcessor(
            processing_program=config.get_processing_program(),
            output_directory=config.get_output_directory(),
            command_template=config.get_command_template()
        )
        
        # Test the command building
        input_path = os.path.join(input_dir, test_file)
        cmd = processor.build_command(input_path)
        cmd_string = " ".join(cmd)
        
        print(f"\nBuilt command: {cmd_string}")
        
        # Test what the command would look like
        print(f"\nExpected command structure:")
        print(f"  Program: {config.get_processing_program()}")
        print(f"  Arguments: -f flac -o {output_dir} {input_path}")
        
        # For this test, let's use a simple echo command instead of xld
        # to verify the structure without needing the actual xld binary
        processor_echo = FileProcessor(
            processing_program="echo",
            output_directory=output_dir,
            command_template="echo 'Processing: {input}' -> Output: {output_dir}"
        )
        
        cmd_echo = processor_echo.build_command(input_path)
        cmd_string_echo = " ".join(cmd_echo)
        
        print(f"\nEcho test command: {cmd_string_echo}")
        
        # Execute the echo command to test
        import subprocess
        try:
            result = subprocess.run(cmd_string_echo, shell=True, capture_output=True, text=True, timeout=10)
            print(f"Echo command result:")
            print(f"  Return code: {result.returncode}")
            print(f"  STDOUT: {result.stdout}")
            print(f"  STDERR: {result.stderr}")
        except Exception as e:
            print(f"Error executing echo command: {e}")

if __name__ == "__main__":
    test_fixed_command_structure()