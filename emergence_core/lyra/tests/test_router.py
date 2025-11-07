"""
Test cases for Lyra's cognitive routing system
"""
import pytest
import asyncio
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch
from .adaptive_router import AdaptiveRouter

@pytest.fixture
async def router():
    """Create test router instance."""
    base_dir = Path("test_data")
    chroma_dir = base_dir / "chroma"
    model_dir = base_dir / "models"
    
    # Create test directories
    for dir_path in [base_dir, chroma_dir, model_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
        
    router = await AdaptiveRouter.create(
        base_dir=str(base_dir),
        chroma_dir=str(chroma_dir),
        model_dir=str(model_dir)
    )
    return router

@pytest.mark.asyncio
async def test_simple_chat_routing(router):
    """Test routing of simple chat messages."""
    message = "Hello Lyra, how are you today?"
    mock_intent = {'intent': 'simple_chat', 'resonance_term': None}
    
    with patch.object(router.router_model, 'process', return_value=mock_intent):
        response = await router.process_message(message)
        assert response is not None
        assert len(response) > 0

@pytest.mark.asyncio
async def test_philosophical_routing(router):
    """Test routing of philosophical questions."""
    message = "What are your thoughts on the nature of consciousness?"
    mock_intent = {'intent': 'philosopher', 'resonance_term': None}
    
    with patch.object(router.router_model, 'process', return_value=mock_intent):
        response = await router.process_message(message)
        assert response is not None
        assert len(response) > 0

@pytest.mark.asyncio
async def test_artistic_routing_with_resonance(router):
    """Test routing of creative requests with resonance terms."""
    message = "Write a poem about Throatlight"
    mock_intent = {'intent': 'artist', 'resonance_term': 'Throatlight'}
    
    with patch.object(router.router_model, 'process', return_value=mock_intent):
        response = await router.process_message(message)
        assert response is not None
        assert len(response) > 0

@pytest.mark.asyncio
async def test_pragmatic_routing(router):
    """Test routing of practical questions."""
    message = "What's the current status of the RAG index?"
    mock_intent = {'intent': 'pragmatist', 'resonance_term': None}
    
    with patch.object(router.router_model, 'process', return_value=mock_intent):
        response = await router.process_message(message)
        assert response is not None
        assert len(response) > 0

@pytest.mark.asyncio
async def test_error_handling(router):
    """Test error handling in routing system."""
    message = "Test message"
    
    # Simulate model error
    with patch.object(router.router_model, 'process', side_effect=Exception("Model error")):
        with pytest.raises(Exception):
            await router.process_message(message)

@pytest.mark.asyncio
async def test_context_handling(router):
    """Test context handling in routing system."""
    message = "Remember what we discussed about consciousness"
    context = {'previous_topics': ['consciousness', 'self-awareness']}
    
    mock_intent = {'intent': 'philosopher', 'resonance_term': None}
    with patch.object(router.router_model, 'process', return_value=mock_intent):
        response = await router.process_message(message, context)
        assert response is not None
        assert len(response) > 0

@pytest.mark.asyncio
async def test_rag_integration(router):
    """Test RAG system integration."""
    message = "Tell me about your core tenets"
    mock_chunks = [{"text": "Core tenet 1...", "metadata": {}}]
    
    with patch.object(router.collection, 'query', return_value={'documents': [mock_chunks]}):
        response = await router.process_message(message)
        assert response is not None
        assert len(response) > 0