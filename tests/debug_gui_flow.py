#!/usr/bin/env python3
"""
Debug the actual GUI flow with the current config
"""

import os
import sys
sys.path.insert(0, 'src')

from infini_converter.config import Config
from infini_converter.processor import FileProcessor

def debug_gui_flow():
    """Debug the actual GUI flow with current config"""
    
    # Load the current config
    config = Config()
    
    print("=== Current Config ===")
    print(f"Input directory: {config.get_input_directory()}")
    print(f"Output directory: {config.get_output_directory()}")
    print(f"Processing program: {config.get_processing_program()}")
    print(f"Command template: {config.get_command_template()}")
    
    # Check if directories exist
    input_dir = config.get_input_directory()
    output_dir = config.get_output_directory()
    
    print(f"\n=== Directory Status ===")
    print(f"Input directory exists: {os.path.exists(input_dir)}")
    print(f"Output directory exists: {os.path.exists(output_dir)}")
    
    if not os.path.exists(input_dir):
        print(f"❌ Input directory does not exist: {input_dir}")
        print("This might be why no files are being processed!")
        return
    
    # Check what files exist in input directory
    print(f"\n=== Input Directory Contents ===")
    try:
        input_files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        print(f"Found {len(input_files)} files:")
        for f in input_files:
            print(f"  - {f}")
    except Exception as e:
        print(f"Error reading input directory: {e}")
    
    # Check what files exist in output directory
    print(f"\n=== Output Directory Contents ===")
    try:
        output_files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
        print(f"Found {len(output_files)} files:")
        for f in output_files:
            print(f"  - {f}")
    except Exception as e:
        print(f"Error reading output directory: {e}")
    
    # Test the processor with current config
    print(f"\n=== Testing Processor ===")
    
    processor = FileProcessor(
        processing_program=config.get_processing_program(),
        output_directory=output_dir,
        command_template=config.get_command_template()
    )
    
    # Test with the first input file
    if input_files:
        test_file = os.path.join(input_dir, input_files[0])
        print(f"Testing with file: {test_file}")
        
        # Build command to see what it would look like
        cmd = processor.build_command(test_file)
        cmd_string = " ".join(cmd)
        print(f"Command: {cmd_string}")
        
        # Check if the processing program exists
        if not os.path.exists(config.get_processing_program()):
            print(f"❌ Processing program does not exist: {config.get_processing_program()}")
            print("This might be causing the processing to fail silently!")
            return
        
        # Try to process the file
        try:
            result = processor.process_file(test_file)
            print(f"Processing result:")
            print(f"  Success: {result['success']}")
            print(f"  Output file: {result.get('output_file', 'N/A')}")
            print(f"  Output exists: {result.get('output_exists', False)}")
            print(f"  Error: {result.get('error', 'None')}")
            
            # Check output directory after processing
            print(f"\nOutput directory after processing:")
            try:
                post_files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
                print(f"Found {len(post_files)} files:")
                for f in post_files:
                    print(f"  - {f}")
                    
                # Check for new files
                if len(post_files) > len(output_files):
                    print(f"✅ New files detected: {len(post_files) - len(output_files)} new files")
                else:
                    print(f"❌ No new files detected")
                    
            except Exception as e:
                print(f"Error reading output directory: {e}")
                
        except Exception as e:
            print(f"❌ Error processing file: {e}")
    
    # Test the GUI logic
    print(f"\n=== Testing GUI Output File Detection Logic ===")
    
    # Simulate the GUI processing_complete method
    output_placeholder_text = "Select or enter output directory path"
    
    # Collect pre-processing files
    pre_files = []
    if output_dir and output_dir != output_placeholder_text and os.path.exists(output_dir):
        try:
            pre_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) 
                         if os.path.isfile(os.path.join(output_dir, f))]
            print(f"Pre-processing files: {len(pre_files)}")
        except Exception as e:
            print(f"Error collecting pre-processing files: {e}")
    
    # Simulate processing
    print("\nSimulating processing...")
    # (In real GUI, this would happen during actual processing)
    
    # Collect post-processing files
    post_files = []
    if output_dir and output_dir != output_placeholder_text and os.path.exists(output_dir):
        try:
            post_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) 
                         if os.path.isfile(os.path.join(output_dir, f))]
            print(f"Post-processing files: {len(post_files)}")
        except Exception as e:
            print(f"Error collecting post-processing files: {e}")
    
    # Find new files
    new_files = []
    if pre_files and post_files:
        pre_basenames = {os.path.basename(f) for f in pre_files}
        for post_file in post_files:
            post_basename = os.path.basename(post_file)
            if post_basename not in pre_basenames:
                new_files.append(post_file)
                print(f"New file detected: {post_basename}")
    
    print(f"\n=== GUI Output Listbox Simulation ===")
    if new_files:
        for file_path in sorted(new_files):
            filename = os.path.basename(file_path)
            print(f"Listbox item: {filename}")
        print(f"✅ Output listbox would contain {len(new_files)} files")
    else:
        print("Listbox item: No new files created")
        print("❌ This might be the issue - no new files are being detected!")

if __name__ == "__main__":
    debug_gui_flow()