#!/usr/bin/env python3
"""
Test script to verify output file display fix
"""

import sys
import os
import tempfile
sys.path.insert(0, 'src')

from infini_converter.processor import FileProcessor

def test_output_file_display():
    """Test output file display with various scenarios"""
    print("Testing output file display...")
    
    # Create test files
    test_dir = '/tmp/test_output_display'
    os.makedirs(test_dir, exist_ok=True)
    
    test_files = []
    for i in range(3):
        test_file = os.path.join(test_dir, f'test{i}.txt')
        with open(test_file, 'w') as f:
            f.write(f"Test content {i}")
        test_files.append(test_file)
    
    # Create a script that creates output files
    script_content = '''#!/bin/bash
input_file="$1"
output_dir="$2"
input_name=$(basename "$input_file" .txt)
output_file="$output_dir/${input_name}_processed.txt"

echo "Processing $input_file..."
echo "Creating output file: $output_file"

# Create output file with some content
echo "Processed content from $input_file" > "$output_file"
echo "Processing completed for $input_file"
'''
    
    script_file = '/tmp/test_output_script.sh'
    with open(script_file, 'w') as f:
        f.write(script_content)
    os.chmod(script_file, 0o755)
    
    # Test processing
    processor = FileProcessor()
    processor.set_processing_program(script_file)
    processor.set_output_directory(test_dir)
    
    results = []
    for test_file in test_files:
        print(f"\nProcessing: {test_file}")
        result = processor.process_file(test_file)
        results.append(result)
        
        print(f"Result: success={result['success']}")
        print(f"Output file: {result['output_file']}")
        print(f"Output exists: {result['output_exists']}")
        
        # Check if file actually exists
        if result['output_file'] and os.path.exists(result['output_file']):
            print(f"File exists: YES")
            with open(result['output_file'], 'r') as f:
                print(f"File content: {f.read()}")
        else:
            print(f"File exists: NO")
    
    # Test GUI output file collection logic
    print("\n=== Testing GUI Output File Collection ===")
    
    # Simulate GUI processing_complete logic
    output_files = []
    
    for i, result in enumerate(results):
        print(f"Result {i+1}: success={result['success']}, output_exists={result.get('output_exists', False)}, output_file={result.get('output_file', 'N/A')}")
        
        # Check if processing was successful and we have an output file path
        if result["success"] and result.get("output_file"):
            output_file = result["output_file"]
            
            # Check if file exists (either from output_exists flag or direct check)
            file_exists = result.get("output_exists", False) or os.path.exists(output_file)
            
            if file_exists and os.path.exists(output_file):
                output_files.append(output_file)
                print(f"Added output file: {output_file}")
            else:
                print(f"Output file not found or doesn't exist: {output_file}")
        else:
            print(f"Skipping unsuccessful result or missing output file")
    
    print(f"\nTotal output files to display: {len(output_files)}")
    print("Output file names:")
    for file_path in sorted(output_files):
        file_name = os.path.basename(file_path)
        print(f"  - {file_name}")
    
    # Test directory scanning
    print("\n=== Testing Directory Scanning ===")
    import glob
    patterns = [
        os.path.join(test_dir, "*_processed*"),
        os.path.join(test_dir, "*.out"),
        os.path.join(test_dir, "*.output"),
        os.path.join(test_dir, "*.result")
    ]
    
    found_files = []
    for pattern in patterns:
        matches = glob.glob(pattern)
        for match in matches:
            if os.path.isfile(match) and match not in output_files:
                found_files.append(match)
    
    if found_files:
        print(f"Found additional output files: {found_files}")
        output_files.extend(found_files)
    
    print(f"\nFinal output files count: {len(output_files)}")
    
    # Clean up
    import shutil
    shutil.rmtree(test_dir)
    os.unlink(script_file)
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_output_file_display()