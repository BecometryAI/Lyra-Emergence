#!/usr/bin/env python3
"""
Example: Using Meta-Cognitive Capabilities

This example demonstrates how to use the meta-cognitive system to:
1. Monitor cognitive processes
2. Learn from action outcomes
3. Track attention allocation
4. Get self-assessment
"""

import time
import random
from datetime import datetime


# Simplified versions for standalone example
class MockCognitiveResources:
    def __init__(self, attention_budget=1.0, processing_budget=1.0):
        self.attention_budget = attention_budget
        self.processing_budget = processing_budget
        self.action_budget = 1.0
        self.time_budget = 1.0
    
    def total(self):
        return (self.attention_budget + self.processing_budget + 
                self.action_budget + self.time_budget)


def main():
    # Import the meta-cognitive system
    # Note: In real usage, import from lyra.cognitive_core.meta_cognition
    print("=" * 60)
    print("Meta-Cognitive Capabilities Example")
    print("=" * 60)
    
    # Simulate a meta-cognitive system
    print("\n[Simulating Meta-Cognitive System]")
    print("In real usage, initialize with:")
    print("  from lyra.cognitive_core.meta_cognition import MetaCognitiveSystem")
    print("  meta_system = MetaCognitiveSystem()")
    
    # Example 1: Processing Monitoring
    print("\n" + "=" * 60)
    print("Example 1: Processing Monitoring")
    print("=" * 60)
    
    print("\n1.1 Monitoring a reasoning process:")
    print("""
with meta_system.monitor.observe('reasoning') as ctx:
    ctx.input_complexity = 0.7
    result = perform_reasoning()
    ctx.output_quality = 0.9
    """)
    
    print("\n1.2 Getting process statistics:")
    print("""
stats = meta_system.monitor.get_process_statistics('reasoning')
print(f"Success rate: {stats.success_rate:.2%}")
print(f"Avg duration: {stats.avg_duration_ms:.1f}ms")
print(f"Avg quality: {stats.avg_quality:.2f}")
    """)
    
    print("\n1.3 Identifying patterns:")
    print("""
patterns = meta_system.monitor.get_identified_patterns()
for pattern in patterns:
    if pattern.pattern_type == 'failure_mode':
        print(f"Failure: {pattern.description}")
        print(f"Suggested fix: {pattern.suggested_adaptation}")
    """)
    
    # Example 2: Action-Outcome Learning
    print("\n" + "=" * 60)
    print("Example 2: Action-Outcome Learning")
    print("=" * 60)
    
    print("\n2.1 Recording what actions achieve:")
    print("""
meta_system.record_action_outcome(
    action_id="act_123",
    action_type="speak",
    intended="provide helpful response",
    actual="provided detailed answer with examples",
    context={
        "user_query_complexity": 0.6,
        "available_context": True
    }
)
    """)
    
    print("\n2.2 Checking action reliability:")
    print("""
reliability = meta_system.get_action_reliability("speak")
print(f"Success rate: {reliability.success_rate:.2%}")
print(f"Common side effects: {reliability.common_side_effects}")
    """)
    
    print("\n2.3 Predicting outcomes:")
    print("""
prediction = meta_system.predict_action_outcome(
    action_type="speak",
    context={"user_query_complexity": 0.8}
)
print(f"Probability of success: {prediction.probability_success:.2%}")
    """)
    
    # Example 3: Attention Allocation
    print("\n" + "=" * 60)
    print("Example 3: Attention Allocation History")
    print("=" * 60)
    
    print("\n3.1 Recording attention allocation:")
    print("""
alloc_id = meta_system.record_attention(
    allocation={
        "goal_1": 0.6,  # 60% attention
        "goal_2": 0.3,  # 30% attention
        "goal_3": 0.1   # 10% attention
    },
    trigger="goal_priority",
    workspace_state=current_workspace
)
    """)
    
    print("\n3.2 Recording what was achieved:")
    print("""
meta_system.record_attention_outcome(
    allocation_id=alloc_id,
    goal_progress={
        "goal_1": 0.4,  # 40% progress
        "goal_2": 0.1   # 10% progress
    },
    discoveries=["new_insight"],
    missed=[]
)
    """)
    
    print("\n3.3 Getting recommendations:")
    print("""
recommendation = meta_system.get_recommended_attention(
    context=workspace,
    goals=active_goals
)
# Uses learned patterns to suggest allocation
    """)
    
    # Example 4: Self-Assessment
    print("\n" + "=" * 60)
    print("Example 4: Self-Assessment and Introspection")
    print("=" * 60)
    
    print("\n4.1 Getting self-assessment:")
    print("""
assessment = meta_system.get_self_assessment()

print("Strengths:")
for strength in assessment.identified_strengths:
    print(f"  ✓ {strength}")

print("\\nWeaknesses:")
for weakness in assessment.identified_weaknesses:
    print(f"  ⚠ {weakness}")

print("\\nAdaptations:")
for adaptation in assessment.suggested_adaptations:
    print(f"  → {adaptation}")
    """)
    
    print("\n4.2 Introspection queries:")
    print("""
# Ask about failures
response = meta_system.introspect("What do I tend to fail at?")
print(response)

# Ask about strengths
response = meta_system.introspect("What am I good at?")
print(response)

# Ask about attention
response = meta_system.introspect("How effective is my attention?")
print(response)
    """)
    
    # Simulated scenario
    print("\n" + "=" * 60)
    print("Simulated Scenario: Learning from 10 Processing Episodes")
    print("=" * 60)
    
    print("\nSimulating 10 cognitive processes...")
    successes = 0
    failures = 0
    
    for i in range(10):
        # Simulate varying complexity and outcomes
        complexity = random.uniform(0.3, 0.9)
        duration = random.uniform(50, 200)
        
        # High complexity tends to fail
        if complexity > 0.7:
            success = random.random() > 0.6  # 40% success rate
            quality = random.uniform(0.1, 0.4) if not success else random.uniform(0.5, 0.7)
        else:
            success = random.random() > 0.2  # 80% success rate
            quality = random.uniform(0.6, 0.9)
        
        if success:
            successes += 1
        else:
            failures += 1
        
        print(f"  Process {i+1}: complexity={complexity:.2f}, "
              f"duration={duration:.1f}ms, success={success}, quality={quality:.2f}")
        
        time.sleep(0.05)  # Small delay for realism
    
    print(f"\nResults: {successes} successes, {failures} failures")
    print(f"Success rate: {successes/10:.1%}")
    
    print("\n📊 Pattern Detection Results:")
    print("  ✓ Detected: High complexity (>0.7) correlates with failure")
    print("  ✓ Suggestion: Break complex inputs into smaller chunks")
    print("  ✓ Detected: Low complexity (<0.5) leads to faster processing")
    print("  ✓ Suggestion: Simplify inputs when speed is important")
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print("""
The meta-cognitive system provides three key capabilities:

1. 🔍 Processing Monitoring
   - Track success/failure patterns
   - Identify what makes processes succeed or fail
   - Detect efficiency factors

2. 🎯 Action-Outcome Learning
   - Learn what actions actually achieve
   - Build reliability models
   - Predict outcomes before acting

3. 👁️ Attention Allocation History
   - Track attention effectiveness
   - Learn optimal allocation patterns
   - Recommend allocations based on context

Together, these enable the system to:
- Understand its own strengths and weaknesses
- Learn from experience
- Adapt strategies based on past performance
- Answer introspective questions about behavior

See USAGE.md for detailed documentation.
    """)
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
