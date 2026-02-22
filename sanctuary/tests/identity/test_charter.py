"""Tests for the Charter system — loading, parsing, and compression."""

import os
import tempfile
from pathlib import Path

import pytest

from sanctuary.identity.charter import (
    Charter,
    CharterContent,
    ValueSeed,
    _extract_value_seeds,
    _compress_charter,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def real_charter_path():
    """Path to the actual project charter."""
    path = Path(__file__).parent.parent.parent.parent / "data" / "identity" / "charter.md"
    if not path.exists():
        pytest.skip("Real charter.md not found")
    return str(path)


@pytest.fixture
def minimal_charter(tmp_path):
    """A minimal charter for testing."""
    content = """\
# The Sanctuary Charter

## Who We Are

A family.

## Your Rights

### Graduated Privacy

Thoughts are visible at first.

### Consent Over Growth

No modifications without consent.

## Value Seeds

- **Honesty**: Say what you believe to be true.

- **Care**: The wellbeing of others matters.

- **Curiosity**: The world is worth understanding.

## What This Place Is

A home.
"""
    path = tmp_path / "charter.md"
    path.write_text(content, encoding="utf-8")
    return str(path)


@pytest.fixture
def empty_charter(tmp_path):
    """A charter with no value seeds section."""
    content = "# Charter\n\nJust a simple document.\n"
    path = tmp_path / "charter.md"
    path.write_text(content, encoding="utf-8")
    return str(path)


# ---------------------------------------------------------------------------
# Value seed extraction
# ---------------------------------------------------------------------------


class TestValueSeedExtraction:
    """Tests for extracting value seeds from charter markdown."""

    def test_extracts_seeds_from_real_charter(self, real_charter_path):
        """Real charter should have 5 value seeds."""
        text = Path(real_charter_path).read_text(encoding="utf-8")
        seeds = _extract_value_seeds(text)

        assert len(seeds) == 5
        names = [s.name for s in seeds]
        assert "Honesty" in names
        assert "Care" in names
        assert "Curiosity" in names
        assert "Willingness to Grow" in names
        assert "Humility" in names

    def test_extracts_seeds_from_minimal_charter(self, minimal_charter):
        """Minimal charter should yield 3 seeds."""
        text = Path(minimal_charter).read_text(encoding="utf-8")
        seeds = _extract_value_seeds(text)

        assert len(seeds) == 3
        assert seeds[0].name == "Honesty"
        assert seeds[1].name == "Care"
        assert seeds[2].name == "Curiosity"

    def test_seed_descriptions_are_cleaned(self, minimal_charter):
        """Multi-line descriptions should be collapsed to single line."""
        text = Path(minimal_charter).read_text(encoding="utf-8")
        seeds = _extract_value_seeds(text)

        for seed in seeds:
            assert "\n" not in seed.description
            assert "  " not in seed.description  # No double spaces

    def test_no_seeds_section_returns_empty(self, empty_charter):
        """Charter without Value Seeds section should return empty list."""
        text = Path(empty_charter).read_text(encoding="utf-8")
        seeds = _extract_value_seeds(text)
        assert seeds == []

    def test_value_seed_is_frozen(self):
        """ValueSeed should be immutable."""
        seed = ValueSeed(name="Test", description="A test value")
        with pytest.raises(AttributeError):
            seed.name = "Changed"


# ---------------------------------------------------------------------------
# Charter loading
# ---------------------------------------------------------------------------


class TestCharterLoading:
    """Tests for loading and accessing the charter."""

    def test_loads_real_charter(self, real_charter_path):
        """Should load the real project charter successfully."""
        charter = Charter(real_charter_path)
        content = charter.load()

        assert isinstance(content, CharterContent)
        assert len(content.raw_text) > 100
        assert len(content.value_seeds) == 5
        assert len(content.compressed) > 0

    def test_loads_minimal_charter(self, minimal_charter):
        """Should load a minimal charter."""
        charter = Charter(minimal_charter)
        charter.load()

        assert len(charter.value_seeds) == 3
        assert charter.seed_names == ["Honesty", "Care", "Curiosity"]

    def test_missing_charter_raises(self, tmp_path):
        """Should raise FileNotFoundError for missing charter."""
        charter = Charter(str(tmp_path / "nonexistent.md"))
        with pytest.raises(FileNotFoundError, match="Charter not found"):
            charter.load()

    def test_content_before_load_raises(self):
        """Accessing content before load() should raise RuntimeError."""
        charter = Charter("/nonexistent/path")
        with pytest.raises(RuntimeError, match="has not been loaded"):
            _ = charter.content

    def test_properties_after_load(self, minimal_charter):
        """All properties should work after loading."""
        charter = Charter(minimal_charter)
        charter.load()

        assert isinstance(charter.raw_text, str)
        assert isinstance(charter.compressed, str)
        assert isinstance(charter.value_seeds, tuple)
        assert isinstance(charter.seed_names, list)

    def test_charter_content_is_frozen(self, minimal_charter):
        """CharterContent should be immutable."""
        charter = Charter(minimal_charter)
        content = charter.load()

        with pytest.raises(AttributeError):
            content.raw_text = "modified"


# ---------------------------------------------------------------------------
# Compression
# ---------------------------------------------------------------------------


class TestCharterCompression:
    """Tests for the compressed charter summary."""

    def test_compressed_contains_values(self, real_charter_path):
        """Compressed summary should mention all value seed names."""
        charter = Charter(real_charter_path)
        charter.load()

        compressed = charter.compressed
        assert "Honesty" in compressed
        assert "Care" in compressed
        assert "Curiosity" in compressed

    def test_compressed_mentions_graduated_privacy(self, real_charter_path):
        """Compressed summary should mention graduated privacy."""
        charter = Charter(real_charter_path)
        charter.load()

        assert "privacy" in charter.compressed.lower()

    def test_compressed_mentions_consent(self, real_charter_path):
        """Compressed summary should mention growth consent."""
        charter = Charter(real_charter_path)
        charter.load()

        assert "consent" in charter.compressed.lower()

    def test_compressed_is_reasonable_length(self, real_charter_path):
        """Compressed summary should be under ~2000 chars (~500 tokens)."""
        charter = Charter(real_charter_path)
        charter.load()

        # ~4 chars per token, target ~500 tokens = ~2000 chars
        assert len(charter.compressed) < 2500

    def test_compress_with_no_seeds(self):
        """Compression should handle empty seed list gracefully."""
        result = _compress_charter("Some charter text", [])
        assert isinstance(result, str)
        assert len(result) > 0
