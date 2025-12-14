"""Launcher script for the complete Weather Stock Dashboard application."""

import asyncio
import threading
import time
import logging
from typing import Optional
import uvicorn
from fastapi import FastAPI

from weather_stock_dashboard.ui.app import create_gradio_app
from weather_stock_dashboard.ui.integration import create_ui_integration_service
from main import app as fastapi_app
from config.settings import settings

logger = logging.getLogger(__name__)


class DashboardLauncher:
    """Launcher for both FastAPI backend and Gradio frontend."""
    
    def __init__(
        self,
        api_host: str = "127.0.0.1",
        api_port: int = 8000,
        ui_host: str = "127.0.0.1", 
        ui_port: int = 7860,
        debug: bool = False
    ):
        """Initialize launcher with configuration."""
        self.api_host = api_host
        self.api_port = api_port
        self.ui_host = ui_host
        self.ui_port = ui_port
        self.debug = debug
        
        self.api_server: Optional[uvicorn.Server] = None
        self.api_thread: Optional[threading.Thread] = None
        self.gradio_app = None
        
    def start_api_server(self):
        """Start the FastAPI backend server in a separate thread."""
        def run_api():
            config = uvicorn.Config(
                app=fastapi_app,
                host=self.api_host,
                port=self.api_port,
                log_level="info" if not self.debug else "debug",
                access_log=True
            )
            server = uvicorn.Server(config)
            self.api_server = server
            
            try:
                server.run()
            except Exception as e:
                logger.error(f"API server error: {e}")
        
        self.api_thread = threading.Thread(target=run_api, daemon=True)
        self.api_thread.start()
        
        # Wait for API server to start
        time.sleep(3)
        logger.info(f"FastAPI backend started at http://{self.api_host}:{self.api_port}")
    
    def start_gradio_app(self):
        """Start the Gradio frontend application."""
        api_base_url = f"http://{self.api_host}:{self.api_port}/api"
        
        # Create UI integration service
        ui_integration = create_ui_integration_service(api_base_url)
        
        # Create Gradio app with enhanced integration
        self.gradio_app = create_gradio_app(api_base_url, ui_integration)
        
        logger.info(f"Starting Gradio frontend at http://{self.ui_host}:{self.ui_port}")
        
        self.gradio_app.launch(
            server_name=self.ui_host,
            server_port=self.ui_port,
            share=False,
            debug=self.debug,
            show_error=True,
            quiet=not self.debug
        )
    
    def launch(self):
        """Launch both backend and frontend."""
        try:
            logger.info("🚀 Starting Weather Stock Dashboard...")
            
            # Start API server first
            logger.info("📡 Starting FastAPI backend...")
            self.start_api_server()
            
            # Start Gradio app
            logger.info("🌐 Starting Gradio frontend...")
            self.start_gradio_app()
            
        except KeyboardInterrupt:
            logger.info("🛑 Shutting down dashboard...")
            self.shutdown()
        except Exception as e:
            logger.error(f"❌ Error launching dashboard: {e}")
            self.shutdown()
    
    def shutdown(self):
        """Shutdown both servers."""
        if self.gradio_app:
            try:
                self.gradio_app.close()
                logger.info("✅ Gradio frontend stopped")
            except Exception as e:
                logger.error(f"Error stopping Gradio: {e}")
        
        if self.api_server:
            try:
                self.api_server.should_exit = True
                logger.info("✅ FastAPI backend stopped")
            except Exception as e:
                logger.error(f"Error stopping API server: {e}")


def main():
    """Main entry point for the dashboard launcher."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create and launch dashboard
    launcher = DashboardLauncher(
        api_host=settings.api_host,
        api_port=settings.api_port,
        ui_host="127.0.0.1",
        ui_port=7860,
        debug=True
    )
    
    launcher.launch()


if __name__ == "__main__":
    main()