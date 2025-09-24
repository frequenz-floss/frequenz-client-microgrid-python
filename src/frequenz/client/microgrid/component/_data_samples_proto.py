# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Loading of ComponentDataSamples objects from protobuf messages."""


import logging
from functools import partial

from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.client.common.microgrid.components import ComponentId

from ..metrics._sample_proto import metric_sample_from_proto_with_issues
from ._data_samples import ComponentDataSamples
from ._state_sample_proto import component_state_sample_from_proto

_logger = logging.getLogger(__name__)


def component_data_samples_from_proto(
    message: electrical_components_pb2.ElectricalComponentTelemetry,
) -> ComponentDataSamples:
    """Convert a protobuf component data message to a component data object.

    Args:
        message: The protobuf message to convert.

    Returns:
        The resulting `ComponentDataSamples` object.
    """
    major_issues: list[str] = []
    minor_issues: list[str] = []

    samples = component_data_samples_from_proto_with_issues(
        message, major_issues=major_issues, minor_issues=minor_issues
    )

    # This approach to logging issues might be too noisy. Samples are received
    # very often, and sometimes can remain unchanged for a long time, leading to
    # repeated log messages. We might need to adjust the logging strategy
    # in the future.
    if major_issues:
        _logger.warning(
            "Found issues in component data samples: %s | Protobuf message:\n%s",
            ", ".join(major_issues),
            message,
        )

    if minor_issues:
        _logger.debug(
            "Found minor issues in component data samples: %s | Protobuf message:\n%s",
            ", ".join(minor_issues),
            message,
        )

    return samples


def component_data_samples_from_proto_with_issues(
    message: electrical_components_pb2.ElectricalComponentTelemetry,
    *,
    major_issues: list[str],
    minor_issues: list[str],
) -> ComponentDataSamples:
    """Convert a protobuf component data message to a component data object collecting issues.

    Args:
        message: The protobuf message to convert.
        major_issues: A list to append major issues to.
        minor_issues: A list to append minor issues to.

    Returns:
        The resulting `ComponentDataSamples` object.
    """
    return ComponentDataSamples(
        component_id=ComponentId(message.electrical_component_id),
        metric_samples=list(
            map(
                partial(
                    metric_sample_from_proto_with_issues,
                    major_issues=major_issues,
                    minor_issues=minor_issues,
                ),
                message.metric_samples,
            )
        ),
        states=list(map(component_state_sample_from_proto, message.state_snapshots)),
    )
