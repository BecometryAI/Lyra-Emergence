"""
Tests for attention allocation history system.

Tests cover:
- AttentionAllocation recording
- AttentionOutcome tracking
- Pattern learning from allocation-outcome pairs
- Recommended allocation based on patterns
"""

import pytest
from datetime import datetime

from lyra.cognitive_core.meta_cognition import (
    AttentionAllocation,
    AttentionOutcome,
    AttentionPattern,
    AttentionHistory,
    AttentionPatternLearner
)


class TestAttentionAllocation:
    """Test AttentionAllocation data structure."""
    
    def test_allocation_creation(self):
        """Test creating an attention allocation."""
        allocation = AttentionAllocation(
            id="alloc_1",
            timestamp=datetime.now(),
            allocation={"goal_1": 0.6, "goal_2": 0.4},
            total_available=1.0,
            trigger="goal_priority",
            workspace_state_hash="abc123"
        )
        
        assert allocation.id == "alloc_1"
        assert allocation.allocation["goal_1"] == 0.6
        assert allocation.total_available == 1.0
        assert allocation.trigger == "goal_priority"


class TestAttentionOutcome:
    """Test AttentionOutcome data structure."""
    
    def test_outcome_creation(self):
        """Test creating an attention outcome."""
        outcome = AttentionOutcome(
            allocation_id="alloc_1",
            goal_progress={"goal_1": 0.3, "goal_2": 0.1},
            discoveries=["insight_1", "pattern_2"],
            missed=["opportunity_1"],
            efficiency=0.75
        )
        
        assert outcome.allocation_id == "alloc_1"
        assert outcome.goal_progress["goal_1"] == 0.3
        assert len(outcome.discoveries) == 2
        assert len(outcome.missed) == 1
        assert outcome.efficiency == 0.75


class TestAttentionPatternLearner:
    """Test AttentionPatternLearner functionality."""
    
    def test_learner_initialization(self):
        """Test learner initialization."""
        learner = AttentionPatternLearner()
        assert len(learner.pattern_outcomes) == 0
        assert len(learner.pattern_examples) == 0
    
    def test_learn_from_allocation(self):
        """Test learning from allocation-outcome pair."""
        learner = AttentionPatternLearner()
        
        allocation = AttentionAllocation(
            id="alloc_1",
            timestamp=datetime.now(),
            allocation={"goal_1": 0.8, "goal_2": 0.2},
            total_available=1.0,
            trigger="focus",
            workspace_state_hash="hash1"
        )
        
        outcome = AttentionOutcome(
            allocation_id="alloc_1",
            goal_progress={"goal_1": 0.5},
            discoveries=["insight"],
            missed=[],
            efficiency=0.9
        )
        
        learner.learn(allocation, outcome)
        
        # Should have recorded the pattern
        assert len(learner.pattern_outcomes) > 0
    
    def test_get_patterns_insufficient_data(self):
        """Test getting patterns with insufficient data."""
        learner = AttentionPatternLearner()
        
        # Add only 2 observations (need 5)
        for i in range(2):
            allocation = AttentionAllocation(
                id=f"alloc_{i}",
                timestamp=datetime.now(),
                allocation={"goal_1": 1.0},
                total_available=1.0,
                trigger="test",
                workspace_state_hash=f"hash{i}"
            )
            outcome = AttentionOutcome(
                allocation_id=f"alloc_{i}",
                goal_progress={},
                discoveries=[],
                missed=[],
                efficiency=0.5
            )
            learner.learn(allocation, outcome)
        
        patterns = learner.get_patterns()
        assert len(patterns) == 0  # Not enough data
    
    def test_get_patterns_sufficient_data(self):
        """Test getting patterns with sufficient data."""
        learner = AttentionPatternLearner()
        
        # Add enough observations
        for i in range(10):
            allocation = AttentionAllocation(
                id=f"alloc_{i}",
                timestamp=datetime.now(),
                allocation={"goal_1": 0.7, "goal_2": 0.3},
                total_available=1.0,
                trigger="focus",
                workspace_state_hash=f"hash{i}"
            )
            outcome = AttentionOutcome(
                allocation_id=f"alloc_{i}",
                goal_progress={"goal_1": 0.4},
                discoveries=[],
                missed=[],
                efficiency=0.8
            )
            learner.learn(allocation, outcome)
        
        patterns = learner.get_patterns()
        assert len(patterns) > 0
    
    def test_patterns_sorted_by_efficiency(self):
        """Test that patterns are sorted by efficiency."""
        learner = AttentionPatternLearner()
        
        # Add pattern with high efficiency
        for i in range(5):
            allocation = AttentionAllocation(
                id=f"high_{i}",
                timestamp=datetime.now(),
                allocation={"goal_1": 0.9, "goal_2": 0.1},
                total_available=1.0,
                trigger="focus",
                workspace_state_hash=f"hash1_{i}"
            )
            outcome = AttentionOutcome(
                allocation_id=f"high_{i}",
                goal_progress={"goal_1": 0.5},
                discoveries=[],
                missed=[],
                efficiency=0.9
            )
            learner.learn(allocation, outcome)
        
        # Add pattern with low efficiency
        for i in range(5):
            allocation = AttentionAllocation(
                id=f"low_{i}",
                timestamp=datetime.now(),
                allocation={"goal_1": 0.1, "goal_2": 0.9},
                total_available=1.0,
                trigger="distributed",
                workspace_state_hash=f"hash2_{i}"
            )
            outcome = AttentionOutcome(
                allocation_id=f"low_{i}",
                goal_progress={},
                discoveries=[],
                missed=["important"],
                efficiency=0.3
            )
            learner.learn(allocation, outcome)
        
        patterns = learner.get_patterns()
        
        # Should be sorted by efficiency (best first)
        if len(patterns) >= 2:
            assert patterns[0].avg_efficiency >= patterns[1].avg_efficiency


