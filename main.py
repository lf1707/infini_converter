"""
Main entry point for Infini Converter
"""

import tkinter as tk
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from infini_converter.gui import InfiniConverterGUI

def main():
    """Main entry point for the application."""
    root = tk.Tk()
    
    # Calculate display scaling for 2K displays
    screen_width = root.winfo_screenwidth()
    scale_factor = 1.4 if screen_width >= 2560 else 1.2 if screen_width >= 1920 else 1.0
    
    # Set window size and position with scaling
    base_width = int(800 * scale_factor)
    base_height = int(700 * scale_factor)
    min_width = int(600 * scale_factor)
    min_height = int(500 * scale_factor)
    
    root.geometry(f"{base_width}x{base_height}")
    root.minsize(min_width, min_height)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # Create the application
    app = InfiniConverterGUI(root)
    
    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main()