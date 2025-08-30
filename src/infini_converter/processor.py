"""
External program processing functionality
"""

import os
import subprocess
from typing import List, Dict, Any
import threading
import time

class FileProcessor:
    def __init__(self, processing_program: str = "", output_directory: str = "", command_template: str = "", env_vars: str = ""):
        self.processing_program = processing_program
        self.output_directory = output_directory
        self.command_template = command_template
        self.env_vars = env_vars
        self.processing_results = []
        self.is_processing = False
        self.should_stop = False
        self.current_file = ""
        self.processed_count = 0
        self.failed_count = 0
    
    def set_processing_program(self, program: str) -> None:
        """
        Set the external program to use for processing.
        
        Args:
            program: Path to the external program
        """
        self.processing_program = program
    
    def set_output_directory(self, directory: str) -> None:
        """
        Set the output directory for processed files.
        
        Args:
            directory: Output directory path
        """
        self.output_directory = directory
        os.makedirs(directory, exist_ok=True)
    
    def set_command_template(self, template: str) -> None:
        """
        Set the command template for subprocess execution.
        
        Args:
            template: Command template with placeholders {env}, {program}, {input}, {output_dir}
        """
        self.command_template = template
    
    def set_env_vars(self, env_vars: str) -> None:
        """
        Set the environment variables for subprocess execution.
        
        Args:
            env_vars: Environment variables string
        """
        self.env_vars = env_vars
    
    def is_placeholder_quoted(self, template: str, placeholder: str) -> bool:
        """
        Check if a placeholder in a template is already quoted.
        
        Args:
            template: The command template
            placeholder: The placeholder to check (e.g., '{input}')
            
        Returns:
            True if the placeholder is quoted, False otherwise
        """
        import re
        
        # Find the placeholder in the template
        placeholder_pos = template.find(placeholder)
        if placeholder_pos == -1:
            return False
        
        # Check for quotes before the placeholder
        # Look for single or double quotes immediately before the placeholder
        before_text = template[:placeholder_pos]
        
        # Check if there's a quote right before the placeholder
        # Patterns like: "{input}", '{input}', "prefix{input}", 'prefix{input}'
        patterns = [
            r'\"' + re.escape(placeholder) + r'\"',  # "{placeholder}"
            r"\'" + re.escape(placeholder) + r'\'',  # '{placeholder}'
            r'\"[^\"]*' + re.escape(placeholder) + r'\"',  # "anything{placeholder}"
            r"\'\[^\']*" + re.escape(placeholder) + r"\'",
        ]
        
        for pattern in patterns:
            if re.search(pattern, template):
                return True
        
        return False
    
    def escape_path_for_shell(self, path: str, raw_escape: bool = False, already_quoted: bool = False) -> str:
        """
        Escape a file path for safe shell command execution.
        
        Args:
            path: The file path to escape
            raw_escape: If True, escape only the most dangerous characters without wrapping in quotes
            already_quoted: If True, the path will be inside quotes in the template
            
        Returns:
            Escaped path safe for shell execution
        """
        if not path:
            return path
        
        if raw_escape:
            if already_quoted:
                # Path will be inside quotes - only escape characters that could break quotes
                escape_map = {
                    '"': '\\"',   # Double quote (could break double quotes)
                    '`': '\\`',   # Backtick (command substitution)
                    '$': '\\$',   # Dollar sign (variable expansion)
                    '\\': '\\\\', # Backslash (escape character)
                    '!': '\\!',   # History expansion
                }
            else:
                # Path will not be inside quotes - escape all dangerous characters
                escape_map = {
                    # Shell metacharacters that need escaping
                    '"': '\\"',   # Double quote
                    "'": "\\'",   # Single quote
                    '`': '\\`',   # Backtick
                    '$': '\\$',   # Dollar sign (variable expansion)
                    '\\': '\\\\', # Backslash
                    '!': '\\!',   # History expansion
                    
                    # Other potentially problematic characters
                    '&': '\\&',   # Background process
                    '|': '\\|',   # Pipe
                    ';': '\\;',   # Command separator
                    '<': '\\<',   # Input redirection
                    '>': '\\>',   # Output redirection
                    '(': '\\(',   # Subshell start
                    ')': '\\)',   # Subshell end
                    '{': '\\{',   # Group start
                    '}': '\\}',   # Group end
                    '[': '\\[',   # Character class start
                    ']': '\\]',   # Character class end
                    '*': '\\*',   # Wildcard
                    '?': '\\?',   # Wildcard
                    '~': '\\~',   # Home directory
                    '#': '\\#',   # Comment
                    
                    # Whitespace characters
                    '\t': '\\\t', # Tab
                    '\n': '\\\n', # Newline
                    '\r': '\\\r', # Carriage return
                    ' ': '\\ ',   # Space (escape when not in quotes)
                }
            
            escaped = path
            # Escape backslash first to avoid double-escaping
            if '\\' in escape_map:
                escaped = escaped.replace('\\', escape_map['\\'])
            # Then escape all other characters
            for char, escaped_char in escape_map.items():
                if char != '\\':  # Skip backslash since we already handled it
                    escaped = escaped.replace(char, escaped_char)
            
            return escaped
        else:
            # Standard escape - use shlex.quote for complete safety
            import shlex
            return shlex.quote(path)
    
    def build_command(self, input_file: str, args: List[str] = None) -> tuple:
        """
        Build the command for processing a file.
        
        Args:
            input_file: Path to the input file
            args: Additional arguments for the processing program
            
        Returns:
            Tuple of (command_list, use_shell)
        """
        if self.command_template and not self.command_template.startswith("Use placeholders:"):
            # Check if placeholders are already quoted in the template
            input_quoted = self.is_placeholder_quoted(self.command_template, '{input}')
            output_quoted = self.is_placeholder_quoted(self.command_template, '{output_dir}') if self.output_directory else False
            
            # Use custom command template with appropriately escaped parameters
            escaped_input = self.escape_path_for_shell(input_file, raw_escape=True, already_quoted=input_quoted)
            escaped_output = self.escape_path_for_shell(self.output_directory, raw_escape=True, already_quoted=output_quoted) if self.output_directory else ""
            
            # Format command template with error handling
            try:
                cmd_template = self.command_template.format(
                    env=self.env_vars,
                    program=self.processing_program,
                    input=escaped_input,
                    output_dir=escaped_output
                )
            except KeyError as e:
                # Handle missing placeholders gracefully
                print(f"Warning: Command template missing placeholder {e}. Using fallback command.")
                env_prefix = f"{self.env_vars} " if self.env_vars else ""
                cmd_template = f"{env_prefix}{self.processing_program} {escaped_input}"
                if escaped_output:
                    cmd_template += f" {escaped_output}"
            except Exception as e:
                print(f"Error formatting command template: {e}. Using fallback command.")
                env_prefix = f"{self.env_vars} " if self.env_vars else ""
                cmd_template = f"{env_prefix}{self.processing_program} {escaped_input}"
                if escaped_output:
                    cmd_template += f" {escaped_output}"
            # For template commands, use shell=True to preserve quotes
            return ([cmd_template], True)
        else:
            # Use default command format - build list for safe execution
            cmd = [self.processing_program]
            if args:
                cmd.extend(args)
            
            # Add input file as parameter
            cmd.append(input_file)
            
            # Add output directory as parameter (if needed)
            if self.output_directory:
                cmd.append(self.output_directory)
            
            # For default commands, use shell=False for security
            return (cmd, False)
    
    def build_command_string(self, input_file: str, args: List[str] = None) -> str:
        """
        Build the command string for display purposes.
        
        Args:
            input_file: Path to the input file
            args: Additional arguments for the processing program
            
        Returns:
            Command string for display
        """
        if self.command_template and not self.command_template.startswith("Use placeholders:"):
            # Check if placeholders are already quoted in the template
            input_quoted = self.is_placeholder_quoted(self.command_template, '{input}')
            output_quoted = self.is_placeholder_quoted(self.command_template, '{output_dir}') if self.output_directory else False
            
            # For template commands, return the formatted template with appropriately escaped paths
            escaped_input = self.escape_path_for_shell(input_file, raw_escape=True, already_quoted=input_quoted)
            escaped_output = self.escape_path_for_shell(self.output_directory, raw_escape=True, already_quoted=output_quoted) if self.output_directory else ""
            
            # Format command template with error handling
            try:
                return self.command_template.format(
                    program=self.processing_program,
                    input=escaped_input,
                    output_dir=escaped_output
                )
            except KeyError as e:
                # Handle missing placeholders gracefully
                print(f"Warning: Command template missing placeholder {e}. Using fallback command.")
                fallback_cmd = f"{self.processing_program} {escaped_input}"
                if escaped_output:
                    fallback_cmd += f" {escaped_output}"
                return fallback_cmd
            except Exception as e:
                print(f"Error formatting command template: {e}. Using fallback command.")
                fallback_cmd = f"{self.processing_program} {escaped_input}"
                if escaped_output:
                    fallback_cmd += f" {escaped_output}"
                return fallback_cmd
        else:
            # For default commands, build and join the command list
            cmd_list, _ = self.build_command(input_file, args)
            return " ".join(cmd_list)
    
    def get_subprocess_command(self, input_file: str, args: List[str] = None) -> str:
        """
        Get the actual subprocess command that will be executed.
        
        Args:
            input_file: Path to the input file
            args: Additional arguments for the processing program
            
        Returns:
            The actual command that will be passed to subprocess
        """
        try:
            cmd_list, use_shell = self.build_command(input_file, args)
            
            if use_shell:
                # For shell commands, return the command as-is (it's already a string)
                return cmd_list[0] if cmd_list else ""
            else:
                # For non-shell commands, join the list with proper quoting
                import shlex
                return " ".join(shlex.quote(arg) for arg in cmd_list)
        except Exception as e:
            print(f"Error building subprocess command: {e}")
            # Return a simple fallback command
            import shlex
            safe_input = shlex.quote(input_file)
            safe_program = shlex.quote(self.processing_program) if self.processing_program else ""
            env_prefix = f"{self.env_vars} " if self.env_vars else ""
            return f"{env_prefix}{safe_program} {safe_input}"
    
        
    def process_file(self, input_file: str, output_file: str = None, args: List[str] = None, progress_callback=None) -> Dict[str, Any]:
        """
        Process a single file using the external program.
        
        Args:
            input_file: Path to the input file
            output_file: Path to the output file (optional)
            args: Additional arguments for the processing program
            
        Returns:
            Dictionary with processing results
        """
        if not self.processing_program:
            return {
                "success": False,
                "error": "No processing program specified",
                "input_file": input_file,
                "output_file": output_file
            }
        
        # Normalize input file path
        normalized_input_file = self.normalize_file_path(input_file)
        
        if not os.path.exists(normalized_input_file):
            return {
                "success": False,
                "error": f"Input file not found: {normalized_input_file}",
                "input_file": normalized_input_file,
                "output_file": output_file
            }
        
        # Determine output file path
        if not output_file:
            input_name = os.path.splitext(os.path.basename(normalized_input_file))[0]
            input_ext = os.path.splitext(os.path.basename(normalized_input_file))[1]
            
            if self.output_directory:
                # Create output file with modified name to avoid conflict
                output_file = os.path.join(self.output_directory, f"{input_name}_processed{input_ext}")
            else:
                # If no output directory, create output file in same directory as input
                input_dir = os.path.dirname(normalized_input_file)
                output_file = os.path.join(input_dir, f"{input_name}_processed{input_ext}")
        
        # Validate output file path
        try:
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # Check if we have write permissions for the output directory
            if output_dir and not os.access(output_dir, os.W_OK):
                return {
                    "success": False,
                    "error": f"No write permission for output directory: {output_dir}",
                    "input_file": input_file,
                    "output_file": output_file
                }
            
            # Check if the output file path is valid
            if output_file and os.path.exists(output_file) and not os.access(output_file, os.W_OK):
                return {
                    "success": False,
                    "error": f"No write permission for output file: {output_file}",
                    "input_file": input_file,
                    "output_file": output_file
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Invalid output path: {str(e)}",
                "input_file": input_file,
                "output_file": output_file
            }
        
        # Build command using template or default format
        cmd_list, use_shell = self.build_command(normalized_input_file, args)
        
        try:
            # Build command string for logging
            cmd_string = self.build_command_string(normalized_input_file, args)
            
            # Log the command being executed
            print(f"Executing command: {cmd_string}")
            
            # Prepare environment variables
            env = None
            if self.env_vars:
                env = os.environ.copy()
                # Parse env vars (simple key=value pairs)
                for env_var in self.env_vars.split():
                    if '=' in env_var:
                        key, value = env_var.split('=', 1)
                        env[key] = value
            
            # Run the external program with real-time output
            process = subprocess.Popen(
                cmd_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                shell=use_shell,
                env=env
            )
            
            # Collect output and look for progress information
            stdout_lines = []
            stderr_lines = []
            progress_info = []
            
            # Use threading to avoid deadlocks when reading stdout/stderr
            def read_stdout():
                if process.stdout:
                    for line in iter(process.stdout.readline, ''):
                        line = line.rstrip()
                        stdout_lines.append(line)
                        print(f"STDOUT: {line}")
                        
                        # Extract percentage from output
                        percentage = self._extract_percentage_from_output(line)
                        if percentage >= 0:
                            progress_info.append({"percentage": percentage, "line": line})
                            print(f"Progress detected: {percentage}%")
                            
                            # Call progress callback if provided
                            if progress_callback:
                                progress_callback(percentage, line)
                        
                        # Also parse detailed progress information
                        progress_match = self._parse_progress_from_output(line)
                        if progress_match:
                            progress_info.append(progress_match)
            
            def read_stderr():
                if process.stderr:
                    for line in iter(process.stderr.readline, ''):
                        line = line.rstrip()
                        stderr_lines.append(line)
                        print(f"STDERR: {line}")
                        
                        # Extract percentage from stderr
                        percentage = self._extract_percentage_from_output(line)
                        if percentage >= 0:
                            progress_info.append({"percentage": percentage, "line": line})
                            print(f"Progress detected: {percentage}%")
                            
                            # Call progress callback if provided
                            if progress_callback:
                                progress_callback(percentage, line)
                        
                        # Also parse detailed progress information
                        progress_match = self._parse_progress_from_output(line)
                        if progress_match:
                            progress_info.append(progress_match)
            
            # Start threads for reading stdout and stderr
            import threading
            stdout_thread = threading.Thread(target=read_stdout)
            stderr_thread = threading.Thread(target=read_stderr)
            
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            
            stdout_thread.start()
            stderr_thread.start()
            
            # Wait for process to complete
            return_code = process.wait(timeout=300)
            
            # Wait for output threads to finish
            stdout_thread.join(timeout=1.0)
            stderr_thread.join(timeout=1.0)
            
            # Combine output
            stdout = "\n".join(stdout_lines)
            stderr = "\n".join(stderr_lines)
            
            print(f"Command execution completed with return code: {return_code}")
            
            # Handle output file - more intelligent logic
            if return_code == 0:
                # Check if the program created its own output file
                output_file_exists = os.path.exists(output_file)
                
                if output_file_exists:
                    # Program created its own output file
                    try:
                        file_size = os.path.getsize(output_file)
                        if file_size == 0:
                            print(f"Warning: Output file exists but is empty: {output_file}")
                        else:
                            print(f"Output file created successfully: {output_file} ({file_size} bytes)")
                    except Exception as e:
                        print(f"Warning: Could not check output file size: {output_file} - {str(e)}")
                elif stdout and stdout.strip():
                    # Program output to stdout, save it to output file
                    try:
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(stdout)
                        print(f"Saved STDOUT to output file: {output_file}")
                    except Exception as e:
                        print(f"Warning: Failed to save STDOUT to output file {output_file}: {str(e)}")
                else:
                    # No output file created and no stdout
                    print(f"Info: No output file created by program")
            
            # If command failed, remove any output file that might have been created
            # Only remove if it's different from the input file and we created it
            if return_code != 0:
                if os.path.exists(output_file) and output_file != input_file:
                    try:
                        # Only remove if it's empty or was created from stdout
                        file_size = os.path.getsize(output_file)
                        if file_size == 0 or (stdout and stdout.strip()):
                            os.remove(output_file)
                            print(f"Removed output file due to command failure: {output_file}")
                    except Exception as e:
                        print(f"Warning: Failed to remove output file {output_file}: {str(e)}")
            
            # Final check for output file existence
            final_output_exists = os.path.exists(output_file)
            print(f"Final output file check: {output_file} exists: {final_output_exists}")
            
            return {
                "success": return_code == 0,
                "return_code": return_code,
                "stdout": stdout,
                "stderr": stderr,
                "input_file": normalized_input_file,
                "output_file": output_file,
                "output_directory": self.output_directory,
                "output_exists": final_output_exists,
                "command": cmd_string,
                "progress_info": progress_info
            }
            
        except subprocess.TimeoutExpired:
            print(f"Command timed out: {cmd_string}")
            print(f"Timeout error: Processing timed out after 300 seconds")
            
            # Remove output file if it exists due to timeout
            # Only remove if it's different from the input file
            if output_file and os.path.exists(output_file) and output_file != input_file:
                try:
                    os.remove(output_file)
                    print(f"Removed output file due to timeout: {output_file}")
                except Exception as e:
                    print(f"Warning: Failed to remove output file {output_file}: {str(e)}")
            
            return {
                "success": False,
                "error": "Processing timed out",
                "input_file": normalized_input_file,
                "output_file": output_file,
                "output_directory": self.output_directory,
                "output_exists": os.path.exists(output_file) if output_file else False,
                "command": cmd_string
            }
        except Exception as e:
            print(f"Command execution failed: {cmd_string}")
            print(f"Exception error: {str(e)}")
            
            # Remove output file if it exists due to exception
            # Only remove if it's different from the input file
            if output_file and os.path.exists(output_file) and output_file != input_file:
                try:
                    os.remove(output_file)
                    print(f"Removed output file due to exception: {output_file}")
                except Exception as remove_error:
                    print(f"Warning: Failed to remove output file {output_file}: {str(remove_error)}")
            
            return {
                "success": False,
                "error": str(e),
                "input_file": normalized_input_file,
                "output_file": output_file,
                "output_directory": self.output_directory,
                "output_exists": os.path.exists(output_file) if output_file else False,
                "command": cmd_string
            }
    
    def process_files_batch(self, files: List[str], output_dir: str = None, args: List[str] = None, progress_callback=None) -> List[Dict[str, Any]]:
        """
        Process multiple files in batch.
        
        Args:
            files: List of input files
            output_dir: Output directory (optional, uses default if not provided)
            args: Additional arguments for the processing program
            
        Returns:
            List of processing results
        """
        if not files:
            return []
        
        if output_dir:
            self.set_output_directory(output_dir)
        
        # Store total number of files for progress tracking
        self.total_files = len(files)
        print(f"Starting processing of {self.total_files} files")
        
        results = []
        self.processing_results = []
        self.is_processing = True
        self.processed_count = 0
        self.failed_count = 0
        
        for i, file_path in enumerate(files):
            # Check if processing should stop
            if self.should_stop:
                print("Processing stopped by user")
                break
            
            # Normalize the file path
            normalized_file_path = self.normalize_file_path(file_path)
            self.current_file = normalized_file_path
            
            # Print progress update
            print(f"Processing file {i+1}/{self.total_files}: {normalized_file_path}")
            
            # Generate output file path
            input_name = os.path.splitext(os.path.basename(normalized_file_path))[0]
            input_ext = os.path.splitext(os.path.basename(normalized_file_path))[1]
            output_file = os.path.join(self.output_directory, f"{input_name}_processed{input_ext}")
            
            # Create file-specific progress callback
            def file_progress_callback(percentage, line):
                # Calculate overall progress
                file_progress = (i + percentage / 100) / len(files) * 100
                self.current_progress = file_progress
                
                # Call global progress callback if provided
                if progress_callback:
                    progress_callback(file_progress, f"File {i+1}/{len(files)}: {os.path.basename(normalized_file_path)} - {line}")
            
            # Process the file with output directory and file as parameters
            result = self.process_file(normalized_file_path, output_file, args, file_progress_callback)
            results.append(result)
            self.processing_results.append(result)
            
            if result["success"]:
                self.processed_count += 1
            else:
                self.failed_count += 1
            
            # Store progress information from subprocess output
            if "progress_info" in result and result["progress_info"]:
                self.progress_info = result["progress_info"]
                # Use the last progress info as current progress
                last_progress = result["progress_info"][-1]
                if "percentage" in last_progress:
                    self.current_progress = last_progress["percentage"]
                elif "value" in last_progress:
                    self.current_progress = last_progress["value"]
            else:
                # Fallback to file count progress
                self.current_progress = (self.processed_count + self.failed_count) / self.total_files * 100
            
            # Print progress after each file
            print(f"Progress: {self.current_progress:.1f}% ({self.processed_count + self.failed_count}/{self.total_files})")
            
            # Small delay to prevent overwhelming the system and allow GUI updates
            time.sleep(0.2)
        
        self.is_processing = False
        self.current_file = ""
        print(f"Processing completed. Success: {self.processed_count}, Failed: {self.failed_count}")
        
        return results
    
    def process_files_async(self, files: List[str], output_dir: str = None, args: List[str] = None, callback=None, progress_callback=None) -> threading.Thread:
        """
        Process files asynchronously in a separate thread.
        
        Args:
            files: List of input files
            output_dir: Output directory
            args: Additional arguments
            callback: Callback function to call when processing is complete
            
        Returns:
            Thread object
        """
        def process_thread():
            results = self.process_files_batch(files, output_dir, args, progress_callback)
            if callback:
                callback(results)
        
        thread = threading.Thread(target=process_thread)
        thread.daemon = True
        thread.start()
        
        return thread
    
    def get_processing_status(self) -> Dict[str, Any]:
        """
        Get current processing status.
        
        Returns:
            Dictionary with processing status information
        """
        return {
            "is_processing": self.is_processing,
            "current_file": self.current_file,
            "processed_count": self.processed_count,
            "failed_count": self.failed_count,
            "total_count": self.total_files if hasattr(self, 'total_files') else self.processed_count + self.failed_count,
            "current_progress": getattr(self, 'current_progress', 0),
            "progress_info": getattr(self, 'progress_info', [])
        }
    
    def get_processing_results(self) -> List[Dict[str, Any]]:
        """
        Get all processing results.
        
        Returns:
            List of processing results
        """
        return self.processing_results
    
    def clear_results(self) -> None:
        """Clear processing results."""
        self.processing_results = []
        self.processed_count = 0
        self.failed_count = 0
    
    def stop_processing(self) -> None:
        """Stop the current processing."""
        print("Stop processing requested")
        self.should_stop = True
        self.is_processing = False
    
    def reset_stop_flag(self) -> None:
        """Reset the stop flag for new processing."""
        self.should_stop = False
    
    def normalize_file_path(self, file_path: str) -> str:
        """
        Normalize file path by handling spaces and special characters.
        
        Args:
            file_path: Original file path
            
        Returns:
            Normalized file path for file system operations
        """
        if not file_path:
            return file_path
        
        # Remove extra spaces from the path
        normalized = file_path.strip()
        
        # Handle escape sequences - convert them to actual characters
        escape_sequences = {
            '\\ ': ' ',      # Escaped space
            '\\\"': '"',     # Escaped double quote
            "\\'": "'",      # Escaped single quote
            '\\$': '$',      # Escaped dollar sign
            '\\\\': '\\',    # Escaped backslash
            '\\`': '`',      # Escaped backtick
            '\\&': '&',      # Escaped ampersand
            '\\|': '|',      # Escaped pipe
            '\\;': ';',      # Escaped semicolon
            '\\<': '<',      # Escaped less than
            '\\>': '>',      # Escaped greater than
            '\\(': '(',      # Escaped left parenthesis
            '\\)': ')',      # Escaped right parenthesis
            '\\{': '{',      # Escaped left brace
            '\\}': '}',      # Escaped right brace
            '\\[': '[',      # Escaped left bracket
            '\\]': ']',      # Escaped right bracket
            '\\*': '*',      # Escaped asterisk
            '\\?': '?',      # Escaped question mark
            '\\~': '~',      # Escaped tilde
            '\\#': '#',      # Escaped hash
            '\\!': '!',      # Escaped exclamation
            '\\t': '\t',     # Escaped tab
            '\\n': '\n',     # Escaped newline
            '\\r': '\r',     # Escaped carriage return
        }
        
        # Process escape sequences
        for escape_seq, actual_char in escape_sequences.items():
            normalized = normalized.replace(escape_seq, actual_char)
        
        # Replace multiple spaces with single space
        import re
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Try to find the actual file
        if not os.path.exists(normalized):
            # Try to find the file by removing extra spaces
            dir_path = os.path.dirname(normalized)
            if dir_path and os.path.exists(dir_path):
                file_name = os.path.basename(normalized)
                # Try to match files with similar names (ignoring extra spaces)
                import glob
                pattern = os.path.join(dir_path, file_name.replace(' ', '*'))
                matches = glob.glob(pattern)
                if matches:
                    normalized = matches[0]
        
        return normalized
    
        
    def _parse_progress_from_output(self, line: str) -> dict:
        """
        Parse progress information from subprocess output.
        Optimized for percentage extraction.
        
        Args:
            line: Output line from subprocess
            
        Returns:
            Dictionary with progress information or None if no progress found
        """
        import re
        
        # First, look for direct percentage patterns (most common)
        percentage_patterns = [
            r'(\d+)%',  # Simple percentage
            r'progress:\s*(\d+)%',
            r'(\d+)%\s*complete',
            r'(\d+)%\s*done',
            r'(\d+)%\s*processed',
            r'(\d+)%\s*finished',
            r'(\d+)%\s*complete',
            r'progress\s*=\s*(\d+)%',
            r'(\d+)%\s*complete.*',
        ]
        
        # Try percentage patterns first
        for pattern in percentage_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                try:
                    percentage = float(match.group(1))
                    # Clamp percentage to 0-100 range
                    percentage = max(0, min(100, percentage))
                    return {
                        "type": "percentage",
                        "value": percentage,
                        "line": line
                    }
                except ValueError:
                    continue
        
        # If no direct percentage found, try count patterns
        count_patterns = [
            r'frame\s*(\d+)\s*of\s*(\d+)',
            r'(\d+)\s*/\s*(\d+)',
            r'processing\s*(\d+)\s*of\s*(\d+)',
            r'file\s*(\d+)\s*of\s*(\d+)',
            r'item\s*(\d+)\s*of\s*(\d+)',
            r'task\s*(\d+)\s*of\s*(\d+)',
            r'(\d+)\s*out\s*of\s*(\d+)',
        ]
        
        for pattern in count_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                try:
                    current = float(match.group(1))
                    total = float(match.group(2))
                    if total > 0:
                        percentage = (current / total) * 100
                        percentage = max(0, min(100, percentage))
                        return {
                            "type": "count",
                            "current": current,
                            "total": total,
                            "percentage": percentage,
                            "line": line
                        }
                except ValueError:
                    continue
        
        return None
    
    def _extract_percentage_from_output(self, line: str) -> float:
        """
        Extract percentage value from output line.
        Returns -1 if no percentage found.
        
        Args:
            line: Output line from subprocess
            
        Returns:
            Percentage value (0-100) or -1 if not found
        """
        progress_info = self._parse_progress_from_output(line)
        if progress_info:
            if progress_info["type"] == "percentage":
                return progress_info["value"]
            elif progress_info["type"] == "count":
                return progress_info["percentage"]
        return -1
    
    def validate_program(self, program_path: str) -> bool:
        """
        Validate that the processing program exists and is executable.
        
        Args:
            program_path: Path to the program
            
        Returns:
            True if the program is valid, False otherwise
        """
        if not program_path:
            return False
        
        # Normalize the program path first
        normalized_path = self.normalize_file_path(program_path)
        
        # Check if the program exists
        if not os.path.exists(normalized_path):
            return False
        
        # Check if it's executable
        if not os.access(normalized_path, os.X_OK):
            return False
        
        return True