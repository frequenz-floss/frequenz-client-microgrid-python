# Frequenz Microgrid API Client Release Notes

## Summary

This release is a major breaking change. The client now targets the Microgrid API specification version `0.18.x` and the `v1` namespace in `frequenz-api-common`. Both upstream projects introduce large structural and naming changes to components, metrics, and telemetry, and this client has been refactored accordingly.

Existing code written for `frequenz-client-microgrid` `v0.9.1` will not work without changes. Upgrading will typically require:

- Bumping dependencies to the new API and common libraries.
- Updating imports for components, metrics, and IDs.
- Migrating from the old ad-hoc component and sensor APIs to the new component/metrics model.
- Adapting to the new power-control and bounds APIs.

For a full overview of upstream changes, consult the [Microgrid API releases](https://github.com/frequenz-floss/frequenz-api-microgrid/releases) and [Common API releases](https://github.com/frequenz-floss/frequenz-api-common/releases).

## Upgrading

The following notes are aimed at users upgrading from `frequenz-client-microgrid` `v0.9.1`.

### Dependencies and imports

- **Dependencies**:

  - `frequenz-api-microgrid` is now required at `>= 0.18.0, < 0.19.0`.
  - `frequenz-api-common` is now required at `>= 0.8.0, < 1.0.0` and uses the `v1` namespace.
  - `frequenz-client-common` is now required at `>= 0.3.6, < 0.4.0` and provides ID and helper types used throughout the client.

  Make sure you pin compatible versions in your own project when upgrading.

- **IDs and common types**:

  IDs come from `frequenz.client.common` (this was already true in `v0.9.1`, but they are now used more consistently):

  ```python
  from frequenz.client.common.microgrid import MicrogridId
  from frequenz.client.common.microgrid.components import ComponentId
  ```

- **Components and metrics**:

  The old component and data types (`Component`, `ComponentCategory`, `BatteryData`, `InverterData`, `ComponentState*`, etc.) that used to live directly under `frequenz.client.microgrid` have been replaced with a richer component and metrics model:

  ```python
  from frequenz.client.microgrid import MicrogridApiClient
  from frequenz.client.microgrid import component, metrics

  # Example component types
  from frequenz.client.microgrid.component import (
      Component,
      ComponentCategory,
      ComponentConnection,
      ComponentDataSamples,
      ComponentStateSample,
      GridConnectionPoint,
      Inverter,
      Battery,
  )

  # Metrics and bounds
  from frequenz.client.microgrid.metrics import Metric, Bounds, MetricSample
  ```

  Update your imports to use these new modules instead of the removed legacy types.

### Metadata: `metadata()` → `get_microgrid_info()`

The old `metadata()` method has been replaced by `get_microgrid_info()` which returns a richer `MicrogridInfo` object.

### Listing components and connections

In `v0.9.1` you would often use:

```python
components = await client.components()
connections = await client.connections(starts={component_id}, ends=set())
```

Now:

- **List components**:

  ```python
  components = await client.list_components(
      components=[ComponentId(1), ComponentId(2)],
      categories=[ComponentCategory.INVERTER, ComponentCategory.BATTERY],
  )
  ```

  Notes:

  - `components` may contain `ComponentId` instances or `Component` objects.
  - `categories` may contain `ComponentCategory` enum values or raw integer category IDs.
  - Filters across `components` and `categories` are combined with `AND`; values inside each list are combined with `OR`.

- **List connections**:

  ```python
  connections = await client.list_connections(
      sources=[ComponentId(1)],
      destinations=[ComponentId(2)],
  )
  ```

  Notes:

  - `sources` and `destinations` accept `ComponentId` or `Component` instances.
  - Filters across `sources` and `destinations` are combined with `AND`; values inside each list are combined with `OR`.
  - Connections now also use `.source` and `.destination` terminology instead of `.start` and `.end`.


### Sensors: `list_sensors()`, `stream_sensor_data()` → *removed* (temporary)

The old `list_sensors()` and `stream_sensor_data()` method has no direct equivalent. It will be reintroduced in a future release once sensor abstractions are reworked to fit the new component and metrics model.

### Power control: `set_power()` / `set_reactive_power()` → `set_component_power_active()` / `set_component_power_reactive()`

In `v0.9.1` you would typically set power using methods like:

```python
await client.set_power(component_id, power_w)
await client.set_reactive_power(component_id, reactive_power_var)
```

These methods have been replaced with lifetime-aware, metric-aligned calls:

```python
# Active power in watts
expiry = await client.set_component_power_active(
    component=ComponentId(1),
    power_w=1_000.0,
    request_lifetime=timedelta(seconds=30),
)

# Reactive power in volt-ampere reactive (var)
expiry = await client.set_component_power_reactive(
    component=ComponentId(1),
    power_var=500.0,
    request_lifetime=timedelta(seconds=30),
)
```

- Both methods accept either `ComponentId` or `Component` instances.

### Bounds: `set_bounds()` → `add_component_bounds()`

In `v0.9.1`, power bounds were earlier set using methods like `set_bounds(component_id, lower, upper)`.

Now the new API reflects the `v0.18` metrics semantics: bounds are attached to metrics and transported as part of telemetry samples. Use `add_component_bounds()` together with `Metric` and `Bounds`:

```python
await client.add_component_bounds(
    component=ComponentId(1),
    target=Metric.ACTIVE_POWER,
    bounds=[Bounds(lower=-1_000.0, upper=1_000.0)],
)
```

Notes:

- Bounds are now metric-specific: you must specify a `Metric` when adding bounds.
- Bounds are represented as at most two ranges, matching `frequenz-api-common` `v1` (`Bounds` may contain up to two inclusive ranges).

### Streaming telemetry: `*_data()` → `receive_component_data_samples_stream()`

The streaming model changed significantly.

In `v0.9.1`, you would use:

```python
receiver = await client.meter_data(component_id)
async for sample in receiver:
    # sample is a MeterData instance
    ...
```

Now, telemetry is integrated around components and metrics using `receive_component_data_samples_stream()` and `ComponentDataSamples`:

```python
receiver: Receiver[ComponentDataSamples] = (
    await client.receive_component_data_samples_stream(
        component=ComponentId(1),
        metrics=[Metric.ACTIVE_POWER, Metric.REACTIVE_POWER],
    )
)

async for samples in receiver:
    # Each `samples` corresponds to a single component at a single timestamp.
    # Metric values and bounds are attached per metric.
```

The upstream Microgrid API `v0.18` changes how samples are structured; important points from the upstream migration notes (see `frequenz-api-microgrid` discussion #278):

- Rated bounds moved into component metadata; telemetry samples now carry operational bounds per metric.
- Old `component_bounds` and `system_{inclusion,exclusion}_bounds` are unified under `samples.metric[x].bounds`.
- Older voltage metrics like `VOLTAGE_PHASE_A` map to `AC_VOLTAGE_PHASE_A_N` and similar; review metric names in `frequenz.client.microgrid.metrics.Metric` when porting code.
- All metrics for a given component at a given time share the same `sampled_at` timestamp.
- At most one `ComponentState` is included per `ComponentData`.

When migrating:

- Prefer requesting only the metrics you actually consume.
- Use the new bounds representation instead of any previously maintained client-side bounds fields.
- Replace sensor-centric streams with component-centric streams; each telemetry message now contains all requested metrics for a component.

## New Features

- Add `get_microgrid_info()` returning a rich `MicrogridInfo` dataclass with ID, enterprise, location, delivery area, status, and timestamps.
- Add a metrics model under `frequenz.client.microgrid.metrics` including the `Metric` enum, `Bounds`, and `MetricSample`/`AggregatedMetricValue`.
- Add high-level methods on `MicrogridApiClient` for listing components and connections, adding component bounds, receiving component data samples streams, and controlling active/reactive power with lifetimes.

## Bug Fixes

- Restore missing `Metric` enum members to match the upstream common API definitions.
- Remove an artificial timeout from the gRPC telemetry stream to avoid spurious cancellations under normal operation.
- Align error handling and validation with the updated API behavior (for example, validating lifetimes and power ranges before sending control requests).
