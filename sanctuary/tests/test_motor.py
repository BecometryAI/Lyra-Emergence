"""Tests for the Motor — action execution for the experiential core.

Tests speech emission, memory execution, goal forwarding, and the
feedback loop back to the sensorium.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from sanctuary.core.schema import (
    CognitiveOutput,
    EmotionalOutput,
    GoalProposal,
    MemoryOp,
)
from sanctuary.motor.motor import Motor


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def motor():
    """A fresh motor."""
    return Motor()


@pytest.fixture
def motor_with_feedback():
    """A motor with a feedback handler that records calls."""
    m = Motor()
    feedback_log = []

    def feedback_handler(action_type, description, success):
        feedback_log.append((action_type, description, success))

    m.set_feedback_handler(feedback_handler)
    return m, feedback_log


@pytest.fixture
def mock_memory():
    """A mock memory substrate."""
    memory = AsyncMock()
    memory.execute_ops = AsyncMock(return_value=["ok"])
    memory.tick = MagicMock()
    return memory


@pytest.fixture
def mock_goal_integrator():
    """A mock goal integrator."""
    gi = MagicMock()
    gi.integrate_proposals = MagicMock(return_value=["added:goal_1"])
    return gi


@pytest.fixture
def mock_authority():
    """A mock authority manager."""
    return MagicMock()


# ---------------------------------------------------------------------------
# Speech execution
# ---------------------------------------------------------------------------


class TestSpeechExecution:
    """Test external speech emission."""

    @pytest.mark.asyncio
    async def test_speech_emitted_to_handler(self, motor):
        """Speech is sent to registered handlers."""
        received = []
        async def handler(text):
            received.append(text)

        motor.on_speech(handler)

        output = CognitiveOutput(external_speech="Hello world")
        await motor.execute(output)

        assert received == ["Hello world"]

    @pytest.mark.asyncio
    async def test_speech_emitted_to_multiple_handlers(self, motor):
        """Speech goes to all registered handlers."""
        log1, log2 = [], []

        async def handler1(text):
            log1.append(text)

        async def handler2(text):
            log2.append(text)

        motor.on_speech(handler1)
        motor.on_speech(handler2)

        output = CognitiveOutput(external_speech="Hi there")
        await motor.execute(output)

        assert log1 == ["Hi there"]
        assert log2 == ["Hi there"]

    @pytest.mark.asyncio
    async def test_no_speech_when_none(self, motor):
        """No handlers called when external_speech is None."""
        called = []
        async def handler(text):
            called.append(text)

        motor.on_speech(handler)

        output = CognitiveOutput(external_speech=None)
        await motor.execute(output)

        assert called == []

    @pytest.mark.asyncio
    async def test_speech_without_handlers(self, motor):
        """Speech without handlers doesn't crash."""
        output = CognitiveOutput(external_speech="Into the void")
        await motor.execute(output)

        assert motor.stats["speech_emitted"] == 1

    @pytest.mark.asyncio
    async def test_speech_handler_error_doesnt_crash(self, motor):
        """A failing handler doesn't stop execution."""
        async def bad_handler(text):
            raise RuntimeError("handler error")

        motor.on_speech(bad_handler)

        output = CognitiveOutput(external_speech="Test")
        await motor.execute(output)  # Should not raise

        assert motor.stats["speech_emitted"] == 1


# ---------------------------------------------------------------------------
# Motor feedback
# ---------------------------------------------------------------------------


