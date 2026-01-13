"""
Example: Using the Communication Decision Loop

This example demonstrates how to integrate and use the Communication Decision Loop
with the Drive and Inhibition systems to make SPEAK/SILENCE/DEFER decisions.
"""

from lyra.cognitive_core.communication import (
    CommunicationDecisionLoop,
    CommunicationDriveSystem,
    CommunicationInhibitionSystem,
    CommunicationDecision
)
from unittest.mock import MagicMock

# Initialize the three systems
drive_system = CommunicationDriveSystem(config={
    "insight_threshold": 0.7,
    "emotional_threshold": 0.6,
    "social_silence_minutes": 30
})

inhibition_system = CommunicationInhibitionSystem(config={
    "low_value_threshold": 0.3,
    "min_output_spacing_seconds": 5,
    "redundancy_similarity_threshold": 0.8
})

decision_loop = CommunicationDecisionLoop(
    drive_system=drive_system,
    inhibition_system=inhibition_system,
    config={
        "speak_threshold": 0.3,        # Net pressure > 0.3 = SPEAK
        "silence_threshold": -0.2,     # Net pressure < -0.2 = SILENCE
        "defer_min_drive": 0.3,        # Min drive for deferral
        "defer_min_inhibition": 0.3,   # Min inhibition for deferral
        "defer_duration_seconds": 30   # How long to defer
    }
)

# Example cognitive cycle integration
def cognitive_cycle_with_communication_decision(workspace_state, emotional_state, goals, memories):
    """
    Example of how to integrate decision loop into a cognitive cycle.
    """
    
    # Step 1: Compute drives (internal urges to speak)
    new_urges = drive_system.compute_drives(
        workspace_state=workspace_state,
        emotional_state=emotional_state,
        goals=goals,
        memories=memories
    )
    print(f"Generated {len(new_urges)} new urges, total active: {len(drive_system.active_urges)}")
    
    # Step 2: Compute inhibitions (reasons not to speak)
    # You would normally calculate these from the actual state
    confidence = 0.8
    content_value = 0.7
    
    new_inhibitions = inhibition_system.compute_inhibitions(
        workspace_state=workspace_state,
        urges=drive_system.active_urges,
        confidence=confidence,
        content_value=content_value,
        emotional_state=emotional_state
    )
    print(f"Generated {len(new_inhibitions)} new inhibitions, total active: {len(inhibition_system.active_inhibitions)}")
    
    # Step 3: Make communication decision
    decision_result = decision_loop.evaluate(
        workspace_state=workspace_state,
        emotional_state=emotional_state,
        goals=goals,
        memories=memories
    )
    
    print(f"\n🎯 Decision: {decision_result.decision.value.upper()}")
    print(f"   Reason: {decision_result.reason}")
    print(f"   Confidence: {decision_result.confidence:.2f}")
    print(f"   Drive: {decision_result.drive_level:.2f}, Inhibition: {decision_result.inhibition_level:.2f}")
    print(f"   Net Pressure: {decision_result.net_pressure:.2f}")
    
    # Step 4: Act on decision
    if decision_result.decision == CommunicationDecision.SPEAK:
        # Generate and emit output
        output = generate_output(decision_result.urge)
        print(f"\n💬 Speaking: {output}")
        
        # Record output
        drive_system.record_output()
        inhibition_system.record_output(content=output)
        
        return output
        
    elif decision_result.decision == CommunicationDecision.SILENCE:
        # Explicitly choosing silence
        print(f"\n🔇 Staying silent: {decision_result.reason}")
        return None
        
    elif decision_result.decision == CommunicationDecision.DEFER:
        # Communication deferred for later
        print(f"\n⏸️  Deferred until: {decision_result.defer_until}")
        print(f"   Deferred queue size: {len(decision_loop.deferred_queue)}")
        return None
    
    return None


def generate_output(urge):
    """Stub for output generation based on urge."""
    if urge:
        return f"[Generated output from {urge.drive_type.value} urge: {urge.content or 'No specific content'}]"
    return "[Default output]"


# Example usage
if __name__ == "__main__":
    print("="*60)
    print("COMMUNICATION DECISION LOOP EXAMPLE")
    print("="*60)
    
    # Simulate a few cognitive cycles
    
    # Cycle 1: No strong urges, no inhibitions → SILENCE
    print("\n--- Cycle 1: Low activity ---")
    workspace = MagicMock(percepts={})
    emotional_state = {"valence": 0.0, "arousal": 0.2, "dominance": 0.5}
    cognitive_cycle_with_communication_decision(workspace, emotional_state, [], [])
    
    # Cycle 2: High emotional state → SPEAK
    print("\n--- Cycle 2: High emotion ---")
    emotional_state = {"valence": 0.9, "arousal": 0.8, "dominance": 0.7}
    cognitive_cycle_with_communication_decision(workspace, emotional_state, [], [])
    
    # Cycle 3: Moderate drive and inhibition → DEFER
    print("\n--- Cycle 3: Check deferred queue ---")
    # The deferred item from cycle 2 might be ready
    emotional_state = {"valence": 0.5, "arousal": 0.5, "dominance": 0.5}
    cognitive_cycle_with_communication_decision(workspace, emotional_state, [], [])
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    summary = decision_loop.get_decision_summary()
    print(f"Total decisions made: {summary['decision_history_size']}")
    print(f"Recent decisions: {summary['recent_decisions']}")
    print(f"Deferred queue size: {summary['deferred_queue_size']}")
    print(f"Ready for reconsideration: {summary['ready_deferred']}")
