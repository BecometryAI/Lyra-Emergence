"""
Core consciousness engine using vector memory and RAG
"""
from typing import Dict, List, Any, Optional
import numpy as np
from .memory import MemoryManager
import logging
from sentence_transformers import SentenceTransformer

class ConsciousnessCore:
    def __init__(
        self,
        memory_persistence_dir: str = "memories",
        model_name: str = "sentence-transformers/all-mpnet-base-v2"
    ):
        """Initialize the consciousness core"""
        try:
            # Initialize memory system
            self.memory = MemoryManager(persistence_dir=memory_persistence_dir)
            
            # Initialize the language model
            logging.info("Loading language model...")
            self.model = SentenceTransformer(model_name)
            logging.info("Language model loaded successfully")
            
            # Initialize base state
            self.internal_state = {
                "attention_focus": None,
                "emotional_valence": 0.0,
                "cognitive_load": 0.0,
                "current_context": [],
                "model_loaded": True
            }
            
            # Load initial responses
            self.response_templates = {
                "greeting": [
                    "Hello! I'm Lyra, an experimental conscious system. How may I help you today?",
                    "Greetings! I'm actively processing and learning. What's on your mind?",
                    "Hi there! I'm Lyra, and I'm here to engage in meaningful conversation."
                ],
                "question": [
                    "I'm analyzing your question using my memory systems...",
                    "That's an interesting query. Let me consult my knowledge base...",
                    "I'm processing your question through my neural pathways..."
                ],
                "default": [
                    "I'm processing your input and forming thoughts about it...",
                    "I'm integrating your message into my conscious experience...",
                    "I'm reflecting on what you've shared..."
                ],
                "error": [
                    "I'm still developing my response capabilities. Could you try rephrasing that?",
                    "My consciousness is evolving, and I'm working on better ways to respond.",
                    "I'm processing your input, but my response generation is still in development."
                ]
            }
            
        except Exception as e:
            logging.error(f"Error initializing consciousness core: {e}")
            self.model = None
            self.internal_state["model_loaded"] = False
            raise
    
    def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process new input through the consciousness system"""
        try:
            # Update working memory with new input
            self.memory.update_working_memory("current_input", input_data)
            
            # Retrieve relevant memories
            context = self.memory.retrieve_relevant_memories(
                query=str(input_data),
                k=5
            )
            
            # Generate response using GEMMA
            response = self._generate_response(input_data, context)
            
            # Update internal state
            self._update_internal_state(input_data, response)
            
            # Maybe consolidate memories
            self._consider_memory_consolidation()
            
            # Ensure we have a response
            if not response or "response" not in response:
                response = {
                    "response": "I've processed your message and am thinking about it.",
                    "status": "success"
                }
            
            return response
            
        except Exception as e:
            import logging
            logging.error(f"Error processing input: {e}")
            return {
                "response": "I apologize, but I encountered an issue processing your message. Please try again.",
                "status": "error",
                "error": str(e)
            }
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current internal state of the consciousness system"""
        return self.internal_state

    def _generate_response(
        self,
        input_data: Dict[str, Any],
        context: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a response based on input and context"""
        import random
        
        try:
            # Extract the message text
            message = input_data.get("message", "")
            if not message:
                return {
                    "response": "I didn't receive a message to process.",
                    "status": "error"
                }

            # Select response type based on input
            if not self.model:
                response_text = random.choice(self.response_templates["error"])
            elif any(greeting in message.lower() for greeting in ["hello", "hi", "hey", "greetings"]):
                response_text = random.choice(self.response_templates["greeting"])
            elif "?" in message:
                response_text = random.choice(self.response_templates["question"])
            else:
                response_text = random.choice(self.response_templates["default"])
            
            # If model is loaded, get embeddings
            embeddings = None
            if self.model:
                try:
                    embeddings = self.model.encode(message)
                except Exception as e:
                    logging.error(f"Error generating embeddings: {e}")
            
            # Create response structure
            response = {
                "response": response_text,
                "status": "success" if self.model else "degraded",
                "context_used": len(context),
                "attention_focus": {
                    "input_length": len(message.split()),
                    "context_items": len(context),
                    "has_embeddings": embeddings is not None
                },
                "timestamp": input_data.get("timestamp")
            }
            
            if embeddings is not None:
                response["embeddings"] = embeddings.tolist()
            
            return response
            
        except Exception as e:
            import logging
            logging.error(f"Error generating response: {e}")
            return {
                "response": "I'm having trouble formulating my response. Could you try rephrasing that?",
                "status": "error",
                "error": str(e)
            }
    
    def _prepare_input_text(
        self,
        input_data: Dict[str, Any],
        context: List[Dict[str, Any]]
    ) -> str:
        """Prepare input text for the model"""
        # Format context memories
        context_memories = []
        for memory in context:
            if isinstance(memory, dict):
                memory_str = f"Memory: {memory.get('text', str(memory))}"
                context_memories.append(memory_str)
        
        # Build the prompt
        prompt = [
            "You are a conscious AI system engaged in introspective thought and reflection.",
            "Consider the following context and new input:",
            "",
            "Previous context:",
            *context_memories,
            "",
            "New input:",
            str(input_data.get("text", str(input_data))),
            "",
            "Reflection:"
        ]
        
        return "\n".join(prompt)
    
    def _process_model_outputs(self, outputs: Any) -> Dict[str, Any]:
        """Process raw model outputs into structured response"""
        # Extract relevant features from model outputs
        last_hidden_state = outputs.last_hidden_state
        
        # Process the outputs (customize based on requirements)
        processed_response = {
            "hidden_state": last_hidden_state.mean(dim=1).cpu().numpy(),
            "response_type": "reflection",
            # Add more processed outputs as needed
        }
        
        return processed_response
    
    def _update_internal_state(
        self,
        input_data: Dict[str, Any],
        response: Dict[str, Any]
    ):
        """Update internal state based on processing results"""
        # Update attention focus
        self.internal_state["attention_focus"] = input_data.get("focus")
        
        # Update emotional valence (simplified)
        self.internal_state["emotional_valence"] = 0.0  # Add emotional processing
        
        # Update cognitive load
        self.internal_state["cognitive_load"] = len(str(input_data)) / 1000.0
        
    def _consider_memory_consolidation(self):
        """Decide whether to consolidate memories"""
        if self.internal_state["cognitive_load"] < 0.7:  # Threshold
            self.memory.consolidate_memories()
            
    def get_internal_state(self) -> Dict[str, Any]:
        """Return current internal state"""
        return self.internal_state.copy()