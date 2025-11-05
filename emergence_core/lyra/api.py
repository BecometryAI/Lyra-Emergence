"""
API server for interacting with the consciousness core
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from .consciousness import ConsciousnessCore
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Lyra Emergence API")

# Initialize consciousness core
try:
    logger.info("Initializing consciousness core...")
    consciousness = ConsciousnessCore()
    logger.info("Consciousness core initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize consciousness core: {e}")
    raise

class Input(BaseModel):
    """Input data model"""
    content: Dict[str, Any]
    type: str = "general"

class Response(BaseModel):
    """Response data model"""
    response: Dict[str, Any]
    internal_state: Dict[str, Any]
    status: str = "success"
    message: Optional[str] = None

@app.post("/process", response_model=Response)
async def process_input(input_data: Input):
    """Process input through the consciousness core"""
    try:
        logger.info(f"Processing input of type: {input_data.type}")
        response = consciousness.process_input(input_data.content)
        internal_state = consciousness.get_internal_state()
        
        return Response(
            response=response,
            internal_state=internal_state,
            status="success",
            message="Input processed successfully"
        )
    except Exception as e:
        logger.error(f"Error processing input: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/state")
async def get_state():
    """Get current internal state"""
    try:
        state = consciousness.get_internal_state()
        return {
            "status": "success",
            "state": state
        }
    except Exception as e:
        logger.error(f"Error getting state: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "0.1.0"
    }