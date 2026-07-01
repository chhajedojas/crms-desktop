"""
Scan state for saving and loading scan state for resume functionality.
"""

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from scanner.data_structures import ScanState, ScanConfiguration
from core import get_logger


class ScanStateManager:
    """Manages scan state for resume functionality."""

    def __init__(self, state_file: Path):
        """
        Initialize scan state manager.

        Args:
            state_file: Path to state file
        """
        self.state_file = state_file
        self.logger = get_logger(__name__)
        self._lock = threading.Lock()

    def save(self, state: ScanState):
        """
        Save scan state to file.

        Args:
            state: Scan state to save
        """
        with self._lock:
            try:
                # Convert set to list for JSON serialization
                state_dict = {
                    "scan_id": state.scan_id,
                    "root_path": state.root_path,
                    "completed_files": list(state.completed_files),
                    "last_checkpoint": state.last_checkpoint.isoformat(),
                    "configuration": {
                        "root_path": state.configuration.root_path,
                        "include_patterns": state.configuration.include_patterns,
                        "exclude_patterns": state.configuration.exclude_patterns,
                        "include_hidden": state.configuration.include_hidden,
                        "include_system": state.configuration.include_system,
                        "follow_symlinks": state.configuration.follow_symlinks,
                        "max_workers": state.configuration.max_workers,
                        "chunk_size": state.configuration.chunk_size,
                        "queue_size": state.configuration.queue_size,
                        "checkpoint_interval": state.configuration.checkpoint_interval,
                        "enable_hash": state.configuration.enable_hash,
                        "enable_duplicate_detection": (
                            state.configuration.enable_duplicate_detection
                        ),
                    }
                    if state.configuration
                    else None,
                }

                with open(self.state_file, "w") as f:
                    json.dump(state_dict, f, indent=2)

                self.logger.debug(f"Saved scan state to {self.state_file}")

            except Exception as e:
                self.logger.error(f"Failed to save scan state: {str(e)}")

    def load(self) -> Optional[ScanState]:
        """
        Load scan state from file.

        Returns:
            ScanState if file exists, None otherwise
        """
        with self._lock:
            try:
                if not self.state_file.exists():
                    return None

                with open(self.state_file, "r") as f:
                    state_dict = json.load(f)

                # Reconstruct ScanState
                configuration = None
                if state_dict.get("configuration"):
                    config_dict = state_dict["configuration"]
                    configuration = ScanConfiguration(
                        root_path=config_dict["root_path"],
                        include_patterns=config_dict.get("include_patterns", []),
                        exclude_patterns=config_dict.get("exclude_patterns", []),
                        include_hidden=config_dict.get("include_hidden", False),
                        include_system=config_dict.get("include_system", False),
                        follow_symlinks=config_dict.get("follow_symlinks", False),
                        max_workers=config_dict.get("max_workers", 4),
                        chunk_size=config_dict.get("chunk_size", 65536),
                        queue_size=config_dict.get("queue_size", 1000),
                        checkpoint_interval=config_dict.get("checkpoint_interval", 1000),
                        enable_hash=config_dict.get("enable_hash", True),
                        enable_duplicate_detection=config_dict.get(
                            "enable_duplicate_detection", True
                        ),
                    )

                state = ScanState(
                    scan_id=state_dict["scan_id"],
                    root_path=state_dict["root_path"],
                    completed_files=set(state_dict["completed_files"]),
                    last_checkpoint=datetime.fromisoformat(state_dict["last_checkpoint"]).replace(
                        tzinfo=timezone.utc
                    ),
                    configuration=configuration,
                )

                self.logger.debug(f"Loaded scan state from {self.state_file}")
                return state

            except Exception as e:
                self.logger.error(f"Failed to load scan state: {str(e)}")
                return None

    def delete(self):
        """Delete scan state file."""
        with self._lock:
            try:
                if self.state_file.exists():
                    self.state_file.unlink()
                    self.logger.debug(f"Deleted scan state file {self.state_file}")
            except Exception as e:
                self.logger.error(f"Failed to delete scan state: {str(e)}")
