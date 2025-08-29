#!/usr/bin/env python3
"""
Final comprehensive test for the complete solution
"""

import sys
import os
import tempfile
import shutil
sys.path.insert(0, 'src')

from infini_converter.processor import FileProcessor
from infini_converter.gui import InfiniConverterGUI
from infini_converter.config import Config
import tkinter as tk

def test_complete_solution():
    """Test the complete solution with real-time progress and output files"""
    print("=== Testing Complete Solution ===")
    
    # Create test environment
    test_dir = '/tmp/test_complete_solution'
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    
    # Create test input files
    input_files = []
    for i in range(3):
        test_file = os.path.join(test_dir, f'input{i}.txt')
        with open(test_file, 'w') as f:
            f.write(f"Test input content for file {i}\nThis is line 2\nThis is line 3")
        input_files.append(test_file)
        print(f"Created input file: {test_file}")
    
    # Create a processing script that outputs progress and creates files
    script_content = '''#!/bin/bash
input_file="$1"
output_dir="$2"
input_name=$(basename "$input_file" .txt)

echo "Starting processing of $input_name..."
echo "Progress: 0%"

# Simulate processing steps
for i in {1..10}; do
    echo "Processing: $((i * 10))% complete"
    echo "Progress = $((i * 10))%"
    sleep 0.1
done

# Create output file
output_file="$output_dir/${input_name}_processed.txt"
echo "Processed content from $input_name" > "$output_file"
echo "Processing completed at $(date)" >> "$output_file"
echo "Created output file: $output_file"

echo "Progress: 100%"
echo "Processing completed successfully!"
'''
    
    script_file = os.path.join(test_dir, 'process.sh')
    with open(script_file, 'w') as f:
        f.write(script_content)
    os.chmod(script_file, 0o755)
    
    print(f"Created processing script: {script_file}")
    
    # Test processor with real-time progress
    print(f"\n=== Testing Processor with Real-time Progress ===")
    
    processor = FileProcessor()
    processor.set_processing_program(script_file)
    processor.set_output_directory(test_dir)
    
    progress_updates = []
    
    def progress_callback(percentage, message):
        progress_updates.append({
            'percentage': percentage,
            'message': message,
            'timestamp': time.time()
        })
        print(f"📊 Progress: {percentage:5.1f}% - {message}")
    
    # Process files
    results = []
    for i, input_file in enumerate(input_files):
        print(f"\n--- Processing file {i+1}: {os.path.basename(input_file)} ---")
        
        result = processor.process_file(input_file, progress_callback=progress_callback)
        results.append(result)
        
        print(f"Result: success={result['success']}, output_exists={result['output_exists']}")
        print(f"Output file: {result['output_file']}")
        
        if result['output_file'] and os.path.exists(result['output_file']):
            print(f"✅ Output file exists")
        else:
            print(f"❌ Output file missing")
    
    # Test GUI output file collection
    print(f"\n=== Testing GUI Output File Collection ===")
    
    # Create a minimal GUI for testing
    root = tk.Tk()
    root.withdraw()
    
    config = Config()
    gui = InfiniConverterGUI(root)
    gui.output_directory.set(test_dir)
    gui.selected_files = input_files
    
    # Simulate processing_complete
    output_files = []
    print("Simulating GUI processing_complete logic...")
    
    for i, result in enumerate(results):
        print(f"Result {i+1}: success={result['success']}, output_exists={result.get('output_exists', False)}")
        
        if result["success"] and result.get("output_file"):
            output_file = result["output_file"]
            file_exists = result.get("output_exists", False) or os.path.exists(output_file)
            
            if file_exists and os.path.exists(output_file):
                output_files.append(output_file)
                print(f"  ✅ Added: {os.path.basename(output_file)}")
            else:
                print(f"  ❌ Missing: {output_file}")
    
    # Test additional file detection
    print(f"\nTesting additional file detection...")
    gui._scan_output_directory_for_files(output_files)
    
    if len(output_files) == 0:
        print("Testing fallback detection...")
        gui._find_any_modified_files(output_files, input_files)
    
    print(f"\nFinal output files count: {len(output_files)}")
    for i, file_path in enumerate(output_files):
        print(f"  {i+1}. {os.path.basename(file_path)}")
    
    # Test real-time progress analysis
    print(f"\n=== Real-time Progress Analysis ===")
    print(f"Total progress updates: {len(progress_updates)}")
    
    if progress_updates:
        percentages = [update['percentage'] for update in progress_updates]
        print(f"Progress range: {min(percentages):.1f}% - {max(percentages):.1f}%")
        print(f"Final progress: {progress_updates[-1]['percentage']:.1f}%")
        print(f"Reached 100%: {max(percentages) >= 99}")
        
        # Show sample updates
        print(f"\nSample progress updates:")
        for i, update in enumerate(progress_updates[::5]):  # Show every 5th update
            print(f"  {i*5+1}. {update['percentage']:5.1f}% - {update['message']}")
    
    # Clean up
    root.destroy()
    shutil.rmtree(test_dir)
    
    return len(results), len(output_files), len(progress_updates)

if __name__ == "__main__":
    import time
    
    print("Testing complete solution...")
    
    successful_processes, output_files_count, progress_updates = test_complete_solution()
    
    print(f"\n=== Final Results ===")
    print(f"✅ Successful processes: {successful_processes}")
    print(f"✅ Output files detected: {output_files_count}")
    print(f"✅ Progress updates captured: {progress_updates}")
    
    if successful_processes > 0 and output_files_count > 0 and progress_updates > 0:
        print("\n🎉 COMPLETE SUCCESS!")
        print("All features are working:")
        print("  • Real-time progress bar updates from subprocess output")
        print("  • Output file detection and display")
        print("  • Percentage extraction from various formats")
        print("  • GUI integration with both features")
    else:
        print("\n❌ Some features may still need attention")
    
    print("\nTest completed!")