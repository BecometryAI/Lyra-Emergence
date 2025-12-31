"""Shared fixtures for integration tests."""

import pytest
import asyncio


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def lyra_api():
    """Provide started LyraAPI instance."""
    from lyra import LyraAPI
    
    api = LyraAPI()
    await api.start()
    
    yield api
    
    await api.stop()
