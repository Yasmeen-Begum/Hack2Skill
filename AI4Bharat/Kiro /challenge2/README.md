# 🚀 Lazy Automation Tool

**Stop wasting time on boring digital tasks!**

A comprehensive automation toolkit featuring:
- 📁 **File Automation** - Rename, organize, and summarize files
- 📧 **Email Summarization** - Analyze emails from any provider
- 🤖 **AI-Powered Analysis** - Multi-agent AI with LangChain, CrewAI, RAG, and Weaviate
- 🌐 **Dual Interfaces** - CLI for power users, Web UI for everyone

Built with Kiro AI using spec-driven development.

## Project Structure

```
lazy_automation/
├── __init__.py
├── cli/                    # Command-line interface components
│   └── __init__.py
├── tasks/                  # Task modules (rename, organize, summarize)
│   ├── __init__.py
│   └── base.py            # Base interfaces for task modules
├── file_operations/        # File system operations with preview support
│   └── __init__.py
└── reporting/              # Reporting and logging components
    └── __init__.py

tests/
├── __init__.py
├── conftest.py            # Pytest configuration and fixtures
├── test_cli.py
├── test_file_operations.py
├── test_rename_task.py
├── test_organize_task.py
├── test_summarize_task.py
└── test_integration.py
```

## Installation

### For Development

Install in editable mode with development dependencies:
```bash
pip install -e ".[dev]"
```

This will install the `lazy-auto` command globally.

### For Direct Execution

You can also run the tool directly without installation:
```bash
python lazy-auto.py --help
```

Or using the module:
```bash
python -m lazy_automation.cli.main --help
```

## Usage

The tool provides three main capabilities:
1. **File Automation** (rename, organize, summarize files)
2. **Email Summarization** (summarize emails from your inbox)
3. **Dual Interfaces** (CLI and web interface)

### Web Interface

Launch the web interface for a user-friendly graphical experience:
```bash
lazy-auto-web
```

Or run directly:
```bash
python -m lazy_automation.web_interface
```

The web interface provides:
- 📝 **Rename Tab**: Batch rename files with pattern preview
- 📁 **Organize Tab**: Organize files by type or date
- 📊 **Summarize Tab**: Generate and download file summaries
- 🔍 **Preview Mode**: See changes before executing
- 💾 **Download Reports**: Save summary reports directly from the browser

For detailed web interface documentation, see [Web Interface Guide](docs/WEB_INTERFACE_GUIDE.md).

### Email Summarizer

Automate the boring task of reading through hundreds of emails:

```bash
# Summarize last 10 emails
python email_summarizer.py --email your@gmail.com

# Only unread emails
python email_summarizer.py --email your@gmail.com --unread-only

# Save summary to file
python email_summarizer.py --email your@gmail.com --output email_summary.txt

# Check specific folder
python email_summarizer.py --email your@gmail.com --folder Sent
```

**Features:**
- 📧 Connect to Gmail, Outlook, Yahoo, iCloud, and more
- 📊 Get statistics on senders, sizes, and attachments
- 🔍 Filter by folder, unread status, or count
- 💾 Export summaries to text files
- 🔐 Secure password handling

For detailed email summarizer documentation, see [Email Summarizer Guide](docs/EMAIL_SUMMARIZER_GUIDE.md).

### Command-Line Interface (File Operations)

The tool provides three main file automation tasks:

### Rename Files

Batch rename files using patterns:
```bash
# Preview rename operation
lazy-auto rename /path/to/dir --pattern "file_{n}.txt" --dry-run

# Execute rename with confirmation
lazy-auto rename /path/to/dir --pattern "doc_{n}.pdf"

# Skip confirmation prompt
lazy-auto rename /path/to/dir --pattern "photo_{n}.jpg" --no-confirm
```

### Organize Files

Organize files into subdirectories:
```bash
# Organize by file type
lazy-auto organize /path/to/dir --rule-type type --dry-run

# Organize by date with conflict handling
lazy-auto organize /path/to/dir --rule-type date --conflict-strategy rename
```

### Summarize Files

Generate summaries of text files:
```bash
# Display summary to console
lazy-auto summarize /path/to/dir --dry-run

# Save summary to file
lazy-auto summarize /path/to/dir --output summary.txt
```

### Common Options

- `--dry-run`: Preview changes without executing them
- `--verbose`: Enable detailed logging
- `--extensions .txt .pdf`: Filter files by extensions
- `--no-confirm`: Skip confirmation prompt (use with caution)

### Exit Codes

- `0`: Success
- `1`: General error
- `2`: Invalid arguments
- `3`: Unexpected error
- `130`: User cancelled (Ctrl+C)

## Testing

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=lazy_automation
```

## Development

This project uses:
- **pytest** for test framework
- **hypothesis** for property-based testing (minimum 100 iterations per property test)
- **pytest-cov** for code coverage reporting

## Complete Documentation

- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete project overview
- **[Web Interface Guide](docs/WEB_INTERFACE_GUIDE.md)** - Gradio web UI documentation
- **[Email Summarizer Guide](docs/EMAIL_SUMMARIZER_GUIDE.md)** - Basic email summarization
- **[AI Email Analyzer Guide](docs/AI_EMAIL_ANALYZER_GUIDE.md)** - Advanced AI email analysis
- **[Development Blog](blog/building-lazy-automation-tool-with-kiro.md)** - How it was built

## Quick Links

- **Demo**: `python demo_web_interface.py`
- **Tests**: `pytest` (115 tests passing)
- **Specs**: `.kiro/specs/lazy-automation-tool/`
- **Examples**: `examples/` directory
