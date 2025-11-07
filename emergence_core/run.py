# Start the Lyra Emergence server
import uvicorn
from lyra.api import create_app
import sys
import signal
import logging
import threading
import time
import os
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@contextmanager
def get_app():
    """Create FastAPI app with proper lifecycle management"""
    app = create_app()
    try:
        yield app
    finally:
        # Add cleanup if needed
        pass

def run_server():
    """Run the Uvicorn server"""
    try:
        # Try to create the socket first to check port availability
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', 8000))
        sock.close()
        
        # Port is available, create app and start server
        with get_app() as app:
            config = uvicorn.Config(
                app,
                host="0.0.0.0",
                port=8000,
                log_level="info",
                reload=False,
                access_log=False,
                workers=1
            )
            server = uvicorn.Server(config)
            server.run()
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise

class ServerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.daemon = False  # Don't daemonize to allow clean shutdown
        self.server = None
        self.error = None
        self.app = None
    
    def run(self):
        try:
            logger.info("Configuring server...")
            self.app = create_app()  # Create app instance
            config = uvicorn.Config(
                self.app,
                host="0.0.0.0",
                port=8000,
                log_level="info",
                reload=False,
                access_log=False,
                workers=1
            )
            self.server = uvicorn.Server(config)
            logger.info("Starting uvicorn server...")
            self.server.run()
        except Exception as e:
            self.error = e
            logger.error(f"Server error: {e}")
            raise
        finally:
            self._stop_event.set()
            logger.info("Server thread stopping")
    
    def stop(self):
        """Stop the server and clean up"""
        logger.info("Stopping server...")
        if self.server:
            self.server.should_exit = True
            logger.info("Server exit flag set")
        self._stop_event.set()
        self.join(timeout=5)  # Wait up to 5 seconds for thread to finish
        logger.info("Server stopped")
        
    def check_error(self):
        """Check if the server thread encountered an error"""
        if self.error:
            raise RuntimeError(f"Server thread error: {self.error}")
        return True

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}. Shutting down...")
    sys.exit(0)

def start_server():
    """Start the server and return the server thread"""
    try:
        logger.info("Starting Lyra Emergence server...")
        
        # Check if port is already in use
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('0.0.0.0', 8000))
            sock.close()
            logger.info("Port 8000 is available")
        except socket.error as e:
            logger.error(f"Port 8000 is not available: {e}")
            raise
        
        # Initialize server components
        try:
            from lyra.api import app
            logger.info("API components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize API components: {e}")
            raise
        
        # Start server thread
        server_thread = ServerThread()
        server_thread.start()
        logger.info("Server thread started")
        
        # Wait briefly to ensure startup
        import time
        time.sleep(2)
        
        # Verify server is running
        if not server_thread.is_alive():
            raise RuntimeError("Server thread failed to start")
            
        # Test server health directly
        try:
            import requests
            response = requests.get('http://localhost:8000/health', timeout=5)
            if response.status_code == 200:
                logger.info("Server health check passed")
            else:
                logger.warning(f"Server responded with status {response.status_code}")
        except Exception as e:
            logger.warning(f"Health check failed (this is expected during startup): {e}")
        
        logger.info("Server startup completed successfully")
        return server_thread
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        raise

def stop_server(server_thread):
    """Stop the server gracefully"""
    if server_thread:
        logger.info("Stopping server...")
        server_thread.stop()
        logger.info("Server stopped")

if __name__ == "__main__":
    server_thread = None
    try:
        server_thread = start_server()
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, lambda s, f: stop_server(server_thread))
        signal.signal(signal.SIGTERM, lambda s, f: stop_server(server_thread))
        
        # Keep the main thread alive until interrupted
        while server_thread.is_alive():
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Error in main thread: {e}")
    finally:
        stop_server(server_thread)