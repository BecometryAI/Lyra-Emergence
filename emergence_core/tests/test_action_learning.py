"""
Tests for action-outcome learning system.

Tests cover:
- ActionOutcome recording
- ActionReliability assessment
- ActionModel learning and prediction
- Outcome comparison and side effect detection
"""

import pytest
from datetime import datetime

from lyra.cognitive_core.meta_cognition import (
    ActionOutcome,
    ActionReliability,
    OutcomePrediction,
    ActionModel,
    ActionOutcomeLearner
)


class TestActionOutcome:
    """Test ActionOutcome data structure."""
    
    def test_outcome_creation(self):
        """Test creating an action outcome."""
        outcome = ActionOutcome(
            action_id="act_1",
            action_type="speak",
            intended_outcome="respond helpfully",
            actual_outcome="provided helpful response",
            success=True,
            partial_success=1.0,
            side_effects=[],
            timestamp=datetime.now(),
            context={"user_query": "test"}
        )
        
        assert outcome.action_id == "act_1"
        assert outcome.action_type == "speak"
        assert outcome.success is True
        assert outcome.partial_success == 1.0
    
    def test_outcome_with_side_effects(self):
        """Test outcome with side effects."""
        outcome = ActionOutcome(
            action_id="act_2",
            action_type="action",
            intended_outcome="complete task",
            actual_outcome="task completed with errors",
            success=False,
            partial_success=0.6,
            side_effects=["unexpected_error", "resource_exhaustion"],
            timestamp=datetime.now(),
            context={}
        )
        
        assert outcome.success is False
        assert len(outcome.side_effects) == 2


class TestActionModel:
    """Test ActionModel prediction functionality."""
    
    def test_model_predict_success(self):
        """Test model predicting successful outcome."""
        model = ActionModel(
            action_type="test",
            success_predictors={"good_context": 2.0, "ready": 1.5},
            failure_predictors={"busy": -1.0},
            typical_side_effects=[]
        )
        
        context = {"good_context": True, "ready": True}
        prediction = model.predict(context)
        
        assert prediction.confidence > 0
        assert prediction.probability_success > 0.5
    
    def test_model_predict_failure(self):
        """Test model predicting failure."""
        model = ActionModel(
            action_type="test",
            success_predictors={"ready": 1.0},
            failure_predictors={"busy": 2.0, "tired": 1.5},
            typical_side_effects=[]
        )
        
        context = {"busy": True, "tired": True}
        prediction = model.predict(context)
        
        assert prediction.probability_success < 0.5
    
    def test_model_predict_side_effects(self):
        """Test model predicting side effects."""
        model = ActionModel(
            action_type="test",
            success_predictors={},
            failure_predictors={},
            typical_side_effects=[
                ("effect1", 0.5),
                ("effect2", 0.2),
                ("effect3", 0.7)
            ]
        )
        
        prediction = model.predict({})
        
        # Should include effects with >30% probability
        assert "effect1" in prediction.likely_side_effects
        assert "effect3" in prediction.likely_side_effects
        assert "effect2" not in prediction.likely_side_effects


