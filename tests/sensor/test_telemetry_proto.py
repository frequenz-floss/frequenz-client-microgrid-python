# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for proto conversion of SensorTelemetry."""


from frequenz.api.common.v1alpha8.microgrid.sensors import sensors_pb2
from frequenz.client.common.microgrid.sensors import SensorId
from google.protobuf.timestamp_pb2 import Timestamp

from frequenz.client.microgrid.sensor import SensorDiagnosticCode, SensorStateCode
from frequenz.client.microgrid.sensor._telemetry_proto import (
    sensor_telemetry_from_proto,
)


def test_sensor_telemetry_from_proto_complete() -> None:
    """Test converting complete SensorTelemetry from proto."""
    proto = sensors_pb2.SensorTelemetry(sensor_id=1)

    # Add metric samples
    sample1 = proto.metric_samples.add()
    sample1.metric = 1  # type: ignore[assignment]
    sample1.sample_time.CopyFrom(Timestamp(seconds=1696118400))
    sample1.value.simple_metric.value = 25.5

    sample2 = proto.metric_samples.add()
    sample2.metric = 2  # type: ignore[assignment]
    sample2.sample_time.CopyFrom(Timestamp(seconds=1696118400))
    sample2.value.simple_metric.value = 60.0

    # Add state snapshot
    snapshot = proto.state_snapshots.add()
    snapshot.origin_time.CopyFrom(Timestamp(seconds=1696118400))
    snapshot.states.append(sensors_pb2.SENSOR_STATE_CODE_OK)

    warning = snapshot.warnings.add()
    warning.diagnostic_code = sensors_pb2.SENSOR_DIAGNOSTIC_CODE_UNKNOWN
    warning.message = "Minor issue"

    telemetry = sensor_telemetry_from_proto(proto)

    assert telemetry.sensor_id == SensorId(1)
    assert len(telemetry.metric_samples) == 2
    assert len(telemetry.state_snapshots) == 1

    # Check metric samples
    metric_values = {s.value for s in telemetry.metric_samples}
    assert 25.5 in metric_values
    assert 60.0 in metric_values

    # Check state snapshot
    snapshot_obj = next(iter(telemetry.state_snapshots))
    assert SensorStateCode.OK in snapshot_obj.states
    assert len(snapshot_obj.warnings) == 1
    warning_obj = next(iter(snapshot_obj.warnings))
    assert warning_obj.diagnostic_code == SensorDiagnosticCode.UNKNOWN


def test_sensor_telemetry_from_proto_empty() -> None:
    """Test converting empty SensorTelemetry from proto."""
    proto = sensors_pb2.SensorTelemetry(sensor_id=1)

    telemetry = sensor_telemetry_from_proto(proto)

    assert telemetry.sensor_id == SensorId(1)
    assert len(telemetry.metric_samples) == 0
    assert len(telemetry.state_snapshots) == 0


def test_sensor_telemetry_from_proto_only_metrics() -> None:
    """Test converting SensorTelemetry with only metric samples."""
    proto = sensors_pb2.SensorTelemetry(sensor_id=1)

    sample = proto.metric_samples.add()
    sample.metric = 1  # type: ignore[assignment]
    sample.sample_time.CopyFrom(Timestamp(seconds=1696118400))
    sample.value.simple_metric.value = 25.5

    telemetry = sensor_telemetry_from_proto(proto)

    assert telemetry.sensor_id == SensorId(1)
    assert len(telemetry.metric_samples) == 1
    assert len(telemetry.state_snapshots) == 0


def test_sensor_telemetry_from_proto_only_state() -> None:
    """Test converting SensorTelemetry with only state snapshots."""
    proto = sensors_pb2.SensorTelemetry(sensor_id=1)

    snapshot = proto.state_snapshots.add()
    snapshot.origin_time.CopyFrom(Timestamp(seconds=1696118400))
    snapshot.states.append(sensors_pb2.SENSOR_STATE_CODE_OK)

    telemetry = sensor_telemetry_from_proto(proto)

    assert telemetry.sensor_id == SensorId(1)
    assert len(telemetry.metric_samples) == 0
    assert len(telemetry.state_snapshots) == 1


