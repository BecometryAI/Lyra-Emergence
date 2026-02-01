"""
Tests for the BottleneckDetector module.

Tests cognitive load monitoring, bottleneck detection, and integration
with communication inhibition.
"""

import pytest
from datetime import datetime, timedelta

from sanctuary.mind.cognitive_core.meta_cognition.bottleneck_detector import (
    BottleneckDetector,
    BottleneckSignal,
    BottleneckState,
    BottleneckType,
)


class TestBottleneckDetector:
    """Tests for BottleneckDetector class."""

    def test_initialization(self):
        """Test detector initializes with default config."""
        detector = BottleneckDetector()

        assert detector.workspace_overload_threshold == 20
        assert detector.subsystem_slowdown_factor == 2.0
        assert detector.resource_exhaustion_threshold == 0.9
        assert not detector.is_overloaded()
        assert detector.get_load() == 0.0

    def test_initialization_with_config(self):
        """Test detector initializes with custom config."""
        config = {
            "workspace_overload_threshold": 10,
            "resource_exhaustion_threshold": 0.8,
        }
        detector = BottleneckDetector(config=config)

        assert detector.workspace_overload_threshold == 10
        assert detector.resource_exhaustion_threshold == 0.8

    def test_no_bottleneck_normal_operation(self):
        """Test no bottleneck detected under normal conditions."""
        detector = BottleneckDetector()

        state = detector.update(
            subsystem_timings={"perception": 10, "attention": 5, "action": 8},
            workspace_percept_count=5,
            goal_resource_utilization=0.3,
        )

        assert not state.is_bottlenecked
        assert len(state.active_bottlenecks) == 0
        assert state.recommendation == "normal_operation"

    def test_workspace_overload_detection(self):
        """Test detection of workspace overload."""
        detector = BottleneckDetector({"workspace_overload_threshold": 10})

        # First update builds baseline
        detector.update(
            subsystem_timings={"perception": 10},
            workspace_percept_count=5,
            goal_resource_utilization=0.3,
        )

        # Update with overloaded workspace
        state = detector.update(
            subsystem_timings={"perception": 10},
            workspace_percept_count=25,  # Well over threshold
            goal_resource_utilization=0.3,
        )

        # Should detect workspace overload
        workspace_bottlenecks = [
            b for b in state.active_bottlenecks
            if b.bottleneck_type == BottleneckType.WORKSPACE_OVERLOAD
        ]
        assert len(workspace_bottlenecks) == 1
        assert workspace_bottlenecks[0].severity > 0

    def test_resource_exhaustion_detection(self):
        """Test detection of goal resource exhaustion."""
        detector = BottleneckDetector({"resource_exhaustion_threshold": 0.9})

        state = detector.update(
            subsystem_timings={"perception": 10},
            workspace_percept_count=5,
            goal_resource_utilization=0.95,  # Over 90% threshold
            waiting_goals=3,
        )

        resource_bottlenecks = [
            b for b in state.active_bottlenecks
            if b.bottleneck_type == BottleneckType.GOAL_RESOURCE_EXHAUSTION
        ]
        assert len(resource_bottlenecks) == 1
        assert "waiting" in resource_bottlenecks[0].description.lower()

    def test_cycle_overrun_detection(self):
        """Test detection of cognitive cycle overrun."""
        detector = BottleneckDetector({"cycle_duration_target_ms": 100})

        state = detector.update(
            subsystem_timings={
                "perception": 50,
                "attention": 40,
                "action": 60,
                "memory_consolidation": 100,
            },  # Total: 250ms, well over 100ms target
            workspace_percept_count=5,
            goal_resource_utilization=0.3,
        )

        cycle_bottlenecks = [
            b for b in state.active_bottlenecks
            if b.bottleneck_type == BottleneckType.CYCLE_OVERRUN
        ]
        assert len(cycle_bottlenecks) == 1

    def test_memory_lag_detection(self):
        """Test detection of memory consolidation lag."""
        detector = BottleneckDetector({"memory_lag_threshold_ms": 100})

        state = detector.update(
            subsystem_timings={
                "perception": 10,
                "memory_consolidation": 500,  # Well over 100ms threshold
            },
            workspace_percept_count=5,
            goal_resource_utilization=0.3,
        )

        memory_bottlenecks = [
            b for b in state.active_bottlenecks
            if b.bottleneck_type == BottleneckType.MEMORY_LAG
        ]
        assert len(memory_bottlenecks) == 1

    def test_subsystem_slowdown_detection(self):
        """Test detection of subsystem slowdown vs baseline."""
        detector = BottleneckDetector({"subsystem_slowdown_factor": 2.0})

        # Build baseline with multiple updates
        for _ in range(15):
            detector.update(
                subsystem_timings={"perception": 10, "attention": 5},
                workspace_percept_count=5,
                goal_resource_utilization=0.3,
            )

        # Now trigger slowdown
        state = detector.update(
            subsystem_timings={"perception": 50, "attention": 5},  # 5x slower
            workspace_percept_count=5,
            goal_resource_utilization=0.3,
        )

        slowdown_bottlenecks = [
            b for b in state.active_bottlenecks
            if b.bottleneck_type == BottleneckType.SUBSYSTEM_SLOWDOWN
        ]
        assert len(slowdown_bottlenecks) == 1
        assert slowdown_bottlenecks[0].source == "perception"

    def test_bottleneck_persistence_required(self):
        """Test that bottleneck must persist for multiple cycles."""
        detector = BottleneckDetector({
            "workspace_overload_threshold": 10,
            "consecutive_cycles_for_bottleneck": 3,
        })

        # First cycle - not yet bottlenecked
        state1 = detector.update(
            subsystem_timings={"perception": 10},
            workspace_percept_count=25,
            goal_resource_utilization=0.3,
        )
        assert not state1.is_bottlenecked

        # Second cycle - still not bottlenecked
        state2 = detector.update(
            subsystem_timings={"perception": 10},
            workspace_percept_count=25,
            goal_resource_utilization=0.3,
        )
        assert not state2.is_bottlenecked

        # Third cycle - now bottlenecked
        state3 = detector.update(
            subsystem_timings={"perception": 10},
            workspace_percept_count=25,
            goal_resource_utilization=0.3,
        )
        assert state3.is_bottlenecked

    def test_bottleneck_clears_when_resolved(self):
        """Test that bottleneck clears when condition resolves."""
        detector = BottleneckDetector({
            "workspace_overload_threshold": 10,
            "consecutive_cycles_for_bottleneck": 1,  # Immediate for testing
        })

        # Trigger bottleneck
        state1 = detector.update(
            subsystem_timings={"perception": 10},
            workspace_percept_count=25,
            goal_resource_utilization=0.3,
        )
        assert state1.is_bottlenecked

        # Resolve condition
        state2 = detector.update(
            subsystem_timings={"perception": 10},
            workspace_percept_count=5,  # Back to normal
            goal_resource_utilization=0.3,
        )
        assert not state2.is_bottlenecked

    def test_overall_load_computation(self):
        """Test overall cognitive load computation."""
        detector = BottleneckDetector({
            "workspace_overload_threshold": 20,
            "cycle_duration_target_ms": 100,
        })

        # Low load
        state1 = detector.update(
            subsystem_timings={"perception": 10, "attention": 5},
            workspace_percept_count=5,
            goal_resource_utilization=0.2,
        )
        assert state1.overall_load < 0.3

        # High load
        state2 = detector.update(
            subsystem_timings={"perception": 100, "attention": 100},
            workspace_percept_count=30,
            goal_resource_utilization=0.9,
        )
        assert state2.overall_load > 0.7

    def test_communication_inhibition_check(self):
        """Test should_inhibit_communication method."""
        detector = BottleneckDetector({
            "workspace_overload_threshold": 10,
            "consecutive_cycles_for_bottleneck": 1,
        })

        # Normal - no inhibition
        detector.update(
            subsystem_timings={"perception": 10},
            workspace_percept_count=5,
            goal_resource_utilization=0.3,
        )
        assert not detector.should_inhibit_communication()

        # Bottlenecked with high load - should inhibit
        detector.update(
            subsystem_timings={"perception": 10},
            workspace_percept_count=50,
            goal_resource_utilization=0.95,
        )
        assert detector.should_inhibit_communication()

    def test_introspection_text_generation(self):
        """Test generation of introspective text about bottleneck."""
        detector = BottleneckDetector({
            "workspace_overload_threshold": 10,
            "consecutive_cycles_for_bottleneck": 1,
        })

        # No bottleneck - no text
        detector.update(
            subsystem_timings={"perception": 10},
            workspace_percept_count=5,
            goal_resource_utilization=0.3,
        )
        assert detector.get_introspection_text() is None

        # With bottleneck - should have text
        detector.update(
            subsystem_timings={"perception": 10},
            workspace_percept_count=30,
            goal_resource_utilization=0.3,
        )
        text = detector.get_introspection_text()
        assert text is not None
        assert "constraints" in text.lower() or "load" in text.lower()

    def test_recommendation_generation(self):
        """Test recommendation generation based on bottleneck type."""
        detector = BottleneckDetector({
            "resource_exhaustion_threshold": 0.5,
            "consecutive_cycles_for_bottleneck": 1,
        })

        state = detector.update(
            subsystem_timings={"perception": 10},
            workspace_percept_count=5,
            goal_resource_utilization=0.95,
        )

        # Should recommend pausing goals for resource exhaustion
        assert "goal" in state.recommendation.lower()

    def test_average_load_tracking(self):
        """Test average load computation over cycles."""
        detector = BottleneckDetector()

        # Run several cycles
        for i in range(10):
            detector.update(
                subsystem_timings={"perception": 10 + i * 5},
                workspace_percept_count=5 + i,
                goal_resource_utilization=0.3 + i * 0.05,
            )

        avg_load = detector.get_average_load(cycles=5)
        assert 0.0 < avg_load < 1.0

    def test_summary_generation(self):
        """Test summary dict generation."""
        detector = BottleneckDetector({
            "workspace_overload_threshold": 10,
            "consecutive_cycles_for_bottleneck": 1,
        })

        detector.update(
            subsystem_timings={"perception": 10},
            workspace_percept_count=25,
            goal_resource_utilization=0.3,
        )

        summary = detector.get_summary()

        assert "is_bottlenecked" in summary
        assert "overall_load" in summary
        assert "recommendation" in summary
        assert "should_inhibit_communication" in summary
        assert isinstance(summary["bottleneck_types"], list)


