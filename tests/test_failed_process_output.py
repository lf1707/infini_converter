#!/usr/bin/env python3
"""
Test to verify that failed processes don't show output files
"""

import sys
import os
import tempfile
import shutil
sys.path.insert(0, 'src')

from infini_converter.processor import FileProcessor

def test_failed_process_no_output():
    """Test that failed processes don't create output files in GUI"""
    print("=== Testing Failed Process Output File Handling ===")
    
    # Create test directory and files
    test_dir = '/tmp/test_failed_process'
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    
    # Create test input file
    test_file = os.path.join(test_dir, 'test.txt')
    with open(test_file, 'w') as f:
        f.write("test content")
    
    # Create a script that FAILS (returns non-zero exit code)
    script_content = '''#!/bin/bash
echo "Starting process..."
echo "This process will fail"
echo "Progress: 50%"
# Create an output file (but process will fail)
echo "Failed output" > "$2/failed_output.txt"
echo "Error: Something went wrong"
exit 1  # This makes the process fail
'''
    
    script_file = os.path.join(test_dir, 'fail_script.sh')
    with open(script_file, 'w') as f:
        f.write(script_content)
    os.chmod(script_file, 0o755)
    
    print(f"Created failing script: {script_file}")
    
    # Test processing
    processor = FileProcessor()
    processor.set_processing_program(script_file)
    processor.set_output_directory(test_dir)
    
    # Process the file
    result = processor.process_file(test_file)
    
    print(f"\nProcessing result:")
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
    
    # Simulate GUI logic
    print(f"\n=== Simulating GUI Output File Collection ===")
    output_files = []
    
    # This is the exact logic from the GUI
    if result["success"] and result.get("output_file"):
        output_file = result["output_file"]
        file_exists = result.get("output_exists", False) or os.path.exists(output_file)
        
        if file_exists and os.path.exists(output_file):
            output_files.append(output_file)
            print(f"  ✅ Added output file: {output_file}")
        else:
            print(f"  ❌ Output file not found or doesn't exist: {output_file}")
    else:
        print(f"  ❌ Skipping unsuccessful result (success={result['success']})")
    
    print(f"\nFinal output files count: {len(output_files)}")
    
    # Verify expected behavior
    if result['success']:
        print("❌ ERROR: Process should have failed but didn't!")
        return False
    elif len(output_files) > 0:
        print("❌ ERROR: Failed process should not show output files!")
        return False
    else:
        print("✅ SUCCESS: Failed process correctly shows no output files")
        return True

def test_successful_process_shows_output():
    """Test that successful processes DO show output files"""
    print(f"\n=== Testing Successful Process Output File Handling ===")
    
    # Create test directory and files
    test_dir = '/tmp/test_success_process'
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    
    # Create test input file
    test_file = os.path.join(test_dir, 'test.txt')
    with open(test_file, 'w') as f:
        f.write("test content")
    
    # Create a script that SUCCEEDS (returns 0 exit code)
    script_content = '''#!/bin/bash
echo "Starting process..."
echo "Progress: 50%"
# Create an output file
echo "Successful output" > "$2/success_output.txt"
echo "Process completed successfully"
exit 0  # This makes the process succeed
'''
    
    script_file = os.path.join(test_dir, 'success_script.sh')
    with open(script_file, 'w') as f:
        f.write(script_content)
    os.chmod(script_file, 0o755)
    
    print(f"Created successful script: {script_file}")
    
    # Test processing
    processor = FileProcessor()
    processor.set_processing_program(script_file)
    processor.set_output_directory(test_dir)
    
    # Process the file
    result = processor.process_file(test_file)
    
    print(f"\nProcessing result:")
    print(f"  Success: {result['success']}")
    print(f"  Return code: {result['return_code']}")
    print(f"  Output file: {result['output_file']}")
    print(f"  Output exists: {result['output_exists']}")
    
    # Simulate GUI logic
    print(f"\n=== Simulating GUI Output File Collection ===")
    output_files = []
    
    # This is the exact logic from the GUI
    if result["success"] and result.get("output_file"):
        output_file = result["output_file"]
        file_exists = result.get("output_exists", False) or os.path.exists(output_file)
        
        if file_exists and os.path.exists(output_file):
            output_files.append(output_file)
            print(f"  ✅ Added output file: {output_file}")
        else:
            print(f"  ❌ Output file not found or doesn't exist: {output_file}")
    else:
        print(f"  ❌ Skipping unsuccessful result (success={result['success']})")
    
    print(f"\nFinal output files count: {len(output_files)}")
    
    # Verify expected behavior
    if not result['success']:
        print("❌ ERROR: Process should have succeeded but didn't!")
        return False
    elif len(output_files) == 0:
        print("❌ ERROR: Successful process should show output files!")
        return False
    else:
        print("✅ SUCCESS: Successful process correctly shows output files")
        return True

if __name__ == "__main__":
    print("Testing output file handling for failed vs successful processes...")
    
    # Test failed process
    failed_test_passed = test_failed_process_no_output()
    
    # Test successful process
    success_test_passed = test_successful_process_shows_output()
    
    print(f"\n=== Final Test Results ===")
    print(f"Failed process test: {'✅ PASSED' if failed_test_passed else '❌ FAILED'}")
    print(f"Successful process test: {'✅ PASSED' if success_test_passed else '❌ FAILED'}")
    
    if failed_test_passed and success_test_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Failed processes correctly show NO output files")
        print("✅ Successful processes correctly show output files")
    else:
        print("\n❌ SOME TESTS FAILED!")
    
    # Cleanup
    shutil.rmtree('/tmp/test_failed_process', ignore_errors=True)
    shutil.rmtree('/tmp/test_success_process', ignore_errors=True)
    
    print("\nTest completed!")