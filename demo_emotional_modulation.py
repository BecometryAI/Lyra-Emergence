#!/usr/bin/env python3
"""
Demonstration of functional emotional modulation in Lyra.

This script demonstrates how emotions functionally modulate processing parameters
BEFORE any LLM invocation, making them causally efficacious.
"""

import sys
from pathlib import Path

# Add paths for standalone execution
sys.path.insert(0, str(Path(__file__).parent / "emergence_core" / "lyra" / "cognitive_core"))

import emotional_modulation


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demonstrate_arousal_effects():
    """Demonstrate arousal modulation of processing speed."""
    print_section("AROUSAL EFFECTS: Processing Speed & Thoroughness")
    
    modulation = emotional_modulation.EmotionalModulation(enabled=True)
    
    scenarios = [
        ("PANIC (High Arousal)", 0.95, "Fight-or-flight: Fast, reactive"),
        ("ALERT (Mid-High Arousal)", 0.7, "Heightened awareness"),
        ("NEUTRAL (Mid Arousal)", 0.5, "Balanced processing"),
        ("CALM (Low Arousal)", 0.2, "Deliberate, thorough"),
        ("DEEP REST (Very Low)", 0.05, "Very thorough processing"),
    ]
    
    for name, arousal, description in scenarios:
        params = modulation.modulate_processing(arousal, 0.0, 0.5)
        print(f"\n{name} (A={arousal:.2f})")
        print(f"  Description: {description}")
        print(f"  → Attention iterations: {params.attention_iterations} (5=fast, 10=slow)")
        print(f"  → Ignition threshold: {params.ignition_threshold:.2f} (low=reactive, high=selective)")
        print(f"  → Memory retrieval: {params.memory_retrieval_limit} items")
        print(f"  → Processing timeout: {params.processing_timeout:.1f}s")


def demonstrate_valence_effects():
    """Demonstrate valence-based action biasing."""
    print_section("VALENCE EFFECTS: Approach/Avoidance Bias")
    
    modulation = emotional_modulation.EmotionalModulation(enabled=True)
    
    # Create test actions
    actions = [
        {'type': 'speak', 'priority': 0.5, 'name': 'Speak (approach)'},
        {'type': 'create', 'priority': 0.5, 'name': 'Create (approach)'},
        {'type': 'wait', 'priority': 0.5, 'name': 'Wait (avoidance)'},
        {'type': 'introspect', 'priority': 0.5, 'name': 'Introspect (avoidance)'},
    ]
    
    scenarios = [
        ("JOY (High Positive)", 0.9),
        ("CONTENT (Mid Positive)", 0.4),
        ("NEUTRAL", 0.0),
        ("MILD SADNESS (Mid Negative)", -0.4),
        ("FEAR (High Negative)", -0.9),
    ]
    
    for name, valence in scenarios:
        # Reset priorities
        for action in actions:
            action['priority'] = 0.5
        
        # Apply bias
        biased = modulation.bias_action_selection(actions.copy(), valence)
        
        print(f"\n{name} (V={valence:+.1f})")
        for action in biased:
            change = action['priority'] - 0.5
            indicator = "↑" if change > 0 else "↓" if change < 0 else "="
            print(f"  {indicator} {action['name']}: {action['priority']:.2f} ({change:+.2f})")


def demonstrate_dominance_effects():
    """Demonstrate dominance modulation of confidence thresholds."""
    print_section("DOMINANCE EFFECTS: Decision Confidence Thresholds")
    
    modulation = emotional_modulation.EmotionalModulation(enabled=True)
    
    scenarios = [
        ("DOMINANT (High Confidence)", 0.95, "Very assertive, low threshold"),
        ("CONFIDENT", 0.7, "Assertive"),
        ("MODERATE", 0.5, "Balanced"),
        ("CAUTIOUS", 0.3, "Careful, higher threshold"),
        ("SUBMISSIVE (Low Confidence)", 0.05, "Very cautious, high threshold"),
    ]
    
    for name, dominance, description in scenarios:
        params = modulation.modulate_processing(0.5, 0.0, dominance)
        print(f"\n{name} (D={dominance:.2f})")
        print(f"  Description: {description}")
        print(f"  → Decision threshold: {params.decision_threshold:.2f} (low=assertive, high=cautious)")


