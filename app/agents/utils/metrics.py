import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from contextlib import contextmanager
from app.agents.utils.logging import setup_logger

logger = setup_logger("Metrics")

@dataclass
class Metric:
    """Individual metric tracking"""
    name: str
    values: list = field(default_factory=list)
    timestamps: list = field(default_factory=list)
    
    def record(self, value: float) -> None:
        """Record a new metric value"""
        self.values.append(value)
        self.timestamps.append(time.time())
        
    def summary(self) -> Dict[str, Any]:
        """Get metric summary statistics"""
        if not self.values:
            return {}
            
        return {
            "count": len(self.values),
            "min": min(self.values),
            "max": max(self.values),
            "mean": sum(self.values) / len(self.values),
            "last": self.values[-1],
            "last_timestamp": self.timestamps[-1]
        }

class PerformanceMonitor:
    """Performance monitoring and metrics collection"""
    
    def __init__(self):
        self.metrics: Dict[str, Metric] = {}
        self._start_time: Optional[float] = None
        self._active = False

    async def initialize(self) -> None:
        """Initialize the metrics collector"""
        self.metrics = {}
        self._active = True
        logger.info("Performance monitoring initialized")

    async def close(self) -> None:
        """Clean up metrics collector"""
        self._active = False
        logger.info("Performance monitoring stopped")

    @contextmanager
    def track(self) -> None: # type: ignore
        """
        Context manager for tracking operation performance
        
        Yields:
            None
        """
        if not self._active:
            yield
            return
            
        start_time = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start_time
            self.record("operation_duration", duration)

    def record(self, metric_name: str, value: float) -> None:
        """
        Record a metric value
        
        Args:
            metric_name: Name of the metric to record
            value: Value to record
        """
        if not self._active:
            return
            
        if metric_name not in self.metrics:
            self.metrics[metric_name] = Metric(name=metric_name)
            
        self.metrics[metric_name].record(value)
        logger.debug(f"Recorded metric: {metric_name}={value}")

    def get_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all recorded metrics with summaries
        
        Returns:
            Dictionary of metric summaries
        """
        return {
            name: metric.summary()
            for name, metric in self.metrics.items()
        }