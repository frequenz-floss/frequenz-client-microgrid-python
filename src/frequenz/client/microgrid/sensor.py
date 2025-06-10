# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Microgrid sensors.

This package provides classes and utilities for working with different types of
sensors in a microgrid environment. [`Sensor`][frequenz.client.microgrid.sensor.Sensor]s
measure various physical metrics in the surrounding environment, such as temperature,
humidity, and solar irradiance.

# Streaming Sensor Data Samples

This package also provides several data structures for handling sensor readings
and states:

* [`SensorDataSamples`][frequenz.client.microgrid.sensor.SensorDataSamples]:
    Represents a collection of sensor data samples.
* [`SensorErrorCode`][frequenz.client.microgrid.sensor.SensorErrorCode]:
    Defines error codes that a sensor can report.
* [`SensorMetric`][frequenz.client.microgrid.sensor.SensorMetric]: Enumerates
    the different metrics a sensor can measure (e.g., temperature, voltage).
* [`SensorMetricSample`][frequenz.client.microgrid.sensor.SensorMetricSample]:
    Represents a single sample of a sensor metric, including its value and
    timestamp.
* [`SensorStateCode`][frequenz.client.microgrid.sensor.SensorStateCode]:
    Defines codes representing the operational state of a sensor.
* [`SensorStateSample`][frequenz.client.microgrid.sensor.SensorStateSample]:
    Represents a single sample of a sensor's state, including its state code
    and timestamp.
"""

import dataclasses
import enum
from dataclasses import dataclass
from datetime import datetime
from typing import assert_never

from frequenz.api.microgrid import sensor_pb2
from frequenz.client.common.microgrid.sensors import SensorId

from ._lifetime import Lifetime
from .metrics import AggregatedMetricValue, AggregationMethod


@dataclasses.dataclass(frozen=True, kw_only=True)
class Sensor:
    """Measures environmental metrics in the microgrid."""

    id: SensorId
    """This sensor's ID."""

    name: str | None = None
    """The name of this sensor."""

    manufacturer: str | None = None
    """The manufacturer of this sensor."""

    model_name: str | None = None
    """The model name of this sensor."""

    operational_lifetime: Lifetime = dataclasses.field(default_factory=Lifetime)
    """The operational lifetime of this sensor."""

    @property
    def identity(self) -> SensorId:
        """The identity of this sensor.

        This uses the sensor ID to identify a sensor without considering the
        other attributes, so even if a sensor state changed, the identity
        remains the same.
        """
        return self.id

    def __str__(self) -> str:
        """Return a human-readable string representation of this instance."""
        name = f":{self.name}" if self.name else ""
        return f"<{type(self).__name__}:{self.id}{name}>"


@enum.unique
class SensorMetric(enum.Enum):
    """The metrics that can be reported by sensors in the microgrid.

    These metrics correspond to various sensor readings primarily related to
    environmental conditions and physical measurements.
    """

    UNSPECIFIED = sensor_pb2.SENSOR_METRIC_UNSPECIFIED
    """Default value (this should not be normally used and usually indicates an issue)."""

    TEMPERATURE = sensor_pb2.SENSOR_METRIC_TEMPERATURE
    """Temperature, in Celsius (°C)."""

    HUMIDITY = sensor_pb2.SENSOR_METRIC_HUMIDITY
    """Humidity, in percentage (%)."""

    PRESSURE = sensor_pb2.SENSOR_METRIC_PRESSURE
    """Pressure, in Pascal (Pa)."""

    IRRADIANCE = sensor_pb2.SENSOR_METRIC_IRRADIANCE
    """Irradiance / Radiation flux, in watts per square meter (W / m²)."""

    VELOCITY = sensor_pb2.SENSOR_METRIC_VELOCITY
    """Velocity, in meters per second (m / s)."""

    ACCELERATION = sensor_pb2.SENSOR_METRIC_ACCELERATION
    """Acceleration in meters per second per second (m / s²)."""

    ANGLE = sensor_pb2.SENSOR_METRIC_ANGLE
    """Angle, in degrees with respect to the (magnetic) North (°)."""

    DEW_POINT = sensor_pb2.SENSOR_METRIC_DEW_POINT
    """Dew point, in Celsius (°C).

    The temperature at which the air becomes saturated with water vapor.
    """


