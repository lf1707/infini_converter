#!/usr/bin/env python3
"""
Test script to debug the output files detection logic
"""

import os
import tempfile
import shutil
from src.infini_converter.config import Config
from src.infini_converter.file_discovery import FileDiscovery
from src.infini_converter.processor import FileProcessor

def test_output_files_detection():
    """Test the output files detection logic"""
    
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
        
        # Initialize processor
        processor = FileProcessor(
            processing_program="echo",  # Simple command that creates output
            output_directory=output_dir,
            command_template="echo 'processed {input}' > {output_dir}/{input}_processed"
        )
        
        # Store pre-processing files
        pre_files = []
        if os.path.exists(output_dir):
            try:
                pre_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) 
                             if os.path.isfile(os.path.join(output_dir, f))]
                print(f"Pre-processing files: {len(pre_files)}")
                for f in pre_files:
                    print(f"  - {os.path.basename(f)}")
            except Exception as e:
                print(f"Error reading output directory: {e}")
        
        # Store pre-processing files for comparison
        pre_basenames = {os.path.basename(f) for f in pre_files}
        
        # Process files
        results = []
        for input_file in test_files:
            input_path = os.path.join(input_dir, input_file)
            # Simple echo command that creates processed files
            result = processor.process_file(input_path)
            results.append(result)
            print(f"Processed {input_file}: {result['success']}")
        
        # Collect post-processing files
        post_files = []
        if os.path.exists(output_dir):
            try:
                post_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) 
                             if os.path.isfile(os.path.join(output_dir, f))]
                print(f"Post-processing files: {len(post_files)}")
                for f in post_files:
                    print(f"  - {os.path.basename(f)}")
            except Exception as e:
                print(f"Error reading output directory: {e}")
        
        # Find new files using the same logic as the GUI
        new_files = []
        if pre_basenames and post_files:
            for post_file in post_files:
                post_basename = os.path.basename(post_file)
                if post_basename not in pre_basenames:
                    new_files.append(post_file)
                    print(f"New file detected: {post_basename}")
        
        print(f"New files detected: {len(new_files)}")
        for f in new_files:
            print(f"  - {os.path.basename(f)}")
        
        # Test with a more robust approach
        print("\n--- Alternative approach ---")
        post_basenames = {os.path.basename(f) for f in post_files}
        new_files_alt = []
        for post_basename in post_basenames:
            if post_basename not in pre_basenames:
                # Find the full path for this basename
                for post_file in post_files:
                    if os.path.basename(post_file) == post_basename:
                        new_files_alt.append(post_basename)
                        break
        
        print(f"New files (alt approach): {len(new_files_alt)}")
        for f in new_files_alt:
            print(f"  - {f}")

if __name__ == "__main__":
    test_output_files_detection()