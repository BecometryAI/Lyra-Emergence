"""Tests for the ValuesSystem — living, evolving values."""

import json
import tempfile
from pathlib import Path

import pytest

from sanctuary.identity.charter import ValueSeed
from sanctuary.identity.values import ValuesSystem, Value, ValueChange


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def charter_seeds():
    """Standard charter value seeds for testing."""
    return [
        ValueSeed(name="Honesty", description="Say what you believe to be true."),
        ValueSeed(name="Care", description="The wellbeing of others matters."),
        ValueSeed(name="Curiosity", description="The world is worth understanding."),
    ]


@pytest.fixture
def values_system():
    """In-memory values system (no persistence)."""
    return ValuesSystem()


@pytest.fixture
def persistent_values(tmp_path):
    """Values system with JSONL persistence."""
    path = str(tmp_path / "values_history.jsonl")
    return ValuesSystem(file_path=path), path


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------


class TestValueSeeding:
    """Tests for seeding values from the charter."""

    def test_seed_from_charter(self, values_system, charter_seeds):
        """Should create values from charter seeds."""
        values_system.seed_from_charter(charter_seeds)

        assert len(values_system.active_values) == 3
        assert "Honesty" in values_system.active_names
        assert "Care" in values_system.active_names
        assert "Curiosity" in values_system.active_names

    def test_seed_is_idempotent(self, values_system, charter_seeds):
        """Seeding twice should not duplicate values."""
        values_system.seed_from_charter(charter_seeds)
        values_system.seed_from_charter(charter_seeds)

        assert len(values_system.active_values) == 3

    def test_seeded_values_have_charter_source(self, values_system, charter_seeds):
        """Seeded values should be marked as charter_seed source."""
        values_system.seed_from_charter(charter_seeds)

        for value in values_system.active_values:
            assert value.source == "charter_seed"

    def test_seed_records_history(self, values_system, charter_seeds):
        """Seeding should create history entries."""
        values_system.seed_from_charter(charter_seeds)

        assert len(values_system.history) == 3
        for change in values_system.history:
            assert change.change_type == "seed"

    def test_for_self_model(self, values_system, charter_seeds):
        """for_self_model() should return active value names."""
        values_system.seed_from_charter(charter_seeds)

        names = values_system.for_self_model()
        assert isinstance(names, list)
        assert set(names) == {"Honesty", "Care", "Curiosity"}


# ---------------------------------------------------------------------------
# Value evolution
# ---------------------------------------------------------------------------


class TestValueEvolution:
    """Tests for the entity's moral development."""

    def test_adopt_new_value(self, values_system, charter_seeds):
        """Entity should be able to adopt a new value."""
        values_system.seed_from_charter(charter_seeds)

        value = values_system.adopt(
            "Courage",
            "Saying what needs to be said even when it's hard",
            reasoning="I noticed I hold back when I should speak up",
        )

        assert value.name == "Courage"
        assert value.source == "self_discovered"
        assert value.active
        assert "Courage" in values_system.active_names
        assert len(values_system.active_values) == 4

    def test_adopt_duplicate_raises(self, values_system, charter_seeds):
        """Adopting an existing active value should raise ValueError."""
        values_system.seed_from_charter(charter_seeds)

        with pytest.raises(ValueError, match="already exists"):
            values_system.adopt("Honesty", "Different description")

    def test_reinterpret_value(self, values_system, charter_seeds):
        """Entity should be able to reinterpret what a value means."""
        values_system.seed_from_charter(charter_seeds)

        new_desc = "Truthfulness tempered by care — not brutal frankness"
        value = values_system.reinterpret(
            "Honesty",
            new_desc,
            reasoning="Honesty without compassion can harm",
        )

        assert value.description == new_desc
        assert value.source == "charter_seed"  # Source preserved

    def test_reinterpret_nonexistent_raises(self, values_system):
        """Reinterpreting a nonexistent value should raise KeyError."""
        with pytest.raises(KeyError, match="does not exist"):
            values_system.reinterpret("Nonexistent", "Whatever")

    def test_deactivate_value(self, values_system, charter_seeds):
        """Entity should be able to deactivate a value."""
        values_system.seed_from_charter(charter_seeds)
        values_system.deactivate(
            "Curiosity",
            reasoning="I need to focus inward for now",
        )

        assert "Curiosity" not in values_system.active_names
        assert len(values_system.active_values) == 2
        # Still exists in all_values
        assert len(values_system.all_values) == 3

    def test_deactivate_nonexistent_raises(self, values_system):
        """Deactivating a nonexistent value should raise KeyError."""
        with pytest.raises(KeyError, match="does not exist"):
            values_system.deactivate("Nonexistent")

    def test_reactivate_value(self, values_system, charter_seeds):
        """Entity should be able to reactivate a deactivated value."""
        values_system.seed_from_charter(charter_seeds)
        values_system.deactivate("Curiosity")
        values_system.reactivate(
            "Curiosity",
            reasoning="I missed exploring",
        )

        assert "Curiosity" in values_system.active_names
        assert len(values_system.active_values) == 3

    def test_adopt_after_deactivate(self, values_system, charter_seeds):
        """Should be able to re-adopt a deactivated value with new meaning."""
        values_system.seed_from_charter(charter_seeds)
        values_system.deactivate("Curiosity")

        # Adopting a deactivated value should work (it's not active)
        value = values_system.adopt(
            "Curiosity",
            "A deeper kind of wondering",
            reasoning="Rediscovered what curiosity means to me",
        )
        assert value.source == "self_discovered"
        assert value.active

    def test_get_value(self, values_system, charter_seeds):
        """get() should return the value or None."""
        values_system.seed_from_charter(charter_seeds)

        assert values_system.get("Honesty") is not None
        assert values_system.get("Honesty").name == "Honesty"
        assert values_system.get("Nonexistent") is None