@enum.unique
class SensorStateCode(enum.Enum):
    """The various states that a sensor can be in."""

    UNSPECIFIED = sensor_pb2.COMPONENT_STATE_UNSPECIFIED
    """Default value (this should not be normally used and usually indicates an issue)."""

    ON = sensor_pb2.COMPONENT_STATE_OK
    """The sensor is up and running."""

    ERROR = sensor_pb2.COMPONENT_STATE_ERROR
    """The sensor is in an error state."""


@enum.unique
class SensorErrorCode(enum.Enum):
    """The various errors that can occur in sensors."""

    UNSPECIFIED = sensor_pb2.ERROR_CODE_UNSPECIFIED
    """Default value (this should not be normally used and usually indicates an issue)."""


@dataclass(frozen=True, kw_only=True)
class SensorStateSample:
    """A sample of state, warnings, and errors for a sensor at a specific time."""

    sampled_at: datetime
    """The time at which this state was sampled."""

    states: frozenset[SensorStateCode | int]
    """The set of states of the sensor.

    If the reported state is not known by the client (it could happen when using an
    older version of the client with a newer version of the server), it will be
    represented as an `int` and **not** the
    [`SensorStateCode.UNSPECIFIED`][frequenz.client.microgrid.sensor.SensorStateCode.UNSPECIFIED]
    value (this value is used only when the state is not known by the server).
    """

    warnings: frozenset[SensorErrorCode | int]
    """The set of warnings for the sensor."""

    errors: frozenset[SensorErrorCode | int]
    """The set of errors for the sensor.

    This set will only contain errors if the sensor is in an error state.
    """


@dataclass(frozen=True, kw_only=True)
class SensorMetricSample:
    """A sample of a sensor metric at a specific time.

    This represents a single sample of a specific metric, the value of which is either
    measured at a particular time.
    """

    sampled_at: datetime
    """The moment when the metric was sampled."""

    metric: SensorMetric | int
    """The metric that was sampled."""

    # In the protocol this is float | AggregatedMetricValue, but for live data we can't
    # receive the AggregatedMetricValue, so we limit this to float for now.
    value: float | AggregatedMetricValue | None
    """The value of the sampled metric."""

    def as_single_value(
        self, *, aggregation_method: AggregationMethod = AggregationMethod.AVG
    ) -> float | None:
        """Return the value of this sample as a single value.

        if [`value`][frequenz.client.microgrid.sensor.SensorMetricSample.value] is a `float`,
        it is returned as is. If `value` is an
        [`AggregatedMetricValue`][frequenz.client.microgrid.metrics.AggregatedMetricValue],
        the value is aggregated using the provided `aggregation_method`.

        Args:
            aggregation_method: The method to use to aggregate the value when `value` is
                a `AggregatedMetricValue`.

        Returns:
            The value of the sample as a single value, or `None` if the value is `None`.
        """
        match self.value:
            case float() | int():
                return self.value
            case AggregatedMetricValue():
                match aggregation_method:
                    case AggregationMethod.AVG:
                        return self.value.avg
                    case AggregationMethod.MIN:
                        return self.value.min
                    case AggregationMethod.MAX:
                        return self.value.max
                    case unexpected:
                        assert_never(unexpected)
            case None:
                return None
            case unexpected:
                assert_never(unexpected)


@dataclass(frozen=True, kw_only=True)
class SensorDataSamples:
    """An aggregate of multiple metrics, states, and errors of a sensor."""

    sensor_id: SensorId
    """The unique identifier of the sensor."""

    metrics: list[SensorMetricSample]
    """The metrics sampled from the sensor."""

    states: list[SensorStateSample]
    """The states sampled from the sensor."""
