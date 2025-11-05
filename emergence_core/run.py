# Start the Lyra Emergence server
import uvicorn
from lyra.api import app
import sys
import signal
import logging
import threading
import time
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_server():
    """Run the Uvicorn server"""
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False,
        access_log=False  # Reduce logging noise
    )

class ServerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.daemon = False
    
    def run(self):
        run_server()
    
    def stop(self):
        self._stop_event.set()

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}. Continuing to run...")

if __name__ == "__main__":
    try:
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("Starting Lyra Emergence server...")
        
        # Create PID file for process management
        with open("server.pid", "w") as f:
            f.write(str(os.getpid()))
        
        # Start server in a separate thread
        server_thread = ServerThread()
        server_thread.start()
        
        # Keep the main thread alive
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt. Server will continue running...")
            except Exception as e:
                logger.error(f"Error in main thread: {e}")
                break
            
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)
    finally:
        # Clean up PID file
        if os.path.exists("server.pid"):
            os.remove("server.pid")