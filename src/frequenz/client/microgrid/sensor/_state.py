# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Sensor state-related types."""

import enum
from collections.abc import Sequence, Set
from dataclasses import dataclass
from datetime import datetime


@enum.unique
class SensorStateCode(enum.Enum):
    """Sensor state code.

    Represents the operational state of a sensor.
    """

    UNSPECIFIED = 0
    """Unspecified state."""

    OK = 1
    """Sensor is operating normally."""

    ERROR = 2
    """Sensor is in an error state."""


@enum.unique
class SensorDiagnosticCode(enum.Enum):
    """Sensor diagnostic code.

    Provides additional diagnostic information about warnings or errors.
    """

    UNSPECIFIED = 0
    """Unspecified diagnostic code."""

    UNKNOWN = 1
    """Unknown diagnostic issue."""

    INTERNAL = 2
    """Internal sensor error."""


@dataclass(frozen=True, kw_only=True)
class SensorDiagnostic:
    """Diagnostic information for a sensor warning or error.

    Provides detailed information about issues affecting a sensor.
    """

    diagnostic_code: SensorDiagnosticCode | int
    """The diagnostic code identifying the type of issue."""

    message: str | None = None
    """Optional human-readable message describing the issue."""

    vendor_diagnostic_code: str | None = None
    """Optional vendor-specific diagnostic code."""


@dataclass(frozen=True, kw_only=True)
class SensorStateSnapshot:
    """A snapshot of a sensor's operational state at a specific time.

    Contains the sensor's state codes and any associated diagnostic information.
    """

    origin_time: datetime
    """The timestamp when this state snapshot was recorded."""

    states: Set[SensorStateCode | int]
    """Set of state codes active at the snapshot time."""

    warnings: Sequence[SensorDiagnostic]
    """Sequence of active warnings with diagnostic information."""

    errors: Sequence[SensorDiagnostic]
    """Sequence of active errors with diagnostic information."""

    # Disable hashing for this class (mypy doesn't seem to understand assigining to
    # None, but it is documented in __hash__ docs).
    __hash__ = None  # type: ignore[assignment]
