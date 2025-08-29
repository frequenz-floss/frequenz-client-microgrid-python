# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Definition of component states."""

import enum
from dataclasses import dataclass
from datetime import datetime

from frequenz.api.common.v1.microgrid.components import components_pb2


@enum.unique
class ComponentStateCode(enum.Enum):
    """The various states that a component can be in."""

    UNSPECIFIED = components_pb2.COMPONENT_STATE_CODE_UNSPECIFIED
    """The state is unspecified (this should not be normally used)."""

    UNKNOWN = components_pb2.COMPONENT_STATE_CODE_UNKNOWN
    """The component is in an unknown or undefined condition.

    This is used when the state can be retrieved from the component but it doesn't match
    any known state.
    """

    UNAVAILABLE = components_pb2.COMPONENT_STATE_CODE_UNAVAILABLE
    """The component is temporarily unavailable for operation."""

    SWITCHING_OFF = components_pb2.COMPONENT_STATE_CODE_SWITCHING_OFF
    """The component is in the process of switching off."""

    OFF = components_pb2.COMPONENT_STATE_CODE_OFF
    """The component has successfully switched off."""

    SWITCHING_ON = components_pb2.COMPONENT_STATE_CODE_SWITCHING_ON
    """The component is in the process of switching on."""

    STANDBY = components_pb2.COMPONENT_STATE_CODE_STANDBY
    """The component is in standby mode and not immediately ready for operation."""

    READY = components_pb2.COMPONENT_STATE_CODE_READY
    """The component is fully operational and ready for use."""

    CHARGING = components_pb2.COMPONENT_STATE_CODE_CHARGING
    """The component is actively consuming energy."""

    DISCHARGING = components_pb2.COMPONENT_STATE_CODE_DISCHARGING
    """The component is actively producing or releasing energy."""

    ERROR = components_pb2.COMPONENT_STATE_CODE_ERROR
    """The component is in an error state and may need attention."""

    EV_CHARGING_CABLE_UNPLUGGED = (
        components_pb2.COMPONENT_STATE_CODE_EV_CHARGING_CABLE_UNPLUGGED
    )
    """The EV charging cable is unplugged from the charging station."""

    EV_CHARGING_CABLE_PLUGGED_AT_STATION = (
        components_pb2.COMPONENT_STATE_CODE_EV_CHARGING_CABLE_PLUGGED_AT_STATION
    )
    """The EV charging cable is plugged into the charging station."""

    EV_CHARGING_CABLE_PLUGGED_AT_EV = (
        components_pb2.COMPONENT_STATE_CODE_EV_CHARGING_CABLE_PLUGGED_AT_EV
    )
    """The EV charging cable is plugged into the vehicle."""

    EV_CHARGING_CABLE_LOCKED_AT_STATION = (
        components_pb2.COMPONENT_STATE_CODE_EV_CHARGING_CABLE_LOCKED_AT_STATION
    )
    """The EV charging cable is locked at the charging station end."""

    EV_CHARGING_CABLE_LOCKED_AT_EV = (
        components_pb2.COMPONENT_STATE_CODE_EV_CHARGING_CABLE_LOCKED_AT_EV
    )
    """The EV charging cable is locked at the vehicle end."""

    RELAY_OPEN = components_pb2.COMPONENT_STATE_CODE_RELAY_OPEN
    """The relay is in an open state, meaning no current can flow through."""

    RELAY_CLOSED = components_pb2.COMPONENT_STATE_CODE_RELAY_CLOSED
    """The relay is in a closed state, allowing current to flow."""

    PRECHARGER_OPEN = components_pb2.COMPONENT_STATE_CODE_PRECHARGER_OPEN
    """The precharger circuit is open, meaning it's not currently active."""

    PRECHARGER_PRECHARGING = components_pb2.COMPONENT_STATE_CODE_PRECHARGER_PRECHARGING
    """The precharger is in a precharging state, preparing the main circuit for activation."""

    PRECHARGER_CLOSED = components_pb2.COMPONENT_STATE_CODE_PRECHARGER_CLOSED
    """The precharger circuit is closed, allowing full current to flow to the main circuit."""