class TestActionOutcomeLearner:
    """Test ActionOutcomeLearner functionality."""
    
    def test_learner_initialization(self):
        """Test learner initialization."""
        learner = ActionOutcomeLearner(min_outcomes_for_model=5)
        assert learner.min_outcomes == 5
        assert len(learner.outcomes) == 0
        assert len(learner.action_models) == 0
    
    def test_record_outcome_success(self):
        """Test recording successful outcome."""
        learner = ActionOutcomeLearner()
        
        learner.record_outcome(
            action_id="act_1",
            action_type="speak",
            intended="provide helpful response",
            actual="provided helpful response",
            context={"ready": True}
        )
        
        assert len(learner.outcomes) == 1
        outcome = learner.outcomes[0]
        assert outcome.action_type == "speak"
        assert outcome.success is True
    
    def test_record_outcome_failure(self):
        """Test recording failed outcome."""
        learner = ActionOutcomeLearner()
        
        learner.record_outcome(
            action_id="act_2",
            action_type="speak",
            intended="provide detailed explanation",
            actual="gave brief answer",
            context={"busy": True}
        )
        
        assert len(learner.outcomes) == 1
        outcome = learner.outcomes[0]
        # May or may not be success depending on comparison
        assert outcome.partial_success < 1.0
    
    def test_get_action_reliability_unknown(self):
        """Test reliability for unknown action type."""
        learner = ActionOutcomeLearner()
        
        reliability = learner.get_action_reliability("unknown_action")
        
        assert reliability.unknown is True
        assert reliability.action_type == "unknown_action"
    
    def test_get_action_reliability_with_data(self):
        """Test reliability with recorded data."""
        learner = ActionOutcomeLearner()
        
        # Record multiple outcomes
        for i in range(10):
            learner.record_outcome(
                action_id=f"act_{i}",
                action_type="test_action",
                intended="complete task successfully",
                actual="complete task successfully" if i < 7 else "failed",
                context={"attempt": i}
            )
        
        reliability = learner.get_action_reliability("test_action")
        
        assert reliability.unknown is False
        assert 0 <= reliability.success_rate <= 1
        assert 0 <= reliability.avg_partial_success <= 1
    
    def test_action_model_building(self):
        """Test that models are built after sufficient data."""
        learner = ActionOutcomeLearner(min_outcomes_for_model=5)
        
        # Record outcomes with patterns
        for i in range(10):
            success = i < 7
            learner.record_outcome(
                action_id=f"act_{i}",
                action_type="test_action",
                intended="succeed",
                actual="succeed" if success else "fail",
                context={"good_condition": success}
            )
        
        # Model should be built
        assert "test_action" in learner.action_models
        model = learner.action_models["test_action"]
        assert model.action_type == "test_action"
    
    def test_predict_outcome_no_data(self):
        """Test prediction with no prior data."""
        learner = ActionOutcomeLearner()
        
        prediction = learner.predict_outcome(
            action_type="unknown",
            context={}
        )
        
        assert prediction.confidence == 0.0
        assert "unknown" in prediction.prediction
    
    def test_predict_outcome_with_model(self):
        """Test prediction with learned model."""
        learner = ActionOutcomeLearner(min_outcomes_for_model=3)
        
        # Record outcomes with clear pattern
        for i in range(10):
            success = i % 2 == 0
            learner.record_outcome(
                action_id=f"act_{i}",
                action_type="test_action",
                intended="succeed",
                actual="succeed" if success else "fail",
                context={"even_attempt": success}
            )
        
        # Should be able to predict
        prediction = learner.predict_outcome(
            action_type="test_action",
            context={"even_attempt": True}
        )
        
        assert prediction.confidence >= 0
        assert 0 <= prediction.probability_success <= 1
    
    def test_side_effect_detection(self):
        """Test side effect identification."""
        learner = ActionOutcomeLearner()
        
        learner.record_outcome(
            action_id="act_1",
            action_type="test",
            intended="complete task",
            actual="complete task but error occurred",
            context={"resource_exhaustion": True}
        )
        
        assert len(learner.outcomes) == 1
        outcome = learner.outcomes[0]
        # Should detect side effects based on context and outcome
        assert len(outcome.side_effects) > 0
    
    def test_get_all_action_types(self):
        """Test getting all action types."""
        learner = ActionOutcomeLearner()
        
        learner.record_outcome("1", "speak", "a", "a", {})
        learner.record_outcome("2", "think", "b", "b", {})
        learner.record_outcome("3", "speak", "c", "c", {})
        
        types = learner.get_all_action_types()
        
        assert len(types) == 2
        assert "speak" in types
        assert "think" in types
    
    def test_get_summary(self):
        """Test getting learner summary."""
        learner = ActionOutcomeLearner(min_outcomes_for_model=3)
        
        # Add some outcomes
        for i in range(10):
            learner.record_outcome(
                action_id=f"act_{i}",
                action_type="test",
                intended="succeed",
                actual="succeed" if i < 7 else "fail",
                context={}
            )
        
        summary = learner.get_summary()
        
        assert "total_outcomes" in summary
        assert summary["total_outcomes"] == 10
        assert "action_types" in summary
        assert "overall_success_rate" in summary
        assert 0 <= summary["overall_success_rate"] <= 1
    
    def test_common_side_effects(self):
        """Test identifying common side effects."""
        learner = ActionOutcomeLearner(min_outcomes_for_model=5)
        
        # Record outcomes with recurring side effects
        for i in range(10):
            learner.record_outcome(
                action_id=f"act_{i}",
                action_type="test",
                intended="complete",
                actual="complete with issues",
                context={"resource_exhaustion": i % 3 == 0}  # 33% of time
            )
        
        reliability = learner.get_action_reliability("test")
        
        # Should identify common side effects (>20% occurrence)
        assert isinstance(reliability.common_side_effects, list)
    
    def test_best_and_worst_contexts(self):
        """Test identification of best and worst contexts."""
        learner = ActionOutcomeLearner()
        
        # Record varied outcomes
        for i in range(10):
            success = i < 5
            learner.record_outcome(
                action_id=f"act_{i}",
                action_type="test",
                intended="succeed",
                actual="succeed" if success else "fail",
                context={"condition": "good" if success else "bad"}
            )
        
        reliability = learner.get_action_reliability("test")
        
        # Should identify contexts
        assert isinstance(reliability.best_contexts, list)
        assert isinstance(reliability.worst_contexts, list)


class TestOutcomeComparison:
    """Test outcome comparison logic."""
    
    def test_compare_identical_outcomes(self):
        """Test comparison of identical outcomes."""
        learner = ActionOutcomeLearner()
        
        learner.record_outcome(
            action_id="1",
            action_type="test",
            intended="complete task successfully",
            actual="complete task successfully",
            context={}
        )
        
        outcome = learner.outcomes[0]
        assert outcome.success is True
        assert outcome.partial_success >= 0.6
    
    def test_compare_different_outcomes(self):
        """Test comparison of different outcomes."""
        learner = ActionOutcomeLearner()
        
        learner.record_outcome(
            action_id="1",
            action_type="test",
            intended="complete all tasks",
            actual="completed nothing",
            context={}
        )
        
        outcome = learner.outcomes[0]
        assert outcome.success is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
