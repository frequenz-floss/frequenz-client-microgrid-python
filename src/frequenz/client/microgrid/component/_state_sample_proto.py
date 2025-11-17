# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Loading of MetricSample and AggregatedMetricValue objects from protobuf messages."""

from functools import partial

from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.client.base import conversion

from .._util import enum_from_proto
from ._state_sample import ComponentErrorCode, ComponentStateCode, ComponentStateSample

_state_from_proto = partial(enum_from_proto, enum_type=ComponentStateCode)
_error_from_proto = partial(enum_from_proto, enum_type=ComponentErrorCode)


def component_state_sample_from_proto(
    message: electrical_components_pb2.ElectricalComponentStateSnapshot,
) -> ComponentStateSample:
    """Convert a protobuf message to a `ComponentStateSample` object.

    Args:
        message: The protobuf message to convert.

    Returns:
        The resulting `ComponentStateSample` object.
    """
    return ComponentStateSample(
        sampled_at=conversion.to_datetime(message.origin_time),
        states=frozenset(map(_state_from_proto, message.states)),
        # pylint: disable-next=fixme
        # TODO: Wrap the full diagnostic object.
        warnings=frozenset(
            map(_error_from_proto, (w.diagnostic_code for w in message.warnings))
        ),
        errors=frozenset(
            map(_error_from_proto, (e.diagnostic_code for e in message.errors))
        ),
    )