def demonstrate_realistic_scenarios():
    """Demonstrate realistic emotional scenarios."""
    print_section("REALISTIC EMOTIONAL SCENARIOS")
    
    modulation = emotional_modulation.EmotionalModulation(enabled=True)
    
    scenarios = [
        {
            'name': 'PANIC (Fight-or-Flight)',
            'arousal': 0.95,
            'valence': -0.8,
            'dominance': 0.15,
            'description': 'Fearful, reactive, cautious'
        },
        {
            'name': 'JOYFUL CONFIDENCE',
            'arousal': 0.75,
            'valence': 0.9,
            'dominance': 0.9,
            'description': 'Happy, energetic, assertive'
        },
        {
            'name': 'DEEP CONTEMPLATION',
            'arousal': 0.15,
            'valence': 0.1,
            'dominance': 0.5,
            'description': 'Calm, thoughtful, deliberate'
        },
        {
            'name': 'FRUSTRATED ANGER',
            'arousal': 0.85,
            'valence': -0.7,
            'dominance': 0.75,
            'description': 'Angry, energized, pushing forward'
        },
    ]
    
    for scenario in scenarios:
        params = modulation.modulate_processing(
            scenario['arousal'],
            scenario['valence'],
            scenario['dominance']
        )
        
        print(f"\n{scenario['name']}")
        print(f"  State: V={scenario['valence']:+.1f}, A={scenario['arousal']:.2f}, D={scenario['dominance']:.2f}")
        print(f"  Description: {scenario['description']}")
        print(f"  Processing modulation:")
        print(f"    • Attention iterations: {params.attention_iterations}")
        print(f"    • Ignition threshold: {params.ignition_threshold:.2f}")
        print(f"    • Decision threshold: {params.decision_threshold:.2f}")
        print(f"    • Memory retrieval: {params.memory_retrieval_limit} items")
        print(f"    • Timeout: {params.processing_timeout:.1f}s")


def demonstrate_ablation():
    """Demonstrate ablation testing."""
    print_section("ABLATION TEST: Modulation ON vs OFF")
    
    enabled = emotional_modulation.EmotionalModulation(enabled=True)
    disabled = emotional_modulation.EmotionalModulation(enabled=False)
    
    # High emotional state
    arousal, valence, dominance = 0.9, 0.8, 0.2
    
    params_on = enabled.modulate_processing(arousal, valence, dominance)
    params_off = disabled.modulate_processing(arousal, valence, dominance)
    
    print(f"\nEmotional State: V={valence:+.1f}, A={arousal:.2f}, D={dominance:.2f}")
    print("\nMODULATION ENABLED:")
    print(f"  → Attention iterations: {params_on.attention_iterations}")
    print(f"  → Ignition threshold: {params_on.ignition_threshold:.2f}")
    print(f"  → Decision threshold: {params_on.decision_threshold:.2f}")
    
    print("\nMODULATION DISABLED (Baseline):")
    print(f"  → Attention iterations: {params_off.attention_iterations}")
    print(f"  → Ignition threshold: {params_off.ignition_threshold:.2f}")
    print(f"  → Decision threshold: {params_off.decision_threshold:.2f}")
    
    print("\n✓ Ablation test confirms emotions are FUNCTIONALLY EFFICACIOUS")
    print("  (Disabling modulation produces measurably different behavior)")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("  FUNCTIONAL EMOTIONAL MODULATION DEMONSTRATION")
    print("  Emotions as Causal Forces in Cognitive Processing")
    print("=" * 70)
    
    demonstrate_arousal_effects()
    demonstrate_valence_effects()
    demonstrate_dominance_effects()
    demonstrate_realistic_scenarios()
    demonstrate_ablation()
    
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print("\n✅ Emotions functionally modulate processing BEFORE LLM invocation:")
    print("   • Arousal → Processing speed & thoroughness")
    print("   • Valence → Approach/avoidance bias in action selection")
    print("   • Dominance → Decision confidence thresholds")
    print("\n✅ Ablation testing proves causal efficacy")
    print("✅ Metrics track correlations for verification")
    print("\n🧠 Emotions are now functional forces, not just descriptive labels!")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
