"""Tests for Phase 2.1: Interruption capability."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from mind.cognitive_core.communication import (
    InterruptionSystem,
    InterruptionRequest,
    InterruptionReason,
)


class TestInterruptionSystem:
    """Tests for the InterruptionSystem."""

    def test_initialization_defaults(self):
        """Test default initialization."""
        system = InterruptionSystem()
        assert system.urgency_threshold == 0.85
        assert system.cooldown_seconds == 60
        assert system.interruption_count == 0
        assert system.last_interruption_time is None

    def test_initialization_with_config(self):
        """Test initialization with custom config."""
        system = InterruptionSystem(config={
            "urgency_threshold": 0.9,
            "cooldown_seconds": 30,
        })
        assert system.urgency_threshold == 0.9
        assert system.cooldown_seconds == 30

    def test_threshold_clamped(self):
        """Urgency threshold is clamped to [0.5, 1.0]."""
        low = InterruptionSystem(config={"urgency_threshold": 0.1})
        assert low.urgency_threshold == 0.5

        high = InterruptionSystem(config={"urgency_threshold": 1.5})
        assert high.urgency_threshold == 1.0

    def test_no_interruption_when_human_not_speaking(self):
        """No interruption if human is not mid-turn."""
        system = InterruptionSystem()
        result = system.evaluate(
            workspace_state=MagicMock(),
            emotional_state={"valence": -0.9, "arousal": 0.95},
            active_urges=[],
            is_human_speaking=False
        )
        assert result is None

    def test_safety_trigger_fires(self):
        """Safety concern should generate interruption."""
        system = InterruptionSystem(config={"urgency_threshold": 0.85})

        workspace = MagicMock()
        percept = MagicMock()
        percept.metadata = {"safety_concern": True}
        workspace.percepts = {"p1": percept}

        request = system.evaluate(
            workspace_state=workspace,
            emotional_state={"valence": 0.0, "arousal": 0.0},
            active_urges=[],
            is_human_speaking=True
        )

        assert request is not None
        assert request.reason == InterruptionReason.SAFETY
        assert request.urgency >= 0.85

    def test_value_conflict_trigger(self):
        """High-severity value conflict should generate interruption."""
        system = InterruptionSystem(config={"urgency_threshold": 0.85})

        workspace = MagicMock()
        percept = MagicMock()
        percept.modality = "introspection"
        percept.raw = {"type": "value_conflict", "severity": 0.9}
        percept.metadata = {}
        workspace.percepts = {"p1": percept}

        request = system.evaluate(
            workspace_state=workspace,
            emotional_state={"valence": 0.0, "arousal": 0.0},
            active_urges=[],
            is_human_speaking=True
        )

        assert request is not None
        assert request.reason == InterruptionReason.VALUE_CONFLICT

    def test_low_severity_value_conflict_no_trigger(self):
        """Low-severity value conflict should NOT trigger interruption."""
        system = InterruptionSystem()

        workspace = MagicMock()
        percept = MagicMock()
        percept.modality = "introspection"
        percept.raw = {"type": "value_conflict", "severity": 0.3}
        percept.salience = 0.3
        percept.complexity = 5
        percept.metadata = {}
        workspace.percepts = {"p1": percept}

        request = system.evaluate(
            workspace_state=workspace,
            emotional_state={"valence": 0.0, "arousal": 0.0},
            active_urges=[],
            is_human_speaking=True
        )

        assert request is None

    def test_critical_insight_trigger(self):
        """High-salience introspective insight should generate interruption."""
        system = InterruptionSystem(config={"urgency_threshold": 0.85})

        workspace = MagicMock()
        percept = MagicMock()
        percept.modality = "introspection"
        percept.salience = 0.95
        percept.complexity = 25
        percept.raw = {"type": "self_model_update"}
        percept.metadata = {}
        workspace.percepts = {"p1": percept}

        request = system.evaluate(
            workspace_state=workspace,
            emotional_state={"valence": 0.0, "arousal": 0.0},
            active_urges=[],
            is_human_speaking=True
        )

        assert request is not None
        assert request.reason == InterruptionReason.CRITICAL_INSIGHT

    def test_emotional_urgency_trigger(self):
        """Extreme distress should generate interruption."""
        system = InterruptionSystem(config={"urgency_threshold": 0.85})

        workspace = MagicMock()
        workspace.percepts = {}

        request = system.evaluate(
            workspace_state=workspace,
            emotional_state={"valence": -0.8, "arousal": 0.95},
            active_urges=[],
            is_human_speaking=True
        )

        assert request is not None
        assert request.reason == InterruptionReason.EMOTIONAL_URGENCY

    def test_correction_trigger(self):
        """High-intensity correction urge should generate interruption."""
        system = InterruptionSystem(config={"urgency_threshold": 0.85})

        urge = MagicMock()
        urge.drive_type = MagicMock()
        urge.drive_type.value = "correction"
        urge.intensity = 0.95
        urge.content = "This is factually wrong"

        workspace = MagicMock()
        workspace.percepts = {}

        request = system.evaluate(
            workspace_state=workspace,
            emotional_state={"valence": 0.0, "arousal": 0.0},
            active_urges=[urge],
            is_human_speaking=True
        )

        assert request is not None
        assert request.reason == InterruptionReason.CORRECTION

    def test_cooldown_prevents_rapid_interruptions(self):
        """Cooldown should prevent repeated interruptions."""
        system = InterruptionSystem(config={
            "urgency_threshold": 0.85,
            "cooldown_seconds": 60
        })

        workspace = MagicMock()
        percept = MagicMock()
        percept.metadata = {"safety_concern": True}
        workspace.percepts = {"p1": percept}

        # First interruption succeeds
        request1 = system.evaluate(
            workspace_state=workspace,
            emotional_state={"valence": 0.0, "arousal": 0.0},
            active_urges=[],
            is_human_speaking=True
        )
        assert request1 is not None
        system.record_interruption(request1)

        # Second within cooldown fails
        request2 = system.evaluate(
            workspace_state=workspace,
            emotional_state={"valence": 0.0, "arousal": 0.0},
            active_urges=[],
            is_human_speaking=True
        )
        assert request2 is None

    def test_cooldown_expires(self):
        """After cooldown expires, interruption should fire again."""
        system = InterruptionSystem(config={
            "urgency_threshold": 0.85,
            "cooldown_seconds": 60
        })

        # Simulate past interruption
        system.last_interruption_time = datetime.now() - timedelta(seconds=120)

        workspace = MagicMock()
        percept = MagicMock()
        percept.metadata = {"safety_concern": True}
        workspace.percepts = {"p1": percept}

        request = system.evaluate(
            workspace_state=workspace,
            emotional_state={"valence": 0.0, "arousal": 0.0},
            active_urges=[],
            is_human_speaking=True
        )
        assert request is not None

    def test_record_interruption(self):
        """Recording interruption updates state correctly."""
        system = InterruptionSystem()

        request = InterruptionRequest(
            reason=InterruptionReason.SAFETY,
            urgency=0.95,
            content_hint="Safety concern"
        )
        system.record_interruption(request)

        assert system.interruption_count == 1
        assert system.last_interruption_time is not None
        assert len(system.interruption_history) == 1
        assert system.interruption_history[0]["reason"] == "safety"

    def test_get_summary(self):
        """Summary should contain expected fields."""
        system = InterruptionSystem()
        summary = system.get_summary()

        assert "interruption_count" in summary
        assert "on_cooldown" in summary
        assert "urgency_threshold" in summary
        assert summary["interruption_count"] == 0
        assert summary["on_cooldown"] is False

    def test_below_threshold_no_interruption(self):
        """Normal emotional states should not trigger interruption."""
        system = InterruptionSystem(config={"urgency_threshold": 0.85})

        workspace = MagicMock()
        workspace.percepts = {}

        request = system.evaluate(
            workspace_state=workspace,
            emotional_state={"valence": 0.3, "arousal": 0.5},
            active_urges=[],
            is_human_speaking=True
        )
        assert request is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
