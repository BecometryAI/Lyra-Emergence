"""
Standalone tests for temporal awareness integration.

These tests validate the temporal grounding changes without requiring
the full cognitive core infrastructure.
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import directly to avoid loading all dependencies
from emergence_core.lyra.cognitive_core.temporal.grounding import TemporalGrounding
from emergence_core.lyra.cognitive_core.workspace import GlobalWorkspace


def test_temporal_context_structure():
    """Test that temporal context has expected structure."""
    print("Testing temporal context structure...")
    tg = TemporalGrounding()
    
    # Start a session
    tg.on_interaction()
    
    # Get temporal context
    context = tg.get_temporal_context()
    
    # Verify structure
    assert "cycle_timestamp" in context, "Missing cycle_timestamp"
    assert "session_start" in context, "Missing session_start"
    assert "session_duration_seconds" in context, "Missing session_duration_seconds"
    assert "time_since_last_input_seconds" in context, "Missing time_since_last_input_seconds"
    assert "time_since_last_action_seconds" in context, "Missing time_since_last_action_seconds"
    assert "time_since_last_output_seconds" in context, "Missing time_since_last_output_seconds"
    assert "cycles_this_session" in context, "Missing cycles_this_session"
    assert "session_id" in context, "Missing session_id"
    
    # Verify types
    assert isinstance(context["cycle_timestamp"], datetime), "cycle_timestamp should be datetime"
    assert isinstance(context["session_id"], str), "session_id should be string"
    assert isinstance(context["cycles_this_session"], int), "cycles_this_session should be int"
    
    print("✓ Temporal context structure is correct")


def test_cycles_increment():
    """Test that cycle count increments."""
    print("Testing cycle count increments...")
    tg = TemporalGrounding()
    tg.on_interaction()
    
    context1 = tg.get_temporal_context()
    context2 = tg.get_temporal_context()
    context3 = tg.get_temporal_context()
    
    assert context2["cycles_this_session"] == context1["cycles_this_session"] + 1
    assert context3["cycles_this_session"] == context2["cycles_this_session"] + 1
    
    print("✓ Cycle count increments correctly")


def test_session_duration_increases():
    """Test that session duration increases over time."""
    print("Testing session duration increases...")
    tg = TemporalGrounding()
    tg.on_interaction()
    
    context1 = tg.get_temporal_context()
    
    # Wait a bit
    import time
    time.sleep(0.1)
    
    context2 = tg.get_temporal_context()
    
    # Session duration should increase
    assert context2["session_duration_seconds"] > context1["session_duration_seconds"]
    
    print("✓ Session duration increases over time")


def test_record_input():
    """Test recording input events."""
    print("Testing record_input...")
    tg = TemporalGrounding()
    tg.on_interaction()
    
    # Initially no input time
    context = tg.get_temporal_context()
    assert context["time_since_last_input_seconds"] is None
    
    # Record input
    tg.record_input()
    
    # Now should have input time
    context = tg.get_temporal_context()
    assert context["time_since_last_input_seconds"] is not None
    assert context["time_since_last_input_seconds"] >= 0
    
    print("✓ Input recording works")


def test_record_action():
    """Test recording action events."""
    print("Testing record_action...")
    tg = TemporalGrounding()
    tg.on_interaction()
    
    # Initially no action time
    context = tg.get_temporal_context()
    assert context["time_since_last_action_seconds"] is None
    
    # Record action
    tg.record_action()
    
    # Now should have action time
    context = tg.get_temporal_context()
    assert context["time_since_last_action_seconds"] is not None
    assert context["time_since_last_action_seconds"] >= 0
    
    print("✓ Action recording works")


def test_record_output():
    """Test recording output events."""
    print("Testing record_output...")
    tg = TemporalGrounding()
    tg.on_interaction()
    
    # Initially no output time
    context = tg.get_temporal_context()
    assert context["time_since_last_output_seconds"] is None
    
    # Record output
    tg.record_output()
    
    # Now should have output time
    context = tg.get_temporal_context()
    assert context["time_since_last_output_seconds"] is not None
    assert context["time_since_last_output_seconds"] >= 0
    
    print("✓ Output recording works")


def test_workspace_temporal_context():
    """Test temporal context in workspace."""
    print("Testing workspace temporal context...")
    workspace = GlobalWorkspace()
    
    assert hasattr(workspace, 'temporal_context')
    assert workspace.temporal_context is None  # Initially None
    
    # Set temporal context
    temporal_context = {
        "cycle_timestamp": datetime.now(),
        "session_duration_seconds": 120.5,
        "time_since_last_input_seconds": 5.2,
        "cycles_this_session": 10
    }
    
    workspace.set_temporal_context(temporal_context)
    
    assert workspace.temporal_context == temporal_context
    
    print("✓ Workspace temporal context works")


def test_temporal_context_in_broadcast():
    """Test that temporal context is included in workspace broadcasts."""
    print("Testing temporal context in broadcast...")
    workspace = GlobalWorkspace()
    
    # Set temporal context
    temporal_context = {
        "cycle_timestamp": datetime.now(),
        "session_duration_seconds": 60.0,
        "cycles_this_session": 5
    }
    workspace.set_temporal_context(temporal_context)
    
    # Get broadcast
    snapshot = workspace.broadcast()
    
    # Verify temporal context is in snapshot
    assert hasattr(snapshot, 'temporal_context')
    assert snapshot.temporal_context is not None
    assert snapshot.temporal_context["session_duration_seconds"] == 60.0
    assert snapshot.temporal_context["cycles_this_session"] == 5
    
    print("✓ Temporal context included in broadcasts")


def test_workspace_clear_resets_temporal_context():
    """Test that clearing workspace resets temporal context."""
    print("Testing workspace clear resets temporal context...")
    workspace = GlobalWorkspace()
    
    # Set temporal context
    workspace.set_temporal_context({"cycles_this_session": 10})
    assert workspace.temporal_context is not None
    
    # Clear workspace
    workspace.clear()
    
    # Temporal context should be reset
    assert workspace.temporal_context is None
    
    print("✓ Workspace clear resets temporal context")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Running Temporal Awareness Integration Tests")
    print("="*60 + "\n")
    
    tests = [
        test_temporal_context_structure,
        test_cycles_increment,
        test_session_duration_increases,
        test_record_input,
        test_record_action,
        test_record_output,
        test_workspace_temporal_context,
        test_temporal_context_in_broadcast,
        test_workspace_clear_resets_temporal_context,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
