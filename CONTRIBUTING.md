# Contributing to ParquetViewer

Thank you for your interest in contributing to ParquetViewer! We welcome contributions from the community.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## How to Contribute

### Reporting Issues

1. Check if the issue already exists
2. Include:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - System information (OS, Python version, etc.)

### Suggesting Enhancements

1. Check existing issues and discussions
2. Describe the enhancement clearly
3. Explain the use case and benefits
4. Provide examples if possible

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/YourFeatureName
   ```
3. **Make your changes**
   - Follow PEP 8 style guide
   - Add comments for complex logic
   - Keep changes focused and atomic
4. **Test your changes**
   - Run the application with your changes
   - Test edge cases
5. **Commit your changes**
   ```bash
   git commit -m "Add: Description of your changes"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/YourFeatureName
   ```
7. **Open a Pull Request**
   - Reference any related issues
   - Describe what your PR does
   - List any breaking changes

## Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/parquet-viewer.git
cd parquet-viewer

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Run the application
python parquet_viewer.py
```

## Coding Standards

### Style
- Follow PEP 8
- Use meaningful variable names
- Keep functions focused and small
- Add docstrings to functions

### Example
```python
def load_parquet_file(file_path: str) -> pd.DataFrame:
    """
    Load a parquet file and return as DataFrame.
    
    Args:
        file_path: Path to the parquet file
        
    Returns:
        DataFrame containing parquet data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not valid parquet
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        return pd.read_parquet(file_path)
    except Exception as e:
        raise ValueError(f"Invalid parquet file: {e}")
```

## Testing

While we don't have automated tests yet, please manually test:
- Opening various parquet files
- Pagination
- Search functionality
- Export to CSV/Excel
- Large files (260MB+)
- Complex data types

## Building the Executable

```bash
# Install build dependencies
pip install PyInstaller

# Build executable
python build_executable.py

# Test the executable
dist\ParquetViewer.exe
```

## Pull Request Process

1. Update documentation if needed
2. Add comments for new functionality
3. Ensure your changes don't break existing features
4. Describe changes clearly in PR description
5. Be responsive to feedback

## Areas for Contribution

- [ ] Bug fixes
- [ ] Performance improvements
- [ ] New features
- [ ] Documentation
- [ ] Testing
- [ ] Cross-platform support (macOS, Linux)
- [ ] Translation/localization

## Questions?

Feel free to:
- Open an issue for discussion
- Check existing issues for answers
- Comment on related PRs

We're here to help!

---

Thank you for making ParquetViewer better! 🎉
