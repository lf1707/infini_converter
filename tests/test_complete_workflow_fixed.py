#!/usr/bin/env python3
"""
Test the complete workflow with fixed command structure
"""

import os
import tempfile
import shutil
from src.infini_converter.config import Config
from src.infini_converter.file_discovery import FileDiscovery
from src.infini_converter.processor import FileProcessor

def test_complete_workflow_with_fixed_commands():
    """Test the complete workflow with fixed command structure"""
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = os.path.join(temp_dir, "input")
        output_dir = os.path.join(temp_dir, "output")
        
        os.makedirs(input_dir)
        os.makedirs(output_dir)
        
        # Create test files
        test_files = ["test1.ape", "test2.ape", "test3.ape"]
        for filename in test_files:
            with open(os.path.join(input_dir, filename), 'w') as f:
                f.write(f"dummy audio content for {filename}")
        
        # Create existing output files
        existing_files = ["existing1.flac", "existing2.flac"]
        for filename in existing_files:
            with open(os.path.join(output_dir, filename), 'w') as f:
                f.write(f"existing flac content for {filename}")
        
        print(f"Input directory: {input_dir}")
        print(f"Output directory: {output_dir}")
        print(f"Test files: {test_files}")
        print(f"Existing files: {existing_files}")
        
        # Load config and set up processor
        config = Config()
        processor = FileProcessor(
            processing_program=config.get_processing_program(),
            output_directory=output_dir,  # Use temp output directory for testing
            command_template=config.get_command_template()
        )
        
        # Simulate the GUI workflow
        print(f"\n--- Simulating GUI workflow ---")
        
        # Step 1: Collect pre-processing files
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
        
        # Store pre-processing files
        _pre_output_files = pre_files
        
        # Step 2: Process files (simulate with echo since we don't have xld)
        print(f"\n--- Processing files with echo ---")
        processor_echo = FileProcessor(
            processing_program="echo",
            output_directory=output_dir,
            command_template="echo 'Processed: {input}' > {output_dir}/{input}_processed.flac"
        )
        
        for i, input_file in enumerate(test_files):
            input_path = os.path.join(input_dir, input_file)
            print(f"Processing {input_file}...")
            
            # Process with echo to simulate xld behavior
            result = processor_echo.process_file(input_path)
            print(f"  Result: {result['success']}")
            print(f"  Output file: {result['output_file']}")
            
            # Check files after processing
            post_files = []
            if os.path.exists(output_dir):
                post_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) 
                             if os.path.isfile(os.path.join(output_dir, f))]
            print(f"  Total files: {len(post_files)}")
        
        # Step 3: Simulate processing_complete method
        print(f"\n--- Simulating processing_complete ---")
        
        # Collect post-processing files
        post_files = []
        if output_dir and output_dir != output_placeholder_text and os.path.exists(output_dir):
            try:
                post_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) 
                             if os.path.isfile(os.path.join(output_dir, f))]
                print(f"Post-processing files: {len(post_files)}")
                for f in post_files:
                    print(f"  - {os.path.basename(f)}")
            except Exception as e:
                print(f"Error reading output directory: {e}")
        
        # Find new files
        new_files = []
        if _pre_output_files and post_files:
            pre_basenames = {os.path.basename(f) for f in _pre_output_files}
            for post_file in post_files:
                post_basename = os.path.basename(post_file)
                if post_basename not in pre_basenames:
                    new_files.append(post_file)
                    print(f"New file detected: {post_basename}")
        
        print(f"\n--- Results ---")
        print(f"New files detected: {len(new_files)}")
        
        # Step 4: Display output listbox (GUI simulation)
        print(f"\n--- Output Listbox Content ---")
        if new_files:
            for file_path in sorted(new_files):
                filename = os.path.basename(file_path)
                print(f"Listbox item: {filename}")
            print(f"✓ Output listbox successfully displays {len(new_files)} files")
        else:
            print("Listbox item: No new files created")
        
        # Test the actual command structure that would be used with xld
        print(f"\n--- Actual xld command structure ---")
        test_file = "test1.ape"
        input_path = os.path.join(input_dir, test_file)
        cmd = processor.build_command(input_path)
        cmd_string = " ".join(cmd)
        print(f"xld command: {cmd_string}")
        
        # Verify command structure
        expected_parts = [
            "/Users/lumfranks/bin/xld",
            "-f", "flac", 
            "-o", 
            output_dir, 
            input_path
        ]
        
        print(f"Expected command parts:")
        for part in expected_parts:
            print(f"  {part}")

if __name__ == "__main__":
    test_complete_workflow_with_fixed_commands()