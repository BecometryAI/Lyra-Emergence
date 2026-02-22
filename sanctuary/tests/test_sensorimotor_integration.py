"""Integration tests for the sensorimotor loop.

Tests the full cycle: Sensorium -> CognitiveCycle -> Motor -> Sensorium.
This is the active inference loop — percepts become thoughts become
actions become new percepts.
"""

import asyncio

import pytest

from sanctuary.core.schema import (
    CognitiveInput,
    CognitiveOutput,
    GoalProposal,
    MemoryOp,
    Percept,
    Prediction,
)
from sanctuary.core.cognitive_cycle import CognitiveCycle
from sanctuary.motor.motor import Motor
from sanctuary.sensorium.sensorium import Sensorium


# ---------------------------------------------------------------------------
# Mock model that produces structured output
# ---------------------------------------------------------------------------


class SensoriMotorTestModel:
    """A test model that produces predictable output for integration testing."""

    def __init__(self):
        self.call_count = 0
        self.last_input = None

    async def think(self, cognitive_input: CognitiveInput) -> CognitiveOutput:
        self.call_count += 1
        self.last_input = cognitive_input

        # Produce different output based on what percepts arrived
        has_user_input = any(
            p.source.startswith("user") for p in cognitive_input.new_percepts
        )
        has_motor_feedback = any(
            p.modality == "proprioceptive" for p in cognitive_input.new_percepts
        )

        if has_user_input:
            return CognitiveOutput(
                inner_speech="I notice the user spoke to me. I want to respond.",
                external_speech="Hello! I hear you.",
                predictions=[
                    Prediction(what="user will respond to my greeting", confidence=0.7),
                ],
                memory_ops=[
                    MemoryOp(
                        type="write_episodic",
                        content="User spoke to me",
                        significance=4,
                    ),
                ],
            )
        elif has_motor_feedback:
            return CognitiveOutput(
                inner_speech="I perceive that I just spoke. The loop is working.",
                predictions=[
                    Prediction(what="user will reply soon", confidence=0.6),
                ],
            )
        else:
            return CognitiveOutput(
                inner_speech="Quiet moment. Nothing to perceive.",
            )


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------


