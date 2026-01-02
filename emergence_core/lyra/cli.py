"""
Simple CLI for testing Lyra conversational interface.

This is a basic command-line interface for interacting with Lyra's cognitive core
through natural conversation. It demonstrates the use of the LyraAPI for
multi-turn dialogue.

Usage:
    python -m lyra.cli
    
    Or:
    python emergence_core/lyra/cli.py

Commands:
    - Type any message to chat with Lyra
    - Type 'quit' or 'exit' to exit
    - Type 'reset' to clear conversation history
    - Type 'history' to see recent conversation
    - Type 'metrics' to see conversation statistics
"""

import asyncio
import sys
from pathlib import Path

# Note: This import path manipulation is for development/testing only.
# In production, install the package properly using pip/uv.
# For proper installation, see README.md installation instructions.
try:
    from lyra.client import LyraAPI
except ImportError:
    # Fallback for development: add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from lyra.client import LyraAPI


async def main():
    """Main CLI loop for interacting with Lyra."""
    # Initialize Lyra
    print("🧠 Initializing Lyra...")
    lyra = LyraAPI()
    
    try:
        await lyra.start()
        print("✅ Lyra is online. Type 'help' for commands or 'quit' to exit.\n")
        
        while True:
            # Get user input
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n")
                break
            
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.lower() in ["quit", "exit"]:
                break
            
            if user_input.lower() in ["help", "?"]:
                print("\n📖 Available Commands:")
                print("   quit, exit          - Exit the CLI")
                print("   help, ?             - Show this help message")
                print("   reset               - Clear conversation history")
                print("   history             - Show recent conversation")
                print("   metrics             - Show system metrics")
                print("   save [label]        - Save current state (optional label)")
                print("   checkpoints         - List all available checkpoints")
                print("   load <id>           - Load a specific checkpoint by ID")
                print("   restore latest      - Restore from most recent checkpoint")
                print("\n   Any other text will be sent to Lyra for conversation.\n")
                continue
            
            if user_input.lower() == "reset":
                lyra.reset_conversation()
                print("🔄 Conversation reset.\n")
                continue
            
            if user_input.lower() == "history":
                history = lyra.get_conversation_history(10)
                if not history:
                    print("No conversation history yet.\n")
                else:
                    print("\n📜 Recent conversation:")
                    for i, turn in enumerate(history, 1):
                        print(f"\n{i}. You: {turn.user_input}")
                        print(f"   Lyra: {turn.system_response}")
                        print(f"   (Response time: {turn.response_time:.2f}s)")
                    print()
                continue
            
            if user_input.lower() == "metrics":
                metrics = lyra.get_metrics()
                print("\n📊 Conversation Metrics:")
                print(f"   Total turns: {metrics['conversation']['total_turns']}")
                print(f"   Average response time: {metrics['conversation']['avg_response_time']:.2f}s")
                print(f"   Timeouts: {metrics['conversation']['timeouts']}")
                print(f"   Errors: {metrics['conversation']['errors']}")
                print(f"   Topics tracked: {metrics['conversation']['topics_tracked']}")
                print(f"   History size: {metrics['conversation']['history_size']}")
                print(f"\n🧠 Cognitive Core Metrics:")
                print(f"   Total cycles: {metrics['cognitive_core']['total_cycles']}")
                print(f"   Average cycle time: {metrics['cognitive_core']['avg_cycle_time_ms']:.2f}ms")
                print(f"   Workspace size: {metrics['cognitive_core']['workspace_size']}")
                print(f"   Current goals: {metrics['cognitive_core']['current_goals']}")
                print()
                continue
            
            # Checkpoint commands
            if user_input.lower().startswith("save"):
                parts = user_input.split(maxsplit=1)
                label = parts[1] if len(parts) > 1 else None
                path = lyra.core.save_state(label)
                if path:
                    print(f"💾 State saved: {path.name}\n")
                else:
                    print("❌ Failed to save state (checkpointing may be disabled)\n")
                continue
            
            if user_input.lower() == "checkpoints":
                if not lyra.core.checkpoint_manager:
                    print("❌ Checkpointing is disabled\n")
                    continue
                
                checkpoints = lyra.core.checkpoint_manager.list_checkpoints()
                if not checkpoints:
                    print("No checkpoints found.\n")
                else:
                    print(f"\n💾 Available Checkpoints ({len(checkpoints)}):")
                    for i, cp in enumerate(checkpoints[:10], 1):  # Show max 10
                        label = cp.metadata.get('user_label', 'N/A')
                        auto = " [auto]" if cp.metadata.get('auto_save') else ""
                        shutdown = " [shutdown]" if cp.metadata.get('shutdown') else ""
                        size_kb = cp.size_bytes / 1024
                        print(f"\n{i}. {cp.timestamp.strftime('%Y-%m-%d %H:%M:%S')}{auto}{shutdown}")
                        print(f"   ID: {cp.checkpoint_id[:16]}...")
                        print(f"   Label: {label}")
                        print(f"   Size: {size_kb:.1f} KB")
                    print()
                continue
            
            if user_input.lower().startswith("load"):
                if not lyra.core.checkpoint_manager:
                    print("❌ Checkpointing is disabled\n")
                    continue
                
                parts = user_input.split(maxsplit=1)
                if len(parts) < 2:
                    print("❌ Usage: load <checkpoint_id>\n")
                    continue
                
                checkpoint_id = parts[1]
                
                # Find checkpoint by ID prefix
                checkpoints = lyra.core.checkpoint_manager.list_checkpoints()
                matching = [cp for cp in checkpoints if cp.checkpoint_id.startswith(checkpoint_id)]
                
                if not matching:
                    print(f"❌ Checkpoint not found: {checkpoint_id}\n")
                    continue
                
                if len(matching) > 1:
                    print(f"❌ Ambiguous checkpoint ID (matches {len(matching)} checkpoints)\n")
                    continue
                
                checkpoint = matching[0]
                
                # Cannot load while running - need to stop first
                print(f"⚠️  Loading checkpoint requires restarting Lyra...")
                print(f"💾 Stopping Lyra...")
                await lyra.stop()
                
                # Restore state
                success = lyra.core.restore_state(checkpoint.path)
                if success:
                    print(f"✅ State restored from {checkpoint.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"🧠 Restarting Lyra...")
                    await lyra.start()
                    print("✅ Lyra is online.\n")
                else:
                    print("❌ Failed to restore state")
                    print("🧠 Restarting Lyra with original state...")
                    await lyra.start()
                    print("✅ Lyra is online.\n")
                continue
            
            if user_input.lower() == "restore latest":
                if not lyra.core.checkpoint_manager:
                    print("❌ Checkpointing is disabled\n")
                    continue
                
                latest = lyra.core.checkpoint_manager.get_latest_checkpoint()
                if not latest:
                    print("❌ No checkpoints found\n")
                    continue
                
                print(f"⚠️  Loading checkpoint requires restarting Lyra...")
                print(f"💾 Stopping Lyra...")
                await lyra.stop()
                
                # Restore state
                success = lyra.core.restore_state(latest)
                if success:
                    print(f"✅ State restored from latest checkpoint")
                    print(f"🧠 Restarting Lyra...")
                    await lyra.start()
                    print("✅ Lyra is online.\n")
                else:
                    print("❌ Failed to restore state")
                    print("🧠 Restarting Lyra with original state...")
                    await lyra.start()
                    print("✅ Lyra is online.\n")
                continue
            
            # Process turn
            print("💭 Thinking...")
            turn = await lyra.chat(user_input)
            
            # Display response with emotion
            emotion = turn.emotional_state
            if emotion:
                valence = emotion.get('valence', 0.0)
                arousal = emotion.get('arousal', 0.0)
                emotion_label = f"[{valence:.1f}V {arousal:.1f}A]"
            else:
                emotion_label = ""
            
            print(f"\nLyra {emotion_label}: {turn.system_response}")
            print(f"(Response time: {turn.response_time:.2f}s)\n")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🛑 Shutting down Lyra...")
        await lyra.stop()
        print("👋 Lyra offline.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