@enum.unique
class ComponentErrorCode(enum.Enum):
    """The various errors that a component can report."""

    UNSPECIFIED = components_pb2.COMPONENT_ERROR_CODE_UNSPECIFIED
    """The error is unspecified (this should not be normally used)."""

    UNKNOWN = components_pb2.COMPONENT_ERROR_CODE_UNKNOWN
    """The component is reporting an unknown or undefined error.

    This is used when the error can be retrieved from the component but it doesn't match
    any known error.
    """

    SWITCH_ON_FAULT = components_pb2.COMPONENT_ERROR_CODE_SWITCH_ON_FAULT
    """The component could not be switched on."""

    UNDERVOLTAGE = components_pb2.COMPONENT_ERROR_CODE_UNDERVOLTAGE
    """The component is operating under the minimum rated voltage."""

    OVERVOLTAGE = components_pb2.COMPONENT_ERROR_CODE_OVERVOLTAGE
    """The component is operating over the maximum rated voltage."""

    OVERCURRENT = components_pb2.COMPONENT_ERROR_CODE_OVERCURRENT
    """The component is drawing more current than the maximum rated value."""

    OVERCURRENT_CHARGING = components_pb2.COMPONENT_ERROR_CODE_OVERCURRENT_CHARGING
    """The component's consumption current is over the maximum rated value during charging."""

    OVERCURRENT_DISCHARGING = (
        components_pb2.COMPONENT_ERROR_CODE_OVERCURRENT_DISCHARGING
    )
    """The component's production current is over the maximum rated value during discharging."""

    OVERTEMPERATURE = components_pb2.COMPONENT_ERROR_CODE_OVERTEMPERATURE
    """The component is operating over the maximum rated temperature."""

    UNDERTEMPERATURE = components_pb2.COMPONENT_ERROR_CODE_UNDERTEMPERATURE
    """The component is operating under the minimum rated temperature."""

    HIGH_HUMIDITY = components_pb2.COMPONENT_ERROR_CODE_HIGH_HUMIDITY
    """The component is exposed to high humidity levels over the maximum rated value."""

    FUSE_ERROR = components_pb2.COMPONENT_ERROR_CODE_FUSE_ERROR
    """The component's fuse has blown."""

    PRECHARGE_ERROR = components_pb2.COMPONENT_ERROR_CODE_PRECHARGE_ERROR
    """The component's precharge unit has failed."""

    PLAUSIBILITY_ERROR = components_pb2.COMPONENT_ERROR_CODE_PLAUSIBILITY_ERROR
    """Plausibility issues within the system involving this component."""

    UNDERVOLTAGE_SHUTDOWN = components_pb2.COMPONENT_ERROR_CODE_UNDERVOLTAGE_SHUTDOWN
    """System shutdown due to undervoltage involving this component."""

    EV_UNEXPECTED_PILOT_FAILURE = (
        components_pb2.COMPONENT_ERROR_CODE_EV_UNEXPECTED_PILOT_FAILURE
    )
    """Unexpected pilot failure in an electric vehicle component."""

    FAULT_CURRENT = components_pb2.COMPONENT_ERROR_CODE_FAULT_CURRENT
    """Fault current detected in the component."""

    SHORT_CIRCUIT = components_pb2.COMPONENT_ERROR_CODE_SHORT_CIRCUIT
    """Short circuit detected in the component."""

    CONFIG_ERROR = components_pb2.COMPONENT_ERROR_CODE_CONFIG_ERROR
    """Configuration error related to the component."""

    ILLEGAL_COMPONENT_STATE_CODE_REQUESTED = (
        components_pb2.COMPONENT_ERROR_CODE_ILLEGAL_COMPONENT_STATE_CODE_REQUESTED
    )
    """Illegal state requested for the component."""

    HARDWARE_INACCESSIBLE = components_pb2.COMPONENT_ERROR_CODE_HARDWARE_INACCESSIBLE
    """Hardware of the component is inaccessible."""

    INTERNAL = components_pb2.COMPONENT_ERROR_CODE_INTERNAL
    """Internal error within the component."""

    UNAUTHORIZED = components_pb2.COMPONENT_ERROR_CODE_UNAUTHORIZED
    """The component is unauthorized to perform the last requested action."""

    EV_CHARGING_CABLE_UNPLUGGED_FROM_STATION = (
        components_pb2.COMPONENT_ERROR_CODE_EV_CHARGING_CABLE_UNPLUGGED_FROM_STATION
    )
    """EV cable was abruptly unplugged from the charging station."""

    EV_CHARGING_CABLE_UNPLUGGED_FROM_EV = (
        components_pb2.COMPONENT_ERROR_CODE_EV_CHARGING_CABLE_UNPLUGGED_FROM_EV
    )
    """EV cable was abruptly unplugged from the vehicle."""

    EV_CHARGING_CABLE_LOCK_FAILED = (
        components_pb2.COMPONENT_ERROR_CODE_EV_CHARGING_CABLE_LOCK_FAILED
    )
    """EV cable lock failure."""

    EV_CHARGING_CABLE_INVALID = (
        components_pb2.COMPONENT_ERROR_CODE_EV_CHARGING_CABLE_INVALID
    )
    """Invalid EV cable."""

    EV_CONSUMER_INCOMPATIBLE = (
        components_pb2.COMPONENT_ERROR_CODE_EV_CONSUMER_INCOMPATIBLE
    )
    """Incompatible EV plug."""

    BATTERY_IMBALANCE = components_pb2.COMPONENT_ERROR_CODE_BATTERY_IMBALANCE
    """Battery system imbalance."""

    BATTERY_LOW_SOH = components_pb2.COMPONENT_ERROR_CODE_BATTERY_LOW_SOH
    """Low state of health (SOH) detected in the battery."""

    BATTERY_BLOCK_ERROR = components_pb2.COMPONENT_ERROR_CODE_BATTERY_BLOCK_ERROR
    """Battery block error."""

    BATTERY_CONTROLLER_ERROR = (
        components_pb2.COMPONENT_ERROR_CODE_BATTERY_CONTROLLER_ERROR
    )
    """Battery controller error."""

    BATTERY_RELAY_ERROR = components_pb2.COMPONENT_ERROR_CODE_BATTERY_RELAY_ERROR
    """Battery relay error."""

    BATTERY_CALIBRATION_NEEDED = (
        components_pb2.COMPONENT_ERROR_CODE_BATTERY_CALIBRATION_NEEDED
    )
    """Battery calibration is needed."""

    RELAY_CYCLE_LIMIT_REACHED = (
        components_pb2.COMPONENT_ERROR_CODE_RELAY_CYCLE_LIMIT_REACHED
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
