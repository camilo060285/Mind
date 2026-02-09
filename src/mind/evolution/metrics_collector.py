"""Real-time metrics collection during system execution."""

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class MetricSnapshot:
    """A point-in-time metric snapshot."""

    timestamp: float
    metric_name: str
    value: Any
    category: str  # e.g., "performance", "resource", "quality"


class MetricsCollector:
    """Collects metrics during system execution."""

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: Dict[str, List[MetricSnapshot]] = {}
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self._counters: Dict[str, int] = {}

    def record_metric(self, name: str, value: Any, category: str = "general") -> None:
        """Record a metric value.

        Args:
            name: Metric name
            value: Metric value
            category: Metric category
        """
        if name not in self.metrics:
            self.metrics[name] = []

        snapshot = MetricSnapshot(
            timestamp=time.time() - self.start_time,
            metric_name=name,
            value=value,
            category=category,
        )
        self.metrics[name].append(snapshot)

    def increment_counter(self, name: str, amount: int = 1) -> None:
        """Increment a counter.

        Args:
            name: Counter name
            amount: Amount to increment
        """
        if name not in self._counters:
            self._counters[name] = 0
        self._counters[name] += amount

    def get_counter(self, name: str) -> int:
        """Get counter value.

        Args:
            name: Counter name

        Returns:
            Counter value
        """
        return self._counters.get(name, 0)

    def finalize(self) -> Dict[str, Any]:
        """Finalize collection and return summary.

        Returns:
            Summary of all metrics
        """
        self.end_time = time.time()
        total_time = self.end_time - self.start_time

        summary = {
            "total_time": total_time,
            "counters": self._counters.copy(),
            "metrics": {},
            "categories": {},
        }

        # Process metrics by category
        for name, snapshots in self.metrics.items():
            if snapshots:
                latest = snapshots[-1]
                summary["metrics"][name] = {
                    "final_value": latest.value,
                    "snapshot_count": len(snapshots),
                }

                category = latest.category
                if category not in summary["categories"]:
                    summary["categories"][category] = []
                summary["categories"][category].append(name)

        return summary

    def get_metric_history(self, name: str) -> List[MetricSnapshot]:
        """Get historical data for a metric.

        Args:
            name: Metric name

        Returns:
            List of snapshots
        """
        return self.metrics.get(name, [])

    def get_metrics_by_category(self, category: str) -> Dict[str, List[MetricSnapshot]]:
        """Get all metrics in a category.

        Args:
            category: Category name

        Returns:
            Dict of metrics in that category
        """
        result = {}
        for name, snapshots in self.metrics.items():
            if snapshots and snapshots[-1].category == category:
                result[name] = snapshots
        return result

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics.

        Returns:
            Summary dictionary
        """
        if self.end_time is None:
            self.finalize()

        summary = {
            "total_metrics_recorded": sum(len(s) for s in self.metrics.values()),
            "total_counters": len(self._counters),
            "execution_time": self.end_time - self.start_time,
            "metric_names": list(self.metrics.keys()),
        }

        return summary

    def reset(self) -> None:
        """Reset all collected data."""
        self.metrics.clear()
        self._counters.clear()
        self.start_time = time.time()
        self.end_time = None
