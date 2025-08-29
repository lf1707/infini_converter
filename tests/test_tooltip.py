#!/usr/bin/env python3
"""
Test script to verify command template tooltip behavior
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from infini_converter.gui import InfiniConverterGUI

def test_tooltip_behavior():
    """Test the command template tooltip behavior"""
    root = tk.Tk()
    root.title("Command Template Tooltip Test")
    root.geometry("400x200")
    
    # Create a simplified version for testing
    command_template = tk.StringVar(value="")
    
    # Frame
    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # Command Template Section
    ttk.Label(main_frame, text="Command Template:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
    
    # Add tooltip for command template
    tooltip_text = "Use placeholders: {program}, {input}, {output_dir}"
    template_tooltip = ttk.Label(main_frame, text=tooltip_text, font=("Arial", 8), foreground="gray")
    template_tooltip.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(0, 5))
    
    template_entry = ttk.Entry(main_frame, textvariable=command_template, width=50)
    template_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
    
    # Hide tooltip initially if command template is not empty
    if command_template.get().strip():
        template_tooltip.grid_forget()
    
    # Add callback to show/hide tooltip based on input
    def on_command_template_change(*args):
        if command_template.get().strip():
            template_tooltip.grid_forget()
        else:
            template_tooltip.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(0, 5))
    
    # Use trace_add instead of trace
    command_template.trace_add('write', on_command_template_change)
    
    # Add test buttons
    test_frame = ttk.Frame(main_frame)
    test_frame.grid(row=1, column=0, columnspan=2, pady=10)
    
    def test_clear():
        command_template.set("")
        print("Cleared command template - tooltip should appear")
    
    def test_set():
        command_template.set("python {input} -o {output}")
        print("Set command template - tooltip should disappear")
    
    ttk.Button(test_frame, text="Clear Template", command=test_clear).pack(side=tk.LEFT, padx=5)
    ttk.Button(test_frame, text="Set Template", command=test_set).pack(side=tk.LEFT, padx=5)
    
    # Status label
    status_label = ttk.Label(main_frame, text="Status: Tooltip should be visible initially")
    status_label.grid(row=2, column=0, columnspan=2, pady=5)
    
    def update_status(*args):
        if command_template.get().strip():
            status_label.config(text="Status: Template set - tooltip hidden")
        else:
            status_label.config(text="Status: Template empty - tooltip visible")
    
    command_template.trace_add('write', update_status)
    
    print("Test started:")
    print("- Initially, tooltip should be visible (empty field)")
    print("- Click 'Set Template' to hide tooltip")
    print("- Click 'Clear Template' to show tooltip")
    print("- Type in the field to automatically hide tooltip")
    print("- Clear the field to automatically show tooltip")
    
    root.mainloop()

if __name__ == "__main__":
    test_tooltip_behavior()