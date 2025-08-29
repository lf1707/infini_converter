#!/usr/bin/env python3
"""
Test script to verify subprocess progress parsing and output file display
"""

import sys
import os
import tempfile
import time
sys.path.insert(0, 'src')

from infini_converter.processor import FileProcessor

def test_subprocess_progress():
    """Test subprocess progress parsing"""
    print("Testing subprocess progress parsing...")
    
    # Create test files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test content for progress parsing")
        test_file = f.name
    
    # Create a script that outputs progress information
    script_content = '''#!/bin/bash
echo "Starting processing..."
for i in {1..5}; do
    echo "Processing: $((i * 20))% complete"
    echo "Frame $i of 5"
    sleep 0.5
done
echo "Processing complete!"
'''
    
    script_file = '/tmp/test_progress_script.sh'
    with open(script_file, 'w') as f:
        f.write(script_content)
    os.chmod(script_file, 0o755)
    
    # Test processing with progress output
    processor = FileProcessor()
    processor.set_output_directory('/tmp')
    processor.set_processing_program(script_file)
    
    try:
        result = processor.process_file(test_file, '/tmp/test_output.txt')
        
        print("Processing result:")
        print(f"Success: {result['success']}")
        print(f"Output exists: {result.get('output_exists', 'N/A')}")
        print(f"Progress info: {result.get('progress_info', [])}")
        print(f"All result keys: {list(result.keys())}")
        
        if result['progress_info']:
            print("Progress information detected:")
            for i, progress in enumerate(result['progress_info']):
                print(f"  {i+1}. {progress}")
        
        # Check if output file was created
        if result['output_exists'] and os.path.exists(result['output_file']):
            print(f"Output file created: {result['output_file']}")
            with open(result['output_file'], 'r') as f:
                print(f"Output content: {f.read()}")
        
    finally:
        # Clean up
        os.unlink(test_file)
        os.unlink(script_file)
        if os.path.exists('/tmp/test_output.txt'):
            os.unlink('/tmp/test_output.txt')

def test_output_file_display():
    """Test output file display logic"""
    print("\nTesting output file display...")
    
    # Create test results
    test_results = [
        {
            "success": True,
            "output_exists": True,
            "output_file": "/tmp/test1_processed.txt"
        },
        {
            "success": True,
            "output_exists": False,
            "output_file": "/tmp/test2_processed.txt"
        },
        {
            "success": False,
            "output_exists": True,
            "output_file": "/tmp/test3_processed.txt"
        }
    ]
    
    # Create actual files
    for i in range(1, 4):
        test_file = f"/tmp/test{i}_processed.txt"
        with open(test_file, 'w') as f:
            f.write(f"Test content {i}")
    
    # Test output file collection logic
    output_files = []
    for result in test_results:
        if result["success"] and result.get("output_exists", False):
            output_file = result["output_file"]
            if output_file and os.path.exists(output_file):
                output_files.append(output_file)
                print(f"Valid output file: {output_file}")
            else:
                print(f"Invalid output file: {output_file}")
    
    print(f"Total valid output files: {len(output_files)}")
    print("Output file names:")
    for file_path in sorted(output_files):
        print(f"  - {os.path.basename(file_path)}")
    
    # Clean up
    for i in range(1, 4):
        test_file = f"/tmp/test{i}_processed.txt"
        if os.path.exists(test_file):
            os.unlink(test_file)

if __name__ == "__main__":
    test_subprocess_progress()
    test_output_file_display()
    print("\nTest completed!")