# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Definition of component states."""

from dataclasses import dataclass
from datetime import datetime

from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.core import enum


@enum.unique
class ComponentStateCode(enum.Enum):
    """The various states that a component can be in."""

    UNSPECIFIED = electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_UNSPECIFIED
    """The state is unspecified (this should not be normally used)."""

    UNKNOWN = electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_UNKNOWN
    """The component is in an unknown or undefined condition.

    This is used when the state can be retrieved from the component but it doesn't match
    any known state.
    """

    UNAVAILABLE = electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_UNAVAILABLE
    """The component is temporarily unavailable for operation."""

    SWITCHING_OFF = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_SWITCHING_OFF
    )
    """The component is in the process of switching off."""

    OFF = electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_OFF
    """The component has successfully switched off."""

    SWITCHING_ON = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_SWITCHING_ON
    )
    """The component is in the process of switching on."""

    STANDBY = electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_STANDBY
    """The component is in standby mode and not immediately ready for operation."""

    READY = electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_READY
    """The component is fully operational and ready for use."""

    CHARGING = electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_CHARGING
    """The component is actively consuming energy."""

    DISCHARGING = electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_DISCHARGING
    """The component is actively producing or releasing energy."""

    ERROR = electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_ERROR
    """The component is in an error state and may need attention."""

    EV_CHARGING_CABLE_UNPLUGGED = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_EV_CHARGING_CABLE_UNPLUGGED
    )
    """The EV charging cable is unplugged from the charging station."""

    EV_CHARGING_CABLE_PLUGGED_AT_STATION = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_EV_CHARGING_CABLE_PLUGGED_AT_STATION  # noqa: E501
    )
    """The EV charging cable is plugged into the charging station."""

    EV_CHARGING_CABLE_PLUGGED_AT_EV = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_EV_CHARGING_CABLE_PLUGGED_AT_EV
    )
    """The EV charging cable is plugged into the vehicle."""

    EV_CHARGING_CABLE_LOCKED_AT_STATION = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_EV_CHARGING_CABLE_LOCKED_AT_STATION  # noqa: E501
    )
    """The EV charging cable is locked at the charging station end."""

    EV_CHARGING_CABLE_LOCKED_AT_EV = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_EV_CHARGING_CABLE_LOCKED_AT_EV
    )
    """The EV charging cable is locked at the vehicle end."""

    RELAY_OPEN = electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_RELAY_OPEN
    """The relay is in an open state, meaning no current can flow through."""

    RELAY_CLOSED = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_RELAY_CLOSED
    )
    """The relay is in a closed state, allowing current to flow."""

    PRECHARGER_OPEN = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_PRECHARGER_OPEN
    )
    """The precharger circuit is open, meaning it's not currently active."""

    PRECHARGER_PRECHARGING = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_PRECHARGER_PRECHARGING
    )
    """The precharger is in a precharging state, preparing the main circuit for activation."""

    PRECHARGER_CLOSED = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_STATE_CODE_PRECHARGER_CLOSED
    )
    """The precharger circuit is closed, allowing full current to flow to the main circuit."""


