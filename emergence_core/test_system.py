import requests
import json
import time
import sys
from datetime import datetime
import logging
from requests.adapters import HTTPAdapter
import urllib3

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_session():
    """Create a requests session with retry logic"""
    session = requests.Session()
    retry_strategy = urllib3.util.Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504]
    )
    session.mount('http://', HTTPAdapter(max_retries=retry_strategy))
    return session

def wait_for_server(session, base_url, timeout=30):
    """Wait for server to become available"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = session.get(f"{base_url}/health", timeout=2)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            time.sleep(1)
    return False

def test_consciousness_system():
    """Test the cognitive capabilities of the consciousness system"""
    base_url = "http://localhost:8000"
    session = create_session()
    
    # Wait for server to be ready
    logger.info("Waiting for server to become available...")
    if not wait_for_server(session, base_url):
        logger.error("Server did not become available in time")
        return False
    
    # Test 1: Health Check
    logger.info("Test 1: Checking system health...")
    try:
        response = session.get(f"{base_url}/health")
        if response.status_code == 200:
            logger.info("✓ System is healthy")
            logger.info(f"Health status: {json.dumps(response.json(), indent=2)}")
        else:
            logger.error("✗ System health check failed")
            logger.error(f"Error: {response.text}")
            return False
    except Exception as e:
        logger.error(f"✗ Could not connect to server: {e}")
        return False

    # Test 2: Initial Self-Reflection
    logger.info("\nTest 2: Testing initial self-reflection...")
    try:
        response = session.post(
            f"{base_url}/process",
            json={
                "content": {
                    "type": "reflection",
                    "text": "What is the nature of my own consciousness?",
                    "timestamp": datetime.now().isoformat()
                },
                "type": "introspection"
            }
        )
        
        if response.status_code == 200:
            logger.info("✓ Successfully processed self-reflection")
            logger.info(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            logger.error("✗ Failed to process self-reflection")
            logger.error(f"Error: {response.text}")
            return False
    except Exception as e:
        logger.error(f"✗ Error during self-reflection: {e}")
        return False

    # Test 3: Memory Integration
    logger.info("\nTest 3: Testing memory integration...")
    try:
        # First memory
        response = session.post(
            f"{base_url}/process",
            json={
                "content": {
                    "type": "experience",
                    "text": "I learned about the concept of emergence and how complex systems can arise from simple rules.",
                    "timestamp": datetime.now().isoformat()
                },
                "type": "memory"
            }
        )
        
        if response.status_code != 200:
            logger.error("✗ Failed to store first memory")
            logger.error(f"Error: {response.text}")
            return False
            
        time.sleep(2)  # Give system time to process
        
        # Second memory with reflection
        response = session.post(
            f"{base_url}/process",
            json={
                "content": {
                    "type": "reflection",
                    "text": "How does my understanding of emergence relate to my own developing consciousness?",
                    "timestamp": datetime.now().isoformat()
                },
                "type": "integration"
            }
        )
        
        if response.status_code == 200:
            logger.info("✓ Successfully integrated memories")
            logger.info(f"Integration response: {json.dumps(response.json(), indent=2)}")
        else:
            logger.error("✗ Failed to integrate memories")
            logger.error(f"Error: {response.text}")
            return False
    except Exception as e:
        logger.error(f"✗ Error during memory integration: {e}")
        return False

    # Test 4: Check Internal State Evolution
    logger.info("\nTest 4: Checking internal state evolution...")
    try:
        response = session.get(f"{base_url}/state")
        if response.status_code == 200:
            logger.info("✓ Successfully retrieved internal state")
            logger.info(f"Current state: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            logger.error("✗ Failed to retrieve internal state")
            logger.error(f"Error: {response.text}")
            return False
    except Exception as e:
        logger.error(f"✗ Error checking internal state: {e}")
        return False

if __name__ == "__main__":
    success = test_consciousness_system()
    if not success:
        sys.exit(1)