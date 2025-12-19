# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Proto conversion for sensor state types."""

from datetime import timezone

from frequenz.api.common.v1alpha8.microgrid.sensors import sensors_pb2
from frequenz.client.base.conversion import to_datetime

from ._state import (
    SensorDiagnostic,
    SensorDiagnosticCode,
    SensorStateCode,
    SensorStateSnapshot,
)


def sensor_diagnostic_from_proto(
    proto: sensors_pb2.SensorDiagnostic,
) -> SensorDiagnostic:
    """Convert a proto SensorDiagnostic to a SensorDiagnostic.

    Args:
        proto: The proto SensorDiagnostic to convert.

    Returns:
        The converted SensorDiagnostic.
    """
    diagnostic_code: SensorDiagnosticCode | int = proto.diagnostic_code
    try:
        diagnostic_code = SensorDiagnosticCode(diagnostic_code)
    except ValueError:
        pass  # Keep as int if unrecognized

    return SensorDiagnostic(
        diagnostic_code=diagnostic_code,
        message=proto.message if proto.message else None,
        vendor_diagnostic_code=(
            proto.vendor_diagnostic_code if proto.vendor_diagnostic_code else None
        ),
    )


def sensor_state_snapshot_from_proto(
    proto: sensors_pb2.SensorStateSnapshot,
) -> SensorStateSnapshot:
    """Convert a proto SensorStateSnapshot to a SensorStateSnapshot.

    Args:
        proto: The proto SensorStateSnapshot to convert.

    Returns:
        The converted SensorStateSnapshot.
    """
    # Convert states
    states = frozenset(
        (
            SensorStateCode(int(state))
            if int(state) in [s.value for s in SensorStateCode]
            else int(state)
        )
        for state in proto.states
    )

    # Convert warnings and errors
    warnings = [sensor_diagnostic_from_proto(w) for w in proto.warnings]
    errors = [sensor_diagnostic_from_proto(e) for e in proto.errors]

    return SensorStateSnapshot(
        origin_time=to_datetime(proto.origin_time).replace(tzinfo=timezone.utc),
        states=states,
        warnings=warnings,
        errors=errors,
    )
