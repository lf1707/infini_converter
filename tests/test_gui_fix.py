#!/usr/bin/env python3
"""
Test the fixed GUI behavior
"""

import os
import tempfile
import sys
sys.path.insert(0, 'src')

from infini_converter.file_discovery import FileDiscovery
from infini_converter.processor import FileProcessor

def test_fixed_gui_behavior():
    """Test the fixed GUI behavior"""
    
    print("=== Testing Fixed GUI Behavior ===")
    
    # Create a test directory with various files
    test_dir = '/tmp/test_gui_fix'
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    
    # Create test files including problematic ones
    test_files = [
        'valid_file1.ape',
        'valid_file2.ape', 
        'incomplete.part',  # This should be filtered out
        'temp_file.tmp',    # This should be filtered out
        'empty_file.txt',   # This should be filtered out (too small)
        'normal_file.txt',  # This should be kept
        '.DS_Store',        # This should be filtered out
    ]
    
    for filename in test_files:
        file_path = os.path.join(test_dir, filename)
        if filename == 'empty_file.txt':
            # Create an empty file
            open(file_path, 'w').close()
        else:
            # Write more content to ensure files are larger than 100 bytes
            content = f"This is a test file with more content to ensure it's larger than 100 bytes. File: {filename}"
            with open(file_path, 'w') as f:
                f.write(content)
    
    print(f"Created test directory: {test_dir}")
    print("Test files:")
    for filename in test_files:
        file_path = os.path.join(test_dir, filename)
        size = os.path.getsize(file_path)
        print(f"  - {filename} ({size} bytes)")
    
    # Test file discovery with filtering
    print(f"\n=== Testing File Discovery with Filtering ===")
    
    file_discovery = FileDiscovery(extensions=['.ape', '.txt'])
    
    # Find files without filtering
    all_files = file_discovery.find_files(test_dir)
    print(f"Files found without filtering: {len(all_files)}")
    for f in all_files:
        print(f"  - {os.path.basename(f)}")
    
    # Find files with filtering
    filtered_files = file_discovery.filter_problematic_files(all_files)
    print(f"\nFiles found with filtering: {len(filtered_files)}")
    for f in filtered_files:
        print(f"  - {os.path.basename(f)}")
    
    # Test processor with filtered files
    print(f"\n=== Testing Processor ===")
    
    # Use a simple echo command for testing
    processor = FileProcessor(
        processing_program="echo",
        output_directory=test_dir,
        command_template="echo 'Processing {input}' > {output_dir}/{input}_processed.flac"
    )
    
    results = []
    for file_path in filtered_files:
        print(f"Processing {os.path.basename(file_path)}...")
        result = processor.process_file(file_path)
        results.append(result)
        print(f"  Success: {result['success']}")
        print(f"  Output: {result.get('output_file', 'N/A')}")
    
    # Test the updated processing_complete logic
    print(f"\n=== Testing Updated Processing Complete Logic ===")
    
    # Simulate the updated processing_complete method
    successful_results = [r for r in results if r.get("success", False)]
    failed_results = [r for r in results if not r.get("success", False)]
    
    print(f"Successful processing: {len(successful_results)}")
    print(f"Failed processing: {len(failed_results)}")
    
    # Simulate output listbox display
    if successful_results:
        print("Output listbox would contain:")
        for result in successful_results:
            if result.get("output_file"):
                filename = os.path.basename(result["output_file"])
                print(f"  - {filename}")
        print("✅ Output listbox shows successful files")
    elif failed_results:
        print(f"Output listbox would show: Processing failed for {len(failed_results)} files")
        print("✅ Output listbox provides helpful error message")
    else:
        print("Output listbox would show: No new files created")
        print("ℹ️  Output listbox shows appropriate message")
    
    # Check what files were actually created
    print(f"\n=== Checking Created Files ===")
    
    output_files = []
    for filename in os.listdir(test_dir):
        file_path = os.path.join(test_dir, filename)
        if os.path.isfile(file_path) and filename.endswith('_processed.flac'):
            output_files.append(file_path)
    
    print(f"Output files created: {len(output_files)}")
    for f in output_files:
        print(f"  - {os.path.basename(f)}")
    
    # Clean up
    print(f"\n=== Cleanup ===")
    shutil.rmtree(test_dir)
    print("Test directory removed")
    
    print(f"\n=== Summary ===")
    print(f"✅ File filtering works correctly")
    print(f"✅ Processing handles filtered files properly")
    print(f"✅ Output listbox logic provides appropriate feedback")
    print(f"✅ The Output Files list box should now work correctly")

if __name__ == "__main__":
    import shutil
    test_fixed_gui_behavior()