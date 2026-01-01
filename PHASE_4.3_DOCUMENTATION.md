# Phase 4.3: Self-Model Accuracy Tracking & Refinement - Documentation

## Overview

Phase 4.3 implements comprehensive tracking, measurement, and visualization of self-model prediction accuracy with automatic refinement based on prediction errors. This closes the feedback loop: **predict → observe → measure → refine**.

## Architecture

### Core Components

#### 1. PredictionRecord Dataclass
Comprehensive record of a single prediction with:
- Unique ID and timestamp
- Category (action, emotion, capability, goal_priority, value_alignment)
- Predicted state and confidence level
- Actual state (filled after observation)
- Correctness and error magnitude
- Context and self-model version

#### 2. AccuracySnapshot Dataclass
Point-in-time accuracy snapshot with:
- Overall and category-specific accuracies
- Calibration score
- Prediction count
- Self-model version

#### 3. Enhanced SelfMonitor
Extended with:
- Prediction tracking system
- Accuracy metrics calculation
- Confidence calibration analysis
- Systematic bias detection
- Automatic self-model refinement
- Temporal accuracy tracking
- Report generation

## Configuration

```python
config = {
    "meta_cognition": {
        # Existing Phase 4.1 config...
        
        # Phase 4.3: Prediction Tracking
        "prediction_tracking": {
            "enabled": True,
            "max_pending_validations": 100,
            "auto_validate": True,
            "validation_timeout": 600  # Seconds before prediction expires
        },
        
        # Phase 4.3: Accuracy Measurement
        "accuracy_measurement": {
            "enable_temporal_tracking": True,
            "snapshot_frequency": 100,  # Every N cycles
            "calibration_bins": 10,
            "trend_window_days": 7
        },
        
        # Phase 4.3: Self-Model Refinement
        "self_model_refinement": {
            "auto_refine": True,
            "refinement_threshold": 0.3,  # Refine if error > threshold
            "learning_rate": 0.1,  # How quickly to adjust confidence
            "require_min_samples": 5  # Min predictions before refinement
        },
        
        # Phase 4.3: Reporting
        "reporting": {
            "enable_periodic_reports": True,
            "report_frequency": 1000,  # Every N cycles
            "report_format": "text",
            "save_reports": True,
            "report_dir": "data/accuracy_reports"
        }
    }
}
```

## Usage Examples

### Recording Predictions

```python
# Record a prediction before taking action
prediction_id = self_monitor.record_prediction(
    category="action",
    predicted_state={"action": "speak", "content": "greeting"},
    confidence=0.85,
    context={"cycle": 100, "goal": "respond"}
)
```

### Validating Predictions

```python
# Validate after observing actual outcome
validated = self_monitor.validate_prediction(
    prediction_id,
    actual_state={"action": "speak", "result": "success"}
)

print(f"Prediction correct: {validated.correct}")
print(f"Error magnitude: {validated.error_magnitude:.2f}")
```

### Auto-Validation

```python
# Automatically validate pending predictions from workspace state
validated_records = self_monitor.auto_validate_predictions(snapshot)
print(f"Auto-validated {len(validated_records)} predictions")
```

### Getting Accuracy Metrics

```python
# Get comprehensive accuracy metrics
metrics = self_monitor.get_accuracy_metrics()

print(f"Overall accuracy: {metrics['overall']['accuracy']:.1%}")
print(f"Action prediction accuracy: {metrics['by_category']['action']['accuracy']:.1%}")
print(f"Calibration score: {metrics['calibration']['calibration_score']:.2f}")
print(f"Trend: {metrics['temporal_trends']['trend_direction']}")
```

### Generating Reports

```python
# Generate human-readable text report
text_report = self_monitor.generate_accuracy_report(format="text")
print(text_report)

# Generate markdown report
md_report = self_monitor.generate_accuracy_report(format="markdown")

# Generate JSON report
json_report = self_monitor.generate_accuracy_report(format="json")
import json
data = json.loads(json_report)
```

### Self-Model Refinement

```python
# Manually trigger refinement from error records
error_records = [r for r in prediction_records if not r.correct]
self_monitor.refine_self_model_from_errors(error_records)

# Automatic refinement happens in cognitive loop when errors exceed threshold
```

### Temporal Tracking

```python
# Take accuracy snapshot
snapshot = self_monitor.record_accuracy_snapshot()
print(f"Snapshot accuracy: {snapshot.overall_accuracy:.1%}")

# Analyze accuracy trends
trend = self_monitor.get_accuracy_trend(days=7)
print(f"Trend direction: {trend['trend_direction']}")
print(f"Rate of change: {trend['rate_of_change']:.3f}")
```

### Identifying Capability Gaps

```python
# Find areas needing more data
gaps = self_monitor.identify_capability_gaps()

for gap in gaps:
    print(f"Gap: {gap['capability']}")
    print(f"Reason: {gap['reason']}")
    print(f"Action: {gap['recommended_action']}")
```

## Integration with Cognitive Loop

The prediction tracking system is automatically integrated into the cognitive loop:

1. **Before Action**: Record prediction about action outcome
2. **Execute Action**: Perform the action
3. **After Action**: Validate prediction against actual outcome
4. **Auto-Validation**: Periodically validate pending predictions from workspace state
5. **Refinement**: Automatically refine self-model when errors exceed threshold
6. **Snapshots**: Take accuracy snapshots every 100 cycles

