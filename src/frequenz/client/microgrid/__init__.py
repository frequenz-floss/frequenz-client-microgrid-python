# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Client to connect to the Microgrid API.

This package provides a low-level interface for interacting with the microgrid API.
"""


from ._client import MicrogridApiClient
from ._component import (
    Component,
    ComponentCategory,
    ComponentMetadata,
    ComponentMetricId,
    ComponentType,
    Fuse,
    GridMetadata,
    InverterType,
)
from ._component_data import (
    BatteryData,
    ComponentData,
    EVChargerData,
    InverterData,
    MeterData,
)
from ._component_error import (
    BatteryError,
    BatteryErrorCode,
    ErrorLevel,
    InverterError,
    InverterErrorCode,
)
from ._component_states import (
    BatteryComponentState,
    BatteryRelayState,
    EVChargerCableState,
    EVChargerComponentState,
    InverterComponentState,
)
from ._connection import Connection
from ._exception import (
    ApiClientError,
    ClientNotConnected,
    DataLoss,
    EntityAlreadyExists,
    EntityNotFound,
    GrpcError,
    InternalError,
    InvalidArgument,
    OperationAborted,
    OperationCancelled,
    OperationNotImplemented,
    OperationOutOfRange,
    OperationPreconditionFailed,
    OperationTimedOut,
    OperationUnauthenticated,
    PermissionDenied,
    ResourceExhausted,
    ServiceUnavailable,
    UnknownError,
    UnrecognizedGrpcStatus,
)
from ._lifetime import Lifetime
from ._metadata import Location, Metadata

__all__ = [
    "ApiClientError",
    "BatteryComponentState",
    "BatteryData",
    "BatteryError",
    "BatteryErrorCode",
    "BatteryRelayState",
    "ClientNotConnected",
    "Component",
    "ComponentCategory",
    "ComponentData",
    "ComponentMetadata",
    "ComponentMetricId",
    "ComponentType",
    "Connection",
    "DataLoss",
    "EVChargerCableState",
    "EVChargerComponentState",
    "EVChargerData",
    "EntityAlreadyExists",
    "EntityNotFound",
    "ErrorLevel",
    "Fuse",
    "GridMetadata",
    "GrpcError",
    "InternalError",
    "InvalidArgument",
    "InverterComponentState",
    "InverterData",
    "InverterError",
    "InverterErrorCode",
    "InverterType",
    "Lifetime",
    "Location",
    "Metadata",
    "MeterData",
    "MicrogridApiClient",
    "OperationAborted",
    "OperationCancelled",
    "OperationNotImplemented",
    "OperationOutOfRange",
    "OperationPreconditionFailed",
    "OperationTimedOut",
    "OperationUnauthenticated",
    "PermissionDenied",
    "ResourceExhausted",
    "ServiceUnavailable",
    "UnknownError",
    "UnrecognizedGrpcStatus",
]
