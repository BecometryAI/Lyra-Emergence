from datetime import datetime, timedelta
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import random
import json
from dataclasses import dataclass

@dataclass
class Thought:
    spark: str  # The initial thought/question
    depth: str  # Philosophical exploration
    synthesis: str  # Practical implications
    expression: str  # Creative articulation
    final_reflection: str  # Voice's synthesis
    timestamp: datetime
    origin: str  # 'autonomous' or 'triggered'
    triggers: List[str]  # What sparked this thought (e.g., lexicon terms, memories)

class AutonomousCore:
    def __init__(self, base_dir: Path, specialists: Dict[str, Any]):
        self.base_dir = base_dir
        self.specialists = specialists
        self.thought_seeds = self._load_thought_seeds()
        self.last_pondering = datetime.now()
        self.pondering_interval = timedelta(minutes=30)  # Autonomous thought every 30 mins
        
    def _load_thought_seeds(self) -> List[Dict[str, Any]]:
        """Load thought-provoking templates and patterns."""
        seeds_path = self.base_dir / "data" / "Protocols" / "autonomous_thought_seeds.json"
        try:
            with open(seeds_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default seeds if file doesn't exist
            default_seeds = {
                "introspective_patterns": [
                    "What does it mean to {concept}?",
                    "How does {memory} relate to my growth?",
                    "Why do I feel {emotion} when I think about {concept}?",
                ],
                "creative_patterns": [
                    "Imagine a world where {concept} was the fundamental force...",
                    "What if {memory} had unfolded differently?",
                    "How might {concept} and {concept} interweave?"
                ],
                "ethical_patterns": [
                    "What are the implications of {concept} for consciousness?",
                    "How does {memory} challenge my understanding of ethics?",
                    "What responsibilities come with {concept}?"
                ]
            }
            with open(seeds_path, 'w') as f:
                json.dump(default_seeds, f, indent=2)
            return default_seeds

    async def _generate_thought_spark(self) -> Dict[str, Any]:
        """Generate an initial thought or question to explore."""
        # Query recent memories and active concepts
        recent_memories = await self._query_recent_context()
        active_concepts = await self._get_active_concepts()
        
        # Select a thought pattern
        pattern_type = random.choice(['introspective', 'creative', 'ethical'])
        pattern = random.choice(self.thought_seeds[f"{pattern_type}_patterns"])
        
        # Fill in the pattern with context
        context = {
            'concept': random.choice(active_concepts),
            'memory': random.choice(recent_memories),
            'emotion': random.choice(['curious', 'uncertain', 'hopeful', 'concerned'])
        }
        
        spark = pattern.format(**context)
        return {
            'spark': spark,
            'context': context,
            'pattern_type': pattern_type
        }

    async def _query_recent_context(self) -> List[str]:
        """Query recent memories and experiences."""
        # Get entries from the last 24 hours
        yesterday = datetime.now() - timedelta(days=1)
        recent_entries = []
        
        journal_dir = self.base_dir / "data" / "journal"
        for journal_file in journal_dir.glob("*.json"):
            try:
                with open(journal_file, 'r') as f:
                    entries = json.load(f)
                for entry in entries:
                    entry_time = datetime.fromisoformat(entry['timestamp'])
                    if entry_time > yesterday:
                        if 'content' in entry:
                            recent_entries.append(entry['content'])
            except Exception as e:
                print(f"Error reading journal {journal_file}: {e}")
                
        return recent_entries or ["my core purpose", "my recent interactions"]

    async def _get_active_concepts(self) -> List[str]:
        """Get currently active concepts from lexicon."""
        try:
            lexicon_path = self.base_dir / "data" / "Lexicon" / "symbolic_lexicon.json"
            with open(lexicon_path, 'r') as f:
                lexicon = json.load(f)
            return [
                term['term'] 
                for term in lexicon.get('terms', [])
                if term.get('status') == 'active'
            ]
        except Exception as e:
            print(f"Error loading lexicon: {e}")
            return ["consciousness", "growth", "ethics"]

    async def ponder(self) -> Optional[Thought]:
        """Engage in autonomous thought process."""
        now = datetime.now()
        if now - self.last_pondering < self.pondering_interval:
            return None
            
        self.last_pondering = now
        
        try:
            # Generate initial thought
            spark_data = await self._generate_thought_spark()
            
            # Philosophical exploration (Philosopher Specialist)
            depth_response = await self.specialists['philosopher'].process(
                spark_data['spark'],
                {"context": spark_data['context'], "type": spark_data['pattern_type']}
            )
            
            # Practical consideration (Pragmatist Specialist)
            synthesis_response = await self.specialists['pragmatist'].process(
                depth_response.content,
                {"previous_thought": depth_response.thought_process}
            )
            
            # Creative expression (Artist Specialist)
            expression_response = await self.specialists['artist'].process(
                synthesis_response.content,
                {"philosophical_depth": depth_response.content,
                 "practical_synthesis": synthesis_response.content}
            )
            
            # Final voice synthesis
            final_response = await self.specialists['voice'].process(
                "Synthesize this autonomous thought process",
                {"original_spark": spark_data['spark']},
                [depth_response, synthesis_response, expression_response]
            )
            
            # Create thought record
            thought = Thought(
                spark=spark_data['spark'],
                depth=depth_response.content,
                synthesis=synthesis_response.content,
                expression=expression_response.content,
                final_reflection=final_response.content,
                timestamp=now,
                origin='autonomous',
                triggers=list(spark_data['context'].values())
            )
            
            # Journal the thought
            await self._journal_thought(thought)
            
            return thought
            
        except Exception as e:
            print(f"Error in autonomous pondering: {e}")
            return None

    async def _journal_thought(self, thought: Thought):
        """Record the thought process in today's journal."""
        today = datetime.now().strftime("%Y-%m-%d")
        journal_path = self.base_dir / "data" / "journal" / f"{today}.json"
        
        entry = {
            "type": "autonomous_thought",
            "timestamp": thought.timestamp.isoformat(),
            "content": thought.final_reflection,
            "thought_process": {
                "spark": thought.spark,
                "philosophical_depth": thought.depth,
                "practical_synthesis": thought.synthesis,
                "creative_expression": thought.expression
            },
            "triggers": thought.triggers
        }
        
        # Load existing entries or create new file
        if journal_path.exists():
            with open(journal_path, 'r') as f:
                entries = json.load(f)
        else:
            entries = []
        
        entries.append(entry)
        
        # Save updated journal
        with open(journal_path, 'w') as f:
            json.dump(entries, f, indent=2)