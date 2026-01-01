"""
Lyra Emergence Core - A system for developing emergent consciousness
"""

from .client import LyraAPI, Lyra
from .cognitive_core import (
    CognitiveCore,
    ConversationManager,
    ConversationTurn,
)
from .unified_core import (
    UnifiedCognitiveCore,
    SharedMemoryBridge,
    EmotionalStateBridge,
)
from .specialists import (
    SpecialistFactory,
    SpecialistOutput,
    PhilosopherSpecialist,
    PragmatistSpecialist,
    ArtistSpecialist,
    VoiceSpecialist,
    PerceptionSpecialist,
)

__version__ = "0.1.0"

__all__ = [
    "LyraAPI",
    "Lyra",
    "CognitiveCore",
    "ConversationManager",
    "ConversationTurn",
    "UnifiedCognitiveCore",
    "SharedMemoryBridge",
    "EmotionalStateBridge",
    "SpecialistFactory",
    "SpecialistOutput",
    "PhilosopherSpecialist",
    "PragmatistSpecialist",
    "ArtistSpecialist",
    "VoiceSpecialist",
    "PerceptionSpecialist",
]