"""System registry for Mind.

Maintains references to autonomously generated systems without storing
their code. Acts as a catalog of generated systems, their metadata,
and orchestration pointers.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils.logger import get_logger

logger = get_logger(__name__)


class SystemRegistry:
    """Registry for tracking generated systems in Mind."""

    def __init__(self, mind_dir: Optional[Path] = None):
        """Initialize system registry.

        Args:
            mind_dir: Mind home directory (default: ~/.mind)
        """
        if mind_dir is None:
            mind_dir = Path.home() / ".mind"

        self.mind_dir = Path(mind_dir)
        self.registry_dir = self.mind_dir / "system_registry"
        self.registry_dir.mkdir(parents=True, exist_ok=True)

        self.registry_file = self.registry_dir / "systems.json"
        self._load_registry()

        logger.info(f"SystemRegistry initialized: {self.registry_dir}")

    def _load_registry(self) -> None:
        """Load existing registry from disk."""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, "r") as f:
                    self.systems = json.load(f)
                logger.debug(f"Loaded registry with {len(self.systems)} systems")
            except Exception as e:
                logger.error(f"Failed to load registry: {e}")
                self.systems = {}
        else:
            self.systems = {}

    def _save_registry(self) -> None:
        """Save registry to disk."""
        try:
            with open(self.registry_file, "w") as f:
                json.dump(self.systems, f, indent=2)
            logger.debug("Registry saved")
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")
            raise

    def register_system(
        self,
        system_id: str,
        system_name: str,
        repo_info: Dict[str, Any],
        spec_dict: Dict[str, Any],
    ) -> None:
        """Register a newly generated system in the registry.

        Args:
            system_id: Unique system identifier
            system_name: Human-readable system name
            repo_info: Repository creation information
            spec_dict: System specification dictionary
        """
        entry = {
            "id": system_id,
            "name": system_name,
            "created_at": datetime.now().isoformat(),
            "repository": {
                "path": repo_info.get("repo_path"),
                "url": repo_info.get("repo_url"),
                "branches": repo_info.get("branches", ["main", "dev"]),
            },
            "specification": spec_dict,
            "status": "active",
            "metadata_file": repo_info.get("metadata_path"),
        }

        self.systems[system_id] = entry
        self._save_registry()

        logger.info(f"System registered: {system_id} ({system_name})")

    def get_system(self, system_id: str) -> Optional[Dict[str, Any]]:
        """Get system registry entry.

        Args:
            system_id: System identifier

        Returns:
            System entry or None if not found
        """
        return self.systems.get(system_id)

    def list_systems(self) -> List[Dict[str, Any]]:
        """List all registered systems.

        Returns:
            List of system entries
        """
        return list(self.systems.values())

    def get_system_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find system by name.

        Args:
            name: System name

        Returns:
            System entry or None
        """
        for system in self.systems.values():
            if system.get("name") == name:
                return system
        return None

    def update_system_status(self, system_id: str, status: str) -> None:
        """Update system status.

        Args:
            system_id: System identifier
            status: New status (e.g., 'active', 'archived', 'error')
        """
        if system_id in self.systems:
            self.systems[system_id]["status"] = status
            self._save_registry()
            logger.info(f"System status updated: {system_id} -> {status}")

    def archive_system(self, system_id: str) -> None:
        """Archive a system (mark as inactive).

        Args:
            system_id: System identifier
        """
        self.update_system_status(system_id, "archived")

    def get_registry_path(self) -> Path:
        """Get path to registry file.

        Returns:
            Path to systems.json
        """
        return self.registry_file

    def export_registry(self, export_path: Path) -> None:
        """Export registry to file.

        Args:
            export_path: Path to export to
        """
        try:
            with open(export_path, "w") as f:
                json.dump(self.systems, f, indent=2)
            logger.info(f"Registry exported: {export_path}")
        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise

    def get_registry_summary(self) -> Dict[str, Any]:
        """Get summary of all registered systems.

        Returns:
            Summary dictionary
        """
        active = sum(1 for s in self.systems.values() if s.get("status") == "active")
        archived = sum(
            1 for s in self.systems.values() if s.get("status") == "archived"
        )

        return {
            "total_systems": len(self.systems),
            "active": active,
            "archived": archived,
            "registry_path": str(self.registry_file),
            "last_updated": datetime.now().isoformat(),
        }
