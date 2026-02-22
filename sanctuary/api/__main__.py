"""Entry point for running the Sanctuary CLI as a module.

Usage:
    python -m sanctuary.api
    python -m sanctuary.api --verbose
    python -m sanctuary.api --show-inner
"""

import sys


def main():
    """Entry point that provides clear error messages for missing deps."""
    try:
        from sanctuary.api.cli import run
    except ImportError as e:
        print(f"[sanctuary] Import error: {e}", file=sys.stderr)
        print(
            "[sanctuary] Try: pip install -e . (or uv pip install -e .)",
            file=sys.stderr,
        )
        sys.exit(1)
    run()


if __name__ == "__main__":
    main()
