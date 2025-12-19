# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for sensor state types."""

from collections.abc import Hashable
from datetime import datetime, timezone

import pytest

from frequenz.client.microgrid.sensor import (
    SensorDiagnostic,
    SensorDiagnosticCode,
    SensorStateCode,
    SensorStateSnapshot,
)


def test_sensor_diagnostic_creation_minimal() -> None:
    """Test SensorDiagnostic creation with minimal fields."""
    diag = SensorDiagnostic(diagnostic_code=SensorDiagnosticCode.INTERNAL)

    assert diag.diagnostic_code == SensorDiagnosticCode.INTERNAL
    assert diag.message is None
    assert diag.vendor_diagnostic_code is None


def test_sensor_diagnostic_creation_full() -> None:
    """Test SensorDiagnostic creation with all fields."""
    diag = SensorDiagnostic(
        diagnostic_code=SensorDiagnosticCode.INTERNAL,
        message="Internal sensor error occurred",
        vendor_diagnostic_code="ACME-ERR-001",
    )

    assert diag.diagnostic_code == SensorDiagnosticCode.INTERNAL
    assert diag.message == "Internal sensor error occurred"
    assert diag.vendor_diagnostic_code == "ACME-ERR-001"


def test_sensor_diagnostic_with_int_code() -> None:
    """Test SensorDiagnostic with integer diagnostic code."""
    diag = SensorDiagnostic(
        diagnostic_code=999,  # Custom vendor code
        message="Custom error",
    )

    assert diag.diagnostic_code == 999
    assert diag.message == "Custom error"


def test_sensor_diagnostic_equality() -> None:
    """Test SensorDiagnostic equality."""
    diag1 = SensorDiagnostic(
        diagnostic_code=SensorDiagnosticCode.INTERNAL,
        message="Error",
    )
    diag2 = SensorDiagnostic(
        diagnostic_code=SensorDiagnosticCode.INTERNAL,
        message="Error",
    )
    diag3 = SensorDiagnostic(
        diagnostic_code=SensorDiagnosticCode.UNKNOWN,
        message="Error",
    )

    assert diag1 == diag2
    assert diag1 != diag3


def test_sensor_diagnostic_hash() -> None:
    """Test SensorDiagnostic hashing for use in sets."""
    diag1 = SensorDiagnostic(diagnostic_code=SensorDiagnosticCode.INTERNAL)
    diag2 = SensorDiagnostic(diagnostic_code=SensorDiagnosticCode.INTERNAL)
    diag3 = SensorDiagnostic(diagnostic_code=SensorDiagnosticCode.UNKNOWN)

    assert hash(diag1) == hash(diag2)
    diag_set = {diag1, diag2, diag3}
    assert len(diag_set) == 2


def test_sensor_state_snapshot_creation() -> None:
    """Test SensorStateSnapshot creation."""
    now = datetime.now(timezone.utc)
    warning1 = SensorDiagnostic(
        diagnostic_code=SensorDiagnosticCode.UNKNOWN,
        message="Minor issue",
    )
    error1 = SensorDiagnostic(
        diagnostic_code=SensorDiagnosticCode.INTERNAL,
        message="Critical issue",
    )

    snapshot = SensorStateSnapshot(
        origin_time=now,
        states=frozenset([SensorStateCode.OK, SensorStateCode.ERROR]),
        warnings=[warning1],
        errors=[error1],
    )

    assert snapshot.origin_time == now
    assert SensorStateCode.OK in snapshot.states
    assert SensorStateCode.ERROR in snapshot.states
    assert len(snapshot.warnings) == 1
    assert warning1 in snapshot.warnings
    assert len(snapshot.errors) == 1
    assert error1 in snapshot.errors


def test_sensor_state_snapshot_empty_diagnostics() -> None:
    """Test SensorStateSnapshot with empty diagnostics."""
    now = datetime.now(timezone.utc)

    snapshot = SensorStateSnapshot(
        origin_time=now,
        states=frozenset([SensorStateCode.OK]),
        warnings=(),
        errors=(),
    )

    assert snapshot.origin_time == now
    assert len(snapshot.states) == 1
    assert len(snapshot.warnings) == 0
    assert len(snapshot.errors) == 0


def test_sensor_state_snapshot_with_int_states() -> None:
    """Test SensorStateSnapshot with integer state codes."""
    now = datetime.now(timezone.utc)

    snapshot = SensorStateSnapshot(
        origin_time=now,
        states=frozenset([1, 999]),  # Mix of enum value and custom code
        warnings=(),
        errors=(),
    )

    assert 1 in snapshot.states  # SensorStateCode.OK
    assert 999 in snapshot.states  # Custom state code


def test_sensor_state_snapshot_equality() -> None:
    """Test SensorStateSnapshot equality."""
    now = datetime.now(timezone.utc)
    diag = SensorDiagnostic(diagnostic_code=SensorDiagnosticCode.INTERNAL)

    snapshot1 = SensorStateSnapshot(
        origin_time=now,
        states=frozenset([SensorStateCode.OK]),
        warnings=[diag],
        errors=(),
    )
    snapshot2 = SensorStateSnapshot(
        origin_time=now,
        states=frozenset([SensorStateCode.OK]),
        warnings=[diag],
        errors=(),
    )

    assert snapshot1 == snapshot2


def test_sensor_state_snapshot_immutable() -> None:
    """Test that SensorStateSnapshot is immutable."""
    now = datetime.now(timezone.utc)
    snapshot = SensorStateSnapshot(
        origin_time=now,
        states=frozenset([SensorStateCode.OK]),
        warnings=(),
        errors=(),
    )

    # Should not be able to modify frozen dataclass
    with pytest.raises(AttributeError):
        snapshot.origin_time = datetime.now(timezone.utc)  # type: ignore[misc]


def test_sensor_state_snapshot_not_hashable() -> None:
    """Test that SensorStateSnapshot is not hashable."""
    now = datetime.now(timezone.utc)
    snapshot = SensorStateSnapshot(
        origin_time=now,
        states=frozenset([SensorStateCode.OK]),
        warnings=(),
        errors=(),
    )

    # Should not be able to modify frozen dataclass
    with pytest.raises(TypeError):
        _ = hash(snapshot)

    assert not isinstance(snapshot, Hashable)


def test_sensor_diagnostic_immutable() -> None:
    """Test that SensorDiagnostic is immutable."""
    diag = SensorDiagnostic(diagnostic_code=SensorDiagnosticCode.INTERNAL)

    # Should not be able to modify frozen dataclass
    with pytest.raises(AttributeError):
        diag.message = "new message"  # type: ignore[misc]
