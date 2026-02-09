"""Distributed state synchronization and consensus.

Implements state management, consistency protocols, and change propagation
for distributed agent coordination.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class StateChange:
    """Record of a state change."""

    change_id: str
    agent_id: str
    timestamp: str
    version: int
    key: str
    old_value: Any = None
    new_value: Any = None
    propagated: bool = False
    replicas: List[str] = field(default_factory=list)


@dataclass
class StateVersion:
    """Version tracking for state keys."""

    key: str
    current_version: int = 0
    last_modified: str = field(default_factory=lambda: datetime.now().isoformat())
    modified_by: str = ""
    value: Any = None
    checksum: str = ""


class StateSync:
    """Manages distributed state synchronization."""

    def __init__(self, agent_id: str, data_dir: Optional[str] = None):
        """Initialize state synchronization.

        Args:
            agent_id: ID of this agent
            data_dir: Directory for state persistence
        """
        self.agent_id = agent_id
        self.local_state: Dict[str, Any] = {}
        self.state_versions: Dict[str, StateVersion] = {}
        self.changes: Dict[str, StateChange] = {}
        self.replicas: Dict[str, Dict[str, Any]] = {}  # agent_id -> state replica

        # Setup data directory
        if data_dir is None:
            data_dir = str(Path.home() / ".mind_statesync")
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.state_file = self.data_dir / f"{agent_id}_state.json"
        self.changes_file = self.data_dir / f"{agent_id}_changes.jsonl"
        self.versions_file = self.data_dir / f"{agent_id}_versions.json"

        self._load_state()
        self._load_versions()
        self._load_changes()
        logger.info(f"StateSync initialized for agent: {agent_id}")

    def set_state(self, key: str, value: Any) -> str:
        """Set a state value.

        Args:
            key: State key
            value: New value

        Returns:
            Change ID
        """
        import uuid

        change_id = str(uuid.uuid4())
        old_value = self.local_state.get(key)

        # Update version
        if key not in self.state_versions:
            self.state_versions[key] = StateVersion(key=key)

        version_info = self.state_versions[key]
        version_info.current_version += 1
        version_info.last_modified = datetime.now().isoformat()
        version_info.modified_by = self.agent_id
        version_info.value = value
        version_info.checksum = self._compute_checksum(value)

        # Record change
        change = StateChange(
            change_id=change_id,
            agent_id=self.agent_id,
            timestamp=datetime.now().isoformat(),
            version=version_info.current_version,
            key=key,
            old_value=old_value,
            new_value=value,
        )

        self.changes[change_id] = change
        self.local_state[key] = value

        self._save_state()
        self._save_change(change)
        self._save_versions()

        logger.debug(f"State updated: {key} (version {version_info.current_version})")
        return change_id

    def get_state(self, key: str) -> Any:
        """Get state value.

        Args:
            key: State key

        Returns:
            State value or None
        """
        return self.local_state.get(key)

    def get_all_state(self) -> Dict[str, Any]:
        """Get all state.

        Returns:
            Full state dictionary
        """
        return self.local_state.copy()

    def sync_state(
        self, key: str, value: Any, version: int, source_agent_id: str
    ) -> bool:
        """Synchronize state from another agent.

        Args:
            key: State key
            value: Value to sync
            version: Version number
            source_agent_id: ID of source agent

        Returns:
            True if state was updated
        """
        # Check if we should accept this state
        if key in self.state_versions:
            local_version = self.state_versions[key].current_version
            if version <= local_version:
                logger.debug(
                    f"Rejected state sync for {key}: version {version} <= {local_version}"
                )
                return False

        # Update state
        self.set_state(key, value)

        # Track replica
        if source_agent_id not in self.replicas:
            self.replicas[source_agent_id] = {}
        self.replicas[source_agent_id][key] = value

        logger.info(f"State synced from {source_agent_id}: {key} (version {version})")
        return True

    def mark_propagated(self, change_id: str, agent_ids: List[str]) -> bool:
        """Mark change as propagated to replicas.

        Args:
            change_id: Change ID
            agent_ids: List of agents that have replica

        Returns:
            True if marked successfully
        """
        if change_id not in self.changes:
            return False

        change = self.changes[change_id]
        change.propagated = True
        change.replicas = agent_ids

        return True

    def get_change(self, change_id: str) -> Optional[StateChange]:
        """Get change information.

        Args:
            change_id: Change ID

        Returns:
            Change record or None
        """
        return self.changes.get(change_id)

    def get_recent_changes(self, limit: int = 10) -> List[StateChange]:
        """Get recent changes.

        Args:
            limit: Maximum number to return

        Returns:
            List of recent changes
        """
        changes = list(self.changes.values())
        return sorted(changes, key=lambda c: c.timestamp, reverse=True)[:limit]

    def get_version(self, key: str) -> Optional[StateVersion]:
        """Get version information for key.

        Args:
            key: State key

        Returns:
            Version info or None
        """
        return self.state_versions.get(key)

    def get_consistency_status(self) -> Dict[str, Any]:
        """Get distributed consistency status.

        Returns:
            Consistency status
        """
        total_keys = len(self.local_state)
        fully_synced = 0
        partially_synced = 0

        for key, version_info in self.state_versions.items():
            if version_info.checksum:
                # Count replicas with same value
                matching_replicas = 0
                for replica_state in self.replicas.values():
                    if key in replica_state:
                        replica_checksum = self._compute_checksum(replica_state[key])
                        if replica_checksum == version_info.checksum:
                            matching_replicas += 1

                if matching_replicas == len(self.replicas):
                    fully_synced += 1
                elif matching_replicas > 0:
                    partially_synced += 1

        total_changes = len(self.changes)
        propagated_changes = sum(1 for c in self.changes.values() if c.propagated)

        return {
            "agent_id": self.agent_id,
            "total_keys": total_keys,
            "fully_synced_keys": fully_synced,
            "partially_synced_keys": partially_synced,
            "consistency_percentage": (
                (fully_synced / total_keys * 100) if total_keys > 0 else 100
            ),
            "total_changes": total_changes,
            "propagated_changes": propagated_changes,
            "replica_count": len(self.replicas),
            "timestamp": datetime.now().isoformat(),
        }

    def get_replica_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get known state of a replica agent.

        Args:
            agent_id: ID of replica agent

        Returns:
            Replica state or None
        """
        return self.replicas.get(agent_id)

    def detect_conflicts(self) -> List[Dict[str, Any]]:
        """Detect state conflicts across replicas.

        Returns:
            List of detected conflicts
        """
        conflicts = []

        for key, version_info in self.state_versions.items():
            local_checksum = version_info.checksum

            for agent_id, replica_state in self.replicas.items():
                if key in replica_state:
                    replica_checksum = self._compute_checksum(replica_state[key])
                    if replica_checksum != local_checksum:
                        conflicts.append(
                            {
                                "key": key,
                                "local_version": version_info.current_version,
                                "local_value": self.local_state.get(key),
                                "replica_agent": agent_id,
                                "replica_value": replica_state[key],
                            }
                        )

        return conflicts

    def resolve_conflict(self, key: str, value: Any) -> None:
        """Resolve state conflict by accepting a value.

        Args:
            key: State key
            value: Value to accept
        """
        self.set_state(key, value)
        logger.info(f"Conflict resolved for {key}: accepted value {value}")

    def reset(self) -> None:
        """Reset state synchronization."""
        self.local_state.clear()
        self.state_versions.clear()
        self.changes.clear()
        self.replicas.clear()
        logger.info(f"StateSync reset for agent: {self.agent_id}")

    # Private methods

    def _compute_checksum(self, value: Any) -> str:
        """Compute checksum for value.

        Args:
            value: Value to checksum

        Returns:
            Hex digest of checksum
        """
        import hashlib

        value_str = json.dumps(value, sort_keys=True, default=str)
        return hashlib.sha256(value_str.encode()).hexdigest()

    def _save_state(self) -> None:
        """Save state to file."""
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.local_state, f, default=str)
        except (OSError, IOError) as e:
            logger.error(f"Error saving state: {e}")

    def _save_versions(self) -> None:
        """Save versions to file."""
        try:
            data = {k: asdict(v) for k, v in self.state_versions.items()}
            with open(self.versions_file, "w") as f:
                json.dump(data, f, default=str)
        except (OSError, IOError) as e:
            logger.error(f"Error saving versions: {e}")

    def _save_change(self, change: StateChange) -> None:
        """Save change to file."""
        try:
            with open(self.changes_file, "a") as f:
                f.write(json.dumps(asdict(change), default=str) + "\n")
        except (OSError, IOError) as e:
            logger.error(f"Error saving change: {e}")

    def _load_state(self) -> None:
        """Load state from file."""
        if not self.state_file.exists():
            return

        try:
            with open(self.state_file, "r") as f:
                self.local_state = json.load(f)
        except (OSError, IOError, json.JSONDecodeError) as e:
            logger.error(f"Error loading state: {e}")

    def _load_versions(self) -> None:
        """Load versions from file."""
        if not self.versions_file.exists():
            return

        try:
            with open(self.versions_file, "r") as f:
                data = json.load(f)
                for key, version_data in data.items():
                    self.state_versions[key] = StateVersion(**version_data)
        except (OSError, IOError, json.JSONDecodeError) as e:
            logger.error(f"Error loading versions: {e}")

    def _load_changes(self) -> None:
        """Load changes from file."""
        if not self.changes_file.exists():
            return

        try:
            with open(self.changes_file, "r") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        change = StateChange(**data)
                        self.changes[change.change_id] = change
                    except (json.JSONDecodeError, TypeError):
                        continue
        except (OSError, IOError) as e:
            logger.error(f"Error loading changes: {e}")
