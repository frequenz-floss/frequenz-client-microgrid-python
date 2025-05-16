# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Client to connect to the Microgrid API.

This package provides a low-level interface for interacting with the microgrid API.
"""


from ._client import MicrogridApiClient
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

__all__ = [
    "ApiClientError",
    "ClientNotConnected",
    "DataLoss",
    "DeliveryArea",
    "EnergyMarketCodeType",
    "EntityAlreadyExists",
    "EntityNotFound",
    "GrpcError",
    "InternalError",
    "InvalidArgument",
    "Lifetime",
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
