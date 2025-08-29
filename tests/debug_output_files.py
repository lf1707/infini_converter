#!/usr/bin/env python3
"""
Comprehensive test to debug output files frame empty issue
"""

import sys
import os
import tempfile
import shutil
import time
sys.path.insert(0, 'src')

from infini_converter.processor import FileProcessor
from infini_converter.config import Config

def test_output_file_generation():
    """Test output file generation with detailed debugging"""
    print("=== Testing Output File Generation ===")
    
    # Create test directory and files
    test_dir = '/tmp/test_output_debug'
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
    
    # Create a script that actually creates output files
    script_content = '''#!/bin/bash
input_file="$1"
output_dir="$2"
input_name=$(basename "$input_file" .txt)
output_file="$output_dir/${input_name}_output.txt"

echo "Processing $input_file"
echo "Creating output file: $output_file"

# Create output file
echo "Processed content from $input_name" > "$output_file"
echo "Output file created successfully"

# List the output directory
echo "Contents of output directory:"
ls -la "$output_dir"
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
        print(f"Output directory before processing: {test_dir}")
        print("Contents before:")
        for item in os.listdir(test_dir):
            print(f"  - {item}")
        
        # Process the file
        result = processor.process_file(input_file)
        results.append(result)
        
        print(f"Processing result:")
        print(f"  Success: {result['success']}")
        print(f"  Output file: {result['output_file']}")
        print(f"  Output exists: {result['output_exists']}")
        
        # Check output directory after processing
        print("Contents after processing:")
        for item in os.listdir(test_dir):
            item_path = os.path.join(test_dir, item)
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path)
                print(f"  - {item} ({size} bytes)")
        
        # Check if output file actually exists
        if result['output_file']:
            if os.path.exists(result['output_file']):
                print(f"✅ Output file exists: {result['output_file']}")
                with open(result['output_file'], 'r') as f:
                    content = f.read()
                    print(f"   Content: {content.strip()}")
            else:
                print(f"❌ Output file does not exist: {result['output_file']}")
    
    # Test GUI output file collection logic
    print(f"\n=== Testing GUI Output File Collection ===")
    
    # Simulate the GUI's processing_complete logic
    output_files = []
    
    for i, result in enumerate(results):
        print(f"\nProcessing result {i+1}:")
        print(f"  success={result['success']}")
        print(f"  output_exists={result.get('output_exists', False)}")
        print(f"  output_file={result.get('output_file', 'N/A')}")
        
        # Check if processing was successful and we have an output file path
        if result["success"] and result.get("output_file"):
            output_file = result["output_file"]
            
            # Check if file exists (either from output_exists flag or direct check)
            file_exists = result.get("output_exists", False) or os.path.exists(output_file)
            
            print(f"  file_exists_check={file_exists}")
            print(f"  os.path.exists={os.path.exists(output_file) if output_file else 'N/A'}")
            
            if file_exists and os.path.exists(output_file):
                output_files.append(output_file)
                print(f"  ✅ Added output file: {output_file}")
            else:
                print(f"  ❌ Output file not found or doesn't exist: {output_file}")
        else:
            print(f"  ❌ Skipping unsuccessful result or missing output file")
    
    print(f"\nOutput files collected: {len(output_files)}")
    for i, file_path in enumerate(output_files):
        print(f"  {i+1}. {file_path}")
    
    # Test directory scanning
    print(f"\n=== Testing Directory Scanning ===")
    
    import glob
    patterns = [
        os.path.join(test_dir, "*_processed*"),
        os.path.join(test_dir, "*.out"),
        os.path.join(test_dir, "*.output"),
        os.path.join(test_dir, "*.result"),
        os.path.join(test_dir, "*_output*"),  # Add this pattern
    ]
    
    found_files = []
    for pattern in patterns:
        matches = glob.glob(pattern)
        print(f"Pattern {pattern}: {matches}")
        for match in matches:
            if os.path.isfile(match) and match not in output_files:
                found_files.append(match)
    
    if found_files:
        print(f"Found additional files: {found_files}")
        output_files.extend(found_files)
    
    # List all files in the directory for manual inspection
    print(f"\n=== All Files in Directory ===")
    all_files = []
    for item in os.listdir(test_dir):
        item_path = os.path.join(test_dir, item)
        if os.path.isfile(item_path):
            all_files.append(item_path)
    
    print(f"All files: {all_files}")
    
    # Check if any files match our expected patterns
    expected_patterns = ['_processed', '_output', '.out', '.output', '.result']
    matching_files = []
    for file_path in all_files:
        for pattern in expected_patterns:
            if pattern in file_path:
                matching_files.append(file_path)
                break
    
    print(f"Files matching expected patterns: {matching_files}")
    
    # Clean up
    print(f"\n=== Cleanup ===")
    shutil.rmtree(test_dir)
    print("Test directory removed")
    
    return len(output_files), len(matching_files)

def test_gui_output_logic():
    """Test the GUI output file logic directly"""
    print(f"\n=== Testing GUI Output File Logic ===")
    
    # Create test results similar to what the processor would return
    test_results = [
        {
            "success": True,
            "output_exists": True,
            "output_file": "/tmp/test_file1_output.txt"
        },
        {
            "success": True,
            "output_exists": False,
            "output_file": "/tmp/test_file2_output.txt"
        },
        {
            "success": False,
            "output_exists": True,
            "output_file": "/tmp/test_file3_output.txt"
        }
    ]
    
    # Simulate the GUI's processing_complete method
    output_files = []
    
    for i, result in enumerate(test_results):
        print(f"Result {i+1}: success={result['success']}, output_exists={result.get('output_exists', False)}, output_file={result.get('output_file', 'N/A')}")
        
        # Check if processing was successful and we have an output file path
        if result["success"] and result.get("output_file"):
            output_file = result["output_file"]
            
            # Check if file exists (either from output_exists flag or direct check)
            file_exists = result.get("output_exists", False) or os.path.exists(output_file)
            
            if file_exists and os.path.exists(output_file):
                output_files.append(output_file)
                print(f"  ✅ Added output file: {output_file}")
            else:
                print(f"  ❌ Output file not found or doesn't exist: {output_file}")
        else:
            print(f"  ❌ Skipping unsuccessful result or missing output file")
    
    print(f"Total output files from GUI logic: {len(output_files)}")
    return len(output_files)

if __name__ == "__main__":
    print("Starting comprehensive output file debugging test...")
    
    # Test actual file generation
    gui_count, manual_count = test_output_file_generation()
    
    # Test GUI logic
    logic_count = test_gui_output_logic()
    
    print(f"\n=== Test Results Summary ===")
    print(f"GUI-collected files: {gui_count}")
    print(f"Manual pattern matches: {manual_count}")
    print(f"GUI logic test files: {logic_count}")
    
    if gui_count == 0:
        print("❌ ISSUE IDENTIFIED: GUI collected 0 files")
        if manual_count > 0:
            print("   But files were actually created!")
            print("   This suggests the GUI logic is not finding the files.")
    else:
        print("✅ GUI successfully collected output files")
    
    print("\nDebugging test completed!")