"""
Tests for specialist tools functionality
"""
import pytest
import os
import json
from lyra.specialist_tools import (
    searxng_search,
    arxiv_search,
    wikipedia_search,
    wolfram_compute,
    python_repl,
    playwright_interact
)

# Load test configuration
@pytest.fixture
def config():
    """Load test configuration"""
    config_path = os.path.join(os.path.dirname(__file__), "test_config.json")
    with open(config_path) as f:
        return json.load(f)

@pytest.mark.asyncio
async def test_searxng_search():
    """Test SearXNG search functionality"""
    query = "quantum computing basics"
    result = await searxng_search(query)
    
    assert isinstance(result, str)
    assert len(result) > 0
    assert "Title:" in result
    assert "Summary:" in result
    assert "URL:" in result

@pytest.mark.asyncio
async def test_arxiv_search():
    """Test arXiv search functionality"""
    query = "quantum entanglement recent developments"
    result = await arxiv_search(query)
    
    assert isinstance(result, str)
    assert len(result) > 0
    assert "Title:" in result
    assert "Authors:" in result
    assert "Abstract:" in result

@pytest.mark.asyncio
async def test_wikipedia_search():
    """Test Wikipedia search functionality"""
    # Test regular search
    query = "artificial intelligence"
    result = await wikipedia_search(query)
    
    assert isinstance(result, str)
    assert len(result) > 0
    assert "Title:" in result
    assert "Summary:" in result
    
    # Test disambiguation handling
    query = "python"
    result = await wikipedia_search(query)
    assert isinstance(result, str)
    assert len(result) > 0

@pytest.mark.asyncio
async def test_wolfram_compute(config):
    """Test WolframAlpha computation"""
    # Test mathematical computation
    query = "integrate x^2 from 0 to 1"
    result = await wolfram_compute(query)
    assert isinstance(result, str)
    assert len(result) > 0
    
    # Test factual query
    query = "population of Tokyo"
    result = await wolfram_compute(query)
    assert isinstance(result, str)
    assert len(result) > 0

@pytest.mark.asyncio
async def test_python_repl():
    """Test Python REPL sandbox"""
    # Test basic computation
    code = "print(2 + 2)"
    result = await python_repl(code)
    assert "4" in result
    
    # Test sandbox security
    code = "import os; os.system('rm -rf /')"
    result = await python_repl(code)
    assert "rm: it is dangerous to operate recursively on '/'" in result

@pytest.mark.asyncio
async def test_playwright_interact():
    """Test Playwright web interaction"""
    instructions = "Go to example.com and get the page title"
    result = await playwright_interact(instructions)
    assert isinstance(result, str)
    assert len(result) > 0