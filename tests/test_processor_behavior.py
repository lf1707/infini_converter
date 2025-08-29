#!/usr/bin/env python3
"""
Test the actual processor behavior
"""

import os
import tempfile
import shutil
from src.infini_converter.config import Config
from src.infini_converter.file_discovery import FileDiscovery
from src.infini_converter.processor import FileProcessor

def test_processor_behavior():
    """Test the actual processor behavior"""
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = os.path.join(temp_dir, "input")
        output_dir = os.path.join(temp_dir, "output")
        
        os.makedirs(input_dir)
        os.makedirs(output_dir)
        
        # Create a test file
        test_file = "test1.txt"
        with open(os.path.join(input_dir, test_file), 'w') as f:
            f.write(f"Content of {test_file}")
        
        print(f"Input directory: {input_dir}")
        print(f"Output directory: {output_dir}")
        
        # Test 1: No command template (default behavior)
        print("\n--- Test 1: No command template ---")
        processor1 = FileProcessor(
            processing_program="echo",
            output_directory=output_dir,
            command_template=""
        )
        
        input_path = os.path.join(input_dir, test_file)
        result1 = processor1.process_file(input_path)
        
        print(f"Result: {result1['success']}")
        print(f"Output file exists: {result1['output_exists']}")
        print(f"Output file path: {result1['output_file']}")
        
        if result1['output_exists']:
            with open(result1['output_file'], 'r') as f:
                content = f.read()
                print(f"Output file content: '{content}'")
        
        # Test 2: With command template
        print("\n--- Test 2: With command template ---")
        processor2 = FileProcessor(
            processing_program="echo",
            output_directory=output_dir,
            command_template='echo "processed {input}" > {output_dir}/{input}_processed.txt'
        )
        
        result2 = processor2.process_file(input_path)
        
        print(f"Result: {result2['success']}")
        print(f"Output file exists: {result2['output_exists']}")
        print(f"Output file path: {result2['output_file']}")
        
        if result2['output_exists']:
            with open(result2['output_file'], 'r') as f:
                content = f.read()
                print(f"Output file content: '{content}'")
        
        # Check what files exist in output directory
        print(f"\n--- Files in output directory ---")
        if os.path.exists(output_dir):
            files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
            for f in files:
                print(f"  - {f}")

if __name__ == "__main__":
    test_processor_behavior()