class TestMotorFeedback:
    """Test that actions produce feedback percepts."""

    @pytest.mark.asyncio
    async def test_speech_produces_feedback(self, motor_with_feedback):
        """Speaking produces a feedback entry."""
        motor, log = motor_with_feedback

        output = CognitiveOutput(external_speech="Hello")
        await motor.execute(output)

        assert len(log) == 1
        action_type, description, success = log[0]
        assert action_type == "speech"
        assert "spoke" in description
        assert success is True

    @pytest.mark.asyncio
    async def test_journal_produces_feedback(self, motor_with_feedback, mock_memory):
        """Journal entries produce feedback."""
        motor, log = motor_with_feedback

        output = CognitiveOutput(
            memory_ops=[
                MemoryOp(type="journal", content="Today I learned something new")
            ]
        )
        await motor.execute(output, memory=mock_memory)

        journal_feedback = [
            entry for entry in log if entry[0] == "journal"
        ]
        assert len(journal_feedback) == 1

    @pytest.mark.asyncio
    async def test_significant_memory_produces_feedback(
        self, motor_with_feedback, mock_memory
    ):
        """High-significance memory writes produce feedback."""
        motor, log = motor_with_feedback

        output = CognitiveOutput(
            memory_ops=[
                MemoryOp(
                    type="write_episodic",
                    content="A pivotal moment",
                    significance=8,
                )
            ]
        )
        await motor.execute(output, memory=mock_memory)

        mem_feedback = [
            entry for entry in log if entry[0] == "memory_write"
        ]
        assert len(mem_feedback) == 1

    @pytest.mark.asyncio
    async def test_low_significance_memory_no_feedback(
        self, motor_with_feedback, mock_memory
    ):
        """Low-significance memory writes don't produce feedback."""
        motor, log = motor_with_feedback

        output = CognitiveOutput(
            memory_ops=[
                MemoryOp(
                    type="write_episodic",
                    content="A minor detail",
                    significance=3,
                )
            ]
        )
        await motor.execute(output, memory=mock_memory)

        mem_feedback = [
            entry for entry in log if entry[0] == "memory_write"
        ]
        assert len(mem_feedback) == 0

    @pytest.mark.asyncio
    async def test_goal_add_produces_feedback(
        self, motor_with_feedback, mock_goal_integrator, mock_authority
    ):
        """Adding a goal produces feedback."""
        motor, log = motor_with_feedback

        output = CognitiveOutput(
            goal_proposals=[
                GoalProposal(action="add", goal="understand the user's mood")
            ]
        )
        await motor.execute(
            output,
            goal_integrator=mock_goal_integrator,
            authority=mock_authority,
        )

        goal_feedback = [entry for entry in log if entry[0] == "goal_set"]
        assert len(goal_feedback) == 1


# ---------------------------------------------------------------------------
# Memory execution
# ---------------------------------------------------------------------------


class TestMemoryExecution:
    """Test memory operation execution through the motor."""

    @pytest.mark.asyncio
    async def test_memory_ops_forwarded(self, motor, mock_memory):
        """Memory ops are forwarded to the memory substrate."""
        output = CognitiveOutput(
            memory_ops=[
                MemoryOp(type="write_episodic", content="Test memory"),
            ],
            emotional_state=EmotionalOutput(felt_quality="curious"),
        )
        await motor.execute(output, memory=mock_memory)

        mock_memory.execute_ops.assert_called_once()
        args = mock_memory.execute_ops.call_args
        assert len(args[0][0]) == 1
        assert args[1]["emotional_tone"] == "curious"

    @pytest.mark.asyncio
    async def test_memory_tick_called(self, motor, mock_memory):
        """Memory tick is called each execution."""
        output = CognitiveOutput()
        await motor.execute(output, memory=mock_memory)
        mock_memory.tick.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_memory_substrate(self, motor):
        """No crash when memory substrate is None."""
        output = CognitiveOutput(
            memory_ops=[MemoryOp(type="write_episodic", content="Lost")]
        )
        await motor.execute(output, memory=None)  # Should not raise


# ---------------------------------------------------------------------------
# Goal execution
# ---------------------------------------------------------------------------


class TestGoalExecution:
    """Test goal proposal forwarding."""

    @pytest.mark.asyncio
    async def test_goals_forwarded_to_integrator(
        self, motor, mock_goal_integrator, mock_authority
    ):
        """Goal proposals are forwarded to the scaffold's goal integrator."""
        output = CognitiveOutput(
            goal_proposals=[
                GoalProposal(action="add", goal="learn something"),
            ]
        )
        await motor.execute(
            output,
            goal_integrator=mock_goal_integrator,
            authority=mock_authority,
        )

        mock_goal_integrator.integrate_proposals.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_goal_integrator(self, motor, mock_authority):
        """No crash when goal integrator is not available."""
        output = CognitiveOutput(
            goal_proposals=[
                GoalProposal(action="add", goal="should be ignored"),
            ]
        )
        await motor.execute(output, goal_integrator=None, authority=mock_authority)


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------


class TestMotorStats:
    """Test motor execution statistics."""

    @pytest.mark.asyncio
    async def test_stats_tracking(self, motor, mock_memory):
        """Stats accumulate across executions."""
        output1 = CognitiveOutput(external_speech="Hello")
        output2 = CognitiveOutput(
            external_speech="World",
            memory_ops=[MemoryOp(type="write_episodic", content="test")],
        )

        await motor.execute(output1)
        await motor.execute(output2, memory=mock_memory)

        stats = motor.stats
        assert stats["speech_emitted"] == 2
        assert stats["memory_ops_executed"] == 1
