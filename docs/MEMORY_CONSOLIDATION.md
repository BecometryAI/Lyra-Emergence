# Memory Consolidation System

A biologically-inspired memory consolidation system that actively maintains, strengthens, and reorganizes memories during idle periods.

## Overview

The memory consolidation system implements processes similar to biological memory systems:

1. **Idle Detection** - Monitors cognitive activity and detects when consolidation can run
2. **Retrieval Strengthening** - Frequently retrieved memories become stronger
3. **Memory Decay** - Unretrieved memories fade over time
4. **Pattern Transfer** - Repeated episodic patterns become semantic knowledge
5. **Association Reorganization** - Co-retrieved memories become more associated
6. **Emotional Reprocessing** - High-emotion memories get special treatment
7. **Background Scheduling** - Consolidation runs during idle periods

## Components

### IdleDetector
Monitors system activity and determines when consolidation can run:

```python
from lyra.memory import IdleDetector

detector = IdleDetector(
    idle_threshold_seconds=30.0,  # Idle after 30s of inactivity
    activity_decay=0.9
)

# Record activity when cognitive processes run
detector.record_activity()

# Check if system is idle
if detector.is_idle():
    budget = detector.get_consolidation_budget()  # 0.0 to 1.0
```

### MemoryConsolidator

The consolidation engine handles:
- **Retrieval strengthening**: Frequently retrieved memories get stronger
- **Time-based decay**: Unretrieved memories fade over time
- **Pattern extraction**: Repeated episodes → semantic knowledge
- **Association tracking**: Co-retrieved memories become associated
- **Emotional processing**: High-emotion memories resist decay

```python
consolidator = MemoryConsolidator(
    storage=storage,
    encoder=encoder,
    strengthening_factor=0.1,  # Boost per retrieval
    decay_rate=0.95,  # Daily decay rate
    deletion_threshold=0.1,  # Minimum activation to keep
    pattern_threshold=3,  # Episodes for semantic transfer
)

# Record when memories are retrieved
consolidator.record_retrieval(memory_id, session_id="session_1")

# Manual consolidation operations
strengthened = consolidator.strengthen_retrieved_memories(hours=24)
decayed, pruned = consolidator.apply_decay(threshold_days=7)
patterns = consolidator.transfer_to_semantic(days=30)
associations = consolidator.reorganize_associations()
emotional = consolidator.reprocess_emotional_memories()
```

### Idle Detection

```python
from lyra.memory import IdleDetector

# Create idle detector
detector = IdleDetector(
    idle_threshold_seconds=30.0,  # Idle after 30s
    activity_decay=0.9
)

# Record activity when cognitive processes occur
detector.record_activity()

# Check if system is idle
if detector.is_idle():
    budget = detector.get_consolidation_budget()
    # Run consolidation with budget
```

### Consolidation Scheduler

```python
from lyra.memory import ConsolidationScheduler

# Create scheduler
scheduler = ConsolidationScheduler(
    engine=consolidator,
    detector=idle_detector,
    check_interval=10.0  # Check every 10 seconds
)

# Start background consolidation
await scheduler.start()

# ... system runs ...

# Get metrics
summary = scheduler.get_metrics_summary()
print(f"Total cycles: {summary['total_cycles']}")
print(f"Total strengthened: {summary['total_strengthened']}")

# Stop when done
await scheduler.stop()
```

## Implementation Details

### Idle Detection
- Monitors system activity
- Calculates consolidation budget based on idle duration
- Budget determines which operations run (minimal/standard/full)

### Consolidation Operations

**Retrieval-based Strengthening:**
- Tracks memory retrievals in log
- Logarithmic strengthening (diminishing returns)
- Updates `base_activation` metadata

**Time-based Decay:**
- Exponential decay for unretrieved memories
- Configurable threshold for deletion
- Preserves memories accessed recently

**Pattern Transfer:**
- Groups episodic memories by shared tags
- Extracts repeated patterns as semantic knowledge
- Weakens individual episodes after pattern extraction

**Association Reorganization:**
- Tracks co-retrieval in sessions
- Strengthens associations between co-retrieved memories
- Decays weak associations over time

**Emotional Memory Processing:**
- High-emotion memories resist decay
- Get extra strengthening during consolidation
- Form stronger associations

## Usage Example

See `examples/memory_consolidation_demo.py` for a complete integration example.

Basic usage:

```python
from lyra.memory import (
    MemoryConsolidator,
    IdleDetector,
    ConsolidationScheduler,
)

# Initialize components
consolidator = MemoryConsolidator(storage, encoder)
idle_detector = IdleDetector(idle_threshold_seconds=30.0)
scheduler = ConsolidationScheduler(consolidator, idle_detector)

# Start background consolidation
await scheduler.start()

# ... your application runs ...

# Stop when done
await scheduler.stop()
```

The consolidation system will automatically:
- Strengthen frequently retrieved memories
- Decay unretrieved memories
- Extract patterns into semantic memory
- Reorganize memory associations
- Give special treatment to emotional memories

All of this happens automatically during idle periods without interfering with active cognition!