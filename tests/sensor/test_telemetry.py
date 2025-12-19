# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for SensorTelemetry dataclass."""

from collections.abc import Hashable
from datetime import datetime, timezone

import pytest
from frequenz.client.common.microgrid.sensors import SensorId

from frequenz.client.microgrid.metrics import MetricSample
from frequenz.client.microgrid.sensor import (
    SensorDiagnostic,
    SensorDiagnosticCode,
    SensorStateCode,
    SensorStateSnapshot,
    SensorTelemetry,
)


def test_sensor_telemetry_creation() -> None:
    """Test SensorTelemetry creation."""
    now = datetime.now(timezone.utc)

    sample1 = MetricSample(metric=1, sampled_at=now, value=25.5, bounds=[])
    sample2 = MetricSample(metric=2, sampled_at=now, value=60.0, bounds=[])

    diagnostic = SensorDiagnostic(diagnostic_code=SensorDiagnosticCode.INTERNAL)
    snapshot = SensorStateSnapshot(
        origin_time=now,
        states={SensorStateCode.OK},
        warnings=(),
        errors=[diagnostic],
    )

    telemetry = SensorTelemetry(
        sensor_id=SensorId(1),
        metric_samples=[sample1, sample2],
        state_snapshots=[snapshot],
    )

    assert telemetry.sensor_id == SensorId(1)
    assert len(telemetry.metric_samples) == 2
    assert sample1 in telemetry.metric_samples
    assert sample2 in telemetry.metric_samples
    assert len(telemetry.state_snapshots) == 1
    assert snapshot in telemetry.state_snapshots


def test_sensor_telemetry_empty() -> None:
    """Test SensorTelemetry with empty collections."""
    telemetry = SensorTelemetry(
        sensor_id=SensorId(1),
        metric_samples=(),
        state_snapshots=(),
    )

    assert telemetry.sensor_id == SensorId(1)
    assert len(telemetry.metric_samples) == 0
    assert len(telemetry.state_snapshots) == 0


def test_sensor_telemetry_multiple_snapshots() -> None:
    """Test SensorTelemetry with multiple state snapshots."""
    now = datetime.now(timezone.utc)

    snapshot1 = SensorStateSnapshot(
        origin_time=now,
        states={SensorStateCode.OK},
        warnings=(),
        errors=(),
    )

    snapshot2 = SensorStateSnapshot(
        origin_time=now,
        states={SensorStateCode.ERROR},
        warnings=(),
        errors=(),
    )

    telemetry = SensorTelemetry(
        sensor_id=SensorId(1),
        metric_samples=(),
        state_snapshots=[snapshot1, snapshot2],
    )

    assert len(telemetry.state_snapshots) == 2
    assert snapshot1 in telemetry.state_snapshots
    assert snapshot2 in telemetry.state_snapshots


def test_sensor_telemetry_equality() -> None:
    """Test SensorTelemetry equality."""
    now = datetime.now(timezone.utc)
    sample = MetricSample(metric=1, sampled_at=now, value=25.5, bounds=[])
    snapshot = SensorStateSnapshot(
        origin_time=now,
        states={SensorStateCode.OK},
        warnings=(),
        errors=(),
    )

    telemetry1 = SensorTelemetry(
        sensor_id=SensorId(1),
        metric_samples=[sample],
        state_snapshots=[snapshot],
    )

    telemetry2 = SensorTelemetry(
        sensor_id=SensorId(1),
        metric_samples=[sample],
        state_snapshots=[snapshot],
    )

    telemetry3 = SensorTelemetry(
        sensor_id=SensorId(2),  # Different sensor ID
        metric_samples=[sample],
        state_snapshots=[snapshot],
    )

    assert telemetry1 == telemetry2
    assert telemetry1 != telemetry3


def test_sensor_telemetry_not_hashable() -> None:
    """Test that SensorTelemetry is not hashable."""
    now = datetime.now(timezone.utc)
    sample = MetricSample(metric=1, sampled_at=now, value=25.5, bounds=[])
    snapshot = SensorStateSnapshot(
        origin_time=now,
        states=frozenset([SensorStateCode.OK]),
        warnings=(),
        errors=(),
    )
    telemetry = SensorTelemetry(
        sensor_id=SensorId(1),
        metric_samples=[sample],
        state_snapshots=[snapshot],
    )

    # Should not be able to modify frozen dataclass
    with pytest.raises(TypeError):
        _ = hash(telemetry)

    assert not isinstance(telemetry, Hashable)