@enum.unique
class ComponentErrorCode(enum.Enum):
    """The various errors that a component can report."""

    UNSPECIFIED = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_UNSPECIFIED
    )
    """The error is unspecified (this should not be normally used)."""

    UNKNOWN = electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_UNKNOWN
    """The component is reporting an unknown or undefined error.

    This is used when the error can be retrieved from the component but it doesn't match
    any known error.
    """

    SWITCH_ON_FAULT = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_SWITCH_ON_FAULT
    )
    """The component could not be switched on."""

    UNDERVOLTAGE = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_UNDERVOLTAGE
    )
    """The component is operating under the minimum rated voltage."""

    OVERVOLTAGE = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_OVERVOLTAGE
    )
    """The component is operating over the maximum rated voltage."""

    OVERCURRENT = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_OVERCURRENT
    )
    """The component is drawing more current than the maximum rated value."""

    OVERCURRENT_CHARGING = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_OVERCURRENT_CHARGING
    )
    """The component's consumption current is over the maximum rated value during charging."""

    OVERCURRENT_DISCHARGING = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_OVERCURRENT_DISCHARGING
    )
    """The component's production current is over the maximum rated value during discharging."""

    OVERTEMPERATURE = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_OVERTEMPERATURE
    )
    """The component is operating over the maximum rated temperature."""

    UNDERTEMPERATURE = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_UNDERTEMPERATURE
    )
    """The component is operating under the minimum rated temperature."""

    HIGH_HUMIDITY = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_HIGH_HUMIDITY
    )
    """The component is exposed to high humidity levels over the maximum rated value."""

    FUSE_ERROR = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_FUSE_ERROR
    )
    """The component's fuse has blown."""

    PRECHARGE_ERROR = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_PRECHARGE_ERROR
    )
    """The component's precharge unit has failed."""

    PLAUSIBILITY_ERROR = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_PLAUSIBILITY_ERROR
    )
    """Plausibility issues within the system involving this component."""

    UNDERVOLTAGE_SHUTDOWN = enum.deprecated_member(
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_UNDERVOLTAGE,
        "UNDERVOLTAGE_SHUTDOWN is deprecated, use UNDERVOLTAGE instead",
    )
    """System shutdown due to undervoltage involving this component.

    Deprecated: Deprecated in v0.18.0
        Use
        [`UNDERVOLTAGE`][frequenz.client.microgrid.component.ComponentErrorCode.UNDERVOLTAGE]
        instead.
    """

    EV_UNEXPECTED_PILOT_FAILURE = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_EV_UNEXPECTED_PILOT_FAILURE
    )
    """Unexpected pilot failure in an electric vehicle component."""

    FAULT_CURRENT = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_FAULT_CURRENT
    )
    """Fault current detected in the component."""

    SHORT_CIRCUIT = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_SHORT_CIRCUIT
    )
    """Short circuit detected in the component."""

    CONFIG_ERROR = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_CONFIG_ERROR
    )
    """Configuration error related to the component."""

    ILLEGAL_ELECTRICAL_COMPONENT_STATE_CODE_REQUESTED = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_ILLEGAL_COMPONENT_STATE_CODE_REQUESTED  # noqa: E501
    )
    """Illegal state requested for the component."""

    HARDWARE_INACCESSIBLE = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_HARDWARE_INACCESSIBLE
    )
    """Hardware of the component is inaccessible."""

    INTERNAL = electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_INTERNAL
    """Internal error within the component."""

    UNAUTHORIZED = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_UNAUTHORIZED
    )
    """The component is unauthorized to perform the last requested action."""

    EV_CHARGING_CABLE_UNPLUGGED_FROM_STATION = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_EV_CHARGING_CABLE_UNPLUGGED_FROM_STATION  # noqa: E501
    )
    """EV cable was abruptly unplugged from the charging station."""

    EV_CHARGING_CABLE_UNPLUGGED_FROM_EV = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_EV_CHARGING_CABLE_UNPLUGGED_FROM_EV  # noqa: E501
    )
    """EV cable was abruptly unplugged from the vehicle."""

    EV_CHARGING_CABLE_LOCK_FAILED = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_EV_CHARGING_CABLE_LOCK_FAILED
    )
    """EV cable lock failure."""

    EV_CHARGING_CABLE_INVALID = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_EV_CHARGING_CABLE_INVALID
    )
    """Invalid EV cable."""

    EV_CONSUMER_INCOMPATIBLE = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_EV_CONSUMER_INCOMPATIBLE
    )
    """Incompatible EV plug."""

    BATTERY_IMBALANCE = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_BATTERY_IMBALANCE
    )
    """Battery system imbalance."""

    BATTERY_LOW_SOH = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_BATTERY_LOW_SOH
    )
    """Low state of health (SOH) detected in the battery."""

    BATTERY_BLOCK_ERROR = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_BATTERY_BLOCK_ERROR
    )
    """Battery block error."""

    BATTERY_CONTROLLER_ERROR = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_BATTERY_CONTROLLER_ERROR
    )
    """Battery controller error."""

    BATTERY_RELAY_ERROR = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_BATTERY_RELAY_ERROR
    )
    """Battery relay error."""

    BATTERY_CALIBRATION_NEEDED = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_BATTERY_CALIBRATION_NEEDED
    )
    """Battery calibration is needed."""

    RELAY_CYCLE_LIMIT_REACHED = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_RELAY_CYCLE_LIMIT_REACHED
    )
    """Relays have been cycled for the maximum number of times."""


@dataclass(frozen=True, kw_only=True)
class ComponentStateSample:
    """A collection of the state, warnings, and errors for a component at a specific time."""

    sampled_at: datetime
    """The time at which this state was sampled."""

    states: frozenset[ComponentStateCode | int]
    """The set of states of the component.

    If the reported state is not known by the client (it could happen when using an
    older version of the client with a newer version of the server), it will be
    represented as an `int` and **not** the
    [`ComponentStateCode.UNKNOWN`][frequenz.client.microgrid.component.ComponentStateCode.UNKNOWN]
    value (this value is used only when the state is not known by the server).
    """

    warnings: frozenset[ComponentErrorCode | int]
    """The set of warnings for the component."""

    errors: frozenset[ComponentErrorCode | int]
    """The set of errors for the component.

    This set will only contain errors if the component is in an error state.
    """
