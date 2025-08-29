#!/usr/bin/env python3
"""
Test the complete GUI workflow for output files detection
"""

import os
import tempfile
import shutil
from src.infini_converter.config import Config
from src.infini_converter.file_discovery import FileDiscovery
from src.infini_converter.processor import FileProcessor

def test_complete_gui_workflow():
    """Test the complete GUI workflow"""
    
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
        
        # Initialize processor with no command template (like the fixed config)
        processor = FileProcessor(
            processing_program="echo",
            output_directory=output_dir,
            command_template=""
        )
        
        # Simulate the GUI process_files method logic
        print("\n--- Simulating GUI process_files method ---")
        
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
        
        # Process all files (like GUI does)
        print(f"\n--- Processing {len(test_files)} files ---")
        for i, input_file in enumerate(test_files):
            input_path = os.path.join(input_dir, input_file)
            print(f"Processing {input_file}...")
            
            # Process the file
            result = processor.process_file(input_path)
            print(f"  Result: {result['success']}")
            print(f"  Output file: {result['output_file']}")
            print(f"  Output exists: {result['output_exists']}")
            
            # Check if output files were created after each file
            post_files = []
            if os.path.exists(output_dir):
                post_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) 
                             if os.path.isfile(os.path.join(output_dir, f))]
            
            print(f"  Total files after processing: {len(post_files)}")
        
        # Now simulate the GUI processing_complete method logic
        print(f"\n--- Simulating GUI processing_complete method ---")
        
        # Collect post-processing files list
        post_files = []
        if output_dir and output_dir != output_placeholder_text and os.path.exists(output_dir):
            try:
                post_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) 
                             if os.path.isfile(os.path.join(output_dir, f))]
                print(f"Found {len(post_files)} files in output directory after processing")
                for f in post_files:
                    print(f"  - {os.path.basename(f)}")
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
                    print(f"New file detected: {post_basename}")
        
        print(f"\n--- Results ---")
        print(f"Pre-processing files: {len(pre_files)}")
        print(f"Post-processing files: {len(post_files)}")
        print(f"New files detected: {len(new_files)}")
        
        # Display new files in output listbox (GUI simulation)
        print(f"\n--- Output listbox content ---")
        if new_files:
            for file_path in sorted(new_files):
                # Display just the filename instead of full path
                filename = os.path.basename(file_path)
                print(f"Listbox item: {filename}")
            print(f"✓ Output listbox contains {len(new_files)} files")
        else:
            print("Listbox item: No new files created")
        
        # Test the actual GUI output listbox display logic
        print(f"\n--- GUI Output Listbox Simulation ---")
        
        # This is the actual code from the GUI processing_complete method
        # (starting from line 866 in gui.py)
        output_listbox_items = []
        if new_files:
            for file_path in sorted(new_files):
                # The original code was using file_path directly (full path)
                # output_listbox_items.append(file_path)  # This was the issue!
                
                # Fixed code should use basename
                filename = os.path.basename(file_path)
                output_listbox_items.append(filename)
        else:
            output_listbox_items.append("No new files created")
        
        print("Output listbox contents:")
        for item in output_listbox_items:
            print(f"  - {item}")

if __name__ == "__main__":
    test_complete_gui_workflow()