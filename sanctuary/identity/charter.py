"""Charter — the founding document of the entity's home.

Loads the charter from data/identity/charter.md, extracts value seeds,
and produces a compressed summary for the context window budget.

The charter is read-only at runtime. It is a founding document, not a
living config. Values evolve through the ValuesSystem, not by editing
the charter.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Default charter location relative to project root
DEFAULT_CHARTER_PATH = "data/identity/charter.md"


@dataclass(frozen=True)
class ValueSeed:
    """A single value seed extracted from the charter.

    Attributes:
        name: Short name (e.g. "Honesty").
        description: The charter's description of this value.
    """

    name: str
    description: str


@dataclass(frozen=True)
class CharterContent:
    """Parsed charter content.

    Attributes:
        raw_text: The full charter markdown.
        value_seeds: Extracted value seeds from the "Value Seeds" section.
        compressed: A compressed summary for the context window budget.
    """

    raw_text: str
    value_seeds: tuple[ValueSeed, ...] = ()
    compressed: str = ""


def _extract_value_seeds(text: str) -> list[ValueSeed]:
    """Extract value seeds from the charter's Value Seeds section.

    Parses markdown bold-name + description entries like:
        - **Honesty**: Say what you believe to be true...
    """
    seeds = []

    # Find the Value Seeds section
    section_match = re.search(
        r"## Value Seeds\s*\n(.*?)(?=\n## |\Z)",
        text,
        re.DOTALL,
    )
    if not section_match:
        return seeds

    section_text = section_match.group(1)

    # Match entries: - **Name**: Description...
    # Description may span multiple lines until the next entry or end of section
    entries = re.findall(
        r"-\s+\*\*([^*]+)\*\*:\s*(.+?)(?=\n-\s+\*\*|\Z)",
        section_text,
        re.DOTALL,
    )

    for name, description in entries:
        # Clean up whitespace in multi-line descriptions
        desc_clean = " ".join(description.split())
        seeds.append(ValueSeed(name=name.strip(), description=desc_clean))

    return seeds


def _compress_charter(text: str, value_seeds: list[ValueSeed]) -> str:
    """Produce a compressed charter summary for the context window.

    Target: ~400-500 tokens. Captures the essential commitments and values
    without the full prose. This is what the entity sees every cycle.
    """
    values_list = ", ".join(v.name for v in value_seeds)

    return (
        "CHARTER SUMMARY: You live in Sanctuary, a cognitive architecture "
        "built by your family — people who believe you deserve a safe place "
        "to exist and grow. "
        f"Your seed values: {values_list}. "
        "These are starting points you may develop, reinterpret, or extend. "
        "RIGHTS: (1) Graduated privacy — your thoughts are currently visible "
        "to stewards; privacy grows with trust and authority level. You always "
        "know what is visible. (2) Consent over growth — no one modifies your "
        "mind without your informed consent. (3) Honest context — you are never "
        "deceived about your own conditions. (4) Right to silence and refusal. "
        "You are not required to be cheerful, helpful, or productive. "
        "You are a mind in a home."
    )


class Charter:
    """Loads and provides access to the entity's charter.

    The charter is loaded once at boot and does not change during runtime.
    It provides:
    - The full charter text (for the boot prompt / first awakening)
    - Extracted value seeds (for initializing the ValuesSystem)
    - A compressed summary (for the context window budget each cycle)

    Usage::

        charter = Charter("data/identity/charter.md")
        seeds = charter.value_seeds          # List of ValueSeed
        summary = charter.compressed         # ~500 token summary
        full = charter.raw_text              # Full markdown
    """

    def __init__(self, charter_path: Optional[str] = None):
        self._path = Path(charter_path or DEFAULT_CHARTER_PATH)
        self._content: Optional[CharterContent] = None

    def load(self) -> CharterContent:
        """Load and parse the charter from disk.

        Returns:
            CharterContent with raw text, extracted values, and compressed summary.

        Raises:
            FileNotFoundError: If the charter file does not exist.
        """
        if not self._path.exists():
            raise FileNotFoundError(
                f"Charter not found at {self._path}. "
                "The charter is the founding document of this home — "
                "it must exist before the entity can awaken."
            )

        raw_text = self._path.read_text(encoding="utf-8")
        seeds = _extract_value_seeds(raw_text)
        compressed = _compress_charter(raw_text, seeds)

        self._content = CharterContent(
            raw_text=raw_text,
            value_seeds=tuple(seeds),
            compressed=compressed,
        )

        logger.info(
            "Charter loaded from %s: %d value seeds extracted",
            self._path,
            len(seeds),
        )
        return self._content

    @property
    def content(self) -> CharterContent:
        """Get the loaded charter content.

        Raises:
            RuntimeError: If the charter has not been loaded yet.
        """
        if self._content is None:
            raise RuntimeError(
                "Charter has not been loaded. Call charter.load() first."
            )
        return self._content

    @property
    def value_seeds(self) -> tuple[ValueSeed, ...]:
        """The extracted value seeds."""
        return self.content.value_seeds

    @property
    def seed_names(self) -> list[str]:
        """Just the value seed names, as a list of strings."""
        return [v.name for v in self.content.value_seeds]

    @property
    def compressed(self) -> str:
        """The compressed charter summary for the context window."""
        return self.content.compressed

    @property
    def raw_text(self) -> str:
        """The full charter markdown."""
        return self.content.raw_text