def test_sensor_telemetry_from_proto_multiple_snapshots() -> None:
    """Test converting SensorTelemetry with multiple state snapshots."""
    proto = sensors_pb2.SensorTelemetry(sensor_id=1)

    # First snapshot
    snapshot1 = proto.state_snapshots.add()
    snapshot1.origin_time.CopyFrom(Timestamp(seconds=1696118400))
    snapshot1.states.append(sensors_pb2.SENSOR_STATE_CODE_OK)

    # Second snapshot
    snapshot2 = proto.state_snapshots.add()
    snapshot2.origin_time.CopyFrom(Timestamp(seconds=1696118460))  # 1 min later
    snapshot2.states.append(sensors_pb2.SENSOR_STATE_CODE_ERROR)

    telemetry = sensor_telemetry_from_proto(proto)

    assert telemetry.sensor_id == SensorId(1)
    assert len(telemetry.state_snapshots) == 2

    # Verify both snapshots are present
    states = {next(iter(s.states)) for s in telemetry.state_snapshots if s.states}
    assert SensorStateCode.OK in states
    assert SensorStateCode.ERROR in states


def test_sensor_telemetry_from_proto_multiple_metrics() -> None:
    """Test converting SensorTelemetry with multiple metric samples."""
    proto = sensors_pb2.SensorTelemetry(sensor_id=1)

    for i in range(5):
        sample = proto.metric_samples.add()
        sample.metric = i + 1  # type: ignore[assignment]
        sample.sample_time.CopyFrom(Timestamp(seconds=1696118400 + i * 10))
        sample.value.simple_metric.value = float(i * 10)

    telemetry = sensor_telemetry_from_proto(proto)

    assert telemetry.sensor_id == SensorId(1)
    assert len(telemetry.metric_samples) == 5

    # Verify all values are present
    metric_values = {s.value for s in telemetry.metric_samples}
    assert metric_values == {0.0, 10.0, 20.0, 30.0, 40.0}


def test_sensor_telemetry_from_proto_complex() -> None:
    """Test converting SensorTelemetry with complex data."""
    proto = sensors_pb2.SensorTelemetry(sensor_id=42)

    # Multiple metric samples
    for i in range(3):
        sample = proto.metric_samples.add()
        sample.metric = i + 1  # type: ignore[assignment]
        sample.sample_time.CopyFrom(Timestamp(seconds=1696118400))
        sample.value.simple_metric.value = float(i * 5)

    # Multiple state snapshots with diagnostics
    snapshot1 = proto.state_snapshots.add()
    snapshot1.origin_time.CopyFrom(Timestamp(seconds=1696118400))
    snapshot1.states.append(sensors_pb2.SENSOR_STATE_CODE_ERROR)

    error1 = snapshot1.errors.add()
    error1.diagnostic_code = sensors_pb2.SENSOR_DIAGNOSTIC_CODE_INTERNAL
    error1.message = "Critical error"

    snapshot2 = proto.state_snapshots.add()
    snapshot2.origin_time.CopyFrom(Timestamp(seconds=1696118460))
    snapshot2.states.append(sensors_pb2.SENSOR_STATE_CODE_OK)

    telemetry = sensor_telemetry_from_proto(proto)

    assert telemetry.sensor_id == SensorId(42)
    assert len(telemetry.metric_samples) == 3
    assert len(telemetry.state_snapshots) == 2

    # Find the snapshot with errors
    error_snapshot = next(s for s in telemetry.state_snapshots if s.errors)
    assert len(error_snapshot.errors) == 1
    error_obj = next(iter(error_snapshot.errors))
    assert error_obj.diagnostic_code == SensorDiagnosticCode.INTERNAL
    assert error_obj.message == "Critical error"
