# Infini Converter

A powerful file processing tool with GUI for batch file conversion and processing.

## Features

- **File Discovery**: Find files in directories with configurable extensions
- **Batch Processing**: Process multiple files using external programs
- **GUI Interface**: User-friendly interface with file lists and progress tracking
- **Configurable Output**: Specify output directory for processed files
- **Logging System**: Optional logging with on/off toggle
- **Settings Management**: Save and load configuration settings

## Installation

### From Source

```bash
git clone <repository-url>
cd infini_converter
pip install -e .
```

### Requirements

- Python 3.7 or higher
- tkinter (usually included with Python)

## Usage

### GUI Mode

Run the application with the GUI:

```bash
python main.py
```

Or if installed:

```bash
infini-converter
```

### Basic Workflow

1. **Select Input Directory**: Choose the directory containing files to process
2. **Configure File Extensions**: Specify which file extensions to look for (e.g., .txt, .csv, .json)
3. **Set Output Directory**: Choose where processed files will be saved
4. **Select Processing Program**: Choose the external program to process files
5. **Find Files**: Click "Find Files" to discover matching files
6. **Process Files**: Select files and click "Process Selected" or "Process All"

### Configuration

The application automatically saves settings to `config/config.json`. You can configure:

- File extensions to search for
- Default output directory
- Processing program path
- Logging preferences

## File Structure

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
├── tests/                     # Unit tests
├── docs/                      # Documentation
├── main.py                    # Entry point
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

## Processing Programs

The application can work with any external program that can process files. Examples:

- Image converters (ImageMagick, ffmpeg)
- Document processors (pandoc, LibreOffice)
- Code formatters (black, clang-format)
- Custom scripts

## Logging

The application includes a comprehensive logging system that can be toggled on/off:

- Logs to both file and console
- Configurable log file location
- Detailed processing information
- Error tracking and debugging

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
```

### Type Checking

```bash
mypy src/
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## Support

For issues and feature requests, please open an issue on the project repository.