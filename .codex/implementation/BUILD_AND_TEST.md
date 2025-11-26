# Build and Test Commands

This document contains verified commands for building, testing, and linting the Lyra-Emergence codebase.

## Environment Setup

### Virtual Environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate (Linux/Mac)
source .venv/bin/activate

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
```

### Install Dependencies
```bash
# Core dependencies
cd emergence_core
pip install -r requirements.txt

# Development/testing dependencies
pip install -r test_requirements.txt

# Optional: Flux.1-schnell for Artist specialist
pip install diffusers safetensors pillow accelerate
```

## Testing

### Run All Tests
```bash
# From project root
pytest emergence_core/tests/

# With verbose output
pytest emergence_core/tests/ -v

# Run specific test file
pytest emergence_core/tests/test_router.py
```

### Test Configuration
Tests are configured in `pyproject.toml`:
- Async mode: strict
- Test paths: `emergence_core/tests`
- Test files: `test_*.py`

## Validation Scripts

### JSON Schema Validation
```bash
# Validate JSON files
python scripts/validate_json.py

# Validate journal entries
python scripts/validate_journal.py
```

### Sequential Workflow Test
```bash
python test_sequential_workflow.py
```

### Flux Setup Verification
```bash
python tools/verify_flux_setup.py
```

## Code Quality

### Python Style
- Follow PEP 8 conventions
- Use meaningful variable names
- Add docstrings for public functions
- Keep imports organized (standard library, third-party, local)

### Pre-commit Checks
Before submitting a pull request:
1. Run all tests: `pytest emergence_core/tests/`
2. Validate JSON files: `python scripts/validate_json.py`
3. Check imports and basic syntax
4. Ensure documentation is updated

## Common Issues

### Import Errors
Ensure you're in the virtual environment:
```bash
which python  # Should point to .venv/bin/python
```

### CUDA/GPU Detection
```bash
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

### ChromaDB Errors
```bash
# Reset ChromaDB
rm -rf model_cache/chroma_db

# Re-initialize
python emergence_core/build_index.py
```

## Notes

- Always activate the virtual environment before running commands
- Tests should pass on Python 3.10 and 3.11
- Some tests may require GPU access for model loading
- Development mode can be enabled with `DEVELOPMENT_MODE=true` in `.env`
