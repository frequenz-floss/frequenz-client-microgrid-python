# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Tests for the microgrid component wrapper."""

import pytest
from frequenz.api.common import components_pb2
from frequenz.client.common.microgrid.components import ComponentCategory, ComponentId

from frequenz.client.microgrid import (
    Component,
)
from frequenz.client.microgrid._component import component_category_from_protobuf


def test_component_category_from_protobuf() -> None:
    """Test the creating component category from protobuf."""
    assert (
        component_category_from_protobuf(
            components_pb2.ComponentCategory.COMPONENT_CATEGORY_UNSPECIFIED
        )
        == ComponentCategory.UNSPECIFIED
    )

    assert (
        component_category_from_protobuf(
            components_pb2.ComponentCategory.COMPONENT_CATEGORY_GRID
        )
        == ComponentCategory.GRID
    )

    assert (
        component_category_from_protobuf(
            components_pb2.ComponentCategory.COMPONENT_CATEGORY_METER
        )
        == ComponentCategory.METER
    )

    assert (
        component_category_from_protobuf(
            components_pb2.ComponentCategory.COMPONENT_CATEGORY_INVERTER
        )
        == ComponentCategory.INVERTER
    )

    assert (
        component_category_from_protobuf(
            components_pb2.ComponentCategory.COMPONENT_CATEGORY_BATTERY
        )
        == ComponentCategory.BATTERY
    )

    assert (
        component_category_from_protobuf(
            components_pb2.ComponentCategory.COMPONENT_CATEGORY_EV_CHARGER
        )
        == ComponentCategory.EV_CHARGER
    )

    assert component_category_from_protobuf(666) == ComponentCategory.UNSPECIFIED  # type: ignore

    with pytest.raises(ValueError):
        component_category_from_protobuf(
            components_pb2.ComponentCategory.COMPONENT_CATEGORY_SENSOR
        )


# pylint: disable=invalid-name
def test_Component() -> None:
    """Test the component category."""
    c0 = Component(ComponentId(0), ComponentCategory.GRID)
    assert c0.is_valid()

    c1 = Component(ComponentId(1), ComponentCategory.GRID)
    assert c1.is_valid()

    c4 = Component(ComponentId(4), ComponentCategory.METER)
    assert c4.is_valid()

    c5 = Component(ComponentId(5), ComponentCategory.INVERTER)
    assert c5.is_valid()

    c6 = Component(ComponentId(6), ComponentCategory.BATTERY)
    assert c6.is_valid()

    c7 = Component(ComponentId(7), ComponentCategory.EV_CHARGER)
    assert c7.is_valid()

    with pytest.raises(ValueError):
        # Should raise error with negative ID
        Component(ComponentId(-1), ComponentCategory.GRID)

    invalid_type = Component(ComponentId(666), -1)  # type: ignore
    assert not invalid_type.is_valid()

    another_invalid_type = Component(ComponentId(666), 666)  # type: ignore
    assert not another_invalid_type.is_valid()
