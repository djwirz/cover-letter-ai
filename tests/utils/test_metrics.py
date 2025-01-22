"""Tests for metrics utilities."""
from app.utils.metrics import MetricsCollector

def test_metrics_recording():
    collector = MetricsCollector()
    collector.record("test_metric", 1.0)
    assert len(collector._metrics["test_metric"]) == 1 