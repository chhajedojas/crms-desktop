"""
Main entry point for CRMS backend.
Handles IPC communication with Electron frontend.
"""

import sys
import asyncio

from core import setup_logging, get_logger, get_settings
from database.connection import DatabaseConnection


class IPCHandler:
    """Handles IPC communication with Electron frontend."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.settings = get_settings()
        self.db_connection = DatabaseConnection()
        self.running = False

    async def handle_command(self, command: dict) -> dict:
        """
        Handle IPC command from Electron.

        Args:
            command: Command dictionary with 'action' and 'data' keys

        Returns:
            Response dictionary with 'success', 'message', and 'data' keys
        """
        action = command.get("action")
        _ = command.get("data", {})

        self.logger.info(f"Received IPC command: {action}")

        try:
            if action == "health_check":
                return {
                    "success": True,
                    "message": "Backend is healthy",
                    "data": {
                        "version": self.settings.app_version,
                        "environment": self.settings.environment,
                    },
                }

            elif action == "scan_directory":
                # Placeholder for v0.2
                return {
                    "success": False,
                    "message": "Scanner not yet implemented",
                    "data": None,
                }

            elif action == "extract_metadata":
                # Placeholder for v0.2
                return {
                    "success": False,
                    "message": "Metadata extraction not yet implemented",
                    "data": None,
                }

            elif action == "search":
                # Placeholder for v0.2
                return {
                    "success": False,
                    "message": "Search not yet implemented",
                    "data": None,
                }

            else:
                return {
                    "success": False,
                    "message": f"Unknown action: {action}",
                    "data": None,
                }

        except Exception as e:
            self.logger.error(f"Error handling command {action}: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "data": None,
            }

    async def run(self):
        """Run the IPC handler loop."""
        self.running = True
        self.logger.info("IPC handler started")

        # In production, this would read from stdin/stdout
        # For now, we'll just log that we're ready
        print("CRMS Backend IPC Handler Ready", file=sys.stderr)
        print("Waiting for IPC commands...", file=sys.stderr)

        # Keep the event loop running
        while self.running:
            await asyncio.sleep(1)


async def main():
    """Main entry point."""
    try:
        # Setup logging
        setup_logging()
        logger = get_logger(__name__)

        logger.info("Starting CRMS backend...")

        # Initialize IPC handler
        handler = IPCHandler()

        # Run handler
        await handler.run()

    except KeyboardInterrupt:
        logger.info("Backend shutdown requested")
    except Exception as e:
        logger.error(f"Backend error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