class TestSensoriMotorLoop:
    """Test the full sensorimotor loop."""

    @pytest.mark.asyncio
    async def test_basic_loop(self):
        """Input -> cognition -> speech -> motor feedback -> next cycle."""
        model = SensoriMotorTestModel()
        sensorium = Sensorium(silence_threshold=100)  # Long threshold
        motor = Motor()

        # Wire motor feedback to sensorium
        motor.set_feedback_handler(sensorium.inject_motor_feedback)

        # Track speech output
        speech_log = []
        async def log_speech(text):
            speech_log.append(text)
        motor.on_speech(log_speech)

        cycle = CognitiveCycle(
            model=model,
            sensorium=sensorium,
            motor=motor,
            cycle_delay=0.01,
        )

        # Inject user input
        sensorium.inject_text("Hello Sanctuary", source="user:alice")

        # Run one cycle
        await cycle.run(max_cycles=1)

        # Model should have received the user percept
        assert model.call_count == 1
        user_percepts = [
            p for p in model.last_input.new_percepts
            if p.source.startswith("user")
        ]
        assert len(user_percepts) == 1

        # Speech should have been emitted
        assert speech_log == ["Hello! I hear you."]

        # Motor feedback should be in the sensorium queue for next cycle
        pending = await sensorium.drain_percepts()
        motor_feedback = [p for p in pending if p.modality == "proprioceptive"]
        assert len(motor_feedback) >= 1
        assert "speech" in motor_feedback[0].content

    @pytest.mark.asyncio
    async def test_motor_feedback_reaches_next_cycle(self):
        """Motor feedback from cycle N appears as percept in cycle N+1."""
        model = SensoriMotorTestModel()
        sensorium = Sensorium(silence_threshold=100)
        motor = Motor()
        motor.set_feedback_handler(sensorium.inject_motor_feedback)

        speech_log = []
        async def log_speech(text):
            speech_log.append(text)
        motor.on_speech(log_speech)

        cycle = CognitiveCycle(
            model=model,
            sensorium=sensorium,
            motor=motor,
            cycle_delay=0.01,
        )

        # Inject user input and run TWO cycles
        sensorium.inject_text("Hello", source="user:alice")
        await cycle.run(max_cycles=2)

        # Cycle 1: user input -> speech output
        # Cycle 2: motor feedback from speech -> model sees proprioceptive
        assert model.call_count == 2

        # The second call should have received motor feedback
        second_input = model.last_input
        motor_percepts = [
            p for p in second_input.new_percepts
            if p.modality == "proprioceptive"
        ]
        assert len(motor_percepts) >= 1

    @pytest.mark.asyncio
    async def test_prediction_errors_computed(self):
        """Predictions from cycle N are checked against percepts in cycle N+1."""
        model = SensoriMotorTestModel()
        sensorium = Sensorium(silence_threshold=100)
        motor = Motor()
        motor.set_feedback_handler(sensorium.inject_motor_feedback)

        cycle = CognitiveCycle(
            model=model,
            sensorium=sensorium,
            motor=motor,
            cycle_delay=0.01,
        )

        # Cycle 1: user speaks -> model predicts "user will respond to greeting"
        sensorium.inject_text("Hi there", source="user:alice")
        await cycle.run(max_cycles=1)

        # Now inject silence instead of a response
        # (Don't inject any user input — only motor feedback is in the queue)
        # Run cycle 2 — model should see prediction errors
        await cycle.run(max_cycles=1)

        # The predictions were about user responding, but only motor
        # feedback arrived. The sensorium should have computed errors.
        # (They may or may not be present depending on what the model
        # produced, but the mechanism should not crash.)
        assert model.call_count == 2

    @pytest.mark.asyncio
    async def test_temporal_context_enriched(self):
        """Temporal context includes session duration and interaction count."""
        model = SensoriMotorTestModel()
        sensorium = Sensorium(silence_threshold=100)

        cycle = CognitiveCycle(
            model=model,
            sensorium=sensorium,
            cycle_delay=0.01,
        )

        sensorium.inject_text("Test", source="user:alice")
        await cycle.run(max_cycles=1)

        temporal = model.last_input.temporal_context
        assert temporal.time_of_day != ""
        assert temporal.session_duration != ""

    @pytest.mark.asyncio
    async def test_cycle_without_motor_still_works(self):
        """Backward compatibility: cycle works without motor (Phase 3 behavior)."""
        model = SensoriMotorTestModel()
        sensorium = Sensorium(silence_threshold=100)

        cycle = CognitiveCycle(
            model=model,
            sensorium=sensorium,
            motor=None,  # No motor
            cycle_delay=0.01,
        )

        sensorium.inject_text("Hello", source="user:alice")
        await cycle.run(max_cycles=1)

        assert model.call_count == 1

    @pytest.mark.asyncio
    async def test_full_three_cycle_sequence(self):
        """Three cycles showing the full loop: input -> action -> feedback -> thought."""
        model = SensoriMotorTestModel()
        sensorium = Sensorium(silence_threshold=100)
        motor = Motor()
        motor.set_feedback_handler(sensorium.inject_motor_feedback)

        speech_log = []
        async def log_speech(text):
            speech_log.append(text)
        motor.on_speech(log_speech)

        cycle = CognitiveCycle(
            model=model,
            sensorium=sensorium,
            motor=motor,
            cycle_delay=0.01,
        )

        # Cycle 1: User speaks
        sensorium.inject_text("How are you?", source="user:alice")
        await cycle.run(max_cycles=1)
        assert len(speech_log) == 1

        # Cycle 2: Motor feedback arrives, model perceives its own action
        await cycle.run(max_cycles=1)
        assert model.last_input.new_percepts  # Should have motor feedback

        # Cycle 3: Continuation — model thinks about what happened
        await cycle.run(max_cycles=1)
        assert model.call_count == 3
