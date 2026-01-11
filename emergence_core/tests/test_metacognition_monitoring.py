"""
Tests for meta-cognitive monitoring system.

Tests cover:
- ProcessingObservation creation and tracking
- Pattern detection (success conditions, failure modes, efficiency factors)
- MetaCognitiveMonitor functionality
- Statistics computation
"""

import pytest
import time
from datetime import datetime

from lyra.cognitive_core.meta_cognition import (
    ProcessingObservation,
    ProcessStats,
    ProcessingContext,
    CognitivePattern,
    PatternDetector,
    MetaCognitiveMonitor,
    generate_id
)
from lyra.cognitive_core.goals.resources import CognitiveResources


class TestProcessingObservation:
    """Test ProcessingObservation data structure."""
    
    def test_observation_creation(self):
        """Test creating a processing observation."""
        obs = ProcessingObservation(
            id="obs_1",
            timestamp=datetime.now(),
            process_type="reasoning",
            duration_ms=150.5,
            success=True,
            input_complexity=0.7,
            output_quality=0.9,
            resources_used=CognitiveResources(attention_budget=0.5),
            metadata={"test": True}
        )
        
        assert obs.id == "obs_1"
        assert obs.process_type == "reasoning"
        assert obs.success is True
        assert obs.input_complexity == 0.7
        assert obs.output_quality == 0.9
        assert obs.error is None
    
    def test_observation_with_error(self):
        """Test observation with error information."""
        obs = ProcessingObservation(
            id="obs_2",
            timestamp=datetime.now(),
            process_type="memory_retrieval",
            duration_ms=50.0,
            success=False,
            input_complexity=0.8,
            output_quality=0.0,
            resources_used=CognitiveResources(),
            error="Timeout error"
        )
        
        assert obs.success is False
        assert obs.error == "Timeout error"


class TestProcessingContext:
    """Test ProcessingContext context manager."""
    
    def test_context_manager_success(self):
        """Test context manager with successful process."""
        monitor = MetaCognitiveMonitor()
        
        with monitor.observe("test_process") as ctx:
            ctx.input_complexity = 0.6
            ctx.output_quality = 0.8
            time.sleep(0.01)  # Simulate work
        
        assert len(monitor.observations) == 1
        obs = monitor.observations[0]
        assert obs.process_type == "test_process"
        assert obs.success is True
        assert obs.duration_ms >= 10  # At least 10ms
        assert obs.input_complexity == 0.6
        assert obs.output_quality == 0.8
    
    def test_context_manager_failure(self):
        """Test context manager with failed process."""
        monitor = MetaCognitiveMonitor()
        
        try:
            with monitor.observe("failing_process") as ctx:
                ctx.input_complexity = 0.9
                raise ValueError("Test error")
        except ValueError:
            pass  # Expected
        
        assert len(monitor.observations) == 1
        obs = monitor.observations[0]
        assert obs.success is False
        assert "Test error" in obs.error


class TestPatternDetector:
    """Test pattern detection functionality."""
    
    def test_pattern_detector_initialization(self):
        """Test pattern detector initialization."""
        detector = PatternDetector(min_observations=3)
        assert detector.min_observations == 3
        assert len(detector.observations_by_type) == 0
    
    def test_detect_failure_mode_high_complexity(self):
        """Test detection of high-complexity failure mode."""
        detector = PatternDetector(min_observations=3)
        
        # Add successful low-complexity observations
        for i in range(5):
            obs = ProcessingObservation(
                id=f"success_{i}",
                timestamp=datetime.now(),
                process_type="reasoning",
                duration_ms=100.0,
                success=True,
                input_complexity=0.3,
                output_quality=0.8,
                resources_used=CognitiveResources()
            )
            detector.update(obs)
        
        # Add failed high-complexity observations
        for i in range(5):
            obs = ProcessingObservation(
                id=f"failure_{i}",
                timestamp=datetime.now(),
                process_type="reasoning",
                duration_ms=200.0,
                success=False,
                input_complexity=0.9,
                output_quality=0.0,
                resources_used=CognitiveResources()
            )
            detector.update(obs)
        
        patterns = detector.get_patterns()
        failure_modes = [p for p in patterns if p.pattern_type == 'failure_mode']
        
        assert len(failure_modes) > 0
        # Should detect high complexity correlation
        assert any("high-complexity" in p.description for p in failure_modes)
    
    def test_detect_success_condition(self):
        """Test detection of success conditions."""
        detector = PatternDetector(min_observations=3)
        
        # Add high-quality successes with good resources
        for i in range(8):
            obs = ProcessingObservation(
                id=f"success_{i}",
                timestamp=datetime.now(),
                process_type="reasoning",
                duration_ms=100.0,
                success=True,
                input_complexity=0.5,
                output_quality=0.9,
                resources_used=CognitiveResources(
                    attention_budget=0.8,
                    processing_budget=0.7
                )
            )
            detector.update(obs)
        
        patterns = detector.get_patterns()
        success_conditions = [p for p in patterns if p.pattern_type == 'success_condition']
        
        assert len(success_conditions) > 0
    
    def test_detect_efficiency_factor(self):
        """Test detection of efficiency factors."""
        detector = PatternDetector(min_observations=3)
        
        # Add fast low-complexity successes
        for i in range(5):
            obs = ProcessingObservation(
                id=f"fast_{i}",
                timestamp=datetime.now(),
                process_type="reasoning",
                duration_ms=50.0,
                success=True,
                input_complexity=0.3,
                output_quality=0.7,
                resources_used=CognitiveResources()
            )
            detector.update(obs)
        
        # Add slow high-complexity successes
        for i in range(5):
            obs = ProcessingObservation(
                id=f"slow_{i}",
                timestamp=datetime.now(),
                process_type="reasoning",
                duration_ms=200.0,
                success=True,
                input_complexity=0.8,
                output_quality=0.7,
                resources_used=CognitiveResources()
            )
            detector.update(obs)
        
        patterns = detector.get_patterns()
        efficiency_factors = [p for p in patterns if p.pattern_type == 'efficiency_factor']
        
        # Should detect that lower complexity leads to faster processing
        assert len(efficiency_factors) > 0


