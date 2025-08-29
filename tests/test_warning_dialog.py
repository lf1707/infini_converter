#!/usr/bin/env python3
"""
Test the resized warning dialog
"""

import tkinter as tk
from tkinter import ttk, scrolledtext

def test_resized_warning_dialog():
    """Test the resized warning dialog dimensions"""
    
    root = tk.Tk()
    root.title("Test Warning Dialog")
    root.geometry("800x600")
    
    def show_warning_dialog():
        """Show a warning dialog similar to the actual GUI"""
        warning_dialog = tk.Toplevel(root)
        warning_dialog.title("Warning - Files Will Be Deleted")
        warning_dialog.geometry("700x350")  # Enlarged size
        warning_dialog.transient(root)
        warning_dialog.grab_set()
        
        # Center the dialog
        warning_dialog.update_idletasks()
        x = (warning_dialog.winfo_screenwidth() // 2) - (warning_dialog.winfo_width() // 2)
        y = (warning_dialog.winfo_screenheight() // 2) - (warning_dialog.winfo_height() // 2)
        warning_dialog.geometry(f"+{x}+{y}")
        
        # Warning message
        ttk.Label(warning_dialog, text="⚠️ WARNING: Files Will Be Deleted", 
                 font=("Arial", 12, "bold"), foreground="red").pack(pady=10)
        
        ttk.Label(warning_dialog, text="The following files will be PERMANENTLY DELETED after successful processing:", 
                 font=("Arial", 10)).pack(pady=5)
        
        # File list
        file_list_text = scrolledtext.ScrolledText(warning_dialog, height=6, width=80, wrap=tk.WORD)
        file_list_text.pack(pady=10, padx=20)
        test_files = [
            "/Volumes/H264/file1.ape",
            "/Volumes/H264/file2.ape", 
            "/Volumes/H264/long_file_name_that_might_wrap_around_the_screen.ape"
        ]
        for i, file_path in enumerate(test_files):
            file_list_text.insert(tk.END, f"{i+1}. {file_path}\n")
        file_list_text.config(state=tk.DISABLED)
        
        # Command display
        ttk.Label(warning_dialog, text="Command to be executed:", font=("Arial", 10, "bold")).pack(pady=5)
        
        command_text = scrolledtext.ScrolledText(warning_dialog, height=4, width=80, wrap=tk.WORD)
        command_text.pack(pady=5, padx=20)
        command_string = "/Users/lumfranks/bin/xld -f flac -o /output/directory /input/file.ape"
        command_text.insert(tk.END, command_string)
        command_text.config(state=tk.DISABLED)
        
        # Buttons
        button_frame = ttk.Frame(warning_dialog)
        button_frame.pack(pady=15)  # Increased padding
        
        def execute_action():
            print("Execute clicked!")
            warning_dialog.destroy()
        
        def cancel_action():
            print("Cancel clicked!")
            warning_dialog.destroy()
        
        ttk.Button(button_frame, text="Execute", command=execute_action).pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Button(button_frame, text="Cancel", command=cancel_action).pack(side=tk.LEFT, padx=10, pady=5)
    
    # Test button
    test_button = ttk.Button(root, text="Show Warning Dialog", command=show_warning_dialog)
    test_button.pack(pady=20)
    
    # Size info
    info_label = ttk.Label(root, text="Warning dialog size: 700x350\nText areas: width 80\nButton padding: padx=10, pady=5")
    info_label.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    test_resized_warning_dialog()