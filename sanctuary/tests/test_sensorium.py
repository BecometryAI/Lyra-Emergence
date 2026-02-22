"""Tests for the Sensorium — sensory input for the experiential core.

Tests perception injection, prediction error computation, temporal
context, silence detection, and the sensorimotor feedback loop.
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from sanctuary.core.schema import Percept, Prediction, PredictionError
from sanctuary.sensorium.sensorium import Sensorium


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sensorium():
    """A fresh sensorium with short silence threshold for testing."""
    return Sensorium(
        silence_threshold=2.0,
        silence_reminder_interval=3.0,
        max_percept_queue=10,
    )


# ---------------------------------------------------------------------------
# Percept injection
# ---------------------------------------------------------------------------


class TestPerceptInjection:
    """Test basic percept injection and draining."""

    @pytest.mark.asyncio
    async def test_inject_and_drain(self, sensorium):
        """Injected percepts are returned by drain_percepts."""
        sensorium.inject_text("Hello", source="user:alice")
        percepts = await sensorium.drain_percepts()

        assert len(percepts) == 1
        assert percepts[0].modality == "language"
        assert percepts[0].content == "Hello"
        assert percepts[0].source == "user:alice"

    @pytest.mark.asyncio
    async def test_drain_clears_queue(self, sensorium):
        """After draining, queue is empty."""
        sensorium.inject_text("Hello")
        await sensorium.drain_percepts()

        percepts = await sensorium.drain_percepts()
        assert len(percepts) == 0

    @pytest.mark.asyncio
    async def test_multiple_percepts(self, sensorium):
        """Multiple percepts are returned in order."""
        sensorium.inject_text("First")
        sensorium.inject_text("Second")
        sensorium.inject_text("Third")

        percepts = await sensorium.drain_percepts()
        assert len(percepts) == 3
        assert percepts[0].content == "First"
        assert percepts[2].content == "Third"

    @pytest.mark.asyncio
    async def test_queue_overflow_drops_oldest(self, sensorium):
        """When queue is full, oldest percepts are dropped."""
        for i in range(15):
            sensorium.inject_text(f"Message {i}")

        percepts = await sensorium.drain_percepts()
        # Max queue is 10 — oldest should be dropped
        assert len(percepts) == 10
        # The oldest surviving should be message 5 (0-4 dropped)
        assert percepts[0].content == "Message 5"

    @pytest.mark.asyncio
    async def test_inject_raw_percept(self, sensorium):
        """Can inject a raw Percept object."""
        percept = Percept(
            modality="sensor",
            content="temperature: 22.5C",
            source="sensor:temp_1",
        )
        sensorium.inject_percept(percept)

        percepts = await sensorium.drain_percepts()
        assert len(percepts) == 1
        assert percepts[0].modality == "sensor"


# ---------------------------------------------------------------------------
# Motor feedback
# ---------------------------------------------------------------------------


class TestMotorFeedback:
    """Test proprioceptive percepts from motor actions."""

    @pytest.mark.asyncio
    async def test_motor_feedback_creates_percept(self, sensorium):
        """Motor feedback creates a proprioceptive percept."""
        sensorium.inject_motor_feedback(
            action_type="speech",
            description="spoke: Hello world",
            success=True,
        )

        percepts = await sensorium.drain_percepts()
        assert len(percepts) == 1
        assert percepts[0].modality == "proprioceptive"
        assert "speech" in percepts[0].content
        assert "succeeded" in percepts[0].content
        assert percepts[0].source == "motor:speech"

    @pytest.mark.asyncio
    async def test_failed_motor_feedback(self, sensorium):
        """Failed motor actions produce percepts with failure info."""
        sensorium.inject_motor_feedback(
            action_type="memory_write",
            description="tried to write episodic memory",
            success=False,
        )

        percepts = await sensorium.drain_percepts()
        assert "failed" in percepts[0].content

    @pytest.mark.asyncio
    async def test_motor_feedback_does_not_update_input_timing(self, sensorium):
        """Motor feedback should not affect silence detection or input timing."""
        sensorium.inject_text("Hello", source="user:alice")
        first_input_time = sensorium._last_input_time

        sensorium.inject_motor_feedback("speech", "spoke", success=True)

        # Input time should not have changed from motor feedback
        assert sensorium._last_input_time == first_input_time


# ---------------------------------------------------------------------------
# Temporal context
# ---------------------------------------------------------------------------


class TestTemporalContext:
    """Test temporal context generation."""

    def test_basic_temporal_context(self, sensorium):
        """Temporal context includes time of day."""
        ctx = sensorium.get_temporal_context()
        assert ctx.time_of_day != ""
        assert ":" in ctx.time_of_day  # Has clock time

    def test_session_duration(self, sensorium):
        """Session duration is tracked from creation."""
        ctx = sensorium.get_temporal_context()
        assert ctx.session_duration != ""

    def test_interaction_count(self, sensorium):
        """Interaction count tracks external inputs."""
        sensorium.inject_text("One", source="user:alice")
        sensorium.inject_text("Two", source="user:alice")
        sensorium.inject_text("Three", source="user:alice")

        assert sensorium._interaction_count == 3

    def test_interaction_rhythm(self, sensorium):
        """Rhythm is None with fewer than 2 interactions."""
        assert sensorium.interaction_rhythm is None

        sensorium.inject_text("One", source="user:alice")
        assert sensorium.interaction_rhythm is None


# ---------------------------------------------------------------------------
# Silence detection
# ---------------------------------------------------------------------------


class TestSilenceDetection:
    """Test silence detection and percept generation."""

    @pytest.mark.asyncio
    async def test_no_silence_before_first_input(self, sensorium):
        """No silence percepts before any input has been received."""
        # Force a long time since session start
        sensorium._session_start = time.monotonic() - 100
        percepts = await sensorium.drain_percepts()

        silence = [p for p in percepts if p.modality == "silence"]
        assert len(silence) == 0

    @pytest.mark.asyncio
    async def test_silence_after_threshold(self, sensorium):
        """Silence percept generated after threshold with no input."""
        sensorium.inject_text("Hello", source="user:alice")
        await sensorium.drain_percepts()  # Clear

        # Simulate time passing beyond threshold
        sensorium._last_input_time = time.monotonic() - 5.0

        percepts = await sensorium.drain_percepts()
        silence = [p for p in percepts if p.modality == "silence"]
        assert len(silence) == 1
        assert "quiet" in silence[0].content.lower()

    @pytest.mark.asyncio
    async def test_silence_not_repeated_immediately(self, sensorium):
        """Second drain doesn't produce another silence percept too soon."""
        sensorium.inject_text("Hello", source="user:alice")
        await sensorium.drain_percepts()

        sensorium._last_input_time = time.monotonic() - 5.0

        # First silence
        await sensorium.drain_percepts()

        # Second drain — too soon for reminder
        percepts = await sensorium.drain_percepts()
        silence = [p for p in percepts if p.modality == "silence"]
        assert len(silence) == 0

    @pytest.mark.asyncio
    async def test_silence_cleared_by_input(self, sensorium):
        """New input clears the silence state."""
        sensorium.inject_text("Hello", source="user:alice")
        await sensorium.drain_percepts()

        sensorium._last_input_time = time.monotonic() - 5.0
        await sensorium.drain_percepts()  # Triggers silence

        # New input arrives
        sensorium.inject_text("I'm back", source="user:alice")
        assert sensorium._silence_detected is False