class TestMetaCognitiveMonitor:
    """Test MetaCognitiveMonitor functionality."""
    
    def test_monitor_initialization(self):
        """Test monitor initialization."""
        monitor = MetaCognitiveMonitor()
        assert len(monitor.observations) == 0
        assert monitor.pattern_detector is not None
    
    def test_record_observation(self):
        """Test recording observations."""
        monitor = MetaCognitiveMonitor()
        
        obs = ProcessingObservation(
            id="obs_1",
            timestamp=datetime.now(),
            process_type="test",
            duration_ms=100.0,
            success=True,
            input_complexity=0.5,
            output_quality=0.8,
            resources_used=CognitiveResources()
        )
        
        monitor.record_observation(obs)
        assert len(monitor.observations) == 1
    
    def test_get_process_statistics(self):
        """Test getting process statistics."""
        monitor = MetaCognitiveMonitor()
        
        # Add multiple observations
        for i in range(10):
            obs = ProcessingObservation(
                id=f"obs_{i}",
                timestamp=datetime.now(),
                process_type="reasoning",
                duration_ms=100.0 + i * 10,
                success=i % 2 == 0,  # 50% success rate
                input_complexity=0.5,
                output_quality=0.7 if i % 2 == 0 else 0.0,
                resources_used=CognitiveResources()
            )
            monitor.record_observation(obs)
        
        stats = monitor.get_process_statistics("reasoning")
        
        assert stats.total_executions == 10
        assert stats.success_rate == 0.5
        assert stats.avg_duration_ms > 100
        assert stats.avg_quality > 0  # Only successful ones counted
    
    def test_get_identified_patterns(self):
        """Test getting identified patterns."""
        monitor = MetaCognitiveMonitor()
        
        # Add observations that should create patterns
        for i in range(10):
            obs = ProcessingObservation(
                id=f"obs_{i}",
                timestamp=datetime.now(),
                process_type="reasoning",
                duration_ms=100.0,
                success=True,
                input_complexity=0.5,
                output_quality=0.8,
                resources_used=CognitiveResources()
            )
            monitor.record_observation(obs)
        
        patterns = monitor.get_identified_patterns()
        assert isinstance(patterns, list)
    
    def test_observe_context_manager(self):
        """Test the observe context manager."""
        monitor = MetaCognitiveMonitor()
        
        with monitor.observe("test_process") as ctx:
            ctx.input_complexity = 0.7
            result = "test"
            ctx.output_quality = 0.9
        
        assert len(monitor.observations) == 1
        assert monitor.observations[0].process_type == "test_process"
    
    def test_get_summary(self):
        """Test getting monitor summary."""
        monitor = MetaCognitiveMonitor()
        
        # Add some observations
        for i in range(5):
            with monitor.observe("reasoning") as ctx:
                ctx.input_complexity = 0.5
                ctx.output_quality = 0.8
        
        summary = monitor.get_summary()
        
        assert "total_observations" in summary
        assert summary["total_observations"] == 5
        assert "process_types" in summary
        assert "identified_patterns" in summary
    
    def test_get_recent_observations(self):
        """Test getting recent observations."""
        monitor = MetaCognitiveMonitor()
        
        # Add observations
        for i in range(20):
            obs = ProcessingObservation(
                id=f"obs_{i}",
                timestamp=datetime.now(),
                process_type="reasoning" if i < 10 else "memory",
                duration_ms=100.0,
                success=True,
                input_complexity=0.5,
                output_quality=0.8,
                resources_used=CognitiveResources()
            )
            monitor.record_observation(obs)
        
        # Get all recent
        recent = monitor.get_recent_observations(limit=10)
        assert len(recent) == 10
        
        # Get filtered
        reasoning_recent = monitor.get_recent_observations(
            process_type="reasoning",
            limit=10
        )
        assert all(o.process_type == "reasoning" for o in reasoning_recent)


class TestGenerateId:
    """Test ID generation."""
    
    def test_generate_id_uniqueness(self):
        """Test that generated IDs are unique."""
        ids = [generate_id() for _ in range(100)]
        assert len(set(ids)) == 100  # All unique


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
