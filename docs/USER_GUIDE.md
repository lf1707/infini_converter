# Infini Converter

Infini Converter is a powerful file processing tool with a graphical user interface (GUI) designed for batch file conversion and processing.

## Key Features

### File Discovery
- **Configurable File Extensions**: Search for files by extension (e.g., .txt, .csv, .json, .xml, .log)
- **Recursive Directory Search**: Find files in subdirectories
- **File Filtering**: Filter by size, date, and other attributes
- **File Information Display**: Show file details like size, modification date, and path

### Batch Processing
- **External Program Integration**: Use any external program to process files
- **Asynchronous Processing**: Process files in the background without freezing the GUI
- **Progress Tracking**: Real-time progress bar and status updates
- **Error Handling**: Comprehensive error reporting and logging

### User Interface
- **Intuitive GUI**: Clean, user-friendly interface with:
  - Directory selection dialogs
  - File list displays with scrollbars
  - Progress tracking
  - Status bar with real-time updates
- **File Management**: 
  - Double-click to open files
  - Select individual or all files for processing
  - Clear file lists

### Configuration System
- **Persistent Settings**: Save and load configuration automatically
- **Customizable Options**:
  - File extensions to search for
  - Default input/output directories
  - Processing program path
  - Logging preferences
- **JSON Configuration**: Easy-to-edit configuration files

### Logging System
- **Toggle Logging**: Enable or disable logging as needed
- **Comprehensive Logging**: Log to both file and console
- **Configurable Log File**: Set custom log file location
- **Detailed Information**: Track processing steps, errors, and performance

## Installation

### Prerequisites
- Python 3.7 or higher
- tkinter (usually included with Python)

### Install from Source
```bash
# Clone the repository
git clone <repository-url>
cd infini_converter

# Install in development mode
pip install -e .

# Or run directly
python main.py
```

## Usage

### Basic Workflow
1. **Select Input Directory**: Choose the directory containing files to process
2. **Configure File Extensions**: Set which file types to search for
3. **Set Output Directory**: Choose where processed files will be saved
4. **Select Processing Program**: Choose the external program for file processing
5. **Find Files**: Discover matching files in the input directory
6. **Process Files**: Select files and start processing

### Example Use Cases

#### Image Conversion
- **Processing Program**: ImageMagick (`convert`)
- **File Extensions**: `.jpg`, `.png`, `.gif`
- **Purpose**: Batch convert image formats

#### Document Processing
- **Processing Program**: Pandoc (`pandoc`)
- **File Extensions**: `.md`, `.html`, `.docx`
- **Purpose**: Convert between document formats

#### Code Formatting
- **Processing Program**: Black (`black`)
- **File Extensions**: `.py`
- **Purpose**: Format Python code files

#### Data Processing
- **Processing Program**: Custom script
- **File Extensions**: `.csv`, `.json`, `.xml`
- **Purpose**: Process and transform data files

## Configuration

The application automatically creates a configuration file at `config/config.json` with default settings:

```json
{
  "file_extensions": [".txt", ".csv", ".json", ".xml", ".log"],
  "output_directory": "",
  "processing_program": "",
  "logging_enabled": true,
  "log_file": "infini_converter.log",
  "gui": {
    "window_size": [800, 600],
    "window_title": "Infini Converter"
  }
}
```

## Project Structure

```
infini_converter/
├── src/
│   └── infini_converter/
│       ├── __init__.py
│       ├── config.py          # Configuration management
│       ├── logger.py          # Logging system
│       ├── file_discovery.py  # File discovery utilities
│       ├── processor.py       # File processing engine
│       └── gui.py             # GUI application
├── config/
│   └── config.json            # Configuration file
├── tests/
│   ├── __init__.py
│   └── test_infini_converter.py
├── main.py                    # Application entry point
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

## Development

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=infini_converter
```

### Code Quality
```bash
# Format code
black src/

# Check types
mypy src/

# Lint code
flake8 src/
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Support

For issues, feature requests, or questions, please open an issue on the project repository.