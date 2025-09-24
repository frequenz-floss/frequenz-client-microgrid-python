# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Loading of Bounds objects from protobuf messages."""


from frequenz.api.common.v1alpha8.metrics import bounds_pb2

from ._bounds import Bounds


def bounds_from_proto(message: bounds_pb2.Bounds) -> Bounds:
    """Create a `Bounds` from a protobuf message."""
    return Bounds(
        lower=message.lower if message.HasField("lower") else None,
        upper=message.upper if message.HasField("upper") else None,
    )
