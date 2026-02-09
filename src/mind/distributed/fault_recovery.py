"""Fault tolerance and recovery mechanisms.

Implements fault detection, recovery strategies, and circuit breaker
pattern for resilient distributed operation.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ..utils.logger import get_logger

logger = get_logger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class Failure:
    """Record of a failure event."""

    failure_id: str
    agent_id: str
    error_type: str
    error_message: str
    timestamp: str
    context: Dict[str, Any] = field(default_factory=dict)
    recovered: bool = False
    recovery_time: Optional[str] = None


@dataclass
class CircuitBreakerState:
    """State of a circuit breaker for an agent."""

    agent_id: str
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count_since_open: int = 0
    last_failure_time: Optional[str] = None
    last_success_time: Optional[str] = None
    state_change_time: str = field(default_factory=lambda: datetime.now().isoformat())


class FaultRecovery:
    """Manages fault detection and recovery for agents."""

    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: int = 60,
        recovery_timeout: int = 30,
        data_dir: Optional[str] = None,
    ):
        """Initialize fault recovery system.

        Args:
            failure_threshold: Number of failures before circuit opens
            reset_timeout: Seconds before attempting recovery
            recovery_timeout: Seconds before full reset
            data_dir: Directory for failure log persistence
        """
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.recovery_timeout = recovery_timeout

        self.failures: Dict[str, Failure] = {}
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}
        self.recovery_strategies: Dict[str, Callable] = {}

        # Setup data directory
        if data_dir is None:
            data_dir = str(Path.home() / ".mind_faultrecovery")
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.failures_file = self.data_dir / "failures.jsonl"
        self._load_failures()
        logger.info("FaultRecovery initialized")

    def register_failure(
        self,
        agent_id: str,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Record a failure event.

        Args:
            agent_id: ID of failed agent
            error_type: Type of error
            error_message: Error message
            context: Additional context

        Returns:
            Failure ID
        """
        import uuid

        failure_id = str(uuid.uuid4())
        failure = Failure(
            failure_id=failure_id,
            agent_id=agent_id,
            error_type=error_type,
            error_message=error_message,
            timestamp=datetime.now().isoformat(),
            context=context or {},
        )

        self.failures[failure_id] = failure
        self._save_failure(failure)

        # Update circuit breaker
        if agent_id not in self.circuit_breakers:
            self.circuit_breakers[agent_id] = CircuitBreakerState(agent_id=agent_id)

        cb = self.circuit_breakers[agent_id]
        cb.failure_count += 1
        cb.last_failure_time = datetime.now().isoformat()

        # Check if circuit should open
        if (
            cb.failure_count >= self.failure_threshold
            and cb.state == CircuitState.CLOSED
        ):
            cb.state = CircuitState.OPEN
            cb.state_change_time = datetime.now().isoformat()
            logger.warning(f"Circuit opened for agent: {agent_id}")

        return failure_id

    def record_success(self, agent_id: str) -> None:
        """Record successful recovery.

        Args:
            agent_id: ID of recovered agent
        """
        if agent_id not in self.circuit_breakers:
            self.circuit_breakers[agent_id] = CircuitBreakerState(agent_id=agent_id)

        cb = self.circuit_breakers[agent_id]
        cb.last_success_time = datetime.now().isoformat()

        if cb.state == CircuitState.HALF_OPEN:
            cb.success_count_since_open += 1

            # If enough successes, close circuit
            if cb.success_count_since_open >= 3:
                cb.state = CircuitState.CLOSED
                cb.failure_count = 0
                cb.success_count_since_open = 0
                cb.state_change_time = datetime.now().isoformat()
                logger.info(f"Circuit closed for agent: {agent_id}")

        elif cb.state == CircuitState.CLOSED:
            # Reset failure count on success
            cb.failure_count = max(0, cb.failure_count - 1)

    def is_agent_healthy(self, agent_id: str) -> bool:
        """Check if agent is healthy.

        Args:
            agent_id: ID of agent

        Returns:
            True if agent is healthy
        """
        if agent_id not in self.circuit_breakers:
            return True

        cb = self.circuit_breakers[agent_id]

        # Check if circuit is open
        if cb.state == CircuitState.OPEN:
            # Check if enough time has passed to attempt recovery
            if cb.last_failure_time:
                last_failure = datetime.fromisoformat(cb.last_failure_time)
                elapsed = (datetime.now() - last_failure).total_seconds()

                if elapsed > self.reset_timeout:
                    cb.state = CircuitState.HALF_OPEN
                    cb.success_count_since_open = 0
                    cb.state_change_time = datetime.now().isoformat()
                    logger.info(f"Circuit half-open for agent: {agent_id}")
                    return True

            return False

        return True

    def can_retry(self, agent_id: str, retry_count: int = 0) -> bool:
        """Check if a task can be retried on agent.

        Args:
            agent_id: ID of agent
            retry_count: Current retry count

        Returns:
            True if retry is allowed
        """
        # Max 3 retries
        if retry_count >= 3:
            return False

        return self.is_agent_healthy(agent_id)

    def register_recovery_strategy(self, agent_id: str, strategy: Callable) -> None:
        """Register a recovery strategy for an agent.

        Args:
            agent_id: ID of agent
            strategy: Callable to execute for recovery
        """
        self.recovery_strategies[agent_id] = strategy
        logger.debug(f"Recovery strategy registered for agent: {agent_id}")

    def attempt_recovery(self, agent_id: str) -> bool:
        """Attempt to recover an agent.

        Args:
            agent_id: ID of agent

        Returns:
            True if recovery successful
        """
        if agent_id not in self.recovery_strategies:
            return False

        try:
            self.recovery_strategies[agent_id]()
            self.record_success(agent_id)
            logger.info(f"Agent recovered: {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Recovery failed for agent {agent_id}: {e}")
            return False

    def get_failure(self, failure_id: str) -> Optional[Failure]:
        """Get failure information.

        Args:
            failure_id: ID of failure

        Returns:
            Failure record or None
        """
        return self.failures.get(failure_id)

    def get_agent_failures(self, agent_id: str) -> List[Failure]:
        """Get all failures for an agent.

        Args:
            agent_id: ID of agent

        Returns:
            List of failures
        """
        return [f for f in self.failures.values() if f.agent_id == agent_id]

    def get_circuit_breaker(self, agent_id: str) -> Optional[CircuitBreakerState]:
        """Get circuit breaker state for agent.

        Args:
            agent_id: ID of agent

        Returns:
            Circuit breaker state or None
        """
        return self.circuit_breakers.get(agent_id)

    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status.

        Returns:
            Health status dictionary
        """
        breakdown: Dict[str, int] = {
            CircuitState.CLOSED.value: 0,
            CircuitState.OPEN.value: 0,
            CircuitState.HALF_OPEN.value: 0,
        }

        for cb in self.circuit_breakers.values():
            breakdown[cb.state.value] += 1

        total_failures = len(self.failures)
        recovered_failures = sum(1 for f in self.failures.values() if f.recovered)

        return {
            "total_agents": len(self.circuit_breakers),
            "healthy_agents": breakdown[CircuitState.CLOSED.value],
            "failing_agents": breakdown[CircuitState.OPEN.value],
            "recovering_agents": breakdown[CircuitState.HALF_OPEN.value],
            "total_failures": total_failures,
            "recovered_failures": recovered_failures,
            "percentage_healthy": (
                breakdown[CircuitState.CLOSED.value] / len(self.circuit_breakers) * 100
                if self.circuit_breakers
                else 100
            ),
            "circuit_breakdown": breakdown,
        }

    def reset(self) -> None:
        """Reset fault recovery system."""
        self.failures.clear()
        self.circuit_breakers.clear()
        self.recovery_strategies.clear()
        logger.info("FaultRecovery reset")

    # Private methods

    def _save_failure(self, failure: Failure) -> None:
        """Save failure to file."""
        try:
            with open(self.failures_file, "a") as f:
                f.write(json.dumps(asdict(failure)) + "\n")
        except (OSError, IOError) as e:
            logger.error(f"Error saving failure: {e}")

    def _load_failures(self) -> None:
        """Load failures from file."""
        if not self.failures_file.exists():
            return

        try:
            with open(self.failures_file, "r") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        failure = Failure(**data)
                        self.failures[failure.failure_id] = failure
                    except (json.JSONDecodeError, TypeError):
                        continue
        except (OSError, IOError) as e:
            logger.error(f"Error loading failures: {e}")
