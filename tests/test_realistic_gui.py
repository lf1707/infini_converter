#!/usr/bin/env python3
"""
Test the actual GUI logic with realistic setup
"""

import os
import tempfile
import shutil
from src.infini_converter.config import Config
from src.infini_converter.file_discovery import FileDiscovery
from src.infini_converter.processor import FileProcessor

def test_realistic_gui_processing():
    """Test with realistic GUI setup"""
    
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
        
        # Initialize processor with realistic GUI settings
        processor = FileProcessor(
            processing_program="echo",
            output_directory=output_dir,
            command_template='{program} -f flac -o {output_dir} {input}'
        )
        
        # Store pre-processing files (like GUI does)
        output_placeholder_text = "Select or enter output directory path"
        pre_files = []
        if output_dir and output_dir != output_placeholder_text and os.path.exists(output_dir):
            try:
                pre_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) 
                             if os.path.isfile(os.path.join(output_dir, f))]
                print(f"Pre-processing files: {len(pre_files)}")
                for f in pre_files:
                    print(f"  - {os.path.basename(f)}")
            except Exception as e:
                print(f"Error reading output directory: {e}")
        
        # Store pre-processing files for comparison later
        _pre_output_files = pre_files
        
        # Process files using the GUI's process_files method logic
        for input_file in test_files:
            input_path = os.path.join(input_dir, input_file)
            
            print(f"\nProcessing {input_file}...")
            
            # Build command using the processor's logic
            cmd = processor.build_command(input_path)
            cmd_string = " ".join(cmd)
            print(f"Command: {cmd_string}")
            
            # Execute the command
            import subprocess
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                print(f"Return code: {result.returncode}")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                
                # Check if output files were created
                post_files = []
                if os.path.exists(output_dir):
                    post_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) 
                                 if os.path.isfile(os.path.join(output_dir, f))]
                
                print(f"Files after processing {input_file}: {len(post_files)}")
                for f in post_files:
                    print(f"  - {os.path.basename(f)}")
                
            except Exception as e:
                print(f"Error processing {input_file}: {e}")
        
        # Now check the final state
        post_files = []
        if os.path.exists(output_dir):
            try:
                post_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) 
                             if os.path.isfile(os.path.join(output_dir, f))]
                print(f"\nFinal post-processing files: {len(post_files)}")
                for f in post_files:
                    print(f"  - {os.path.basename(f)}")
            except Exception as e:
                print(f"Error reading output directory: {e}")
        
        # Find new files using the GUI logic
        new_files = []
        if _pre_output_files and post_files:
            pre_basenames = {os.path.basename(f) for f in _pre_output_files}
            for post_file in post_files:
                post_basename = os.path.basename(post_file)
                if post_basename not in pre_basenames:
                    new_files.append(post_file)
                    print(f"New file detected: {post_basename}")
        
        print(f"\nNew files detected: {len(new_files)}")
        for f in new_files:
            print(f"  - {os.path.basename(f)}")
        
        # Test with a proper command template that actually creates files
        print("\n--- Testing with a proper command template ---")
        
        # Use a command that actually creates output files
        processor2 = FileProcessor(
            processing_program="echo",
            output_directory=output_dir,
            command_template='echo "processed {input}" > {output_dir}/{input}_processed.txt'
        )
        
        # Process one file with the new template
        input_path = os.path.join(input_dir, "test1.txt")
        cmd = processor2.build_command(input_path)
        cmd_string = " ".join(cmd)
        print(f"New command: {cmd_string}")
        
        import subprocess
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            print(f"Return code: {result.returncode}")
            
            # Check if output files were created
            post_files = []
            if os.path.exists(output_dir):
                post_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) 
                             if os.path.isfile(os.path.join(output_dir, f))]
            
            print(f"Files after processing with new template: {len(post_files)}")
            for f in post_files:
                print(f"  - {os.path.basename(f)}")
                
        except Exception as e:
            print(f"Error with new template: {e}")

if __name__ == "__main__":
    test_realistic_gui_processing()