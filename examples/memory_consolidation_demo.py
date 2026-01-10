"""
Memory Consolidation Integration Example

Demonstrates how to use the memory consolidation system with
idle detection and background scheduling.

Author: Lyra Emergence Team
"""
import asyncio
from datetime import datetime
from lyra.memory import (
    MemoryStorage,
    MemoryEncoder,
    MemoryConsolidator,
    EpisodicMemory,
    IdleDetector,
    ConsolidationScheduler,
)


async def main():
    """Example of integrating memory consolidation."""
    
    # Initialize memory system
    print("Initializing memory system...")
    storage = MemoryStorage(
        persistence_dir="memories",
        chain_dir="chain"
    )
    encoder = MemoryEncoder()
    
    # Initialize consolidation system
    print("Initializing consolidation system...")
    consolidator = MemoryConsolidator(
        storage=storage,
        encoder=encoder,
        strengthening_factor=0.1,  # 10% boost per retrieval
        decay_rate=0.95,  # 5% decay per day
        deletion_threshold=0.1,  # Delete memories below 10% activation
        pattern_threshold=3,  # Need 3 occurrences for semantic transfer
    )
    
    # Initialize idle detection
    idle_detector = IdleDetector(
        idle_threshold_seconds=30.0,  # Idle after 30 seconds of inactivity
        activity_decay=0.9
    )
    
    # Initialize consolidation scheduler
    scheduler = ConsolidationScheduler(
        engine=consolidator,
        detector=idle_detector,
        check_interval=10.0  # Check every 10 seconds
    )
    
    # Start background consolidation
    print("Starting background consolidation...")
    await scheduler.start()
    
    try:
        # Simulate some cognitive activity
        episodic = EpisodicMemory(storage, encoder)
        
        print("\nStoring some experiences...")
        for i in range(5):
            experience = {
                "description": f"Experience {i}",
                "timestamp": datetime.now().isoformat(),
                "emotional_tone": ["curious", "engaged"]
            }
            episodic.store_experience(experience, use_blockchain=False)
            idle_detector.record_activity()  # Mark system as active
            await asyncio.sleep(0.5)
        
        # Simulate retrievals
        print("\nSimulating memory retrievals...")
        for i in range(3):
            # In real usage, this would be called by the retrieval system
            consolidator.record_retrieval(f"exp_0", session_id="session_1")
            consolidator.record_retrieval(f"exp_1", session_id="session_1")
            idle_detector.record_activity()
            await asyncio.sleep(0.5)
        
        # Now let system go idle to trigger consolidation
        print("\nSystem going idle... consolidation should run soon...")
        print(f"Idle threshold: {idle_detector.idle_threshold}s")
        
        # Wait for consolidation to run
        await asyncio.sleep(35)  # Wait for idle + consolidation
        
        # Check consolidation metrics
        print("\nConsolidation Metrics:")
        summary = scheduler.get_metrics_summary()
        print(f"  Total cycles: {summary['total_cycles']}")
        print(f"  Total strengthened: {summary['total_strengthened']}")
        print(f"  Total decayed: {summary['total_decayed']}")
        print(f"  Total pruned: {summary['total_pruned']}")
        print(f"  Total patterns extracted: {summary['total_patterns']}")
        print(f"  Total associations updated: {summary['total_associations']}")
        
        # Get recent metrics
        recent = scheduler.get_recent_metrics(limit=3)
        if recent:
            print(f"\nMost recent consolidation:")
            last = recent[-1]
            print(f"  Timestamp: {last.timestamp}")
            print(f"  Budget used: {last.budget_used:.2f}")
            print(f"  Duration: {last.consolidation_duration_ms:.1f}ms")
        
        # Check associations
        print("\nMemory Associations:")
        associated = consolidator.get_associated_memories("exp_0", threshold=0.05)
        for mem_id, strength in associated[:3]:
            print(f"  {mem_id} -> strength: {strength:.3f}")
        
    finally:
        # Stop background consolidation
        print("\nStopping background consolidation...")
        await scheduler.stop()
        print("Done!")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
