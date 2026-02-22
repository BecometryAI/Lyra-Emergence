"""Sanctuary API — External interfaces.

Public API, CLI, and runner for interacting with the Sanctuary cognitive system.

Phase 6: Integration + Validation.

Imports are lazy to allow ``python -m sanctuary.api`` to work even when
optional heavy dependencies (torch, transformers, etc.) are not installed.
"""

__all__ = [
    "RunnerConfig",
    "SanctuaryRunner",
    "SanctuaryAPI",
]


def __getattr__(name: str):
    if name == "SanctuaryRunner":
        from sanctuary.api.runner import SanctuaryRunner
        return SanctuaryRunner
    if name == "RunnerConfig":
        from sanctuary.api.runner import RunnerConfig
        return RunnerConfig
    if name == "SanctuaryAPI":
        from sanctuary.api.sanctuary_api import SanctuaryAPI
        return SanctuaryAPI
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
