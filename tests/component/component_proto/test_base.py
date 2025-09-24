# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for protobuf conversion of the base/common part of Component objects."""


from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from google.protobuf.timestamp_pb2 import Timestamp

from frequenz.client.microgrid import Lifetime
from frequenz.client.microgrid.component import ComponentCategory
from frequenz.client.microgrid.component._component_proto import (
    ComponentBaseData,
    component_base_from_proto_with_issues,
)

from .conftest import base_data_as_proto


def test_complete(default_component_base_data: ComponentBaseData) -> None:
    """Test parsing of a complete base component proto."""
    major_issues: list[str] = []
    minor_issues: list[str] = []
    base_data = default_component_base_data._replace(
        category=ComponentCategory.CHP,  # Just to pick a valid category
    )
    proto = base_data_as_proto(base_data)
    parsed = component_base_from_proto_with_issues(
        proto, major_issues=major_issues, minor_issues=minor_issues
    )

    assert not major_issues
    assert not minor_issues
    assert parsed == base_data


def test_missing_category_specific_info(
    default_component_base_data: ComponentBaseData,
) -> None:
    """Test parsing with missing optional category specific info."""
    major_issues: list[str] = []
    minor_issues: list[str] = []
    base_data = default_component_base_data._replace(
        name=None,
        manufacturer=None,
        model_name=None,
        category=ComponentCategory.UNSPECIFIED,
        lifetime=Lifetime(),
        rated_bounds={},
        category_specific_info={},
    )
    proto = base_data_as_proto(base_data)
    proto.ClearField("operational_lifetime")
    proto.ClearField("metric_config_bounds")

    parsed = component_base_from_proto_with_issues(
        proto, major_issues=major_issues, minor_issues=minor_issues
    )

    assert sorted(major_issues) == sorted(["category is unspecified"])
    assert sorted(minor_issues) == sorted(
        [
            "name is empty",
            "manufacturer is empty",
            "model_name is empty",
            "missing operational lifetime, considering it always operational",
        ]
    )
    assert parsed == base_data


def test_category_specific_info_mismatch(
    default_component_base_data: ComponentBaseData,
) -> None:
    """Test category and category specific info mismatch."""
    major_issues: list[str] = []
    minor_issues: list[str] = []
    base_data = default_component_base_data._replace(
        category=ComponentCategory.GRID_CONNECTION_POINT,
        category_specific_info={"type": "BATTERY_TYPE_LI_ION"},
        category_mismatched=True,
    )
    proto = base_data_as_proto(base_data)
    proto.category_specific_info.battery.type = (
        electrical_components_pb2.BATTERY_TYPE_LI_ION
    )

    parsed = component_base_from_proto_with_issues(
        proto, major_issues=major_issues, minor_issues=minor_issues
    )
    # Actual message from _component_base_from_proto_with_issues
    assert major_issues == ["category_type.metadata does not match the category_type"]
    assert not minor_issues
    assert parsed == base_data


def test_invalid_lifetime(default_component_base_data: ComponentBaseData) -> None:
    """Test parsing with missing optional metadata."""
    major_issues: list[str] = []
    minor_issues: list[str] = []
    base_data = default_component_base_data._replace(
        category=ComponentCategory.CHP, lifetime=Lifetime()
    )
    proto = base_data_as_proto(base_data)
    proto.operational_lifetime.start_timestamp.CopyFrom(
        Timestamp(seconds=1696204800)  # 2023-10-02T00:00:00Z
    )
    proto.operational_lifetime.end_timestamp.CopyFrom(
        Timestamp(seconds=1696118400)  # 2023-10-01T00:00:00Z
    )

    parsed = component_base_from_proto_with_issues(
        proto, major_issues=major_issues, minor_issues=minor_issues
    )

    assert major_issues == [
        "invalid operational lifetime (Start (2023-10-02 00:00:00+00:00) must be "
        "before or equal to end (2023-10-01 00:00:00+00:00)), considering it as "
        "missing (i.e. always operational)"
    ]
    assert not minor_issues
    assert parsed == base_data
