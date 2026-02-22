"""Entry point for running the Sanctuary CLI as a module.

Usage:
    python -m sanctuary.api
    python -m sanctuary.api --verbose
    python -m sanctuary.api --show-inner
"""

from sanctuary.api.cli import run

if __name__ == "__main__":
    run()
