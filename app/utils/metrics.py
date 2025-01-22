"""Metrics collection utilities for the application."""

class MetricsCollector:
    def __init__(self):
        self._metrics = {}

    def record(self, metric: str, value: float):
        if metric not in self._metrics:
            self._metrics[metric] = []
        self._metrics[metric].append(value) 