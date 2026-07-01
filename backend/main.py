"""
Main entry point for CRMS backend.
Handles IPC communication with Electron frontend.
"""

import sys
import asyncio
from typing import Optional, Any
from pydantic import BaseModel, Field, field_validator

from core import setup_logging, get_logger, get_settings
from database.connection import DatabaseConnection


class IPCCommand(BaseModel):
    """Pydantic model for IPC command validation."""

    action: str = Field(..., description="Command action to execute")
    data: Optional[dict] = Field(default_factory=dict, description="Command data")

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        """Validate action is not empty and reasonable length."""
        if not v or not v.strip():
            raise ValueError("Action cannot be empty")
        if len(v) > 100:
            raise ValueError("Action cannot exceed 100 characters")
        return v.strip()

    @field_validator("data")
    @classmethod
    def validate_data(cls, v: Optional[dict]) -> Optional[dict]:
        """Validate data size and structure."""
        if v is None:
            return None
        # Limit data size to prevent memory exhaustion
        data_str = str(v)
        if len(data_str) > 1_000_000:  # 1MB limit
            raise ValueError("Data size exceeds 1MB limit")
        return v


class IPCResponse(BaseModel):
    """Pydantic model for IPC response."""

    success: bool = Field(..., description="Whether command succeeded")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(default=None, description="Response data")

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate message length."""
        if len(v) > 1000:
            raise ValueError("Message cannot exceed 1000 characters")
        return v


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
        try:
            # Validate command structure with Pydantic
            validated_command = IPCCommand(**command)
            action = validated_command.action

            self.logger.info(f"Received IPC command: {action}")

            if action == "health_check":
                response = IPCResponse(
                    success=True,
                    message="Backend is healthy",
                    data={
                        "version": self.settings.app_version,
                        "environment": self.settings.environment,
                    },
                )
                return response.model_dump()

            elif action == "scan_directory":
                # Placeholder for v0.2
                response = IPCResponse(
                    success=False,
                    message="Scanner not yet implemented",
                    data=None,
                )
                return response.model_dump()

            elif action == "extract_metadata":
                # Placeholder for v0.2
                response = IPCResponse(
                    success=False,
                    message="Metadata extraction not yet implemented",
                    data=None,
                )
                return response.model_dump()

            elif action == "search":
                # Placeholder for v0.2
                response = IPCResponse(
                    success=False,
                    message="Search not yet implemented",
                    data=None,
                )
                return response.model_dump()

            else:
                response = IPCResponse(
                    success=False,
                    message=f"Unknown action: {action}",
                    data=None,
                )
                return response.model_dump()

        except ValueError as e:
            # Pydantic validation error
            self.logger.warning(f"Invalid IPC command: {str(e)}")
            response = IPCResponse(
                success=False,
                message="Invalid command format",
                data=None,
            )
            return response.model_dump()
        except Exception as e:
            self.logger.error(f"Error handling command: {str(e)}", exc_info=True)
            response = IPCResponse(
                success=False,
                message="Internal server error",
                data=None,
            )
            return response.model_dump()

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
