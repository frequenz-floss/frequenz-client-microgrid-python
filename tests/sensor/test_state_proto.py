# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for proto conversion of sensor state types."""

from datetime import datetime, timezone

from frequenz.api.common.v1alpha8.microgrid.sensors import sensors_pb2
from google.protobuf.timestamp_pb2 import Timestamp

from frequenz.client.microgrid.sensor import SensorDiagnosticCode, SensorStateCode
from frequenz.client.microgrid.sensor._state_proto import (
    sensor_diagnostic_from_proto,
    sensor_state_snapshot_from_proto,
)


def test_sensor_diagnostic_from_proto() -> None:
    """Test converting SensorDiagnostic from proto."""
    proto = sensors_pb2.SensorDiagnostic(
        diagnostic_code=sensors_pb2.SENSOR_DIAGNOSTIC_CODE_INTERNAL,
        message="Internal error",
        vendor_diagnostic_code="VENDOR-001",
    )

    diag = sensor_diagnostic_from_proto(proto)

    assert diag.diagnostic_code == SensorDiagnosticCode.INTERNAL
    assert diag.message == "Internal error"
    assert diag.vendor_diagnostic_code == "VENDOR-001"


def test_sensor_diagnostic_from_proto_minimal() -> None:
    """Test converting minimal SensorDiagnostic from proto."""
    proto = sensors_pb2.SensorDiagnostic(
        diagnostic_code=sensors_pb2.SENSOR_DIAGNOSTIC_CODE_UNKNOWN,
    )

    diag = sensor_diagnostic_from_proto(proto)

    assert diag.diagnostic_code == SensorDiagnosticCode.UNKNOWN
    assert diag.message is None
    assert diag.vendor_diagnostic_code is None


def test_sensor_diagnostic_from_proto_empty_strings() -> None:
    """Test converting SensorDiagnostic with empty strings."""
    proto = sensors_pb2.SensorDiagnostic(
        diagnostic_code=sensors_pb2.SENSOR_DIAGNOSTIC_CODE_INTERNAL,
        message="",
        vendor_diagnostic_code="",
    )

    diag = sensor_diagnostic_from_proto(proto)

    assert diag.diagnostic_code == SensorDiagnosticCode.INTERNAL
    assert diag.message is None
    assert diag.vendor_diagnostic_code is None


def test_sensor_diagnostic_from_proto_unknown_code() -> None:
    """Test converting SensorDiagnostic with unknown diagnostic code."""
    proto = sensors_pb2.SensorDiagnostic(
        diagnostic_code=999,  # type: ignore[arg-type]
        message="Unknown error",
    )

    diag = sensor_diagnostic_from_proto(proto)

    assert diag.diagnostic_code == 999  # Preserved as int
    assert diag.message == "Unknown error"


def test_sensor_state_snapshot_from_proto() -> None:
    """Test converting SensorStateSnapshot from proto."""
    proto = sensors_pb2.SensorStateSnapshot()
    proto.origin_time.CopyFrom(Timestamp(seconds=1696118400))  # 2023-10-01T00:00:00Z
    proto.states.append(sensors_pb2.SENSOR_STATE_CODE_OK)
    proto.states.append(sensors_pb2.SENSOR_STATE_CODE_ERROR)

    warning = proto.warnings.add()
    warning.diagnostic_code = sensors_pb2.SENSOR_DIAGNOSTIC_CODE_UNKNOWN
    warning.message = "Warning message"

    error = proto.errors.add()
    error.diagnostic_code = sensors_pb2.SENSOR_DIAGNOSTIC_CODE_INTERNAL
    error.message = "Error message"

    snapshot = sensor_state_snapshot_from_proto(proto)

    assert snapshot.origin_time == datetime(2023, 10, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert SensorStateCode.OK in snapshot.states
    assert SensorStateCode.ERROR in snapshot.states
    assert len(snapshot.warnings) == 1
    warning_diag = next(iter(snapshot.warnings))
    assert warning_diag.diagnostic_code == SensorDiagnosticCode.UNKNOWN
    assert warning_diag.message == "Warning message"
    assert len(snapshot.errors) == 1
    error_diag = next(iter(snapshot.errors))
    assert error_diag.diagnostic_code == SensorDiagnosticCode.INTERNAL
    assert error_diag.message == "Error message"


def test_sensor_state_snapshot_from_proto_empty() -> None:
    """Test converting empty SensorStateSnapshot from proto."""
    proto = sensors_pb2.SensorStateSnapshot()
    proto.origin_time.CopyFrom(Timestamp(seconds=1696118400))
    # No states, warnings, or errors

    snapshot = sensor_state_snapshot_from_proto(proto)

    assert snapshot.origin_time == datetime(2023, 10, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert len(snapshot.states) == 0
    assert len(snapshot.warnings) == 0
    assert len(snapshot.errors) == 0


def test_sensor_state_snapshot_from_proto_unknown_state() -> None:
    """Test converting SensorStateSnapshot with unknown state codes."""
    proto = sensors_pb2.SensorStateSnapshot()
    proto.origin_time.CopyFrom(Timestamp(seconds=1696118400))
    proto.states.append(sensors_pb2.SENSOR_STATE_CODE_OK)
    proto.states.append(999)  # type: ignore[arg-type]

    snapshot = sensor_state_snapshot_from_proto(proto)

    assert SensorStateCode.OK in snapshot.states
    assert 999 in snapshot.states  # Preserved as int
    assert len(snapshot.states) == 2


def test_sensor_state_snapshot_from_proto_multiple_diagnostics() -> None:
    """Test converting SensorStateSnapshot with multiple diagnostics."""
    proto = sensors_pb2.SensorStateSnapshot()
    proto.origin_time.CopyFrom(Timestamp(seconds=1696118400))
    proto.states.append(sensors_pb2.SENSOR_STATE_CODE_ERROR)

    # Multiple warnings
    warning1 = proto.warnings.add()
    warning1.diagnostic_code = sensors_pb2.SENSOR_DIAGNOSTIC_CODE_UNKNOWN
    warning1.message = "Warning 1"

    warning2 = proto.warnings.add()
    warning2.diagnostic_code = sensors_pb2.SENSOR_DIAGNOSTIC_CODE_INTERNAL
    warning2.message = "Warning 2"

    # Multiple errors
    error1 = proto.errors.add()
    error1.diagnostic_code = sensors_pb2.SENSOR_DIAGNOSTIC_CODE_INTERNAL
    error1.message = "Error 1"

    error2 = proto.errors.add()
    error2.diagnostic_code = sensors_pb2.SENSOR_DIAGNOSTIC_CODE_UNKNOWN
    error2.message = "Error 2"

    snapshot = sensor_state_snapshot_from_proto(proto)

    assert len(snapshot.warnings) == 2
    assert len(snapshot.errors) == 2
    # Check that all messages are present
    warning_messages = {w.message for w in snapshot.warnings}
    assert "Warning 1" in warning_messages
    assert "Warning 2" in warning_messages
    error_messages = {e.message for e in snapshot.errors}
    assert "Error 1" in error_messages
    assert "Error 2" in error_messages
