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
    
    # Set window size and position
    root.geometry("800x700")
    root.minsize(600, 500)
    
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