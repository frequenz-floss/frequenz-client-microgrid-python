# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Sensor telemetry types."""

from collections.abc import Sequence
from dataclasses import dataclass

from frequenz.client.common.microgrid.sensors import SensorId

from ..metrics._sample import MetricSample
from ._state import SensorStateSnapshot


@dataclass(frozen=True, kw_only=True)
class SensorTelemetry:
    """Telemetry data from a sensor.

    Contains metric measurements and state snapshots for a specific sensor.
    """

    sensor_id: SensorId
    """The unique identifier of the sensor that produced this telemetry."""

    metric_samples: Sequence[MetricSample]
    """List of metric measurements from the sensor."""

    state_snapshots: Sequence[SensorStateSnapshot]
    """List of state snapshots indicating the sensor's operational status."""

    # Disable hashing for this class (mypy doesn't seem to understand assigining to
    # None, but it is documented in __hash__ docs).
    __hash__ = None  # type: ignore[assignment]
