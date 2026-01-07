# Configuration Guide

This guide explains how to configure the Lyra Emergence system's paths and settings.

## System Configuration

The system uses JSON configuration files to define paths for various components like models, cache, logs, and data storage. The main configuration file is `config/system.json`.

### Default Configuration

By default, the system uses relative paths that work from the project root:

```json
{
    "base_dir": ".",
    "chroma_dir": "./data/chroma",
    "model_dir": "./models",
    "cache_dir": "./data/cache",
    "log_dir": "./logs"
}
```

### Configuration Files

- **`config/system.json`**: Main system configuration (gitignored, can be customized locally)
- **`config/system.json.example`**: Template configuration file (committed to git)
- **`emergence_core/config/system.json`**: Alternative configuration location with additional settings

### Environment Variable Overrides

You can override any configuration path using environment variables without modifying the config files:

- `LYRA_BASE_DIR`: Override the base directory
- `LYRA_CHROMA_DIR`: Override the ChromaDB storage directory
- `LYRA_MODEL_DIR`: Override the model cache directory
- `LYRA_CACHE_DIR`: Override the general cache directory
- `LYRA_LOG_DIR`: Override the log directory

These can be set in your shell or in a `.env` file:

```bash
# In your .env file or shell
export LYRA_BASE_DIR=/custom/path/to/project
export LYRA_CHROMA_DIR=/custom/path/to/chroma
export LYRA_MODEL_DIR=/path/to/models
export LYRA_CACHE_DIR=/path/to/cache
export LYRA_LOG_DIR=/path/to/logs
```

See `emergence_core/.env.example` for a complete example.

### Path Resolution

The system automatically resolves paths using the following rules:

1. **Environment variables take precedence**: If an environment variable is set, it overrides the config file
2. **Relative paths are resolved**: Relative paths in both config files and environment variables are resolved against the project root
3. **Absolute paths are preserved**: Absolute paths are used as-is

### Usage in Code

To load the system configuration in Python:

```python
from lyra.config import SystemConfig
from pathlib import Path

# Load with default project root detection
config = SystemConfig.from_json('config/system.json')

# Or specify project root explicitly
project_root = Path('/path/to/project')
config = SystemConfig.from_json('config/system.json', project_root=project_root)

# Access the resolved paths
print(config.base_dir)    # Always returns an absolute Path
print(config.chroma_dir)  # Always returns an absolute Path
```

### Setup for Development

1. **First time setup**: Copy the example config
   ```bash
   cp config/system.json.example config/system.json
   ```

2. **Customize if needed**: Edit `config/system.json` for local paths (this file is gitignored)

3. **Or use environment variables**: Set the `LYRA_*` environment variables instead

### Setup for Production

For production deployments, we recommend using environment variables rather than modifying config files:

```bash
# Set environment variables in your deployment configuration
export LYRA_BASE_DIR=/opt/lyra
export LYRA_CHROMA_DIR=/var/lib/lyra/chroma
export LYRA_MODEL_DIR=/opt/lyra/models
export LYRA_CACHE_DIR=/var/cache/lyra
export LYRA_LOG_DIR=/var/log/lyra
```

### Migration from Old Configuration

If you have an existing setup with hardcoded absolute paths:

1. The paths in `config/system.json` have been updated to use relative paths
2. Your local setup will continue to work with the default relative paths
3. If you need custom paths, set them via environment variables rather than editing the config file
4. The `config/system.json` file is now gitignored to prevent committing local paths

## Testing

Tests verify that:
- Configuration loads correctly from JSON files
- Relative paths are resolved to absolute paths
- Environment variables override config file values
- Both relative and absolute paths in environment variables work correctly

Run the configuration tests:
```bash
uv run pytest emergence_core/tests/test_config_loading.py -v
```
