#!/usr/bin/env python3
"""
Test to verify that when output_exists=False, no fallback file detection occurs
"""

import sys
import os
import tempfile
import shutil
sys.path.insert(0, 'src')

from infini_converter.processor import FileProcessor

def test_output_exists_false_no_fallback():
    """Test that when output_exists=False, no fallback detection occurs"""
    print("=== Testing output_exists=False Behavior ===")
    
    # Create test directory and files
    test_dir = '/tmp/test_output_exists_false'
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    
    # Create test input file
    test_file = os.path.join(test_dir, 'test.txt')
    with open(test_file, 'w') as f:
        f.write("test content")
    
    # Create a script that succeeds but doesn't create the expected output file
    script_content = '''#!/bin/bash
echo "Processing file..."
echo "Progress: 100%"
# Create a different file (not the expected one)
echo "Different output" > "$2/different_file.txt"
echo "Done"
exit 0
'''
    
    script_file = os.path.join(test_dir, 'script.sh')
    with open(script_file, 'w') as f:
        f.write(script_content)
    os.chmod(script_file, 0o755)
    
    # Test processing
    processor = FileProcessor()
    processor.set_processing_program(script_file)
    processor.set_output_directory(test_dir)
    
    result = processor.process_file(test_file)
    
    print(f"Processing result:")
    print(f"  Success: {result['success']}")
    print(f"  Return code: {result['return_code']}")
    print(f"  Output file: {result['output_file']}")
    print(f"  Output exists: {result['output_exists']}")
    
    # Check what files were actually created
    print(f"\nFiles in output directory:")
    for item in os.listdir(test_dir):
        item_path = os.path.join(test_dir, item)
        if os.path.isfile(item_path):
            print(f"  - {item}")
    
    # Simulate NEW simplified GUI logic
    print(f"\n=== Simulating NEW Simplified GUI Logic ===")
    output_files = []
    
    # NEW simplified logic
    if result["success"] and result.get("output_file"):
        output_file = result["output_file"]
        
        # If output_exists is False, stop - don't try to find potential files
        if not result.get("output_exists", False):
            print(f"  ❌ Output file does not exist: {output_file}")
            print(f"  ❌ STOPPING - no fallback detection")
        else:
            # File exists, add it to the list
            if os.path.exists(output_file):
                output_files.append(output_file)
                print(f"  ✅ Added output file: {output_file}")
            else:
                print(f"  ❌ Output file marked as existing but not found: {output_file}")
    else:
        print(f"  ❌ Skipping unsuccessful result or missing output file")
    
    print(f"\nFinal output files count: {len(output_files)}")
    
    # Verify expected behavior
    expected_behavior = (
        result['success'] and  # Process succeeded
        not result['output_exists'] and  # Output file doesn't exist
        len(output_files) == 0  # No output files added to GUI
    )
    
    if expected_behavior:
        print("✅ SUCCESS: When output_exists=False, no fallback detection occurs")
        return True
    else:
        print("❌ FAILED: Behavior doesn't match expectations")
        return False

def test_output_exists_true_shows_file():
    """Test that when output_exists=True, file is shown"""
    print(f"\n=== Testing output_exists=True Behavior ===")
    
    # Create test directory and files
    test_dir = '/tmp/test_output_exists_true'
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    
    # Create test input file
    test_file = os.path.join(test_dir, 'test.txt')
    with open(test_file, 'w') as f:
        f.write("test content")
    
    # Create a script that creates the expected output file
    script_content = '''#!/bin/bash
echo "Processing file..."
echo "Progress: 100%"
# Create the expected output file
echo "Expected output" > "$2/test_processed.txt"
echo "Done"
exit 0
'''
    
    script_file = os.path.join(test_dir, 'script.sh')
    with open(script_file, 'w') as f:
        f.write(script_content)
    os.chmod(script_file, 0o755)
    
    # Test processing
    processor = FileProcessor()
    processor.set_processing_program(script_file)
    processor.set_output_directory(test_dir)
    
    result = processor.process_file(test_file)
    
    print(f"Processing result:")
    print(f"  Success: {result['success']}")
    print(f"  Return code: {result['return_code']}")
    print(f"  Output file: {result['output_file']}")
    print(f"  Output exists: {result['output_exists']}")
    
    # Simulate NEW simplified GUI logic
    print(f"\n=== Simulating NEW Simplified GUI Logic ===")
    output_files = []
    
    # NEW simplified logic
    if result["success"] and result.get("output_file"):
        output_file = result["output_file"]
        
        # If output_exists is False, stop - don't try to find potential files
        if not result.get("output_exists", False):
            print(f"  ❌ Output file does not exist: {output_file}")
            print(f"  ❌ STOPPING - no fallback detection")
        else:
            # File exists, add it to the list
            if os.path.exists(output_file):
                output_files.append(output_file)
                print(f"  ✅ Added output file: {output_file}")
            else:
                print(f"  ❌ Output file marked as existing but not found: {output_file}")
    else:
        print(f"  ❌ Skipping unsuccessful result or missing output file")
    
    print(f"\nFinal output files count: {len(output_files)}")
    
    # Verify expected behavior
    expected_behavior = (
        result['success'] and  # Process succeeded
        result['output_exists'] and  # Output file exists
        len(output_files) == 1  # Output file added to GUI
    )
    
    if expected_behavior:
        print("✅ SUCCESS: When output_exists=True, file is shown")
        return True
    else:
        print("❌ FAILED: Behavior doesn't match expectations")
        return False

if __name__ == "__main__":
    print("Testing simplified output file handling...")
    
    # Test output_exists=False behavior
    test1_passed = test_output_exists_false_no_fallback()
    
    # Test output_exists=True behavior
    test2_passed = test_output_exists_true_shows_file()
    
    print(f"\n=== Final Test Results ===")
    print(f"output_exists=False test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"output_exists=True test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ When output_exists=False: No fallback detection, no files shown")
        print("✅ When output_exists=True: File is shown in GUI")
    else:
        print("\n❌ SOME TESTS FAILED!")
    
    # Cleanup
    shutil.rmtree('/tmp/test_output_exists_false', ignore_errors=True)
    shutil.rmtree('/tmp/test_output_exists_true', ignore_errors=True)
    
    print("\nTest completed!")