class TestAttentionHistory:
    """Test AttentionHistory functionality."""
    
    def test_history_initialization(self):
        """Test history initialization."""
        history = AttentionHistory()
        assert len(history.allocations) == 0
        assert len(history.outcomes) == 0
        assert history.pattern_learner is not None
    
    def test_record_allocation(self):
        """Test recording an allocation."""
        history = AttentionHistory()
        
        alloc_id = history.record_allocation(
            allocation={"goal_1": 0.6, "goal_2": 0.4},
            trigger="goal_priority",
            workspace_state="test_state"
        )
        
        assert alloc_id is not None
        assert len(history.allocations) == 1
        assert history.allocations[0].id == alloc_id
    
    def test_record_outcome(self):
        """Test recording an outcome."""
        history = AttentionHistory()
        
        alloc_id = history.record_allocation(
            allocation={"goal_1": 0.6, "goal_2": 0.4},
            trigger="test",
            workspace_state="test"
        )
        
        history.record_outcome(
            allocation_id=alloc_id,
            goal_progress={"goal_1": 0.3, "goal_2": 0.1},
            discoveries=["insight"],
            missed=[]
        )
        
        assert alloc_id in history.outcomes
        outcome = history.outcomes[alloc_id]
        assert outcome.efficiency > 0
    
    def test_efficiency_computation(self):
        """Test efficiency computation."""
        history = AttentionHistory()
        
        # Good outcome: high progress, discoveries, nothing missed
        efficiency_good = history._compute_efficiency(
            goal_progress={"goal_1": 0.8, "goal_2": 0.6},
            discoveries=["insight1", "insight2"],
            missed=[]
        )
        
        # Bad outcome: no progress, no discoveries, missed items
        efficiency_bad = history._compute_efficiency(
            goal_progress={},
            discoveries=[],
            missed=["important1", "important2"]
        )
        
        assert efficiency_good > efficiency_bad
        assert 0 <= efficiency_good <= 1
        assert 0 <= efficiency_bad <= 1
    
    def test_get_recommended_allocation(self):
        """Test getting recommended allocation."""
        history = AttentionHistory()
        
        # Mock goals
        class MockGoal:
            def __init__(self, id, priority):
                self.id = id
                self.priority = priority
        
        goals = [
            MockGoal("goal_1", 0.8),
            MockGoal("goal_2", 0.2)
        ]
        
        recommendation = history.get_recommended_allocation(
            context="test",
            goals=goals
        )
        
        assert isinstance(recommendation, dict)
        # Should allocate proportional to priority
        if recommendation:
            assert recommendation.get("goal_1", 0) > recommendation.get("goal_2", 0)
    
    def test_get_attention_patterns(self):
        """Test getting learned patterns."""
        history = AttentionHistory()
        
        # Record enough allocations to form patterns
        for i in range(10):
            alloc_id = history.record_allocation(
                allocation={"goal_1": 0.7, "goal_2": 0.3},
                trigger="focus",
                workspace_state=f"state_{i}"
            )
            history.record_outcome(
                allocation_id=alloc_id,
                goal_progress={"goal_1": 0.4},
                discoveries=[],
                missed=[],
                efficiency=0.8
            )
        
        patterns = history.get_attention_patterns()
        assert isinstance(patterns, list)
    
    def test_get_recent_allocations(self):
        """Test getting recent allocations."""
        history = AttentionHistory()
        
        # Record multiple allocations
        for i in range(20):
            history.record_allocation(
                allocation={"goal_1": 1.0},
                trigger="test",
                workspace_state=f"state_{i}"
            )
        
        recent = history.get_recent_allocations(limit=10)
        
        assert len(recent) == 10
        # Should be most recent
        assert recent[-1].id == history.allocations[-1].id
    
    def test_get_allocation_stats(self):
        """Test getting allocation statistics."""
        history = AttentionHistory()
        
        # Record allocations with outcomes
        for i in range(5):
            alloc_id = history.record_allocation(
                allocation={"goal_1": 1.0},
                trigger="test",
                workspace_state=f"state_{i}"
            )
            history.record_outcome(
                allocation_id=alloc_id,
                goal_progress={"goal_1": 0.5},
                discoveries=[],
                missed=[],
                efficiency=0.7
            )
        
        stats = history.get_allocation_stats()
        
        assert stats["total_allocations"] == 5
        assert stats["allocations_with_outcomes"] == 5
        assert 0 <= stats["avg_efficiency"] <= 1
    
    def test_get_summary(self):
        """Test getting comprehensive summary."""
        history = AttentionHistory()
        
        # Record some data
        for i in range(10):
            alloc_id = history.record_allocation(
                allocation={"goal_1": 0.6, "goal_2": 0.4},
                trigger="test",
                workspace_state=f"state_{i}"
            )
            history.record_outcome(
                allocation_id=alloc_id,
                goal_progress={"goal_1": 0.3},
                discoveries=[],
                missed=[],
                efficiency=0.75
            )
        
        summary = history.get_summary()
        
        assert "total_allocations" in summary
        assert "avg_efficiency" in summary
        assert "patterns_learned" in summary
        assert "top_patterns" in summary
    
    def test_allocation_limit(self):
        """Test that old allocations are pruned."""
        history = AttentionHistory()
        
        # Record more than the limit (1000)
        for i in range(1100):
            history.record_allocation(
                allocation={"goal": 1.0},
                trigger="test",
                workspace_state=f"state_{i}"
            )
        
        # Should be pruned to max
        assert len(history.allocations) == 1000


class TestPatternExtraction:
    """Test pattern key extraction."""
    
    def test_extract_focused_pattern(self):
        """Test extracting focused attention pattern."""
        learner = AttentionPatternLearner()
        
        allocation = AttentionAllocation(
            id="alloc_1",
            timestamp=datetime.now(),
            allocation={"goal_1": 0.9, "goal_2": 0.1},
            total_available=1.0,
            trigger="focus",
            workspace_state_hash="hash"
        )
        
        pattern_key = learner._extract_pattern_key(allocation)
        
        assert "focused" in pattern_key or "goal_1" in pattern_key
    
    def test_extract_distributed_pattern(self):
        """Test extracting distributed attention pattern."""
        learner = AttentionPatternLearner()
        
        allocation = AttentionAllocation(
            id="alloc_1",
            timestamp=datetime.now(),
            allocation={
                "goal_1": 0.25,
                "goal_2": 0.25,
                "goal_3": 0.25,
                "goal_4": 0.25
            },
            total_available=1.0,
            trigger="distributed",
            workspace_state_hash="hash"
        )
        
        pattern_key = learner._extract_pattern_key(allocation)
        
        assert "distributed" in pattern_key or "balanced" in pattern_key


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
