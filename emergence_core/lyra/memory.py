"""
Memory management system for Lyra's consciousness core
"""
from typing import Dict, List, Any
import chromadb
from chromadb.config import Settings
import json
from datetime import datetime

class MemoryManager:
    def __init__(self, persistence_dir: str = "memories"):
        """Initialize the memory management system"""
        self.client = chromadb.PersistentClient(path=persistence_dir)
        
        # Create collections for different types of memories
        self.episodic_memory = self.client.get_or_create_collection("episodic_memory")
        self.semantic_memory = self.client.get_or_create_collection("semantic_memory")
        self.procedural_memory = self.client.get_or_create_collection("procedural_memory")
        
        # Working memory cache
        self.working_memory: Dict[str, Any] = {}
        
    def store_experience(self, experience: Dict[str, Any]):
        """Store a new experience in episodic memory"""
        timestamp = datetime.now().isoformat()
        
        # Embed and store the experience
        self.episodic_memory.add(
            documents=[json.dumps(experience)],
            metadatas=[{"timestamp": timestamp, "type": "experience"}],
            ids=[f"exp_{timestamp}"]
        )
        
    def store_concept(self, concept: Dict[str, Any]):
        """Store semantic knowledge"""
        timestamp = datetime.now().isoformat()
        
        self.semantic_memory.add(
            documents=[json.dumps(concept)],
            metadatas=[{"timestamp": timestamp, "type": "concept"}],
            ids=[f"concept_{timestamp}"]
        )
        
    def retrieve_relevant_memories(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant memories based on a query"""
        # Search across all memory types
        episodic_results = self.episodic_memory.query(
            query_texts=[query],
            n_results=k
        )
        
        semantic_results = self.semantic_memory.query(
            query_texts=[query],
            n_results=k
        )
        
        # Combine and process results
        memories = []
        for result in episodic_results["documents"][0]:
            memories.append(json.loads(result))
            
        for result in semantic_results["documents"][0]:
            memories.append(json.loads(result))
            
        return memories
    
    def update_working_memory(self, key: str, value: Any):
        """Update working memory"""
        self.working_memory[key] = value
        
    def get_working_memory(self, key: str) -> Any:
        """Retrieve from working memory"""
        return self.working_memory.get(key)
    
    def consolidate_memories(self):
        """Consolidate important working memory items into long-term memory"""
        for key, value in self.working_memory.items():
            if self._should_consolidate(key, value):
                self.store_concept({
                    "key": key,
                    "value": value,
                    "consolidated_at": datetime.now().isoformat()
                })
    
    def _should_consolidate(self, key: str, value: Any) -> bool:
        """Determine if a memory should be consolidated"""
        # Add logic for determining memory importance
        return True  # Placeholder implementation