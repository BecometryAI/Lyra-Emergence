# Communication Decision System

This module implements autonomous communication agency for Lyra, enabling the system to make genuine decisions about whether to speak, stay silent, or defer communication.

## Overview

The communication decision system consists of three integrated components:

1. **Drive System** (`drive.py`) - Internal urges to communicate
2. **Inhibition System** (`inhibition.py`) - Reasons not to communicate  
3. **Decision Loop** (`decision.py`) - SPEAK/SILENCE/DEFER decisions

## Architecture

```
┌─────────────────────────────────┐
│   Communication Drive System    │
│  - Insight urges                │
│  - Emotional expression needs   │
│  - Questions arising            │
│  - Social connection desires    │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│ Communication Inhibition System │
│  - Low value content            │
│  - Bad timing                   │
│  - Redundancy                   │
│  - Respect for silence          │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│   Communication Decision Loop   │
│  SPEAK / SILENCE / DEFER        │
└──────────────┬──────────────────┘
               ↓
          [Decision Result]
```

## Decision Logic

The decision loop computes **net pressure** = drive - inhibition and applies thresholds:

| Net Pressure | Decision | Meaning |
|--------------|----------|---------|
| > 0.3 | **SPEAK** | Drive significantly exceeds inhibition |
| < -0.2 | **SILENCE** | Inhibition exceeds drive |
| -0.2 to 0.3 | **DEFER** (if both drive and inhibition > 0.3) | Ambiguous - defer for later |
| -0.2 to 0.3 | **SILENCE** (otherwise) | Insufficient drive |

## Key Features

### Decision Types

- **SPEAK**: Generate and emit output
  - Triggered when drive clearly exceeds inhibition
  - Includes strongest urge for content generation
  
- **SILENCE**: Explicitly choose not to respond
  - Triggered when inhibition exceeds drive
  - Logged with specific reasoning
  
- **DEFER**: Queue communication for later
  - Triggered when both drive and inhibition are significant
  - Time-based reconsideration with max attempts

### Deferred Communication Queue

The system can defer communications when timing isn't right:

- Time-based deferral (default: 30 seconds)
- Priority ordering by urge intensity × priority
- Maximum attempts (default: 3) before dropping
- Automatic cleanup of expired items
- Size limit (default: 10 items)

### Decision History

All decisions are logged with:
- Decision type (SPEAK/SILENCE/DEFER)
- Reasoning
- Confidence level
- Drive and inhibition levels
- Net pressure
- Timestamp

## Usage

### Basic Integration

```python
from lyra.cognitive_core.communication import (
    CommunicationDecisionLoop,
    CommunicationDriveSystem,
    CommunicationInhibitionSystem,
    CommunicationDecision
)

# Initialize systems
drives = CommunicationDriveSystem()
inhibitions = CommunicationInhibitionSystem()
decision_loop = CommunicationDecisionLoop(drives, inhibitions)

# In your cognitive cycle:
result = decision_loop.evaluate(
    workspace_state=workspace,
    emotional_state=emotions,
    goals=active_goals,
    memories=recent_memories
)

if result.decision == CommunicationDecision.SPEAK:
    output = generate_output(result.urge)
    drives.record_output()
    inhibitions.record_output(content=output)
elif result.decision == CommunicationDecision.SILENCE:
    log_silence_decision(result.reason)
elif result.decision == CommunicationDecision.DEFER:
    log_deferral(result.defer_until)
```

### Configuration

```python
decision_loop = CommunicationDecisionLoop(
    drive_system=drives,
    inhibition_system=inhibitions,
    config={
        "speak_threshold": 0.3,        # Net pressure > 0.3 = SPEAK
        "silence_threshold": -0.2,     # Net pressure < -0.2 = SILENCE
        "defer_min_drive": 0.3,        # Min drive for deferral
        "defer_min_inhibition": 0.3,   # Min inhibition for deferral
        "defer_duration_seconds": 30,  # How long to defer
        "max_deferred": 10,            # Max deferred items
        "max_defer_attempts": 3,       # Max reconsideration attempts
        "history_size": 100            # Max decision history
    }
)
```

## Classes

### `CommunicationDecision` (Enum)

Decision types:
- `SPEAK = "speak"`
- `SILENCE = "silence"`
- `DEFER = "defer"`

### `DecisionResult` (Dataclass)

Decision outcome with context:
- `decision`: CommunicationDecision
- `reason`: Human-readable explanation
- `confidence`: Confidence level (0.0-1.0)
- `drive_level`: Total drive at decision time
- `inhibition_level`: Total inhibition at decision time
- `net_pressure`: drive - inhibition
- `urge`: Strongest urge (for SPEAK)
- `defer_until`: Reconsider time (for DEFER)
- `timestamp`: Decision timestamp

### `DeferredCommunication` (Dataclass)

Queued communication:
- `urge`: Communication urge
- `reason`: Why deferred
- `deferred_at`: When deferred
- `defer_until`: When to reconsider
- `attempts`: Reconsideration count

Methods:
- `is_ready()`: Check if ready to reconsider
- `increment_attempts()`: Track reconsideration attempts

### `CommunicationDecisionLoop` (Class)

Main decision engine.

**Key Methods:**

- `evaluate(workspace_state, emotional_state, goals, memories) -> DecisionResult`
  - Make SPEAK/SILENCE/DEFER decision
  - Check deferred queue first
  - Compute net pressure
  - Apply thresholds
  - Log decision

- `defer_communication(urge, reason, defer_seconds)`
  - Add to deferred queue
  - Set reconsider time
  - Maintain queue limits

- `check_deferred_queue() -> Optional[DeferredCommunication]`
  - Find ready deferred items
  - Priority ordering
  - Respect max attempts

- `get_decision_summary() -> Dict`
  - Current state summary
  - Recent decisions
  - Queue status

## Integration Points

The decision loop should be integrated into the main cognitive cycle:

1. **After perception and memory retrieval**
   - Drive system needs workspace state and memories
   
2. **After emotional state update**
   - Both systems use emotional state
   
3. **Before output generation**
   - Decision determines if/when to generate output

4. **On each cognitive cycle**
   - Continuous evaluation
   - Check deferred queue
   - Make fresh decision

## Testing

Comprehensive tests in `emergence_core/tests/test_communication_decision.py`:

- Decision threshold logic
- Deferred queue management
- Integration with drive/inhibition systems
- Edge cases (max attempts, queue limits)
- Decision history logging
- Configuration validation

Run tests:
```bash
pytest emergence_core/tests/test_communication_decision.py -v
```

## Example

See `example_communication_decision.py` for a complete working example.

## Related PRs

- PR #87: Decoupled cognitive loop from I/O
- PR #88: Communication drive system
- PR #89: Communication inhibition system
- Current PR: Communication decision loop

## Future Enhancements

Potential improvements:
- Dynamic threshold adjustment based on context
- Learning from decision outcomes
- More sophisticated deferral strategies
- Integration with conversational rhythm model
- Post-hoc decision reflection