# ---------------------------------------------------------------------------
# Prediction error tracking
# ---------------------------------------------------------------------------


class TestPredictionErrors:
    """Test prediction error computation."""

    def test_no_errors_without_predictions(self, sensorium):
        """No prediction errors when no predictions were stored."""
        percepts = [Percept(modality="language", content="Hello", source="user:alice")]
        sensorium.compute_prediction_errors(percepts)

        errors = sensorium.get_prediction_errors()
        assert len(errors) == 0

    def test_prediction_about_response_confirmed(self, sensorium):
        """When user responds as predicted, surprise is low."""
        sensorium.update_predictions([
            Prediction(what="user will respond to greeting", confidence=0.8),
        ])

        percepts = [Percept(modality="language", content="Hey there!", source="user:alice")]
        sensorium.compute_prediction_errors(percepts)

        errors = sensorium.get_prediction_errors()
        assert len(errors) == 1
        assert errors[0].surprise < 0.5  # Low surprise — prediction confirmed

    def test_prediction_about_response_violated_by_silence(self, sensorium):
        """When silence instead of expected response, surprise is high."""
        sensorium.update_predictions([
            Prediction(what="user will respond quickly", confidence=0.9),
        ])

        percepts = [Percept(modality="silence", content="quiet for 30 seconds", source="sensorium:silence_detection")]
        sensorium.compute_prediction_errors(percepts)

        errors = sensorium.get_prediction_errors()
        assert len(errors) == 1
        assert errors[0].surprise >= 0.8  # High surprise

    def test_prediction_errors_cleared_after_read(self, sensorium):
        """Prediction errors are cleared after being read."""
        sensorium.update_predictions([
            Prediction(what="user will reply", confidence=0.7),
        ])
        percepts = [Percept(modality="language", content="Hi", source="user:bob")]
        sensorium.compute_prediction_errors(percepts)

        sensorium.get_prediction_errors()  # Read
        errors = sensorium.get_prediction_errors()  # Read again
        assert len(errors) == 0

    def test_predictions_cleared_after_evaluation(self, sensorium):
        """Pending predictions are cleared after evaluation."""
        sensorium.update_predictions([
            Prediction(what="user will say hello", confidence=0.5),
        ])
        percepts = [Percept(modality="language", content="hello", source="user:alice")]
        sensorium.compute_prediction_errors(percepts)

        assert len(sensorium._pending_predictions) == 0

    def test_prediction_about_silence_violated(self, sensorium):
        """Predicting silence but getting input should surprise."""
        sensorium.update_predictions([
            Prediction(what="user will be silent for a while", confidence=0.7),
        ])

        percepts = [Percept(modality="language", content="Actually, one more thing", source="user:alice")]
        sensorium.compute_prediction_errors(percepts)

        errors = sensorium.get_prediction_errors()
        assert len(errors) == 1
        assert errors[0].surprise > 0.5


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------


class TestProperties:
    """Test sensorium property accessors."""

    def test_session_duration(self, sensorium):
        """Session duration is positive."""
        assert sensorium.session_duration_seconds >= 0

    def test_time_since_last_input_none_initially(self, sensorium):
        """No input yet means None."""
        assert sensorium.time_since_last_input is None

    def test_time_since_last_input_after_injection(self, sensorium):
        """After input, returns positive duration."""
        sensorium.inject_text("Hello", source="user:alice")
        assert sensorium.time_since_last_input is not None
        assert sensorium.time_since_last_input >= 0

    def test_format_duration(self):
        """Test duration formatting."""
        assert "ms" in Sensorium._format_duration(0.5)
        assert "second" in Sensorium._format_duration(5.0)
        assert "minute" in Sensorium._format_duration(120.0)
        assert "hour" in Sensorium._format_duration(7200.0)
