# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Definition of a component data aggregate."""

from dataclasses import dataclass

from frequenz.client.common.microgrid.components import ComponentId

from ..metrics._sample import MetricSample
from ._state_sample import ComponentStateSample


@dataclass(frozen=True, kw_only=True)
class ComponentDataSamples:
    """An aggregate of multiple metrics, states, and errors of a component."""

    component_id: ComponentId
    """The unique identifier of the component."""

    metric_samples: list[MetricSample]
    """The metrics sampled from the component."""

    states: list[ComponentStateSample]
    """The states sampled from the component."""
