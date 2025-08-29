"""
File discovery and management utilities
"""

import os
import glob
from pathlib import Path
from typing import List, Optional

class FileDiscovery:
    def __init__(self, extensions: List[str] = None):
        self.extensions = extensions or [".txt", ".csv", ".json", ".xml", ".log"]
    
    def find_files(self, directory: str, recursive: bool = True) -> List[str]:
        """
        Find all files with specified extensions in the given directory.
        
        Args:
            directory: Directory to search
            recursive: Whether to search subdirectories
            
        Returns:
            List of file paths
        """
        if not os.path.exists(directory):
            return []
        
        files = []
        
        for ext in self.extensions:
            if recursive:
                pattern = os.path.join(directory, "**", f"*{ext}")
                found_files = glob.glob(pattern, recursive=True)
            else:
                pattern = os.path.join(directory, f"*{ext}")
                found_files = glob.glob(pattern)
            
            files.extend(found_files)
        
        return sorted(files)
    
    def set_extensions(self, extensions: List[str]) -> None:
        """
        Set the file extensions to search for.
        
        Args:
            extensions: List of file extensions (e.g., [".txt", ".csv"])
        """
        self.extensions = extensions
    
    def add_extension(self, extension: str) -> None:
        """
        Add a file extension to the search list.
        
        Args:
            extension: File extension (e.g., ".txt")
        """
        if not extension.startswith("."):
            extension = f".{extension}"
        
        if extension not in self.extensions:
            self.extensions.append(extension)
    
    def remove_extension(self, extension: str) -> None:
        """
        Remove a file extension from the search list.
        
        Args:
            extension: File extension to remove
        """
        if not extension.startswith("."):
            extension = f".{extension}"
        
        if extension in self.extensions:
            self.extensions.remove(extension)
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Get information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        if not os.path.exists(file_path):
            return {}
        
        path = Path(file_path)
        stat = path.stat()
        
        return {
            "name": path.name,
            "path": str(path.absolute()),
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "extension": path.suffix,
            "directory": str(path.parent)
        }
    
    def filter_files_by_size(self, files: List[str], min_size: int = 0, max_size: Optional[int] = None) -> List[str]:
        """
        Filter files by size range.
        
        Args:
            files: List of file paths
            min_size: Minimum file size in bytes
            max_size: Maximum file size in bytes (None for no limit)
            
        Returns:
            Filtered list of file paths
        """
        filtered = []
        
        for file_path in files:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                if size >= min_size and (max_size is None or size <= max_size):
                    filtered.append(file_path)
        
        return filtered
    
    def filter_files_by_date(self, files: List[str], start_date: Optional[float] = None, end_date: Optional[float] = None) -> List[str]:
        """
        Filter files by modification date range.
        
        Args:
            files: List of file paths
            start_date: Start timestamp (None for no limit)
            end_date: End timestamp (None for no limit)
            
        Returns:
            Filtered list of file paths
        """
        filtered = []
        
        for file_path in files:
            if os.path.exists(file_path):
                mod_time = os.path.getmtime(file_path)
                if (start_date is None or mod_time >= start_date) and (end_date is None or mod_time <= end_date):
                    filtered.append(file_path)
        
        return filtered
    
    def filter_problematic_files(self, files: List[str]) -> List[str]:
        """
        Filter out problematic files that might cause processing issues.
        
        Args:
            files: List of file paths
            
        Returns:
            Filtered list of file paths (problematic files removed)
        """
        filtered = []
        problematic_patterns = ['.part', '.tmp', '.temp', '.bak', '.swp', '.DS_Store']
        
        for file_path in files:
            filename = os.path.basename(file_path)
            
            # Skip files with problematic patterns
            is_problematic = any(pattern in filename for pattern in problematic_patterns)
            
            # Also skip files that are too small (likely incomplete)
            if os.path.exists(file_path):
                try:
                    size = os.path.getsize(file_path)
                    is_too_small = size < 50  # Less than 50 bytes
                except:
                    is_too_small = True
                
                if not is_problematic and not is_too_small:
                    filtered.append(file_path)
                    print(f"Keeping file: {filename} (size={size}, problematic={is_problematic}, too_small={is_too_small})")
                else:
                    print(f"Skipping file: {filename} (size={size}, problematic={is_problematic}, too_small={is_too_small})")
        
        return filtered