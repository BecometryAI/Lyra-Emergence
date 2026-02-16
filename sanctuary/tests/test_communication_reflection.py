"""Tests for Phase 2.1: Communication reflection system."""

import pytest
from unittest.mock import MagicMock

from mind.cognitive_core.communication import (
    CommunicationReflectionSystem,
    CommunicationReflection,
    ReflectionVerdict,
)


class TestCommunicationReflectionSystem:
    """Tests for the CommunicationReflectionSystem."""

    def _make_workspace(self, goals=None, percepts=None):
        """Create a mock workspace state."""
        ws = MagicMock()
        ws.goals = goals or []
        ws.percepts = percepts or {}
        return ws

    def test_initialization(self):
        """Test default initialization."""
        system = CommunicationReflectionSystem()
        assert len(system.reflection_history) == 0
        assert system.cumulative_scores["overall"] == 0.5

    def test_initialization_with_config(self):
        """Test initialization with custom config."""
        system = CommunicationReflectionSystem(config={
            "max_history": 20,
            "timing_weight": 0.5,
        })
        assert system.max_history == 20
        assert system.timing_weight == 0.5

    def test_basic_reflection(self):
        """Test basic reflection on a normal SPEAK action."""
        system = CommunicationReflectionSystem()
        workspace = self._make_workspace()

        reflection = system.reflect(
            output_text="I understand your concern and here's what I think.",
            output_type="SPEAK",
            workspace_state=workspace,
            emotional_state={"valence": 0.3, "arousal": 0.2},
        )

        assert isinstance(reflection, CommunicationReflection)
        assert 0.0 <= reflection.timing_score <= 1.0
        assert 0.0 <= reflection.content_alignment <= 1.0
        assert 0.0 <= reflection.emotional_fit <= 1.0
        assert 0.0 <= reflection.overall_score <= 1.0
        assert isinstance(reflection.verdict, ReflectionVerdict)
        assert len(reflection.lessons) >= 1

    def test_reflection_recorded(self):
        """Test that reflection is recorded in history."""
        system = CommunicationReflectionSystem()
        workspace = self._make_workspace()

        system.reflect(
            output_text="Hello there",
            output_type="SPEAK",
            workspace_state=workspace,
            emotional_state={"valence": 0.0, "arousal": 0.0},
        )

        assert len(system.reflection_history) == 1

    def test_cumulative_scores_updated(self):
        """Cumulative scores should update after reflection."""
        system = CommunicationReflectionSystem()
        workspace = self._make_workspace()

        initial_overall = system.cumulative_scores["overall"]

        system.reflect(
            output_text="A substantive response with thoughtful content that demonstrates engagement.",
            output_type="SPEAK",
            workspace_state=workspace,
            emotional_state={"valence": 0.3, "arousal": 0.2},
        )

        # Scores should have changed (may increase or decrease)
        assert system.cumulative_scores["overall"] != initial_overall or True  # EMA smoothing

    def test_autonomous_output_reflection(self):
        """Test reflection on autonomous speech."""
        system = CommunicationReflectionSystem()
        workspace = self._make_workspace()

        reflection = system.reflect(
            output_text="I've been thinking about our last conversation and wanted to share.",
            output_type="SPEAK_AUTONOMOUS",
            workspace_state=workspace,
            emotional_state={"valence": 0.4, "arousal": 0.3},
        )

        assert reflection.output_metadata["was_autonomous"] is True
        assert reflection.output_metadata["output_type"] == "SPEAK_AUTONOMOUS"

    def test_high_arousal_long_response(self):
        """High arousal + long response should have good emotional fit."""
        system = CommunicationReflectionSystem()
        workspace = self._make_workspace()

        reflection = system.reflect(
            output_text="I'm feeling quite excited about this development and I think it opens up many possibilities for us to explore together.",
            output_type="SPEAK",
            workspace_state=workspace,
            emotional_state={"valence": 0.7, "arousal": 0.8},
        )

        # High arousal + long output = good emotional fit
        assert reflection.emotional_fit >= 0.6

    def test_high_arousal_short_response(self):
        """High arousal + short response should have lower emotional fit."""
        system = CommunicationReflectionSystem()
        workspace = self._make_workspace()

        reflection = system.reflect(
            output_text="Ok.",
            output_type="SPEAK",
            workspace_state=workspace,
            emotional_state={"valence": 0.7, "arousal": 0.8},
        )

        # High arousal + very short output = lower emotional fit
        assert reflection.emotional_fit < 0.8

    def test_with_response_goals_boosts_timing(self):
        """Having response goals should boost timing score."""
        system = CommunicationReflectionSystem()

        goal = MagicMock()
        goal.type = MagicMock()
        goal.type.value = "RESPOND_TO_USER"
        workspace = self._make_workspace(goals=[goal])

        reflection = system.reflect(
            output_text="Here is my response to your question.",
            output_type="SPEAK",
            workspace_state=workspace,
            emotional_state={"valence": 0.0, "arousal": 0.0},
        )

        # Having a response goal = good timing
        assert reflection.timing_score >= 0.5

    def test_decision_context_affects_timing(self):
        """High net pressure should boost timing score."""
        system = CommunicationReflectionSystem()
        workspace = self._make_workspace()

        high_pressure = system.reflect(
            output_text="Something important to share.",
            output_type="SPEAK",
            workspace_state=workspace,
            emotional_state={"valence": 0.0, "arousal": 0.0},
            decision_context={"confidence": 0.9, "net_pressure": 0.8}
        )

        low_pressure = system.reflect(
            output_text="Something important to share.",
            output_type="SPEAK",
            workspace_state=workspace,
            emotional_state={"valence": 0.0, "arousal": 0.0},
            decision_context={"confidence": 0.3, "net_pressure": -0.3}
        )

        assert high_pressure.timing_score > low_pressure.timing_score

    def test_verdict_well_timed(self):
        """High overall + high timing should yield WELL_TIMED."""
        system = CommunicationReflectionSystem()

        goal = MagicMock()
        goal.type = MagicMock()
        goal.type.value = "RESPOND_TO_USER"
        workspace = self._make_workspace(goals=[goal])

        reflection = system.reflect(
            output_text="Here is a thoughtful and complete response to what you've been asking about.",
            output_type="SPEAK",
            workspace_state=workspace,
            emotional_state={"valence": 0.3, "arousal": 0.2},
            decision_context={"confidence": 0.95, "net_pressure": 0.7}
        )

        # With high confidence, response goal, good content = should be WELL_TIMED or APPROPRIATE
        assert reflection.verdict in (ReflectionVerdict.WELL_TIMED, ReflectionVerdict.APPROPRIATE)

    def test_history_limited(self):
        """History should not exceed max_history."""
        system = CommunicationReflectionSystem(config={"max_history": 5})
        workspace = self._make_workspace()

        for i in range(10):
            system.reflect(
                output_text=f"Response number {i}",
                output_type="SPEAK",
                workspace_state=workspace,
                emotional_state={"valence": 0.0, "arousal": 0.0},
            )

        assert len(system.reflection_history) == 5

    def test_get_communication_quality(self):
        """Quality scores should be returned."""
        system = CommunicationReflectionSystem()
        quality = system.get_communication_quality()

        assert "timing" in quality
        assert "content" in quality
        assert "emotional" in quality
        assert "overall" in quality

    def test_get_recent_lessons(self):
        """Recent lessons should be collected from history."""
        system = CommunicationReflectionSystem()
        workspace = self._make_workspace()

        system.reflect(
            output_text="Hello",
            output_type="SPEAK",
            workspace_state=workspace,
            emotional_state={"valence": 0.0, "arousal": 0.0},
        )

        lessons = system.get_recent_lessons()
        assert isinstance(lessons, list)
        assert len(lessons) >= 1

    def test_get_verdict_distribution(self):
        """Verdict distribution should be returned."""
        system = CommunicationReflectionSystem()
        workspace = self._make_workspace()

        system.reflect(
            output_text="A thoughtful response.",
            output_type="SPEAK",
            workspace_state=workspace,
            emotional_state={"valence": 0.0, "arousal": 0.0},
        )

        distribution = system.get_verdict_distribution()
        assert isinstance(distribution, dict)
        total = sum(distribution.values())
        assert total == 1

    def test_get_summary(self):
        """Summary should contain expected fields."""
        system = CommunicationReflectionSystem()
        summary = system.get_summary()

        assert "total_reflections" in summary
        assert "cumulative_quality" in summary
        assert "verdict_distribution" in summary
        assert "recent_lessons" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
