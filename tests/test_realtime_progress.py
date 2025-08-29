#!/usr/bin/env python3
"""
Test script to verify real-time progress bar functionality
"""

import sys
import os
import tempfile
import time
sys.path.insert(0, 'src')

from infini_converter.processor import FileProcessor

def test_realtime_progress():
    """Test real-time progress extraction from subprocess output"""
    print("Testing real-time progress extraction...")
    
    # Create test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test content for real-time progress")
        test_file = f.name
    
    # Create a script that outputs progress information in real-time
    script_content = '''#!/bin/bash
echo "Starting processing..."
for i in {1..10}; do
    echo "Processing: $((i * 10))% complete"
    echo "Progress = $((i * 10))%"
    echo "Frame $i of 10"
    sleep 0.3
done
echo "Processing 100% finished!"
echo "All tasks completed!"
'''
    
    script_file = '/tmp/test_realtime_progress.sh'
    with open(script_file, 'w') as f:
        f.write(script_content)
    os.chmod(script_file, 0o755)
    
    # Test processing with progress callback
    processor = FileProcessor()
    processor.set_processing_program(script_file)
    processor.set_output_directory('/tmp')
    
    progress_updates = []
    
    def progress_callback(percentage, message):
        progress_updates.append({
            'percentage': percentage,
            'message': message,
            'timestamp': time.time()
        })
        print(f"📊 Progress: {percentage:.1f}% - {message}")
    
    try:
        print("Starting file processing with real-time progress...")
        result = processor.process_file(test_file, '/tmp/test_realtime_output.txt', progress_callback=progress_callback)
        
        print(f"\nProcessing result:")
        print(f"Success: {result['success']}")
        print(f"Output exists: {result.get('output_exists', 'N/A')}")
        print(f"Total progress updates: {len(progress_updates)}")
        
        # Analyze progress updates
        if progress_updates:
            print(f"\nProgress update analysis:")
            print(f"First update: {progress_updates[0]['percentage']:.1f}% at {progress_updates[0]['message']}")
            print(f"Last update: {progress_updates[-1]['percentage']:.1f}% at {progress_updates[-1]['message']}")
            
            # Check if progress is monotonic
            percentages = [update['percentage'] for update in progress_updates]
            is_monotonic = all(percentages[i] <= percentages[i+1] for i in range(len(percentages)-1))
            print(f"Progress is monotonic: {is_monotonic}")
            
            # Check if we reached 100%
            final_percentage = progress_updates[-1]['percentage']
            print(f"Final percentage: {final_percentage:.1f}%")
            print(f"Reached 100%: {final_percentage >= 99}")
        
        # Show all progress updates
        print(f"\nAll progress updates:")
        for i, update in enumerate(progress_updates):
            print(f"  {i+1}. {update['percentage']:5.1f}% - {update['message']}")
        
    finally:
        # Clean up
        os.unlink(test_file)
        os.unlink(script_file)
        if os.path.exists('/tmp/test_realtime_output.txt'):
            os.unlink('/tmp/test_realtime_output.txt')

def test_percentage_extraction():
    """Test percentage extraction from various output formats"""
    print("\n" + "="*50)
    print("Testing percentage extraction from various formats...")
    
    processor = FileProcessor()
    
    test_lines = [
        "Processing: 25% complete",
        "Progress: 50% done",
        "Frame 75 of 100",
        "Processing file 2 of 4",
        "120/300 files processed",
        "Progress = 80%",
        "99% finished",
        "No progress here",
        "Error: something went wrong",
        "Progress: 100% - All tasks completed",
        "Encoding: 45% complete"
    ]
    
    print("Testing percentage extraction:")
    for line in test_lines:
        percentage = processor._extract_percentage_from_output(line)
        if percentage >= 0:
            print(f"✅ '{line}' -> {percentage}%")
        else:
            print(f"❌ '{line}' -> No percentage found")

def test_batch_progress():
    """Test batch processing with progress callbacks"""
    print("\n" + "="*50)
    print("Testing batch processing with progress callbacks...")
    
    # Create test files
    test_dir = '/tmp/test_batch_progress'
    os.makedirs(test_dir, exist_ok=True)
    
    test_files = []
    for i in range(3):
        test_file = os.path.join(test_dir, f'test{i}.txt')
        with open(test_file, 'w') as f:
            f.write(f"Test content {i}")
        test_files.append(test_file)
    
    # Create processing script
    script_content = '''#!/bin/bash
echo "Processing $1..."
for i in {1..5}; do
    echo "Progress: $((i * 20))%"
    sleep 0.1
done
echo "Done!"
'''
    
    script_file = '/tmp/test_batch_script.sh'
    with open(script_file, 'w') as f:
        f.write(script_content)
    os.chmod(script_file, 0o755)
    
    # Test batch processing
    processor = FileProcessor()
    processor.set_processing_program(script_file)
    processor.set_output_directory(test_dir)
    
    batch_progress_updates = []
    
    def batch_progress_callback(percentage, message):
        batch_progress_updates.append({
            'percentage': percentage,
            'message': message,
            'timestamp': time.time()
        })
        print(f"📦 Batch Progress: {percentage:.1f}% - {message}")
    
    try:
        print("Starting batch processing...")
        results = processor.process_files_batch(test_files, progress_callback=batch_progress_callback)
        
        print(f"\nBatch processing completed:")
        print(f"Files processed: {len(results)}")
        print(f"Successful: {sum(1 for r in results if r['success'])}")
        print(f"Progress updates: {len(batch_progress_updates)}")
        
        # Show progress timeline
        if batch_progress_updates:
            print(f"\nBatch progress timeline:")
            for i, update in enumerate(batch_progress_updates[:10]):  # Show first 10 updates
                print(f"  {i+1}. {update['percentage']:5.1f}% - {update['message']}")
            if len(batch_progress_updates) > 10:
                print(f"  ... and {len(batch_progress_updates) - 10} more updates")
        
    finally:
        # Clean up
        import shutil
        shutil.rmtree(test_dir)
        os.unlink(script_file)

if __name__ == "__main__":
    test_realtime_progress()
    test_percentage_extraction()
    test_batch_progress()
    print("\n" + "="*50)
    print("All tests completed!")