## Metrics Interpretation

### Overall Accuracy
- **0.0-0.5**: Poor prediction quality, major self-model issues
- **0.5-0.7**: Moderate quality, needs improvement
- **0.7-0.85**: Good quality, reliable predictions
- **0.85-1.0**: Excellent quality, highly calibrated

### Calibration Score
- **0.0-0.5**: Poorly calibrated, confidence doesn't match accuracy
- **0.5-0.7**: Moderately calibrated
- **0.7-0.85**: Well calibrated
- **0.85-1.0**: Excellently calibrated

Good calibration means: when you say 80% confident, you're correct 80% of the time.

### Trend Direction
- **improving**: Accuracy increasing over time (learning)
- **stable**: Consistent performance
- **declining**: Accuracy decreasing (may need attention)

## Systematic Biases

The system can detect several types of biases:

1. **Overconfidence**: High confidence predictions are often wrong
2. **Underconfidence**: Low confidence predictions are often right
3. **Emotion Prediction Bias**: Systematic errors in emotional prediction
4. **Capability Overestimation**: Claiming capabilities beyond actual performance

## Report Example

```
=== SELF-MODEL ACCURACY REPORT ===
Generated: 2026-01-01 15:30:00

OVERALL PERFORMANCE
- Accuracy: 78.5% (157/200 predictions correct)
- Calibration Score: 0.82 (well calibrated)
- Trend: Improving ✓

ACCURACY BY CATEGORY
- Actions: 85.3% (71/83) - STRONG
- Emotions: 72.1% (44/61) - MODERATE
- Capabilities: 81.0% (34/42) - STRONG
- Goal Priorities: 57.1% (8/14) - NEEDS IMPROVEMENT

CALIBRATION ANALYSIS
- Slight overconfidence detected (+0.08)
- When I say 90% confident, I'm correct 82% of time
- Recommendation: Lower confidence estimates slightly

IDENTIFIED BIASES
- Systematic overestimation of emotional valence (+0.15 avg error)

CAPABILITY GAPS
- Need more data on: creative_writing, tool_calling
- High uncertainty in: abstract_reasoning

RECENT TRENDS
- Recent accuracy (24h): 82.1%
- Weekly accuracy (7d): 78.5%
- Overall trend: Improving accuracy over time ✓

=== END REPORT ===
```

## Success Criteria

- ✅ Structured prediction recording with PredictionRecord dataclass
- ✅ Prediction validation system (manual + automatic)
- ✅ Comprehensive accuracy metrics by category and confidence
- ✅ Confidence calibration analysis
- ✅ Systematic bias detection
- ✅ Automatic self-model refinement from errors
- ✅ Capability boundary tracking and updates
- ✅ Capability gap identification
- ✅ Human-readable accuracy reports (text + markdown)
- ✅ Temporal accuracy tracking with snapshots
- ✅ Accuracy trend analysis
- ✅ Integration with cognitive loop
- ✅ All tests pass (16+ tests)
- ✅ Documentation complete with examples

## Future Enhancements

### Phase 4.4 (Future)
- Multi-step prediction chains
- Counterfactual reasoning ("what if I had done X?")
- Prediction explanation generation
- Interactive accuracy dashboard
- Cross-session accuracy persistence
- Prediction confidence tuning based on context

### Advanced Features
- Uncertainty quantification with confidence intervals
- Prediction ensembles (multiple predictions, pick best)
- Meta-learning (learning how to learn better)
- Transfer learning across prediction categories
- Anomaly detection in prediction patterns

## Technical Notes

### Performance Considerations
- Prediction records stored in memory (Dict)
- Pending validations limited to max_pending_validations (default: 100)
- Accuracy history limited to 1000 snapshots (deque)
- Old predictions auto-expire after validation_timeout (default: 600s)

### Storage
- Prediction records: In-memory only (not persisted)
- Accuracy snapshots: In-memory deque + daily_snapshots dict
- Reports: Can be saved to disk (if save_reports enabled)

### Thread Safety
- Not thread-safe (designed for single-threaded cognitive loop)
- All operations are synchronous (no async)

## Debugging

### Enable Debug Logging
```python
import logging
logging.getLogger("emergence_core.lyra.cognitive_core.meta_cognition").setLevel(logging.DEBUG)
```

### Check Stats
```python
stats = self_monitor.get_stats()
print(f"Predictions validated: {stats['predictions_validated']}")
print(f"Snapshots taken: {stats['accuracy_snapshots_taken']}")
print(f"Refinements made: {stats['self_model_refinements']}")
```

### Inspect Prediction Records
```python
for prediction_id, record in self_monitor.prediction_records.items():
    print(f"ID: {prediction_id[:8]}")
    print(f"Category: {record.category}")
    print(f"Correct: {record.correct}")
    print(f"Confidence: {record.predicted_confidence:.2f}")
    print()
```

## References

- Phase 4.1: Advanced Self-Monitoring (foundational self-model)
- Phase 4.2: Introspective Loop (autonomous introspection)
- Phase 4.3: Self-Model Accuracy Tracking (this phase)
