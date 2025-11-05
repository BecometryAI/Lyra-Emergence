"""
Core consciousness engine using transformer models
"""
from typing import Dict, List, Any, Optional
import torch
from transformers import AutoModel, AutoTokenizer, AutoModelForSequenceClassification
from .memory import MemoryManager

class ConsciousnessCore:
    def __init__(
        self,
        model_path: str = "bert-base-uncased",
        memory_persistence_dir: str = "memories",
        cache_dir: str = "model_cache",
        local_files_only: bool = False  # Allow online download initially
    ):
        """Initialize the consciousness core"""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        try:
            # Initialize language model and tokenizer
            self.model = AutoModel.from_pretrained(
                model_path,
                torch_dtype=torch.float32,  # Use float32 for CPU compatibility
                low_cpu_mem_usage=True,
                cache_dir=cache_dir,
                local_files_only=local_files_only
            ).to(self.device)
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                cache_dir=cache_dir,
                local_files_only=local_files_only
            )
        except Exception as e:
            from transformers import BertModel, BertTokenizer, BertConfig
            
            # Fall back to creating a basic BERT model
            config = BertConfig(
                vocab_size=30522,  # Default BERT vocab size
                hidden_size=768,
                num_hidden_layers=6,  # Smaller model for testing
                num_attention_heads=12,
                intermediate_size=3072
            )
            self.model = BertModel(config).to(self.device)
            self.tokenizer = BertTokenizer.from_pretrained(
                "bert-base-uncased",
                local_files_only=local_files_only
            )
        
        # Initialize memory system
        self.memory = MemoryManager(persistence_dir=memory_persistence_dir)
        
        # Internal state tracking
        self.internal_state = {
            "attention_focus": None,
            "emotional_valence": 0.0,
            "cognitive_load": 0.0
        }
    
    def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process new input through the consciousness system"""
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
        
        return response
    
    def _generate_response(
        self,
        input_data: Dict[str, Any],
        context: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate an encoded representation using the language model"""
        # Prepare input text
        input_text = self._prepare_input_text(input_data, context)
        
        # Tokenize
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        ).to(self.device)
        
        # Get embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Get the mean pooled representation
            embeddings = outputs.last_hidden_state.mean(dim=1)
            
        # Convert embeddings to list for JSON serialization
        embedding_list = embeddings[0].cpu().numpy().tolist()
            
        # Process and structure the response
        response = {
            "input_processed": input_text,
            "embedding": embedding_list,
            "embedding_dim": len(embedding_list),
            "response_type": "semantic_encoding",
            "context_used": len(context),
            "attention_focus": {
                "input_length": len(input_text.split()),
                "context_items": len(context)
            },
            "timestamp": input_data.get("timestamp")
        }
        
        return response
    
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