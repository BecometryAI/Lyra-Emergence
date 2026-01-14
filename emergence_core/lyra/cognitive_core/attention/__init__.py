"""
Attention subsystem with precision-weighted attention.

This module contains attention-related components for IWMT,
including precision weighting based on uncertainty.
"""

from .precision import PrecisionWeighting

__all__ = [
    "PrecisionWeighting",
]
