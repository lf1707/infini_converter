"""
GUI application for Infini Converter
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import os
import subprocess
import sys
import threading
import time
import json
from typing import List, Optional

from infini_converter.config import Config
from infini_converter.logger import Logger
from infini_converter.file_discovery import FileDiscovery
from infini_converter.processor import FileProcessor

class StdoutRedirector:
    """Redirect stdout to GUI log"""
    def __init__(self, gui_instance):
        self.gui = gui_instance
        self.original_stdout = sys.stdout
    
    def write(self, text):
        # Write to original stdout
        self.original_stdout.write(text)
        
        # Write to GUI log if it contains useful information
        if text.strip():
            self.gui.log_message(f"[PROCESS] {text.strip()}")
    
    def flush(self):
        self.original_stdout.flush()

class InfiniConverterGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Infini Converter")
        
        # Initialize components
        self.config = Config()
        self.logger = Logger(self.config.get_log_file(), self.config.is_logging_enabled())
        self.file_discovery = FileDiscovery(self.config.get_file_extensions())
        self.processor = FileProcessor(
            self.config.get_processing_program(), 
            self.config.get_output_directory(),
            self.config.get_command_template(),
            self.config.get_env_vars()
        )
        
        # Redirect stdout to capture processor logs
        self.original_stdout = sys.stdout
        self.stdout_redirector = StdoutRedirector(self)
        sys.stdout = self.stdout_redirector
        
        # GUI variables
        # Get the directory where main.py is located as default input directory
        main_py_dir = os.path.dirname(os.path.abspath(__file__))
        main_py_dir = os.path.dirname(main_py_dir)  # Go up one level to the project directory
        
        # Use saved values if they exist, otherwise use defaults
        input_dir = self.config.get_input_directory()
        if not input_dir:
            input_dir = main_py_dir  # Use default if null
        
        output_dir = self.config.get_output_directory()
        if not output_dir:
            output_dir = input_dir  # Default output to input directory if not set
        
        self.input_directory = tk.StringVar(value=input_dir)
        self.output_directory = tk.StringVar(value=output_dir)
        self.processing_program = tk.StringVar(value=self.config.get_processing_program())
        self.command_template = tk.StringVar(value=self.config.get_command_template())
        self.env_vars = tk.StringVar(value=self.config.get_env_vars())
        self.file_extensions = tk.StringVar(value=", ".join(self.config.get_file_extensions()))
        self.logging_enabled = tk.BooleanVar(value=self.config.is_logging_enabled())
        self.log_radio_var = tk.BooleanVar(value=False)
        self.sync_side_by_side = tk.BooleanVar(value=False)
        self.del_origin_file = tk.BooleanVar(value=False)
        self.show_command_confirm = tk.BooleanVar(value=self.config.is_command_confirm_enabled())
        self.selected_files = []
        self.processing_thread = None
        
        self.setup_gui()
        self.load_initial_settings()
    
    def setup_gui(self):
        """Setup the main GUI layout."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Logo Section
        self.setup_logo(main_frame)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=0)  # Fixed width for buttons
        
        # Directory Selection Section
        ttk.Label(main_frame, text="Input Directory:", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky=tk.W, pady=8)
        
        input_entry = ttk.Entry(main_frame, textvariable=self.input_directory, font=("Arial", 11))
        input_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=8)
        
        # Set placeholder text for the input directory widget
        main_py_dir = os.path.dirname(os.path.abspath(__file__))
        main_py_dir = os.path.dirname(main_py_dir)  # Go up one level to the project directory
        input_placeholder_text = f"Default: {main_py_dir}"
        if not self.input_directory.get().strip():
            input_entry.insert(0, input_placeholder_text)
            input_entry.config(foreground="gray")
        
        # Add callback to handle placeholder text
        def on_input_focus_in(event):
            if input_entry.get() == input_placeholder_text:
                input_entry.delete(0, tk.END)
                input_entry.config(foreground="black")
        
        def on_input_focus_out(event):
            if not input_entry.get().strip():
                input_entry.insert(0, input_placeholder_text)
                input_entry.config(foreground="gray")
        
        def on_input_change(*args):
            current_text = self.input_directory.get()
            if current_text == input_placeholder_text:
                input_entry.config(foreground="gray")
            elif current_text.strip():
                input_entry.config(foreground="black")
            
            # Auto-save configuration when input directory changes
            if current_text and current_text != input_placeholder_text:
                self.config.set_input_directory(current_text)
                self.config.save_config()
        
        # Bind focus events
        input_entry.bind('<FocusIn>', on_input_focus_in)
        input_entry.bind('<FocusOut>', on_input_focus_out)
        
        # Use trace_add for variable changes
        self.input_directory.trace_add('write', on_input_change)
        
        ttk.Button(main_frame, text="📁", command=self.browse_input_directory, width=4).grid(row=1, column=2, pady=8)
        
        ttk.Label(main_frame, text="Output Directory:", font=("Arial", 11, "bold")).grid(row=2, column=0, sticky=tk.W, pady=8)
        
        # Output Directory and Same as Input Section
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=8)
        
        output_entry = ttk.Entry(output_frame, textvariable=self.output_directory, font=("Arial", 11))
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.sync_checkbox = ttk.Checkbutton(output_frame, text="Same as Input", variable=self.sync_side_by_side, 
                                            command=self.toggle_sync_side_by_side)
        self.sync_checkbox.pack(side=tk.LEFT)
        
        ttk.Button(main_frame, text="📁", command=self.browse_output_directory, width=4).grid(row=2, column=2, pady=8)
        
        # Set placeholder text for the output directory widget
        main_py_dir = os.path.dirname(os.path.abspath(__file__))
        main_py_dir = os.path.dirname(main_py_dir)  # Go up one level to the project directory
        output_placeholder_text = f"Default: {main_py_dir}"
        if not self.output_directory.get().strip():
            output_entry.insert(0, output_placeholder_text)
            output_entry.config(foreground="gray")
        
        # Add callback to handle placeholder text
        def on_output_focus_in(event):
            if output_entry.get() == output_placeholder_text:
                output_entry.delete(0, tk.END)
                output_entry.config(foreground="black")
        
        def on_output_focus_out(event):
            if not output_entry.get().strip():
                output_entry.insert(0, output_placeholder_text)
                output_entry.config(foreground="gray")
        
        def on_output_change(*args):
            current_text = self.output_directory.get()
            if current_text == output_placeholder_text:
                output_entry.config(foreground="gray")
            elif current_text.strip():
                output_entry.config(foreground="black")
            
            # Auto-save configuration when output directory changes
            if current_text and current_text != output_placeholder_text:
                self.config.set_output_directory(current_text)
                self.config.save_config()
        
        # Bind focus events
        output_entry.bind('<FocusIn>', on_output_focus_in)
        output_entry.bind('<FocusOut>', on_output_focus_out)
        
        # Use trace_add for variable changes
        self.output_directory.trace_add('write', on_output_change)
        
        # Processing Program Section
        ttk.Label(main_frame, text="Program:", font=("Arial", 11, "bold")).grid(row=3, column=0, sticky=tk.W, pady=8)
        
        # Program and Env Section
        program_frame = ttk.Frame(main_frame)
        program_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=8)
        
        ttk.Entry(program_frame, textvariable=self.processing_program, font=("Arial", 11)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Label(program_frame, text="Env:", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=(0, 2))
        env_entry = ttk.Entry(program_frame, textvariable=self.env_vars, width=15, font=("Arial", 11))
        env_entry.pack(side=tk.LEFT)
        
        # Set placeholder text for Env entry
        env_placeholder_text = "e.g., LC_ALL=C"
        if not self.env_vars.get().strip():
            env_entry.insert(0, env_placeholder_text)
            env_entry.config(foreground="gray")
        
        # Add callback to handle placeholder text
        def on_env_focus_in(event):
            if env_entry.get() == env_placeholder_text:
                env_entry.delete(0, tk.END)
                env_entry.config(foreground="black")
        
        def on_env_focus_out(event):
            if not env_entry.get().strip():
                env_entry.insert(0, env_placeholder_text)
                env_entry.config(foreground="gray")
                # Clear the actual env vars when placeholder is shown
                self.config.set_env_vars("")
            else:
                env_entry.config(foreground="black")
        
        def on_env_change(*args):
            current_text = self.env_vars.get()
            if current_text == env_placeholder_text:
                env_entry.config(foreground="gray")
            elif current_text.strip():
                env_entry.config(foreground="black")
            
            # Auto-save configuration when env vars changes
            if current_text and current_text != env_placeholder_text:
                self.config.set_env_vars(current_text)
                self.config.save_config()
                self.processor.set_env_vars(current_text)
        
        # Bind focus events
        env_entry.bind('<FocusIn>', on_env_focus_in)
        env_entry.bind('<FocusOut>', on_env_focus_out)
        
        # Use trace_add for variable changes
        self.env_vars.trace_add('write', on_env_change)
        
        ttk.Button(main_frame, text="📁", command=self.browse_processing_program, width=4).grid(row=3, column=2, pady=8)
        
        # Command Template Section
        ttk.Label(main_frame, text="CMD Template:", font=("Arial", 11, "bold")).grid(row=4, column=0, sticky=tk.W, pady=8)
        
        template_entry = ttk.Entry(main_frame, textvariable=self.command_template, font=("Arial", 11))
        template_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=8)
        
        ttk.Button(main_frame, text="📁", command=self.browse_command_template, width=4).grid(row=4, column=2, pady=8)
        
        # Set placeholder text for the entry widget
        placeholder_text = "Use placeholders: {env}, {program}, {input}, {output_dir}"
        if not self.command_template.get().strip():
            template_entry.insert(0, placeholder_text)
            template_entry.config(foreground="gray")
        
        # Add callback to handle placeholder text
        def on_command_template_focus_in(event):
            if template_entry.get() == placeholder_text:
                template_entry.delete(0, tk.END)
                template_entry.config(foreground="black")
        
        def on_command_template_focus_out(event):
            if not template_entry.get().strip():
                template_entry.insert(0, placeholder_text)
                template_entry.config(foreground="gray")
                # Clear the actual template in processor when placeholder is shown
                self.processor.set_command_template("")
        
        # Template validation will be handled inline to avoid scope issues
        
        def on_command_template_change(*args):
            current_text = self.command_template.get()
            if current_text == placeholder_text:
                template_entry.config(foreground="gray")
                # Clear the actual template in processor when placeholder is shown
                self.processor.set_command_template("")
                self.config.set_command_template("")
                self.config.save_config()
            elif current_text.strip():
                template_entry.config(foreground="black")
                # Update the processor template only when it's not placeholder text
                if self.is_valid_command_template(current_text):
                    self.processor.set_command_template(current_text)
                    self.config.set_command_template(current_text)
                    self.config.save_config()
                else:
                    self.processor.set_command_template("")
                    self.config.set_command_template("")
                    self.config.save_config()
        
        # Bind focus events
        template_entry.bind('<FocusIn>', on_command_template_focus_in)
        template_entry.bind('<FocusOut>', on_command_template_focus_out)
        
        # Use trace_add for variable changes
        self.command_template.trace_add('write', on_command_template_change)
        
        # File Extensions Section
        ttk.Label(main_frame, text="File Extensions:", font=("Arial", 11, "bold")).grid(row=6, column=0, sticky=tk.W, pady=8)
        ttk.Entry(main_frame, textvariable=self.file_extensions, width=50, font=("Arial", 11)).grid(row=6, column=1, sticky=(tk.W, tk.E), pady=8)
        ttk.Button(main_frame, text="🔍", command=self.find_files, width=4).grid(row=6, column=2, pady=8)
        
        # Add trace for file extensions auto-save
        def on_file_extensions_change(*args):
            extensions = [ext.strip() for ext in self.file_extensions.get().split(",") if ext.strip()]
            if extensions:
                self.config.set_file_extensions(extensions)
                self.config.save_config()
        
        self.file_extensions.trace_add('write', on_file_extensions_change)
        
        # Save and Options Frame
        save_options_frame = ttk.Frame(main_frame)
        save_options_frame.grid(row=7, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Save Button
        ttk.Button(save_options_frame, text="💾", command=self.save_settings, width=4).pack(side=tk.RIGHT, padx=5)
        
        # Load Saved Button
        ttk.Button(save_options_frame, text="📂", command=self.load_saved_settings, width=4).pack(side=tk.RIGHT, padx=5)
        
        # Show Command Confirm checkbox
        self.command_confirm_checkbox = ttk.Checkbutton(save_options_frame, text="CMD Show", variable=self.show_command_confirm)
        self.command_confirm_checkbox.pack(side=tk.RIGHT, padx=5)
        
        # Del Origin File checkbox
        self.del_origin_checkbox = ttk.Checkbutton(save_options_frame, text="Del Origin File", variable=self.del_origin_file)
        self.del_origin_checkbox.pack(side=tk.RIGHT, padx=5)
        
        # Add trace for command confirm auto-save
        def on_command_confirm_change(*args):
            self.config.set_command_confirm_enabled(self.show_command_confirm.get())
            self.config.save_config()
        
        def on_env_vars_change(*args):
            self.config.set_env_vars(self.env_vars.get())
            self.config.save_config()
        
        def on_del_origin_file_change(*args):
            self.config.set_del_origin_file_enabled(self.del_origin_file.get())
            self.config.save_config()
        
        self.show_command_confirm.trace_add('write', on_command_confirm_change)
        self.env_vars.trace_add('write', on_env_vars_change)
        self.del_origin_file.trace_add('write', on_del_origin_file_change)
        
        # Options Section
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # File Lists Section (Parallel Layout)
        lists_frame = ttk.Frame(main_frame)
        lists_frame.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Input Files Section (Left)
        input_frame = ttk.Frame(lists_frame)
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Label(input_frame, text="Input Files:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # Create frame for input file list and scrollbar
        input_list_frame = ttk.Frame(input_frame)
        input_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input file list with scrollbar and multi-selection enabled
        input_scrollbar = ttk.Scrollbar(input_list_frame)
        input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(input_list_frame, height=18, yscrollcommand=input_scrollbar.set, selectmode=tk.MULTIPLE)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        input_scrollbar.config(command=self.file_listbox.yview)
        
        # Bind double-click to open file
        self.file_listbox.bind('<Double-Button-1>', self.open_file)
        
        # Process buttons between frames (centered)
        button_frame = ttk.Frame(lists_frame)
        button_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)
        
        # Create a container to center buttons vertically
        button_container = ttk.Frame(button_frame)
        button_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        ttk.Button(button_container, text="▶", command=self.process_selected_files, width=4).pack(pady=2)
        ttk.Button(button_container, text="⏩", command=self.process_all_files, width=4).pack(pady=2)
        ttk.Button(button_container, text="■", command=self.stop_processing, width=4).pack(pady=2)
        ttk.Button(button_container, text="🗑️", command=self.clear_file_list, width=4).pack(pady=2)
        
        # Output Files Section (Right)
        output_frame = ttk.Frame(lists_frame)
        output_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Label(output_frame, text="Output Files:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # Create frame for output file list and scrollbar
        output_list_frame = ttk.Frame(output_frame)
        output_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Output file list with scrollbar
        output_scrollbar = ttk.Scrollbar(output_list_frame)
        output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.output_listbox = tk.Listbox(output_list_frame, height=18, yscrollcommand=output_scrollbar.set)
        self.output_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        output_scrollbar.config(command=self.output_listbox.yview)
        
                
                
        # Processing Controls
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Status Bar with Log checkbox
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=11, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create radio button style for Log button
        self.log_button = ttk.Radiobutton(status_frame, text="Log", command=self.toggle_log_combined, value="log")
        self.log_button.pack(side=tk.RIGHT, padx=5)
        
        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=11, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Configure main frame to expand
        main_frame.rowconfigure(8, weight=1)
        
        # Log Frame Section
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=12, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Log frame controls
        log_controls_frame = ttk.Frame(log_frame)
        log_controls_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Create frame for log text and scrollbar
        self.log_text_frame = ttk.Frame(log_frame)
        self.log_text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Log text with scrollbar
        log_scrollbar = ttk.Scrollbar(self.log_text_frame)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = scrolledtext.ScrolledText(self.log_text_frame, height=4, wrap=tk.WORD, yscrollcommand=log_scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.config(command=self.log_text.yview)
        
        # Hide log text frame initially
        self.log_text_frame.pack_forget()
        
        # Initialize log visibility state
        self.log_visible = False
        
        # Configure log frame to expand
        log_frame.rowconfigure(0, weight=1)
        
        # Update main frame row configuration
        main_frame.rowconfigure(12, weight=1)
    
    def setup_logo(self, parent):
        """Setup the logo section."""
        # Find the logo file path
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logo.png")
        
        # Create logo frame
        logo_frame = ttk.Frame(parent)
        logo_frame.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        try:
            # Load and resize logo
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((200, 60), Image.Resampling.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_image)
            
            # Create logo label
            logo_label = ttk.Label(logo_frame, image=logo_photo)
            logo_label.image = logo_photo  # Keep a reference to prevent garbage collection
            logo_label.pack()
            
        except Exception as e:
            # Fallback to text logo if image loading fails
            fallback_text = "∞ Infini Converter"
            logo_label = ttk.Label(logo_frame, text=fallback_text, 
                                 font=("Arial", 16, "bold"), foreground="blue")
            logo_label.pack()
            
            self.logger.warning(f"Could not load logo image: {e}")
            self.log_message(f"Using text logo instead of image")
    
    def browse_input_directory(self):
        """Browse for input directory."""
        directory = filedialog.askdirectory(title="Select Input Directory")
        if directory:
            old_input_dir = self.input_directory.get()
            # Check if old value was placeholder text
            input_placeholder_text = "Select or enter input directory path"
            if old_input_dir == input_placeholder_text:
                old_input_dir = ""
            
            self.input_directory.set(directory)
            
            # If output directory was the same as input directory (default), update it too
            if self.output_directory.get() == old_input_dir or self.output_directory.get() == "Select or enter output directory path":
                self.output_directory.set(directory)
                self.processor.set_output_directory(directory)
                self.logger.info(f"Output directory automatically updated to: {directory}")
                self.log_message(f"Output directory automatically updated to: {directory}")
            
            self.logger.info(f"Input directory set to: {directory}")
            self.log_message(f"Input directory set to: {directory}")
    
    def browse_output_directory(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_directory.set(directory)
            self.processor.set_output_directory(directory)
            self.logger.info(f"Output directory set to: {directory}")
            self.log_message(f"Output directory set to: {directory}")
    
    def browse_processing_program(self):
        """Browse for processing program."""
        program = filedialog.askopenfilename(
            title="Select Program",
            filetypes=[("Executable files", "*.exe *.bat *.sh *.py"), ("All files", "*.*")]
        )
        if program:
            self.processing_program.set(program)
            self.processor.set_processing_program(program)
            self.config.set_processing_program(program)
            self.config.save_config()
            self.logger.info(f"Processing program set to: {program}")
            self.log_message(f"Processing program set to: {program}")
    
    def browse_command_template(self):
        """Browse for command template file."""
        template_file = filedialog.askopenfilename(
            title="Select Command Template File",
            filetypes=[("Template files", "*.txt *.template *.cmd"), ("All files", "*.*")]
        )
        if template_file:
            try:
                with open(template_file, 'r') as f:
                    template_content = f.read().strip()
                self.command_template.set(template_content)
                self.config.set_command_template(template_content)
                self.config.save_config()
                self.logger.info(f"Command template loaded from: {template_file}")
                self.log_message(f"Command template loaded from: {template_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load template file: {e}")
                self.logger.error(f"Failed to load template file: {e}")
    
    def find_files(self):
        """Find files in the input directory."""
        input_dir = self.input_directory.get()
        # Check if input_dir is placeholder text
        input_placeholder_text = "Select or enter input directory path"
        if input_dir == input_placeholder_text or not input_dir or not os.path.exists(input_dir):
            messagebox.showerror("Error", "Please select a valid input directory.")
            return
        
        # Update file extensions
        extensions = [ext.strip() for ext in self.file_extensions.get().split(",") if ext.strip()]
        if extensions:
            self.file_discovery.set_extensions(extensions)
            self.config.set_file_extensions(extensions)
        
        # Find files
        files = self.file_discovery.find_files(input_dir)
        
        # Filter out problematic files
        filtered_files = self.file_discovery.filter_problematic_files(files)
        
        if len(filtered_files) != len(files):
            skipped_count = len(files) - len(filtered_files)
            self.log_message(f"Skipped {skipped_count} problematic files")
        
        # Normalize file paths to handle spaces
        normalized_files = []
        for file_path in filtered_files:
            normalized_path = self.processor.normalize_file_path(file_path)
            if normalized_path != file_path:
                self.log_message(f"Normalized file path: {file_path} -> {normalized_path}")
            normalized_files.append(normalized_path)
        
        self.selected_files = normalized_files
        
        # Update listbox
        self.file_listbox.delete(0, tk.END)
        for file_path in normalized_files:
            self.file_listbox.insert(tk.END, file_path)
        
        self.status_var.set(f"Found {len(filtered_files)} files (filtered from {len(files)})")
        self.logger.info(f"Found {len(filtered_files)} files in {input_dir} (filtered from {len(files)})")
        self.log_message(f"Found {len(filtered_files)} files in {input_dir} (filtered from {len(files)})")
    
    def process_selected_files(self):
        """Process selected files from the list."""
        selected_indices = self.file_listbox.curselection()
        selected_files = []
        
        # If no files selected in listbox, check if there's a file in the input box
        if not selected_indices:
            input_path = self.input_directory.get().strip()
            if input_path and os.path.exists(input_path):
                # If it's a file, add it to the list and select it
                if os.path.isfile(input_path):
                    self.selected_files = [input_path]
                    # Update listbox
                    self.file_listbox.delete(0, tk.END)
                    self.file_listbox.insert(tk.END, input_path)
                    # Select the file in the listbox
                    self.file_listbox.selection_set(0)
                    selected_indices = (0,)
                    selected_files = [input_path]
                    self.log_message(f"Automatically selected file from input box: {os.path.basename(input_path)}")
                # If it's a directory, find files in it
                elif os.path.isdir(input_path):
                    self.find_files()
                    # Select all found files
                    if self.selected_files:
                        self.file_listbox.selection_set(0, len(self.selected_files) - 1)
                        selected_indices = tuple(range(len(self.selected_files)))
                        selected_files = self.selected_files.copy()
                        self.log_message(f"Automatically selected {len(selected_files)} files from directory")
            
            # If still no files selected, show warning
            if not selected_indices:
                messagebox.showwarning("Warning", "Please select files to process or enter a file/directory path.")
                return
        else:
            selected_files = [self.selected_files[i] for i in selected_indices]
        
        # For sync side by side, pass both files and selected indices
        if self.sync_side_by_side.get():
            if not selected_files:
                messagebox.showwarning("Warning", "No files selected for processing.")
                return
            self._process_files_with_sync_side_by_side(selected_files, selected_indices)
        else:
            self.process_files(selected_files)
    
    def process_all_files(self):
        """Process all files in the list."""
        if not self.selected_files:
            # Check if there's a file/directory in the input box
            input_path = self.input_directory.get().strip()
            if input_path and os.path.exists(input_path):
                if os.path.isfile(input_path):
                    # Add the single file to the list
                    self.selected_files = [input_path]
                    # Update listbox
                    self.file_listbox.delete(0, tk.END)
                    self.file_listbox.insert(tk.END, input_path)
                    self.log_message(f"Automatically added file from input box: {os.path.basename(input_path)}")
                elif os.path.isdir(input_path):
                    # Find files in the directory
                    self.find_files()
                    if not self.selected_files:
                        messagebox.showwarning("Warning", "No files found in the specified directory.")
                        return
                    self.log_message(f"Automatically found {len(self.selected_files)} files from directory")
            else:
                messagebox.showwarning("Warning", "No files to process. Please enter a file/directory path or find files first.")
                return
        
        # Check if Same as Input is enabled
        if self.sync_side_by_side.get():
            # For sync side by side mode, use all files with their indices
            selected_indices = list(range(len(self.selected_files)))
            self._process_files_with_sync_side_by_side(self.selected_files, selected_indices)
        else:
            # For normal mode, use batch processing
            self.process_files(self.selected_files)
    
    def _process_files_with_sync_side_by_side(self, files: List[str], selected_indices: List[int]):
        """Process files individually with sync side by side (each file to its own directory)."""
        # Show confirmation dialog if either deletion warning or command confirmation is needed
        show_deletion = self.del_origin_file.get() and files
        show_command = self.show_command_confirm.get()
        
        if show_deletion or show_command:
            # Get actual file paths for confirmation
            actual_files = [self.selected_files[i] for i in selected_indices]
            
            # Determine dialog title and content
            if show_deletion and show_command:
                title = "Warning - Files Will Be Deleted"
                show_command_preview = True
            elif show_deletion:
                title = "Warning - Files Will Be Deleted"
                show_command_preview = False
            else:  # show_command only
                title = "Command Confirmation - Sync Side by Side"
                show_command_preview = True
            
            # Use specialized sync side by side confirmation dialog
            if not self.show_sync_side_by_side_confirmation_dialog(actual_files, title, 
                                                                  show_deletion_warning=show_deletion,
                                                                  show_command_preview=show_command_preview):
                self.status_var.set("Processing cancelled")
                self.log_message("Processing cancelled by user")
                return
        
        # Start processing
        self._start_sync_side_by_side_processing(files, selected_indices)
    
    def _start_sync_side_by_side_processing(self, files: List[str], selected_indices: List[int]):
        """Start the actual sync side by side processing after confirmation."""
        # Validate command template - show error instead of using default format
        template_text = self.command_template.get()
        if not self.is_valid_command_template(template_text):
            messagebox.showerror("Error", "Please enter a valid command template.\n\nUse placeholders like:\n{program} {input} {output_dir}\n\nDo not use the placeholder text as the actual template.")
            return
        
        # Process files one by one with individual output directories
        results = []
        total_files = len(selected_indices)
        
        # Initialize progress tracking
        self.processor.is_processing = True
        self.processor.processed_count = 0
        self.processor.failed_count = 0
        
        # Clear output listbox for sync side by side mode
        self.output_listbox.delete(0, tk.END)
        
        # Use the selected_indices to get the actual files from the original selected_files list
        for i, original_index in enumerate(selected_indices):
            if i >= len(files):
                break
                
            # Get the actual file path from the original selected_files list
            file_path = self.selected_files[original_index]
            file_output_dir = os.path.dirname(file_path)
            
            # Collect pre-processing files for this specific output directory
            pre_files = []
            if os.path.exists(file_output_dir):
                try:
                    pre_files = [os.path.join(file_output_dir, f) for f in os.listdir(file_output_dir) 
                                 if os.path.isfile(os.path.join(file_output_dir, f))]
                    print(f"Collected {len(pre_files)} pre-processing files from {file_output_dir}")
                except Exception as e:
                    print(f"Error reading output directory {file_output_dir}: {e}")
            
            # Update output directory for this specific file
            self.output_directory.set(file_output_dir)
            self.processor.set_output_directory(file_output_dir)
            
            self.logger.info(f"Processing {file_path} with output directory: {file_output_dir}")
            self.log_message(f"Processing {os.path.basename(file_path)} -> {file_output_dir}")
            
            # Update status and progress bar
            progress = (i / total_files) * 100
            self.progress_var.set(progress)
            self.status_var.set(f"Processing: {os.path.basename(file_path)} ({i+1}/{total_files})")
            self.root.update()
            self.root.update_idletasks()
            
            # Build command and process this single file
            self.processor.clear_results()
            self.processor.reset_stop_flag()
            self.processor.current_file = file_path
            
            try:
                # Show processing start for this file
                file_progress = ((i + 0.1) / total_files) * 100  # Start of file processing
                self.progress_var.set(file_progress)
                self.root.update()
                
                # Process the file synchronously for sync side by side mode
                result = self.processor.process_file(file_path)
                results.append(result)
                
                # Show completion for this file
                file_progress = ((i + 0.9) / total_files) * 100  # Near completion of file processing
                self.progress_var.set(file_progress)
                self.root.update()
                
                # Collect post-processing files for this specific output directory (BEFORE deleting original)
                post_files = []
                if os.path.exists(file_output_dir):
                    try:
                        post_files = [os.path.join(file_output_dir, f) for f in os.listdir(file_output_dir) 
                                     if os.path.isfile(os.path.join(file_output_dir, f))]
                        print(f"Found {len(post_files)} files in output directory after processing")
                    except Exception as e:
                        print(f"Error reading output directory {file_output_dir}: {e}")
                
                # Find new files for this specific file processing
                new_files_for_this_file = []
                if pre_files and post_files:
                    pre_basenames = {os.path.basename(f) for f in pre_files}
                    for post_file in post_files:
                        post_basename = os.path.basename(post_file)
                        if post_basename not in pre_basenames:
                            new_files_for_this_file.append(post_file)
                            print(f"New file detected for {os.path.basename(file_path)}: {post_file}")
                
                # Add new files to output listbox with full paths
                for new_file_path in sorted(new_files_for_this_file):
                    self.output_listbox.insert(tk.END, new_file_path)
                    print(f"Added new file to output list: {new_file_path}")
                
                if new_files_for_this_file:
                    self.log_message(f"Found {len(new_files_for_this_file)} new output files for {os.path.basename(file_path)}")
                
                # Update processed count
                if result["success"]:
                    self.processor.processed_count += 1
                    self.logger.info(f"Successfully processed: {file_path}")
                    self.log_message(f"✓ {os.path.basename(file_path)}")
                    
                    # Delete original file if checkbox is enabled and processing was successful
                    if self.del_origin_file.get():
                        try:
                            os.remove(file_path)
                            self.logger.info(f"Deleted original file: {file_path}")
                            self.log_message(f"🗑️ Deleted: {os.path.basename(file_path)}")
                        except Exception as e:
                            self.logger.error(f"Failed to delete {file_path}: {e}")
                            self.log_message(f"⚠️ Failed to delete {os.path.basename(file_path)}: {e}")
                else:
                    self.processor.failed_count += 1
                    self.logger.error(f"Failed to process: {file_path} - {result.get('error', 'Unknown error')}")
                    self.log_message(f"✗ {os.path.basename(file_path)} - {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                self.processor.failed_count += 1
                error_result = {"success": False, "file": file_path, "error": str(e)}
                results.append(error_result)
                self.logger.error(f"Exception processing {file_path}: {e}")
                self.log_message(f"✗ {os.path.basename(file_path)} - {e}")
        
        # Mark processing as complete
        self.processor.is_processing = False
        self.processor.current_file = ""
        
        # Final progress update
        self.progress_var.set(100)
        self.root.update_idletasks()
        
        # Show summary for sync side by side mode
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        self.status_var.set(f"Processing complete: {successful} successful, {failed} failed")
        self.logger.info(f"Processing complete: {successful} successful, {failed} failed")
        self.log_message(f"Processing complete: {successful} successful, {failed} failed")
    
    def process_files(self, files: List[str]):
        """Process files asynchronously (normal mode - all files to same output directory)."""
        if not self.processing_program.get():
            messagebox.showerror("Error", "Please select a processing program.")
            return
        
        # Normal mode - process all files with same output directory
        output_dir = self.output_directory.get()
        output_placeholder_text = "Select or enter output directory path"
        if not output_dir or output_dir == output_placeholder_text:
            messagebox.showerror("Error", "Please select an output directory.")
            return
        
        # Validate command template - show error instead of using default format
        template_text = self.command_template.get()
        if not self.is_valid_command_template(template_text):
            messagebox.showerror("Error", "Please enter a valid command template.\n\nUse placeholders like:\n{program} {input} {output_dir}\n\nDo not use the placeholder text as the actual template.")
            return
        
        # Update processor settings
        self.processor.set_processing_program(self.processing_program.get())
        self.processor.set_output_directory(output_dir)
        self.processor.set_command_template(template_text)
        self.processor.set_env_vars(self.env_vars.get())
        
        self.output_listbox.delete(0, tk.END)
        
        # Collect pre-processing files list
        output_dir = self.output_directory.get()
        output_placeholder_text = "Select or enter output directory path"
        pre_files = []
        if output_dir and output_dir != output_placeholder_text and os.path.exists(output_dir):
            try:
                pre_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) 
                             if os.path.isfile(os.path.join(output_dir, f))]
                print(f"Collected {len(pre_files)} pre-processing files from output directory")
            except Exception as e:
                print(f"Error reading output directory: {e}")
        
        # Store pre-processing files for comparison later
        self._pre_output_files = pre_files
        self._output_dir_for_comparison = output_dir  # Store the output directory path
        
        # Show confirmation dialog if either deletion warning or command confirmation is needed
        show_deletion = self.del_origin_file.get() and files
        show_command = self.show_command_confirm.get()
        
        if show_deletion or show_command:
            # Determine dialog title and content
            if show_deletion and show_command:
                title = "Warning - Files Will Be Deleted"
                show_command_preview = True
            elif show_deletion:
                title = "Warning - Files Will Be Deleted"
                show_command_preview = False
            else:  # show_command only
                title = "Command Confirmation"
                show_command_preview = True
            
            if not self.show_confirmation_dialog(files, title, 
                                               show_deletion_warning=show_deletion,
                                               show_command_preview=show_command_preview):
                self.status_var.set("Processing cancelled")
                self.log_message("Processing cancelled by user")
                return
        
        # Create progress callback for real-time updates
        def progress_callback(percentage, message):
            print(f"Real-time progress: {percentage:.1f}% - {message}")
            self.progress_var.set(percentage)
            self.status_var.set(f"Processing: {message}")
            self.root.update_idletasks()
        
        # Start processing in a separate thread
        self.processing_thread = self.processor.process_files_async(
            files,
            callback=self.processing_complete,
            progress_callback=progress_callback
        )
        
        # Start status update loop
        self.log_message("Started processing files...")
        self.update_processing_status()
    
    def update_processing_status(self):
        """Update processing status in the UI."""
        if self.processor.is_processing:
            status = self.processor.get_processing_status()
            total = status["total_count"]
            
            # Debug output
            print(f"GUI Status Update - Processing: {status['is_processing']}, Current: {status['current_file']}, Processed: {status['processed_count']}, Total: {total}")
            
            if total > 0:
                # Use subprocess progress if available, otherwise fall back to file count
                if "current_progress" in status and status["current_progress"] > 0:
                    progress = status["current_progress"]
                    print(f"Using subprocess progress: {progress:.1f}%")
                else:
                    progress = (status["processed_count"] + status["failed_count"]) / total * 100
                    print(f"Using file count progress: {progress:.1f}%")
                
                self.progress_var.set(progress)
                # Force GUI update
                self.root.update_idletasks()
                print(f"GUI Progress Bar Updated: {progress:.1f}%")
            
            self.status_var.set(f"Processing: {os.path.basename(status['current_file'])} ({status['processed_count']}/{total})")
            
            # Schedule next update
            self.root.after(200, self.update_processing_status)  # Increased interval to reduce CPU usage
        else:
            print("GUI Status Update - Processing is not active")
    
    def processing_complete(self, results: List[dict]):
        """Handle processing completion."""
        self.progress_var.set(100)
        
        # Collect post-processing files list BEFORE deleting original files
        output_dir = getattr(self, '_output_dir_for_comparison', self.output_directory.get())
        output_placeholder_text = "Select or enter output directory path"
        post_files = []
        
        if output_dir and output_dir != output_placeholder_text and os.path.exists(output_dir):
            try:
                post_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) 
                             if os.path.isfile(os.path.join(output_dir, f))]
                print(f"Found {len(post_files)} files in output directory after processing")
            except Exception as e:
                print(f"Error reading output directory: {e}")
        
        # Collect pre-processing files list (stored before starting processing)
        pre_files = getattr(self, '_pre_output_files', [])
        
        # Find new files (files in post_files but not in pre_files)
        new_files = []
        if pre_files and post_files:
            pre_basenames = {os.path.basename(f) for f in pre_files}
            for post_file in post_files:
                post_basename = os.path.basename(post_file)
                if post_basename not in pre_basenames:
                    new_files.append(post_file)
                    print(f"New file detected: {post_file}")
        
        print(f"Pre-processing files: {len(pre_files)}")
        print(f"Post-processing files: {len(post_files)}")
        print(f"New files detected: {len(new_files)}")
        
        # Display new files in output listbox with full paths
        self.output_listbox.delete(0, tk.END)
        if new_files:
            for file_path in sorted(new_files):
                # Display full path instead of just filename
                self.output_listbox.insert(tk.END, file_path)
                print(f"Added new file to output list: {file_path}")
            self.log_message(f"Found {len(new_files)} new output files")
        else:
            # Check if any processing occurred but failed
            if results:
                failed_count = len([r for r in results if not r.get("success", False)])
                if failed_count > 0:
                    self.output_listbox.insert(tk.END, f"Processing failed for {failed_count} files")
                    self.log_message(f"Processing failed for {failed_count} files - check logs for details")
                else:
                    self.output_listbox.insert(tk.END, "No new files created")
                    self.log_message("No new files were created by the processing")
            else:
                self.output_listbox.insert(tk.END, "No new files created")
                self.log_message("No new files were created by the processing")
        
        # Force GUI update
        self.root.update_idletasks()
        
        # Handle deletion of original files if enabled (AFTER collecting post-processing files)
        if self.del_origin_file.get():
            for result in results:
                if result.get("success") and result.get("file"):
                    file_path = result["file"]
                    try:
                        os.remove(file_path)
                        self.logger.info(f"Deleted original file: {file_path}")
                        self.log_message(f"🗑️ Deleted: {os.path.basename(file_path)}")
                    except Exception as e:
                        self.logger.error(f"Failed to delete {file_path}: {e}")
                        self.log_message(f"⚠️ Failed to delete {os.path.basename(file_path)}: {e}")
        
        # Auto-refresh input file list after processing
        input_dir = self.input_directory.get()
        if input_dir and input_dir != output_placeholder_text and os.path.exists(input_dir):
            self.log_message("Auto-refreshing input file list...")
            self.find_files()
        else:
            self.log_message("Input directory not set or invalid, skipping auto-refresh")
        
        # Show summary
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        self.status_var.set(f"Processing complete: {successful} successful, {failed} failed")
        self.logger.info(f"Processing complete: {successful} successful, {failed} failed")
        self.log_message(f"Processing complete: {successful} successful, {failed} failed")
        
        if new_files:
            self.log_message(f"New output files generated: {len(new_files)}")
        else:
            self.log_message("No new output files were generated")
        
        # Removed messagebox popup to avoid interrupting user workflow
    
    def calculate_dialog_size(self, files: List[str], show_deletion_warning: bool, show_command_preview: bool, is_sync_mode: bool = False) -> tuple:
        """Calculate dynamic dialog size based on file count and content."""
        import math
        
        # Base dimensions
        base_width = 600 if not is_sync_mode else 700
        base_height = 400 if not is_sync_mode else 450
        
        # Calculate file list height (approximately 20px per file line)
        file_list_height = max(60, len(files) * 25)  # Min 60px, 25px per file
        
        # Calculate command preview area
        command_height = 0
        command_width_addition = 0
        if show_command_preview:
            # Estimate command content size
            if is_sync_mode:
                # Sync mode shows more detailed info per file
                command_height = max(200, len(files) * 80)  # 80px per file for detailed commands
                command_width_addition = 400
            else:
                # Normal mode shows simpler commands
                command_height = max(150, len(files) * 60)  # 60px per file for normal commands
                command_width_addition = 300
        
        # Calculate deletion warning height
        deletion_height = 100 if show_deletion_warning else 0
        
        # Calculate total dimensions
        total_width = base_width + command_width_addition
        total_height = base_height + file_list_height + command_height + deletion_height
        
        # Add padding and UI elements
        total_height += 200  # For title, buttons, margins, etc.
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Apply limits with margin
        max_width = screen_width - 150  # 150px margin
        max_height = screen_height - 150  # 150px margin
        
        # Ensure minimum size
        min_width = 500
        min_height = 400
        
        # Final dimensions with limits
        final_width = max(min_width, min(total_width, max_width))
        final_height = max(min_height, min(total_height, max_height))
        
        return final_width, final_height
    
    def show_confirmation_dialog(self, files: List[str], title: str = "Confirmation", 
                               show_deletion_warning: bool = False, 
                               show_command_preview: bool = True) -> bool:
        """Unified confirmation dialog that can show deletion warnings and/or command previews."""
        if not files:
            return False
        
        # Create confirmation dialog
        confirm_dialog = tk.Toplevel(self.root)
        confirm_dialog.title(title)
        
        # Calculate dynamic size based on file count and content
        dialog_width, dialog_height = self.calculate_dialog_size(
            files, show_deletion_warning, show_command_preview, is_sync_mode=False
        )
        
        # Set the calculated geometry
        confirm_dialog.geometry(f"{dialog_width}x{dialog_height}")
            
        confirm_dialog.transient(self.root)
        confirm_dialog.grab_set()
        
        # Center the dialog
        confirm_dialog.update_idletasks()
        x = (confirm_dialog.winfo_screenwidth() // 2) - (confirm_dialog.winfo_width() // 2)
        y = (confirm_dialog.winfo_screenheight() // 2) - (confirm_dialog.winfo_height() // 2)
        confirm_dialog.geometry(f"+{x}+{y}")
        
        # Title based on content
        if show_deletion_warning:
            title_text = "⚠️ WARNING: Files Will Be Deleted"
            title_color = "red"
        elif show_command_preview:
            title_text = "🔍 Command Preview"
            title_color = "blue"
        else:
            title_text = "⚠️ Confirmation Required"
            title_color = "orange"
            
        ttk.Label(confirm_dialog, text=title_text, 
                 font=("Arial", 14, "bold"), foreground=title_color).pack(pady=10)
        
        # Main content frame
        content_frame = ttk.Frame(confirm_dialog)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Deletion warning section
        if show_deletion_warning:
            ttk.Label(content_frame, text="The following files will be PERMANENTLY DELETED after successful processing:", 
                     font=("Arial", 10)).pack(pady=5)
        
        # File list
        ttk.Label(content_frame, text="Files to process:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # File list - dynamic height based on number of files
        file_list_height = max(6, min(15, len(files)))  # Between 6 and 15 lines
        file_list_text = scrolledtext.ScrolledText(content_frame, height=file_list_height, width=90, wrap=tk.WORD)
        file_list_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        for i, file_path in enumerate(files):
            file_list_text.insert(tk.END, f"{i+1}. {file_path}\n")
        file_list_text.config(state=tk.DISABLED)
        
        # Command preview section
        if show_command_preview:
            ttk.Label(content_frame, text="Command preview:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 5))
            
            # Create a frame for command list with better organization
            command_frame = ttk.Frame(content_frame)
            command_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            
            # Command list text widget - dynamic height based on number of files
            command_height = max(8, min(20, len(files) + 5))  # Base height + files, with limits
            command_text = scrolledtext.ScrolledText(command_frame, height=command_height, width=100, wrap=tk.WORD)
            command_text.pack(fill=tk.BOTH, expand=True, pady=5)
            
            # Add header for command list
            command_text.insert(tk.END, "=" * 100 + "\n")
            command_text.insert(tk.END, f"SUBPROCESS COMMANDS ({len(files)} files to process)\n")
            command_text.insert(tk.END, "=" * 100 + "\n\n")
            
            # Show actual subprocess commands for all files
            for i, file_path in enumerate(files):
                # Get the actual subprocess command that will be executed (with error handling)
                try:
                    subprocess_cmd = self.processor.get_subprocess_command(file_path)
                    template_cmd = self.processor.build_command_string(file_path)
                except Exception as e:
                    print(f"Error generating commands for {file_path}: {e}")
                    subprocess_cmd = f"Error: {str(e)}"
                    template_cmd = f"Error: {str(e)}"
                
                command_text.insert(tk.END, f"File {i+1}/{len(files)}: {os.path.basename(file_path)}\n")
                command_text.insert(tk.END, f"  Subprocess Command: {subprocess_cmd}\n")
                command_text.insert(tk.END, f"  Template Command:  {template_cmd}\n")
                command_text.insert(tk.END, f"  Input File:        {file_path}\n")
                command_text.insert(tk.END, f"  Output Directory:  {self.output_directory.get()}\n")
                
                # Show shell execution mode (with error handling)
                try:
                    cmd_list, use_shell = self.processor.build_command(file_path)
                    shell_mode = "shell=True" if use_shell else "shell=False"
                except Exception as e:
                    print(f"Error determining shell mode for {file_path}: {e}")
                    shell_mode = "shell=False (error)"
                command_text.insert(tk.END, f"  Execution Mode:    {shell_mode}\n")
                
                command_text.insert(tk.END, "-" * 100 + "\n")
            
            # Add summary information
            command_text.insert(tk.END, f"\n" + "=" * 100 + "\n")
            command_text.insert(tk.END, "EXECUTION SUMMARY\n")
            command_text.insert(tk.END, "=" * 100 + "\n")
            command_text.insert(tk.END, f"  Total files:         {len(files)}\n")
            command_text.insert(tk.END, f"  Processing program:   {self.processing_program.get()}\n")
            command_text.insert(tk.END, f"  Output directory:    {self.output_directory.get()}\n")
            command_text.insert(tk.END, f"  Command template:    {self.command_template.get()}\n")
            command_text.insert(tk.END, f"  Delete originals:    {'Yes' if show_deletion_warning else 'No'}\n")
            
            command_text.config(state=tk.DISABLED)
        
        # Additional info
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(fill=tk.X, pady=10)
        
        info_text = f"Total files: {len(files)}\n"
        info_text += f"Output directory: {self.output_directory.get()}\n"
        info_text += f"Processing program: {self.processing_program.get()}"
        
        ttk.Label(info_frame, text=info_text, font=("Arial", 9), 
                 foreground="gray").pack(anchor=tk.W)
        
        # Add a separator line above buttons
        separator = ttk.Separator(content_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(10, 20))
        
        # Buttons - create a more prominent button section
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        result = [False]  # Use list to store result for closure
        
        def on_execute():
            result[0] = True
            confirm_dialog.destroy()
        
        def on_cancel():
            result[0] = False
            confirm_dialog.destroy()
        
        # Button text based on context
        execute_text = "Execute" if show_command_preview else "Continue"
        if show_deletion_warning:
            execute_text = "Delete & Execute"
        
        # Create buttons with enhanced styling and visibility
        button_style = {"width": 18, "padding": 10}
        
        # Execute button - more prominent
        execute_btn = ttk.Button(
            button_frame, 
            text=f"✓ {execute_text}", 
            command=on_execute,
            **button_style
        )
        execute_btn.pack(side=tk.LEFT, padx=25)
        
        # Cancel button
        cancel_btn = ttk.Button(
            button_frame, 
            text="✗ Cancel", 
            command=on_cancel,
            **button_style
        )
        cancel_btn.pack(side=tk.LEFT, padx=25)
        
        # Apply custom styling to make buttons more visible
        try:
            style = ttk.Style()
            # Configure a more prominent style for execute button
            style.configure("Execute.TButton", font=("Arial", 10, "bold"))
            execute_btn.configure(style="Execute.TButton")
        except:
            pass  # Style configuration not available, use default
        
        # Set default button behavior
        confirm_dialog.bind('<Return>', lambda e: on_execute())
        confirm_dialog.bind('<Escape>', lambda e: on_cancel())
        
        # Focus on execute button by default and make it stand out
        execute_btn.focus_set()
        
        # Add visual emphasis to execute button if deletion is enabled
        if show_deletion_warning:
            execute_btn.configure(text=f"⚠️ {execute_text}")
        
        # Button styling already applied inline
        
        # Wait for dialog to close
        self.root.wait_window(confirm_dialog)
        
        return result[0]
    
    def is_valid_command_template(self, template_text: str) -> bool:
        """Check if template text is valid (not placeholder text)."""
        placeholder_text = "Use placeholders: {env}, {program}, {input}, {output_dir}"
        return template_text and template_text.strip() and template_text != placeholder_text
    
    def show_sync_side_by_side_confirmation_dialog(self, files: List[str], title: str = "Confirmation", 
                                                 show_deletion_warning: bool = False, 
                                                 show_command_preview: bool = True) -> bool:
        """Specialized confirmation dialog for sync side by side mode showing individual output directories."""
        if not files:
            return False
        
        # Create confirmation dialog
        confirm_dialog = tk.Toplevel(self.root)
        confirm_dialog.title(title)
        
        # Calculate dynamic size based on file count and content
        dialog_width, dialog_height = self.calculate_dialog_size(
            files, show_deletion_warning, show_command_preview, is_sync_mode=True
        )
        
        # Set the calculated geometry
        confirm_dialog.geometry(f"{dialog_width}x{dialog_height}")
            
        confirm_dialog.transient(self.root)
        confirm_dialog.grab_set()
        
        # Center the dialog
        confirm_dialog.update_idletasks()
        x = (confirm_dialog.winfo_screenwidth() // 2) - (confirm_dialog.winfo_width() // 2)
        y = (confirm_dialog.winfo_screenheight() // 2) - (confirm_dialog.winfo_height() // 2)
        confirm_dialog.geometry(f"+{x}+{y}")
        
        # Title based on content
        if show_deletion_warning:
            title_text = "⚠️ WARNING: Files Will Be Deleted (Sync Side by Side Mode)"
            title_color = "red"
        elif show_command_preview:
            title_text = "🔍 Command Preview - Sync Side by Side Mode"
            title_color = "blue"
        else:
            title_text = "⚠️ Confirmation Required - Sync Side by Side Mode"
            title_color = "orange"
            
        ttk.Label(confirm_dialog, text=title_text, 
                 font=("Arial", 14, "bold"), foreground=title_color).pack(pady=10)
        
        # Main content frame
        content_frame = ttk.Frame(confirm_dialog)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Mode explanation
        mode_info = "📍 Sync Side by Side Mode: Each file will be processed in its own directory"
        ttk.Label(content_frame, text=mode_info, 
                 font=("Arial", 10, "italic"), foreground="blue").pack(pady=5)
        
        # Deletion warning section
        if show_deletion_warning:
            ttk.Label(content_frame, text="The following files will be PERMANENTLY DELETED after successful processing:", 
                     font=("Arial", 10)).pack(pady=5)
        
        # File list
        ttk.Label(content_frame, text="Files to process:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # File list - dynamic height based on number of files (sync mode shows 2 lines per file)
        file_list_height = max(6, min(20, len(files) * 2))  # 2 lines per file, with limits
        file_list_text = scrolledtext.ScrolledText(content_frame, height=file_list_height, width=100, wrap=tk.WORD)
        file_list_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        for i, file_path in enumerate(files):
            output_dir = os.path.dirname(file_path)
            file_list_text.insert(tk.END, f"{i+1}. {file_path}\n")
            file_list_text.insert(tk.END, f"   Output: {output_dir}\n")
        file_list_text.config(state=tk.DISABLED)
        
        # Command preview section
        if show_command_preview:
            ttk.Label(content_frame, text="Command preview:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 5))
            
            # Create a frame for command list with better organization
            command_frame = ttk.Frame(content_frame)
            command_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            
            # Command list text widget - dynamic height based on number of files (sync mode shows ~7 lines per file)
            command_height = max(10, min(25, len(files) * 7))  # 7 lines per file for detailed commands, with limits
            command_text = scrolledtext.ScrolledText(command_frame, height=command_height, width=100, wrap=tk.WORD)
            command_text.pack(fill=tk.BOTH, expand=True, pady=5)
            
            # Add header for command list
            command_text.insert(tk.END, "=" * 100 + "\n")
            command_text.insert(tk.END, f"SYNC SIDE BY SIDE COMMANDS ({len(files)} files to process)\n")
            command_text.insert(tk.END, "=" * 100 + "\n\n")
            
            # Show actual subprocess commands for all files with their individual output directories
            for i, file_path in enumerate(files):
                # Temporarily set output directory to file's directory for command generation
                original_output_dir = self.output_directory.get()
                file_output_dir = os.path.dirname(file_path)
                self.output_directory.set(file_output_dir)
                self.processor.set_output_directory(file_output_dir)
                
                # Get the actual subprocess command that will be executed (with error handling)
                try:
                    subprocess_cmd = self.processor.get_subprocess_command(file_path)
                    template_cmd = self.processor.build_command_string(file_path)
                except Exception as e:
                    print(f"Error generating commands for {file_path}: {e}")
                    subprocess_cmd = f"Error: {str(e)}"
                    template_cmd = f"Error: {str(e)}"
                
                command_text.insert(tk.END, f"File {i+1}/{len(files)}: {os.path.basename(file_path)}\n")
                command_text.insert(tk.END, f"  Subprocess Command: {subprocess_cmd}\n")
                command_text.insert(tk.END, f"  Template Command:  {template_cmd}\n")
                command_text.insert(tk.END, f"  Input File:        {file_path}\n")
                command_text.insert(tk.END, f"  Output Directory:  {file_output_dir}\n")
                
                # Show shell execution mode (with error handling)
                try:
                    cmd_list, use_shell = self.processor.build_command(file_path)
                    shell_mode = "shell=True" if use_shell else "shell=False"
                except Exception as e:
                    print(f"Error determining shell mode for {file_path}: {e}")
                    shell_mode = "shell=False (error)"
                command_text.insert(tk.END, f"  Execution Mode:    {shell_mode}\n")
                
                command_text.insert(tk.END, "-" * 100 + "\n")
                
                # Restore original output directory
                self.output_directory.set(original_output_dir)
                self.processor.set_output_directory(original_output_dir)
            
            # Add summary information
            command_text.insert(tk.END, f"\n" + "=" * 100 + "\n")
            command_text.insert(tk.END, "SYNC SIDE BY SIDE EXECUTION SUMMARY\n")
            command_text.insert(tk.END, "=" * 100 + "\n")
            command_text.insert(tk.END, f"  Total files:         {len(files)}\n")
            command_text.insert(tk.END, f"  Processing program:   {self.processing_program.get()}\n")
            command_text.insert(tk.END, f"  Mode:                Each file processed in its own directory\n")
            command_text.insert(tk.END, f"  Command template:    {self.command_template.get()}\n")
            command_text.insert(tk.END, f"  Delete originals:    {'Yes' if show_deletion_warning else 'No'}\n")
            
            command_text.config(state=tk.DISABLED)
        
        # Additional info
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(fill=tk.X, pady=10)
        
        info_text = f"Total files: {len(files)}\n"
        info_text += f"Mode: Sync Side by Side (each file in its own directory)\n"
        info_text += f"Processing program: {self.processing_program.get()}"
        
        ttk.Label(info_frame, text=info_text, font=("Arial", 9), 
                 foreground="gray").pack(anchor=tk.W)
        
        # Add a separator line above buttons
        separator = ttk.Separator(content_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(10, 20))
        
        # Buttons - create a more prominent button section
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        result = [False]  # Use list to store result for closure
        
        def on_execute():
            result[0] = True
            confirm_dialog.destroy()
        
        def on_cancel():
            result[0] = False
            confirm_dialog.destroy()
        
        # Button text based on context
        execute_text = "Execute" if show_command_preview else "Continue"
        if show_deletion_warning:
            execute_text = "Delete & Execute"
        
        # Create buttons with enhanced styling and visibility
        button_style = {"width": 18, "padding": 10}
        
        # Execute button - more prominent
        execute_btn = ttk.Button(
            button_frame, 
            text=f"✓ {execute_text}", 
            command=on_execute,
            **button_style
        )
        execute_btn.pack(side=tk.LEFT, padx=25)
        
        # Cancel button
        cancel_btn = ttk.Button(
            button_frame, 
            text="✗ Cancel", 
            command=on_cancel,
            **button_style
        )
        cancel_btn.pack(side=tk.LEFT, padx=25)
        
        # Apply custom styling to make buttons more visible
        try:
            style = ttk.Style()
            # Configure a more prominent style for execute button
            style.configure("Execute.TButton", font=("Arial", 10, "bold"))
            execute_btn.configure(style="Execute.TButton")
        except:
            pass  # Style configuration not available, use default
        
        # Set default button behavior
        confirm_dialog.bind('<Return>', lambda e: on_execute())
        confirm_dialog.bind('<Escape>', lambda e: on_cancel())
        
        # Focus on execute button by default and make it stand out
        execute_btn.focus_set()
        
        # Add visual emphasis to execute button if deletion is enabled
        if show_deletion_warning:
            execute_btn.configure(text=f"⚠️ {execute_text}")
        
        # Button styling already applied inline
        
        # Wait for dialog to close
        self.root.wait_window(confirm_dialog)
        
        return result[0]
    
    def show_command_confirmation(self, files: List[str], title: str = "Command Confirmation") -> bool:
        """Show command confirmation dialog with preview of commands to be executed."""
        return self.show_confirmation_dialog(files, title, show_deletion_warning=False, show_command_preview=True)
    
    def _find_related_output_files(self, original_output_file: str, output_files: list) -> bool:
        """Find related output files that might have been created."""
        import glob
        
        if not original_output_file:
            return False
        
        # Get the directory and base name
        output_dir = os.path.dirname(original_output_file)
        if not output_dir:
            output_dir = self.output_directory.get()
        
        if not output_dir or not os.path.exists(output_dir):
            return False
        
        # Get the base name without _processed suffix
        base_name = os.path.basename(original_output_file)
        if base_name.endswith('_processed'):
            base_name = base_name[:-10]  # Remove '_processed'
        
        # Look for files with similar names
        patterns = [
            os.path.join(output_dir, f"{base_name}*"),
            os.path.join(output_dir, f"*{base_name}*")
        ]
        
        found_files = []
        for pattern in patterns:
            matches = glob.glob(pattern)
            for match in matches:
                if match != original_output_file and os.path.isfile(match) and match not in output_files:
                    found_files.append(match)
        
        if found_files:
            output_files.extend(found_files)
            return True
        
        return False
    
    def _scan_output_directory_for_files(self, output_files: list):
        """Scan output directory for any processed files."""
        output_dir = self.output_directory.get()
        if not output_dir or not os.path.exists(output_dir):
            return
        
        import glob
        patterns = [
            os.path.join(output_dir, "*_processed*"),
            os.path.join(output_dir, "*.out"),
            os.path.join(output_dir, "*.output"),
            os.path.join(output_dir, "*.result"),
            os.path.join(output_dir, "*_output*"),  # Add output pattern
            os.path.join(output_dir, "*_converted*"),  # Add converted pattern
            os.path.join(output_dir, "*_rendered*"),  # Add rendered pattern
        ]
        
        found_files = []
        for pattern in patterns:
            matches = glob.glob(pattern)
            for match in matches:
                if os.path.isfile(match) and match not in output_files:
                    found_files.append(match)
        
        if found_files:
            print(f"Found additional output files in directory: {found_files}")
            output_files.extend(found_files)
    
    def _find_any_modified_files(self, output_files: list, original_files: list):
        """Find any files in output directory that weren't in original files."""
        output_dir = self.output_directory.get()
        if not output_dir or not os.path.exists(output_dir):
            return
        
        # Get original file basenames to exclude
        original_basenames = {os.path.basename(f) for f in original_files}
        
        # Look for any files that might be outputs
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)
            if os.path.isfile(item_path) and item not in original_basenames:
                # Check if it's likely an output file (not a script, config, etc.)
                if not item.endswith(('.sh', '.bat', '.exe', '.py', '.conf', '.config')):
                    if item_path not in output_files:
                        output_files.append(item_path)
                        print(f"Found potential output file: {item_path}")
    
    def stop_processing(self):
        """Stop the current processing."""
        if self.processor.is_processing:
            self.status_var.set("Stopping processing...")
            self.log_message("Stopping processing...")
            self.processor.stop_processing()
            
            # Wait for thread to finish gracefully
            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join(timeout=5.0)  # Wait up to 5 seconds
                
            self.status_var.set("Processing stopped")
            self.log_message("Processing stopped by user")
            self.progress_var.set(0)
        else:
            self.status_var.set("No processing in progress")
            self.log_message("No processing in progress to stop")
    
    def clear_file_list(self):
        """Clear the file list."""
        self.file_listbox.delete(0, tk.END)
        self.selected_files = []
        self.status_var.set("File list cleared")
        self.log_message("File list cleared")
    
    def open_file(self, event):
        """Open the selected file with the default application."""
        selection = self.file_listbox.curselection()
        if selection:
            file_path = self.selected_files[selection[0]]
            if os.path.exists(file_path):
                try:
                    os.startfile(file_path)  # Windows
                except AttributeError:
                    try:
                        opener = 'open' if os.name == 'posix' else 'xdg-open'
                        # Keep the file path as-is for command line execution
                        subprocess.run([opener, file_path], check=True)  # macOS/Linux
                    except:
                        messagebox.showerror("Error", "Could not open file.")
    
    def toggle_log_combined(self):
        """Combined toggle for log enable and show/hide."""
        if self.log_visible:
            # Disable logging and hide log frame
            self.log_text_frame.pack_forget()
            self.log_visible = False
            self.logging_enabled.set(False)
            self.logger.set_enabled(False)
            self.config.set_logging_enabled(False)
            self.config.save_config()
            self.log_button.state(['!selected'])  # Unselect radio button
        else:
            # Enable logging and show log frame
            self.log_text_frame.pack(fill=tk.BOTH, expand=True)
            self.log_visible = True
            self.logging_enabled.set(True)
            self.logger.set_enabled(True)
            self.config.set_logging_enabled(True)
            self.config.save_config()
            self.log_button.state(['selected'])  # Select radio button
        
        self.logger.info(f"Logging {'enabled' if self.logging_enabled.get() else 'disabled'}")
        self.log_message(f"Logging {'enabled' if self.logging_enabled.get() else 'disabled'}")
    
    def toggle_logging(self):
        """Toggle logging on/off."""
        enabled = self.logging_enabled.get()
        self.logger.set_enabled(enabled)
        self.config.set_logging_enabled(enabled)
        self.config.save_config()
        self.logger.info(f"Logging {'enabled' if enabled else 'disabled'}")
        self.log_message(f"Logging {'enabled' if enabled else 'disabled'}")
    
    def save_settings(self):
        """Save current settings to configuration with file selection."""
        # Create dialog for config selection/saving
        save_dialog = tk.Toplevel(self.root)
        save_dialog.title("Save Configuration")
        save_dialog.geometry("450x400")
        save_dialog.transient(self.root)
        save_dialog.grab_set()
        
        # Center the dialog
        save_dialog.update_idletasks()
        x = (save_dialog.winfo_screenwidth() // 2) - (save_dialog.winfo_width() // 2)
        y = (save_dialog.winfo_screenheight() // 2) - (save_dialog.winfo_height() // 2)
        save_dialog.geometry(f"+{x}+{y}")
        
        # Dialog content
        ttk.Label(save_dialog, text="💾 Save Configuration", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        # Get saved configs
        saved_configs = self.config.list_saved_configs()
        
        if saved_configs:
            ttk.Label(save_dialog, text="Select existing configuration or enter new name:").pack(pady=5)
            
            # Create frame for existing configs
            config_frame = ttk.Frame(save_dialog)
            config_frame.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)
            
            # Listbox for existing configs
            scrollbar = ttk.Scrollbar(config_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            config_listbox = tk.Listbox(config_frame, yscrollcommand=scrollbar.set, height=8)
            config_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=config_listbox.yview)
            
            # Add configs to listbox with full names
            for config_name in saved_configs:
                config_listbox.insert(tk.END, f"{config_name}.json")
            
            # Select first item by default
            if saved_configs:
                config_listbox.selection_set(0)
                config_listbox.focus_set()
            
            # New name input
            new_name_frame = ttk.Frame(save_dialog)
            new_name_frame.pack(pady=10, padx=20, fill=tk.X)
            
            ttk.Label(new_name_frame, text="Or enter new name:").pack(side=tk.LEFT)
            name_var = tk.StringVar()
            name_entry = ttk.Entry(new_name_frame, textvariable=name_var, width=25)
            name_entry.pack(side=tk.LEFT, padx=5)
            
            # Auto-fill name entry when selecting from list
            def on_select(event):
                selection = config_listbox.curselection()
                if selection:
                    selected_name = config_listbox.get(selection[0]).replace('.json', '')
                    name_var.set(selected_name)
            
            config_listbox.bind('<<ListboxSelect>>', on_select)
        else:
            ttk.Label(save_dialog, text="Enter new configuration name:").pack(pady=5)
            
            name_frame = ttk.Frame(save_dialog)
            name_frame.pack(pady=5, padx=20)
            
            name_var = tk.StringVar()
            name_entry = ttk.Entry(name_frame, textvariable=name_var, width=30)
            name_entry.pack()
            name_entry.focus()
        
        # Buttons
        button_frame = ttk.Frame(save_dialog)
        button_frame.pack(pady=15)
        
        def save_config():
            config_name = name_var.get().strip()
            if not config_name:
                messagebox.showerror("Error", "Please enter a configuration name.")
                return
            
            try:
                # Update config with current settings
                self.config.set_input_directory(self.input_directory.get())
                self.config.set_output_directory(self.output_directory.get())
                self.config.set_processing_program(self.processing_program.get())
                self.config.set_command_template(self.command_template.get())
                self.config.set_env_vars(self.env_vars.get())
                self.config.set_logging_enabled(self.logging_enabled.get())
                self.config.set_command_confirm_enabled(self.show_command_confirm.get())
                self.config.set_del_origin_file_enabled(self.del_origin_file.get())
                
                extensions = [ext.strip() for ext in self.file_extensions.get().split(",") if ext.strip()]
                self.config.set_file_extensions(extensions)
                
                # Save with custom name
                config_path = self.config.save_config_as(config_name)
                self.status_var.set(f"Configuration saved: {config_name}")
                self.logger.info(f"Configuration saved as: {config_name}")
                self.log_message(f"Configuration saved as: {config_name}")
                save_dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {e}")
        
        def cancel_save():
            save_dialog.destroy()
        
        def delete_config():
            if saved_configs:
                selection = config_listbox.curselection()
                if selection:
                    config_full_name = config_listbox.get(selection[0])
                    config_name = config_full_name.replace('.json', '')
                    
                    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the configuration '{config_full_name}'?"):
                        try:
                            config_path = self.config.get_config_path(config_name)
                            if os.path.exists(config_path):
                                os.remove(config_path)
                            
                            # Refresh the listbox
                            config_listbox.delete(0, tk.END)
                            updated_configs = self.config.list_saved_configs()
                            for updated_config in updated_configs:
                                config_listbox.insert(tk.END, f"{updated_config}.json")
                            
                            # Clear name entry if it was the deleted config
                            if name_var.get() == config_name:
                                name_var.set("")
                            
                            # Select first item if available
                            if updated_configs:
                                config_listbox.selection_set(0)
                                config_listbox.focus_set()
                                # Auto-fill name entry with first selection
                                name_var.set(updated_configs[0])
                            
                            self.log_message(f"Configuration deleted: {config_full_name}")
                            messagebox.showinfo("Success", f"Configuration '{config_full_name}' has been deleted.")
                            
                        except Exception as e:
                            messagebox.showerror("Error", f"Failed to delete configuration: {e}")
                else:
                    messagebox.showerror("Error", "Please select a configuration to delete.")
            else:
                messagebox.showerror("Error", "No configurations available to delete.")
        
        # Add buttons
        ttk.Button(button_frame, text="Save", command=save_config).pack(side=tk.LEFT, padx=5)
        
        # Add delete button only if there are saved configs
        if saved_configs:
            ttk.Button(button_frame, text="Delete", command=delete_config).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Cancel", command=cancel_save).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to save
        name_entry.bind('<Return>', lambda e: save_config())
        
        # Wait for dialog to close
        self.root.wait_window(save_dialog)
    
    def load_saved_settings(self):
        """Load saved settings from configuration with selection dialog showing full names."""
        # Create dialog for config selection
        load_dialog = tk.Toplevel(self.root)
        load_dialog.title("Load Configuration")
        load_dialog.geometry("450x400")
        load_dialog.transient(self.root)
        load_dialog.grab_set()
        
        # Center the dialog
        load_dialog.update_idletasks()
        x = (load_dialog.winfo_screenwidth() // 2) - (load_dialog.winfo_width() // 2)
        y = (load_dialog.winfo_screenheight() // 2) - (load_dialog.winfo_height() // 2)
        load_dialog.geometry(f"+{x}+{y}")
        
        # Dialog content
        ttk.Label(load_dialog, text="📂 Load Configuration", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        # Get saved configs
        saved_configs = self.config.list_saved_configs()
        
        if saved_configs:
            ttk.Label(load_dialog, text="Select a configuration to load:").pack(pady=5)
            
            # Create listbox for config selection
            list_frame = ttk.Frame(load_dialog)
            list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
            
            scrollbar = ttk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            config_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=10)
            config_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=config_listbox.yview)
            
            # Add configs to listbox with full names including .json extension
            for config_name in saved_configs:
                config_listbox.insert(tk.END, f"{config_name}.json")
            
            # Select first item by default
            if saved_configs:
                config_listbox.selection_set(0)
                config_listbox.focus_set()
            
            # Add config info display
            info_frame = ttk.Frame(load_dialog)
            info_frame.pack(pady=5, padx=20, fill=tk.X)
            
            info_text = tk.Text(info_frame, height=4, width=50, wrap=tk.WORD, font=("Arial", 8))
            info_text.pack(fill=tk.BOTH, expand=True)
            
            def show_config_info(event):
                selection = config_listbox.curselection()
                if selection:
                    config_full_name = config_listbox.get(selection[0])
                    config_name = config_full_name.replace('.json', '')
                    config_path = self.config.get_config_path(config_name)
                    
                    try:
                        with open(config_path, 'r') as f:
                            config_data = json.load(f)
                        
                        info_content = f"Configuration: {config_full_name}\n"
                        info_content += f"Program: {config_data.get('processing_program', 'Not set')}\n"
                        info_content += f"Output: {config_data.get('output_directory', 'Not set')}\n"
                        info_content += f"Extensions: {', '.join(config_data.get('file_extensions', []))}"
                        
                        info_text.delete(1.0, tk.END)
                        info_text.insert(1.0, info_content)
                    except:
                        info_text.delete(1.0, tk.END)
                        info_text.insert(1.0, "Error loading config info")
            
            config_listbox.bind('<<ListboxSelect>>', show_config_info)
            
            # Show initial selection info
            if saved_configs:
                show_config_info(None)
            
            def load_selected_config():
                selection = config_listbox.curselection()
                if not selection:
                    messagebox.showerror("Error", "Please select a configuration to load.")
                    return
                
                config_full_name = config_listbox.get(selection[0])
                config_name = config_full_name.replace('.json', '')
                config_path = self.config.get_config_path(config_name)
                
                try:
                    # Load the selected config
                    if self.config.load_config_from(config_path):
                        # Update GUI with loaded settings
                        self._update_gui_from_config()
                        self.status_var.set(f"Configuration loaded: {config_full_name}")
                        self.logger.info(f"Configuration loaded: {config_full_name}")
                        self.log_message(f"Configuration loaded: {config_full_name}")
                        load_dialog.destroy()
                    else:
                        messagebox.showerror("Error", f"Failed to load configuration: {config_full_name}")
                        
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load configuration: {e}")
            
            def cancel_load():
                load_dialog.destroy()
            
            # Buttons
            button_frame = ttk.Frame(load_dialog)
            button_frame.pack(pady=10)
            
            ttk.Button(button_frame, text="Load", command=load_selected_config).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Cancel", command=cancel_load).pack(side=tk.LEFT, padx=5)
            
            # Bind double-click to load
            config_listbox.bind('<Double-Button-1>', lambda e: load_selected_config())
            
        else:
            ttk.Label(load_dialog, text="No saved configurations found.", 
                     font=("Arial", 10), foreground="gray").pack(pady=20)
            
            ttk.Button(load_dialog, text="OK", command=load_dialog.destroy).pack(pady=10)
        
        # Wait for dialog to close
        self.root.wait_window(load_dialog)
    
    def _update_gui_from_config(self):
        """Update GUI elements from the current config."""
        # Get default directory
        main_py_dir = os.path.dirname(os.path.abspath(__file__))
        main_py_dir = os.path.dirname(main_py_dir)
        
        # Set input directory with saved value or default
        input_dir = self.config.get_input_directory()
        if not input_dir:
            input_dir = main_py_dir
        self.input_directory.set(input_dir)
        
        # Set output directory with saved value or default
        output_dir = self.config.get_output_directory()
        if not output_dir:
            output_dir = input_dir
        self.output_directory.set(output_dir)
        
        # Set other fields with saved values
        self.processing_program.set(self.config.get_processing_program())
        self.command_template.set(self.config.get_command_template())
        self.env_vars.set(self.config.get_env_vars())
        self.file_extensions.set(", ".join(self.config.get_file_extensions()))
        self.logging_enabled.set(self.config.is_logging_enabled())
        self.show_command_confirm.set(self.config.is_command_confirm_enabled())
        
        # Update processor settings
        self.processor.set_output_directory(self.output_directory.get())
        self.processor.set_processing_program(self.processing_program.get())
        self.processor.set_env_vars(self.env_vars.get())
        # Only set command template if it's valid (not placeholder text)
        template_text = self.command_template.get()
        if self.is_valid_command_template(template_text):
            self.processor.set_command_template(template_text)
        else:
            self.processor.set_command_template("")
        
        # Clear file lists
        self.selected_files = []
        self.file_listbox.delete(0, tk.END)
        self.output_listbox.delete(0, tk.END)
        self.log_message("Cleared file lists")
    
    def manage_config_files(self):
        """Show dialog to manage saved configuration files."""
        # Create dialog for config management
        manage_dialog = tk.Toplevel(self.root)
        manage_dialog.title("Manage Configurations")
        manage_dialog.geometry("500x400")
        manage_dialog.transient(self.root)
        manage_dialog.grab_set()
        
        # Center the dialog
        manage_dialog.update_idletasks()
        x = (manage_dialog.winfo_screenwidth() // 2) - (manage_dialog.winfo_width() // 2)
        y = (manage_dialog.winfo_screenheight() // 2) - (manage_dialog.winfo_height() // 2)
        manage_dialog.geometry(f"+{x}+{y}")
        
        # Dialog content
        ttk.Label(manage_dialog, text="⚙️ Manage Configurations", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        # Get saved configs
        saved_configs = self.config.list_saved_configs()
        
        if saved_configs:
            ttk.Label(manage_dialog, text="Saved configurations:").pack(pady=5)
            
            # Create listbox for config management
            list_frame = ttk.Frame(manage_dialog)
            list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
            
            scrollbar = ttk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            config_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=10)
            config_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=config_listbox.yview)
            
            # Add configs to listbox
            for config_name in saved_configs:
                config_listbox.insert(tk.END, config_name)
            
            # Select first item by default
            if saved_configs:
                config_listbox.selection_set(0)
                config_listbox.focus_set()
            
            # Buttons frame
            button_frame = ttk.Frame(manage_dialog)
            button_frame.pack(pady=10)
            
            def delete_config():
                selection = config_listbox.curselection()
                if not selection:
                    messagebox.showerror("Error", "Please select a configuration to delete.")
                    return
                
                config_name = config_listbox.get(selection[0])
                
                if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the configuration '{config_name}'?"):
                    try:
                        config_path = self.config.get_config_path(config_name)
                        if os.path.exists(config_path):
                            os.remove(config_path)
                        
                        # Refresh the listbox
                        config_listbox.delete(0, tk.END)
                        updated_configs = self.config.list_saved_configs()
                        for updated_config in updated_configs:
                            config_listbox.insert(tk.END, updated_config)
                        
                        if updated_configs:
                            config_listbox.selection_set(0)
                        
                        self.log_message(f"Configuration deleted: {config_name}")
                        messagebox.showinfo("Success", f"Configuration '{config_name}' has been deleted.")
                        
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to delete configuration: {e}")
            
            def rename_config():
                selection = config_listbox.curselection()
                if not selection:
                    messagebox.showerror("Error", "Please select a configuration to rename.")
                    return
                
                old_name = config_listbox.get(selection[0])
                
                # Create rename dialog
                rename_dialog = tk.Toplevel(manage_dialog)
                rename_dialog.title("Rename Configuration")
                rename_dialog.geometry("300x120")
                rename_dialog.transient(manage_dialog)
                rename_dialog.grab_set()
                
                ttk.Label(rename_dialog, text="New name:").pack(pady=5)
                
                new_name_var = tk.StringVar(value=old_name)
                new_name_entry = ttk.Entry(rename_dialog, textvariable=new_name_var, width=25)
                new_name_entry.pack(pady=5)
                new_name_entry.focus()
                new_name_entry.select_range(0, tk.END)
                
                def do_rename():
                    new_name = new_name_var.get().strip()
                    if not new_name or new_name == old_name:
                        rename_dialog.destroy()
                        return
                    
                    try:
                        old_path = self.config.get_config_path(old_name)
                        new_path = self.config.get_config_path(new_name)
                        
                        if os.path.exists(new_path):
                            messagebox.showerror("Error", f"A configuration named '{new_name}' already exists.")
                            return
                        
                        if os.path.exists(old_path):
                            os.rename(old_path, new_path)
                            
                            # Refresh the listbox
                            config_listbox.delete(0, tk.END)
                            updated_configs = self.config.list_saved_configs()
                            for updated_config in updated_configs:
                                config_listbox.insert(tk.END, updated_config)
                            
                            # Select the renamed item
                            for i, config in enumerate(updated_configs):
                                if config == new_name:
                                    config_listbox.selection_set(i)
                                    break
                            
                            self.log_message(f"Configuration renamed: {old_name} → {new_name}")
                            messagebox.showinfo("Success", f"Configuration renamed to '{new_name}'.")
                        
                        rename_dialog.destroy()
                        
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to rename configuration: {e}")
                
                ttk.Button(rename_dialog, text="Rename", command=do_rename).pack(pady=5)
                
                # Bind Enter key to rename
                new_name_entry.bind('<Return>', lambda e: do_rename())
                
                # Wait for rename dialog to close
                manage_dialog.wait_window(rename_dialog)
            
            ttk.Button(button_frame, text="Delete", command=delete_config).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Rename", command=rename_config).pack(side=tk.LEFT, padx=5)
            
        else:
            ttk.Label(manage_dialog, text="No saved configurations found.", 
                     font=("Arial", 10), foreground="gray").pack(pady=20)
        
        # Close button
        ttk.Button(manage_dialog, text="Close", command=manage_dialog.destroy).pack(pady=10)
        
        # Wait for dialog to close
        self.root.wait_window(manage_dialog)
    
    def toggle_sync_side_by_side(self):
        """Toggle sync side by side functionality."""
        if self.sync_side_by_side.get():
            # Check if files are selected OR input directory has a value
            selected_indices = self.file_listbox.curselection()
            input_dir = self.input_directory.get()
            
            if selected_indices:
                # Use the first selected file from the listbox for sync side by side
                selected_index = selected_indices[0]
                selected_file_path = self.selected_files[selected_index]
                sync_output_dir = os.path.dirname(selected_file_path)
                self.output_directory.set(sync_output_dir)
                self.processor.set_output_directory(sync_output_dir)
                self.logger.info(f"Same as Input enabled: Output directory set to {sync_output_dir}")
                self.log_message(f"Same as Input enabled: Output directory set to {sync_output_dir}")
            elif input_dir and input_dir.strip() and input_dir != "Select or enter input directory path":
                # Use input directory as output directory
                sync_output_dir = input_dir
                self.output_directory.set(sync_output_dir)
                self.processor.set_output_directory(sync_output_dir)
                self.logger.info(f"Same as Input enabled: Output directory set to {sync_output_dir}")
                self.log_message(f"Same as Input enabled: Output directory set to {sync_output_dir}")
            else:
                self.sync_side_by_side.set(False)  # Uncheck if neither files selected nor input directory has value
                messagebox.showwarning("Warning", "Please select files or enter an input directory first to enable Same as Input.")
        else:
            # When unchecked, just log the change but don't modify the output directory
            self.logger.info("Same as Input disabled")
            self.log_message("Same as Input disabled")
    
    def load_initial_settings(self):
        """Load initial settings from configuration."""
        # Get the directory where main.py is located as default input directory
        main_py_dir = os.path.dirname(os.path.abspath(__file__))
        main_py_dir = os.path.dirname(main_py_dir)  # Go up one level to the project directory
        
        # Set input directory with default if null
        input_dir = self.config.get_input_directory()
        if not input_dir:
            input_dir = main_py_dir
        self.input_directory.set(input_dir)
        
        # Set output directory with default if null (same as input directory)
        output_dir = self.config.get_output_directory()
        if not output_dir:
            output_dir = input_dir
        self.output_directory.set(output_dir)
        
        if self.config.get_processing_program():
            self.processing_program.set(self.config.get_processing_program())
        
        if self.config.get_command_template():
            self.command_template.set(self.config.get_command_template())
        
        self.logging_enabled.set(self.config.is_logging_enabled())
        self.show_command_confirm.set(self.config.is_command_confirm_enabled())
        self.del_origin_file.set(self.config.is_del_origin_file_enabled())
        
        extensions = self.config.get_file_extensions()
        if extensions:
            self.file_extensions.set(", ".join(extensions))
        
        self.logger.info("Initial settings loaded")
        self.log_message("Initial settings loaded")
    
    def log_message(self, message: str):
        """Add a message to the log text widget."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)  # Scroll to the end
        
        # Limit log size to prevent memory issues
        lines = self.log_text.get("1.0", tk.END).split('\n')
        if len(lines) > 1000:  # Keep last 1000 lines
            self.log_text.delete("1.0", f"{len(lines)-1000}.0")