class TestBottleneckSignal:
    """Tests for BottleneckSignal dataclass."""

    def test_signal_creation(self):
        """Test signal creation with required fields."""
        signal = BottleneckSignal(
            bottleneck_type=BottleneckType.WORKSPACE_OVERLOAD,
            severity=0.7,
            source="workspace",
            description="Test bottleneck",
        )

        assert signal.bottleneck_type == BottleneckType.WORKSPACE_OVERLOAD
        assert signal.severity == 0.7
        assert signal.consecutive_cycles == 1

    def test_severity_clamping(self):
        """Test that severity is clamped to [0, 1]."""
        signal1 = BottleneckSignal(
            bottleneck_type=BottleneckType.WORKSPACE_OVERLOAD,
            severity=1.5,  # Should be clamped to 1.0
            source="workspace",
            description="Test",
        )
        assert signal1.severity == 1.0

        signal2 = BottleneckSignal(
            bottleneck_type=BottleneckType.WORKSPACE_OVERLOAD,
            severity=-0.5,  # Should be clamped to 0.0
            source="workspace",
            description="Test",
        )
        assert signal2.severity == 0.0


class TestBottleneckState:
    """Tests for BottleneckState dataclass."""

    def test_state_defaults(self):
        """Test state has sensible defaults."""
        state = BottleneckState()

        assert not state.is_bottlenecked
        assert state.overall_load == 0.0
        assert state.active_bottlenecks == []
        assert state.recommendation == "normal_operation"

    def test_get_severity(self):
        """Test get_severity returns max of active bottlenecks."""
        state = BottleneckState(
            active_bottlenecks=[
                BottleneckSignal(
                    bottleneck_type=BottleneckType.WORKSPACE_OVERLOAD,
                    severity=0.5,
                    source="workspace",
                    description="Test 1",
                ),
                BottleneckSignal(
                    bottleneck_type=BottleneckType.MEMORY_LAG,
                    severity=0.8,
                    source="memory",
                    description="Test 2",
                ),
            ]
        )

        assert state.get_severity() == 0.8

    def test_get_severity_empty(self):
        """Test get_severity returns 0 when no bottlenecks."""
        state = BottleneckState()
        assert state.get_severity() == 0.0
