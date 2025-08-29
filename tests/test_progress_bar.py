#!/usr/bin/env python3
"""
Test script to verify progress bar updates in the GUI
"""

import sys
import os
sys.path.insert(0, 'src')

from infini_converter.gui import InfiniConverterGUI
from infini_converter.processor import FileProcessor
from infini_converter.config import Config
import tkinter as tk
from tkinter import ttk
import threading
import time

def test_progress_bar():
    """Test progress bar updates in the GUI"""
    print("Testing progress bar updates...")
    
    # Create test files
    test_dir = '/tmp/test_gui_progress'
    os.makedirs(test_dir, exist_ok=True)
    test_files = []
    for i in range(3):
        test_file = os.path.join(test_dir, f'test{i}.txt')
        with open(test_file, 'w') as f:
            f.write(f'Test content {i}')
        test_files.append(test_file)
    
    # Create root window
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    # Create GUI instance
    config = Config()
    config.set_processing_program('/bin/echo')
    config.set_output_directory('/tmp')
    
    gui = InfiniConverterGUI(root)
    
    # Set up test data
    gui.selected_files = test_files
    gui.processor.total_files = len(test_files)
    gui.processor.processed_count = 0
    gui.processor.failed_count = 0
    gui.processor.is_processing = True
    gui.processor.current_file = test_files[0]
    
    # Test progress bar updates
    def simulate_processing():
        print("Starting simulated processing...")
        for i in range(len(test_files)):
            gui.processor.current_file = test_files[i]
            gui.processor.processed_count = i + 1
            
            # Get current progress
            status = gui.processor.get_processing_status()
            progress = (status['processed_count'] + status['failed_count']) / status['total_count'] * 100
            
            print(f"Progress: {progress:.1f}% - File: {os.path.basename(status['current_file'])}")
            
            # Update GUI
            gui.progress_var.set(progress)
            gui.status_var.set(f"Processing: {os.path.basename(status['current_file'])} ({status['processed_count']}/{status['total_count']})")
            root.update_idletasks()
            
            time.sleep(1)  # Simulate processing time
        
        gui.processor.is_processing = False
        print("Processing completed!")
        root.quit()
    
    # Start simulation in separate thread
    sim_thread = threading.Thread(target=simulate_processing)
    sim_thread.daemon = True
    sim_thread.start()
    
    # Run GUI update loop
    def update_loop():
        if gui.processor.is_processing:
            status = gui.processor.get_processing_status()
            if status['total_count'] > 0:
                progress = (status['processed_count'] + status['failed_count']) / status['total_count'] * 100
                gui.progress_var.set(progress)
                gui.status_var.set(f"Processing: {os.path.basename(status['current_file'])} ({status['processed_count']}/{status['total_count']})")
                print(f"GUI Update: {progress:.1f}%")
            root.after(100, update_loop)
    
    update_loop()
    
    # Show the window briefly
    root.deiconify()
    root.geometry("400x200")
    root.title("Progress Bar Test")
    
    # Add progress bar to window
    progress_bar = ttk.Progressbar(root, variable=gui.progress_var, maximum=100)
    progress_bar.pack(pady=20, padx=20, fill=tk.X)
    
    status_label = ttk.Label(root, textvariable=gui.status_var)
    status_label.pack(pady=10)
    
    # Run for 5 seconds then quit
    root.after(5000, root.quit)
    root.mainloop()
    
    print("Progress bar test completed!")

if __name__ == "__main__":
    test_progress_bar()