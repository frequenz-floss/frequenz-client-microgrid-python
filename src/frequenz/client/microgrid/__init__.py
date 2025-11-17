# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Client to connect to the Microgrid API.

This package provides a low-level interface for interacting with the microgrid API.
"""


from ._client import (
    DEFAULT_CHANNEL_OPTIONS,
    DEFAULT_GRPC_CALL_TIMEOUT,
    MicrogridApiClient,
    Validity,
)
from ._delivery_area import DeliveryArea, EnergyMarketCodeType
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
from ._location import Location
from ._microgrid_info import MicrogridInfo, MicrogridStatus

__all__ = [
    "ApiClientError",
    "ClientNotConnected",
    "DEFAULT_CHANNEL_OPTIONS",
    "DEFAULT_GRPC_CALL_TIMEOUT",
    "DataLoss",
    "DeliveryArea",
    "EnergyMarketCodeType",
    "EntityAlreadyExists",
    "EntityNotFound",
    "GrpcError",
    "InternalError",
    "InvalidArgument",
    "Lifetime",
    "Location",
    "MicrogridApiClient",
    "MicrogridInfo",
    "MicrogridStatus",
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
    "Validity",
]
