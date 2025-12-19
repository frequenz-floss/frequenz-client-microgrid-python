# Frequenz Microgrid API Client Release Notes

## Summary

This release reintroduces sensor support that was temporarily removed in the v0.18.0 release. The new sensor API has been redesigned to fit the updated component and metrics model introduced in v0.18.0.

## New Features

- New `sensor` module (`frequenz.client.microgrid.sensor`) with sensor related types.
- New `MicrogridApiClient` methods

    * `list_sensors()`: fetch sensor metadata.
    * `receive_sensor_telemetry_stream()`: stream sensor telemetry data.

Example:

```python
import asyncio
from frequenz.client.microgrid import MicrogridApiClient
from frequenz.client.microgrid.metrics import Metric

URL = "grpc://[::1]:62060"

async def main() -> None:
    print(f"Connecting to {URL}...")
    async with MicrogridApiClient(URL) as client:
        print("Listing available sensors...")
        sensors = list(await client.list_sensors())

        if not sensors:
            print("No sensors found.")
            return

        print(f"Found {len(sensors)}: {sensors}.")
        print()

        sensor = sensors[0]
        print(f"Streaming telemetry from sensor {sensor.id} ({sensor.name})...")
        telemetry_stream = client.receive_sensor_telemetry_stream(
            sensors[0].id, list(Metric)
        )
        async for telemetry in telemetry_stream:
            print(f"\tReceived: {telemetry}")

asyncio.run(main())
```

## Upgrading (from v0.9)

### Sensor support restored with new API

Sensor support that was removed in v0.18.0 is now back, but with a redesigned API that aligns with the v0.18.0 component and metrics model.

#### `list_sensors()`

The method name remains the same, but the signature and return type have changed:

```python
# Old v0.9.1 API
sensors: Iterable[Sensor] = await client.list_sensors()

# New v0.18.2 API (same method name, different types)
from frequenz.client.common.microgrid.sensors import SensorId
from frequenz.client.microgrid.sensor import Sensor

sensors: Iterable[Sensor] = await client.list_sensors()

# You can also filter by sensor IDs
sensors = await client.list_sensors(sensors=[SensorId(1), SensorId(2)])
```
The `Sensor` class now provides a new attribute `microgrid_id: MicrogridId` and the `identity` property now returns a tuple `(SensorId, MicrogridId)` instead of just `SensorId`.

#### `stream_sensor_data()` → `receive_sensor_telemetry_stream()`

The streaming method has been renamed and its return type changed:

```python
# Old v0.9.1 API
from frequenz.client.microgrid.sensor import SensorDataSamples, SensorMetric

receiver: Receiver[SensorDataSamples] = client.stream_sensor_data(
    sensor=SensorId(1),
    metrics=[SensorMetric.TEMPERATURE, SensorMetric.HUMIDITY],  # optional
)

async for samples in receiver:
    # samples.metric_samples, samples.state_sample, etc.
    ...

# New v0.18.2 API
from frequenz.client.microgrid.sensor import SensorTelemetry
from frequenz.client.microgrid.metrics import Metric

receiver: Receiver[SensorTelemetry] = client.receive_sensor_telemetry_stream(
    sensor=SensorId(1),
    metrics=[Metric.TEMPERATURE, Metric.AC_VOLTAGE],  # required
)

async for telemetry in receiver:
    # telemetry.sensor_id: SensorId
    # telemetry.metric_samples: Sequence[MetricSample]
    # telemetry.state_snapshots: Sequence[SensorStateSnapshot]
    for sample in telemetry.metric_samples:
        print(f"{sample.metric}: {sample.value} at {sample.sampled_at}")
    ...
```

Key differences:

- **Method renamed**: `stream_sensor_data()` → `receive_sensor_telemetry_stream()`
- **Metrics parameter is now required**: You must specify which metrics to stream. The old API allowed `None` to stream all metrics.
- **Uses unified `Metric` enum**: The old `SensorMetric` enum is removed. Use `frequenz.client.microgrid.metrics.Metric` instead.
- **Return type changed**: `SensorDataSamples` → `SensorTelemetry`
- **State samples changed**: `SensorStateSample` → `SensorStateSnapshot` with different structure (see below)

#### Sensor state types

The sensor state types have been redesigned:

| Old v0.9.1 type           | New v0.18.2 type                          |
|---------------------------|-------------------------------------------|
| `SensorMetric`            | *Removed* — use `Metric`                  |
| `SensorStateCode`         | `SensorStateCode` (different values)      |
| `SensorErrorCode`         | `SensorDiagnosticCode`                    |
| `SensorStateSample`       | `SensorStateSnapshot`                     |
| `SensorMetricSample`      | `MetricSample`                            |
| `SensorDataSamples`       | `SensorTelemetry`                         |

The new `SensorStateSnapshot` structure:

```python
@dataclass(frozen=True, kw_only=True)
class SensorStateSnapshot:
    origin_time: datetime          # was `sampled_at`
    states: Set[SensorStateCode | int]  # was `frozenset`
    warnings: Sequence[SensorDiagnostic]  # new
    errors: Sequence[SensorDiagnostic]    # replaces error codes
```

The new `SensorDiagnostic` provides richer error/warning information:

```python
@dataclass(frozen=True, kw_only=True)
class SensorDiagnostic:
    diagnostic_code: SensorDiagnosticCode | int
    message: str | None
    vendor_diagnostic_code: str | None
```

#### Import changes

Update your imports for sensor types:

```python
# Old v0.9.1
from frequenz.client.microgrid.sensor import (
    Sensor,
    SensorDataSamples,
    SensorErrorCode,
    SensorMetric,
    SensorMetricSample,
    SensorStateCode,
    SensorStateSample,
)

# New v0.18.2
from frequenz.client.microgrid.sensor import (
    Sensor,
    SensorDiagnostic,
    SensorDiagnosticCode,
    SensorStateCode,
    SensorStateSnapshot,
    SensorTelemetry,
)
from frequenz.client.microgrid.metrics import Metric, MetricSample
from frequenz.client.common.microgrid.sensors import SensorId
```
