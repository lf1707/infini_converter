#!/usr/bin/env python3
"""
Test script to verify the output file fix
"""

import sys
import os
import tempfile
import shutil
sys.path.insert(0, 'src')

from infini_converter.processor import FileProcessor

def test_fixed_output_file_generation():
    """Test output file generation with the fix"""
    print("=== Testing Fixed Output File Generation ===")
    
    # Create test directory and files
    test_dir = '/tmp/test_output_fixed'
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    
    input_files = []
    for i in range(2):
        test_file = os.path.join(test_dir, f'test{i}.txt')
        with open(test_file, 'w') as f:
            f.write(f"Test input content {i}")
        input_files.append(test_file)
        print(f"Created input file: {test_file}")
    
    # Create a better script that creates output files
    script_content = '''#!/bin/bash
input_file="$1"
output_dir="$2"
input_name=$(basename "$input_file" .txt)
output_file="$output_dir/${input_name}_output.txt"

echo "Processing $input_file"
echo "Output directory: $output_dir"
echo "Output file: $output_file"

# Create output file
echo "Processed content from $input_name at $(date)" > "$output_file"
echo "Output file created successfully: $output_file"

# Verify file was created
if [ -f "$output_file" ]; then
    echo "File verification: SUCCESS"
    ls -la "$output_file"
else
    echo "File verification: FAILED"
fi
'''
    
    script_file = os.path.join(test_dir, 'process_script.sh')
    with open(script_file, 'w') as f:
        f.write(script_content)
    os.chmod(script_file, 0o755)
    
    print(f"Created processing script: {script_file}")
    
    # Test processing
    processor = FileProcessor()
    processor.set_processing_program(script_file)
    processor.set_output_directory(test_dir)
    
    results = []
    for i, input_file in enumerate(input_files):
        print(f"\n--- Processing file {i+1}: {input_file} ---")
        
        # Check output directory before processing
        print(f"Output directory contents before:")
        for item in os.listdir(test_dir):
            if os.path.isfile(os.path.join(test_dir, item)):
                print(f"  - {item}")
        
        # Process the file
        result = processor.process_file(input_file)
        results.append(result)
        
        print(f"Processing result:")
        print(f"  Success: {result['success']}")
        print(f"  Output file: {result['output_file']}")
        print(f"  Output exists: {result['output_exists']}")
        
        # Check output directory after processing
        print("Output directory contents after:")
        for item in os.listdir(test_dir):
            if os.path.isfile(os.path.join(test_dir, item)):
                print(f"  - {item}")
        
        # Check if output file actually exists
        if result['output_file']:
            if os.path.exists(result['output_file']):
                print(f"✅ Output file exists: {result['output_file']}")
                with open(result['output_file'], 'r') as f:
                    content = f.read()
                    print(f"   Content: {content.strip()}")
            else:
                print(f"❌ Output file does not exist: {result['output_file']}")
    
    # Test GUI output file collection
    print(f"\n=== Testing GUI Output File Collection ===")
    
    output_files = []
    for i, result in enumerate(results):
        print(f"Result {i+1}: success={result['success']}, output_exists={result.get('output_exists', False)}, output_file={result.get('output_file', 'N/A')}")
        
        if result["success"] and result.get("output_file"):
            output_file = result["output_file"]
            file_exists = result.get("output_exists", False) or os.path.exists(output_file)
            
            if file_exists and os.path.exists(output_file):
                output_files.append(output_file)
                print(f"  ✅ Added output file: {output_file}")
            else:
                print(f"  ❌ Output file not found: {output_file}")
    
    print(f"\nOutput files collected: {len(output_files)}")
    for i, file_path in enumerate(output_files):
        print(f"  {i+1}. {os.path.basename(file_path)}")
    
    # Clean up
    shutil.rmtree(test_dir)
    
    return len(output_files)

if __name__ == "__main__":
    print("Testing output file fix...")
    
    output_count = test_fixed_output_file_generation()
    
    print(f"\n=== Test Results ===")
    if output_count > 0:
        print(f"✅ SUCCESS: {output_count} output files collected")
        print("The output files frame should now show files!")
    else:
        print(f"❌ FAILED: {output_count} output files collected")
        print("The issue may still persist.")
    
    print("Test completed!")