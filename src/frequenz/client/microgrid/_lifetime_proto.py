# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Loading of Lifetime objects from protobuf messages."""

from frequenz.api.common.v1alpha8.microgrid import lifetime_pb2
from frequenz.client.base.conversion import to_datetime

from ._lifetime import Lifetime


def lifetime_from_proto(
    message: lifetime_pb2.Lifetime,
) -> Lifetime:
    """Create a [`Lifetime`][frequenz.client.microgrid.Lifetime] from a protobuf message."""
    start = (
        to_datetime(message.start_timestamp)
        if message.HasField("start_timestamp")
        else None
    )
    end = (
        to_datetime(message.end_timestamp)
        if message.HasField("end_timestamp")
        else None
    )
    return Lifetime(start=start, end=end)
