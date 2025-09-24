# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Fixtures and utilities for testing component protobuf conversion."""

from datetime import datetime, timezone

import pytest
from frequenz.api.common.v1alpha8.metrics import bounds_pb2
from frequenz.api.common.v1alpha8.microgrid import lifetime_pb2
from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.client.base.conversion import to_timestamp
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.components import ComponentId
from google.protobuf.timestamp_pb2 import Timestamp

from frequenz.client.microgrid import Lifetime
from frequenz.client.microgrid.component import Component, ComponentCategory
from frequenz.client.microgrid.component._component_proto import ComponentBaseData
from frequenz.client.microgrid.metrics import Bounds, Metric

DEFAULT_LIFETIME = Lifetime(
    start=datetime(2020, 1, 1, tzinfo=timezone.utc),
    end=datetime(2030, 1, 1, tzinfo=timezone.utc),
)
DEFAULT_COMPONENT_ID = ComponentId(42)
DEFAULT_MICROGRID_ID = MicrogridId(1)
DEFAULT_NAME = "test_component"
DEFAULT_MANUFACTURER = "test_manufacturer"
DEFAULT_MODEL_NAME = "test_model"


@pytest.fixture
def component_id() -> ComponentId:
    """Provide a test component ID."""
    return DEFAULT_COMPONENT_ID


@pytest.fixture
def microgrid_id() -> MicrogridId:
    """Provide a test microgrid ID."""
    return DEFAULT_MICROGRID_ID


@pytest.fixture
def default_component_base_data(
    component_id: ComponentId, microgrid_id: MicrogridId
) -> ComponentBaseData:
    """Provide a fixture for common component fields."""
    return ComponentBaseData(
        component_id=component_id,
        microgrid_id=microgrid_id,
        name=DEFAULT_NAME,
        manufacturer=DEFAULT_MANUFACTURER,
        model_name=DEFAULT_MODEL_NAME,
        category=ComponentCategory.UNSPECIFIED,
        lifetime=DEFAULT_LIFETIME,
        rated_bounds={Metric.AC_ACTIVE_ENERGY: Bounds(lower=0, upper=100)},
        category_specific_info={},
        category_mismatched=False,
    )


def assert_base_data(base_data: ComponentBaseData, other: Component) -> None:
    """Assert this ComponentBaseData equals a Component."""
    assert base_data.component_id == other.id
    assert base_data.microgrid_id == other.microgrid_id
    assert base_data.name == other.name
    assert base_data.manufacturer == other.manufacturer
    assert base_data.model_name == other.model_name
    assert base_data.category == other.category
    assert base_data.lifetime == other.operational_lifetime
    assert base_data.rated_bounds == other.rated_bounds
    assert base_data.category_specific_info == other.category_specific_metadata


def base_data_as_proto(
    base_data: ComponentBaseData,
) -> electrical_components_pb2.ElectricalComponent:
    """Convert this ComponentBaseData to a protobuf Component."""
    proto = electrical_components_pb2.ElectricalComponent(
        id=int(base_data.component_id),
        microgrid_id=int(base_data.microgrid_id),
        name=base_data.name or "",
        manufacturer=base_data.manufacturer or "",
        model_name=base_data.model_name or "",
        category=(
            base_data.category
            if isinstance(base_data.category, int)
            else int(base_data.category.value)  # type: ignore[arg-type]
        ),
    )
    if base_data.lifetime:
        lifetime_dict: dict[str, Timestamp] = {}
        if base_data.lifetime.start is not None:
            lifetime_dict["start_timestamp"] = to_timestamp(base_data.lifetime.start)
        if base_data.lifetime.end is not None:
            lifetime_dict["end_timestamp"] = to_timestamp(base_data.lifetime.end)
        proto.operational_lifetime.CopyFrom(lifetime_pb2.Lifetime(**lifetime_dict))
    if base_data.rated_bounds:
        for metric, bounds in base_data.rated_bounds.items():
            bounds_dict: dict[str, float] = {}
            if bounds.lower is not None:
                bounds_dict["lower"] = bounds.lower
            if bounds.upper is not None:
                bounds_dict["upper"] = bounds.upper
            metric_value = metric.value if isinstance(metric, Metric) else metric
            proto.metric_config_bounds.append(
                electrical_components_pb2.MetricConfigBounds(
                    metric=metric_value,  # type: ignore[arg-type]
                    config_bounds=bounds_pb2.Bounds(**bounds_dict),
                )
            )
    return proto