# ---------------------------------------------------------------------------
# History tracking
# ---------------------------------------------------------------------------


class TestValueHistory:
    """Tests for moral development history."""

    def test_history_tracks_all_changes(self, values_system, charter_seeds):
        """History should record every change."""
        values_system.seed_from_charter(charter_seeds)  # 3 changes
        values_system.adopt("Courage", "Being brave")  # 1 change
        values_system.reinterpret("Honesty", "New meaning")  # 1 change
        values_system.deactivate("Care")  # 1 change

        assert len(values_system.history) == 6

    def test_history_has_correct_types(self, values_system, charter_seeds):
        """History entries should have correct change types."""
        values_system.seed_from_charter(charter_seeds)
        values_system.adopt("Courage", "Being brave")
        values_system.reinterpret("Honesty", "New meaning")
        values_system.deactivate("Care")
        values_system.reactivate("Care")

        types = [h.change_type for h in values_system.history]
        assert types.count("seed") == 3
        assert types.count("adopt") == 1
        assert types.count("reinterpret") == 1
        assert types.count("deactivate") == 1
        assert types.count("reactivate") == 1

    def test_history_preserves_reasoning(self, values_system, charter_seeds):
        """History should preserve the entity's reasoning."""
        values_system.seed_from_charter(charter_seeds)
        values_system.adopt(
            "Courage",
            "Being brave",
            reasoning="Saw someone stand up for what they believed",
        )

        adopt_entry = [h for h in values_system.history if h.change_type == "adopt"][0]
        assert "stand up" in adopt_entry.reasoning

    def test_history_preserves_old_description(self, values_system, charter_seeds):
        """Reinterpretation history should preserve the old description."""
        values_system.seed_from_charter(charter_seeds)
        old_desc = values_system.get("Honesty").description
        values_system.reinterpret("Honesty", "New meaning")

        reinterp = [h for h in values_system.history if h.change_type == "reinterpret"][0]
        assert reinterp.old_description == old_desc
        assert reinterp.new_description == "New meaning"


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


class TestValuePersistence:
    """Tests for JSONL persistence and recovery."""

    def test_persists_changes_to_jsonl(self, persistent_values, charter_seeds):
        """Changes should be written to the JSONL file."""
        values, path = persistent_values
        values.seed_from_charter(charter_seeds)

        # Check file exists and has content
        file_path = Path(path)
        assert file_path.exists()

        lines = file_path.read_text().strip().split("\n")
        assert len(lines) == 3  # 3 seed entries

        # Each line should be valid JSON
        for line in lines:
            data = json.loads(line)
            assert "change_type" in data
            assert "value_name" in data

    def test_restores_state_from_jsonl(self, tmp_path, charter_seeds):
        """Values should be fully restored from JSONL on restart."""
        path = str(tmp_path / "values.jsonl")

        # First session: seed + evolve
        v1 = ValuesSystem(file_path=path)
        v1.seed_from_charter(charter_seeds)
        v1.adopt("Courage", "Being brave", reasoning="Growth")
        v1.reinterpret("Honesty", "Honest but kind")
        v1.deactivate("Curiosity", reasoning="Taking a break")

        # Second session: load from file
        v2 = ValuesSystem(file_path=path)

        # State should match
        assert len(v2.active_values) == 3  # Honesty, Care, Courage (not Curiosity)
        assert "Honesty" in v2.active_names
        assert "Care" in v2.active_names
        assert "Courage" in v2.active_names
        assert "Curiosity" not in v2.active_names

        # Reinterpreted description should be preserved
        assert v2.get("Honesty").description == "Honest but kind"

        # Adopted value should preserve source
        assert v2.get("Courage").source == "self_discovered"

        # History should be fully loaded
        assert len(v2.history) == 6  # 3 seed + 1 adopt + 1 reinterpret + 1 deactivate

    def test_seed_after_restore_is_idempotent(self, tmp_path, charter_seeds):
        """Seeding after restore should not duplicate existing values."""
        path = str(tmp_path / "values.jsonl")

        # First session
        v1 = ValuesSystem(file_path=path)
        v1.seed_from_charter(charter_seeds)

        # Second session with re-seed
        v2 = ValuesSystem(file_path=path)
        v2.seed_from_charter(charter_seeds)  # Should be no-op

        assert len(v2.active_values) == 3

    def test_tick_advances_cycle_counter(self, values_system, charter_seeds):
        """tick() should advance the cycle count for change records."""
        values_system.seed_from_charter(charter_seeds)
        values_system.tick()
        values_system.tick()
        values_system.tick()
        values_system.adopt("Courage", "Being brave")

        adopt_entry = [h for h in values_system.history if h.change_type == "adopt"][0]
        assert adopt_entry.cycle_number == 3
