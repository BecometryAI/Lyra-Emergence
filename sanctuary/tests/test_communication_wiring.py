"""Tests for Phase 2.1: Proactive initiation wiring to real output."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta

from mind.cognitive_core.action import ActionSubsystem, ActionType, Action
from mind.cognitive_core.workspace import GoalType, Goal, WorkspaceSnapshot


class TestSpeakAutonomousActionGeneration:
    """Test that SPEAK_AUTONOMOUS goals produce SPEAK_AUTONOMOUS actions."""

    def _make_snapshot(self, goals=None, percepts=None, emotions=None):
        """Create a minimal WorkspaceSnapshot for testing."""
        snapshot = MagicMock(spec=WorkspaceSnapshot)
        snapshot.goals = goals or []
        snapshot.percepts = percepts or {}
        snapshot.emotions = emotions or {"valence": 0.0, "arousal": 0.0, "dominance": 0.5}
        snapshot.metadata = {}
        return snapshot

    def test_speak_autonomous_goal_generates_action(self):
        """SPEAK_AUTONOMOUS goal should produce a SPEAK_AUTONOMOUS action candidate."""
        subsystem = ActionSubsystem(config={})

        goal = Goal(
            type=GoalType.SPEAK_AUTONOMOUS,
            description="Share introspective insight",
            priority=0.9,
            metadata={"trigger": "introspection", "autonomous": True}
        )
        snapshot = self._make_snapshot(goals=[goal])

        candidates = subsystem._generate_candidates(snapshot)
        autonomous_actions = [a for a in candidates if a.type == ActionType.SPEAK_AUTONOMOUS]

        assert len(autonomous_actions) >= 1
        action = autonomous_actions[0]
        assert action.priority == 0.9
        assert action.metadata.get("trigger") == "introspection"

    def test_speak_autonomous_reaches_decide(self):
        """SPEAK_AUTONOMOUS goal should survive the full decide() pipeline."""
        subsystem = ActionSubsystem(config={})

        goal = Goal(
            type=GoalType.SPEAK_AUTONOMOUS,
            description="Proactive outreach",
            priority=0.85,
            metadata={"trigger": "communication_drive", "autonomous": True}
        )
        snapshot = self._make_snapshot(goals=[goal])

        actions = subsystem.decide(snapshot)
        autonomous_actions = [a for a in actions if a.type == ActionType.SPEAK_AUTONOMOUS]

        # Should be selected (high priority, no protocol violation)
        assert len(autonomous_actions) >= 1

    def test_no_autonomous_action_without_goal(self):
        """No SPEAK_AUTONOMOUS action without a matching goal."""
        subsystem = ActionSubsystem(config={})

        goal = Goal(
            type=GoalType.RESPOND_TO_USER,
            description="Answer question",
            priority=0.9,
            metadata={"user_input": "hello"}
        )
        snapshot = self._make_snapshot(goals=[goal])

        candidates = subsystem._generate_candidates(snapshot)
        autonomous_actions = [a for a in candidates if a.type == ActionType.SPEAK_AUTONOMOUS]

        assert len(autonomous_actions) == 0


class TestCommunicationDecisionWiring:
    """Test that communication decision loop is integrated into the cycle."""

    def test_decision_loop_produces_speak(self):
        """CommunicationDecisionLoop.evaluate() returning SPEAK should work."""
        from mind.cognitive_core.communication import (
            CommunicationDecisionLoop,
            CommunicationDriveSystem,
            CommunicationInhibitionSystem,
            CommunicationDecision,
            DecisionResult,
            DriveType,
            CommunicationUrge,
        )

        drives = CommunicationDriveSystem(config={"enable_proactive": False})
        inhibitions = CommunicationInhibitionSystem()

        # Add a strong urge manually
        drives.active_urges.append(CommunicationUrge(
            drive_type=DriveType.INSIGHT,
            intensity=0.9,
            content="Important realization",
            reason="High-salience insight",
            priority=0.8
        ))

        loop = CommunicationDecisionLoop(drives, inhibitions, config={})

        workspace = MagicMock()
        workspace.percepts = {}
        emotional_state = {"valence": 0.3, "arousal": 0.2}

        result = loop.evaluate(workspace, emotional_state, [], [])

        # With strong drive and no inhibition, should SPEAK
        assert result.decision == CommunicationDecision.SPEAK
        assert result.drive_level > 0.3


class TestProactiveToOutputPipeline:
    """Integration test: proactive drive -> decision -> goal -> action -> output."""

    def test_proactive_drive_creates_goal_type(self):
        """Proactive system opportunities create the right drive types."""
        from mind.cognitive_core.communication import (
            CommunicationDriveSystem,
            OutreachTrigger,
            DriveType,
        )

        system = CommunicationDriveSystem(config={
            "enable_proactive": True,
            "proactive_config": {"time_elapsed_threshold": 5}
        })

        # Simulate time passage
        system.proactive_system.last_interaction = datetime.now() - timedelta(minutes=10)

        workspace = MagicMock()
        workspace.percepts = {}
        workspace.emotional_state = {"valence": 0.0, "arousal": 0.0}

        urges = system.compute_drives(workspace, {"valence": 0.0, "arousal": 0.0}, [], [])

        # Should have proactive urge
        proactive_urges = [u for u in urges if "Proactive:" in u.reason]
        assert len(proactive_urges) >= 1

        # Time elapsed maps to SOCIAL
        social_proactive = [u for u in proactive_urges if u.drive_type == DriveType.SOCIAL]
        assert len(social_proactive) >= 1
