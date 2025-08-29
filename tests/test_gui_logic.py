#!/usr/bin/env python3
"""
Test the actual GUI logic for output files detection
"""

import os
import tempfile
import shutil
from src.infini_converter.config import Config
from src.infini_converter.file_discovery import FileDiscovery
from src.infini_converter.processor import FileProcessor

def test_gui_output_logic():
    """Test the actual GUI logic for output files detection"""
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = os.path.join(temp_dir, "input")
        output_dir = os.path.join(temp_dir, "output")
        
        os.makedirs(input_dir)
        os.makedirs(output_dir)
        
        # Create some test files
        test_files = ["test1.txt", "test2.txt", "test3.txt"]
        for filename in test_files:
            with open(os.path.join(input_dir, filename), 'w') as f:
                f.write(f"Content of {filename}")
        
        # Create some existing output files
        existing_output_files = ["existing1.txt", "existing2.txt"]
        for filename in existing_output_files:
            with open(os.path.join(output_dir, filename), 'w') as f:
                f.write(f"Existing {filename}")
        
        print(f"Input directory: {input_dir}")
        print(f"Output directory: {output_dir}")
        print(f"Input files: {test_files}")
        print(f"Existing output files: {existing_output_files}")
        
        # Simulate the GUI logic
        print("\n--- Simulating GUI processing logic ---")
        
        # This is what happens in process_files method
        output_placeholder_text = "Select or enter output directory path"
        pre_files = []
        if output_dir and output_dir != output_placeholder_text and os.path.exists(output_dir):
            try:
                pre_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) 
                             if os.path.isfile(os.path.join(output_dir, f))]
                print(f"Collected {len(pre_files)} pre-processing files from output directory")
                for f in pre_files:
                    print(f"  - {os.path.basename(f)}")
            except Exception as e:
                print(f"Error reading output directory: {e}")
        
        # Store pre-processing files for comparison later
        _pre_output_files = pre_files
        
        # This is what happens in processing_complete method
        post_files = []
        if output_dir and output_dir != output_placeholder_text and os.path.exists(output_dir):
            try:
                post_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) 
                             if os.path.isfile(os.path.join(output_dir, f))]
                print(f"Found {len(post_files)} files in output directory after processing")
            except Exception as e:
                print(f"Error reading output directory: {e}")
        
        # Collect pre-processing files (stored before starting processing)
        pre_files = _pre_output_files
        
        # Find new files (files in post_files but not in pre_files)
        new_files = []
        if pre_files and post_files:
            pre_basenames = {os.path.basename(f) for f in pre_files}
            for post_file in post_files:
                post_basename = os.path.basename(post_file)
                if post_basename not in pre_basenames:
                    new_files.append(post_file)
                    print(f"New file detected: {post_file}")
        
        print(f"Pre-processing files: {len(pre_files)}")
        print(f"Post-processing files: {len(post_files)}")
        print(f"New files detected: {len(new_files)}")
        
        # Display new files in output listbox (simulated)
        print("\n--- Output listbox simulation ---")
        if new_files:
            for file_path in sorted(new_files):
                # Display just the filename instead of full path
                filename = os.path.basename(file_path)
                print(f"Listbox item: {filename}")
        else:
            print("Listbox item: No new files created")
        
        # Test what happens if we don't use basename
        print("\n--- Full path simulation (current issue) ---")
        if new_files:
            for file_path in sorted(new_files):
                # This is what's currently happening (showing full path)
                print(f"Listbox item: {file_path}")
        else:
            print("Listbox item: No new files created")

if __name__ == "__main__":
    test_gui_output_logic()