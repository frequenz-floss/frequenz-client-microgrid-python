# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for Battery components."""

import dataclasses

import pytest
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid.component import (
    Battery,
    BatteryType,
    ComponentCategory,
    LiIonBattery,
    NaIonBattery,
    UnrecognizedBattery,
    UnspecifiedBattery,
)


@dataclasses.dataclass(frozen=True, kw_only=True)
class BatteryTestCase:
    """Test case for battery components."""

    cls: type[UnspecifiedBattery | LiIonBattery | NaIonBattery]
    expected_type: BatteryType
    name: str


@pytest.fixture
def component_id() -> ComponentId:
    """Provide a test component ID."""
    return ComponentId(42)


@pytest.fixture
def microgrid_id() -> MicrogridId:
    """Provide a test microgrid ID."""
    return MicrogridId(1)


def test_abstract_battery_cannot_be_instantiated(
    component_id: ComponentId, microgrid_id: MicrogridId
) -> None:
    """Test that Battery base class cannot be instantiated."""
    with pytest.raises(TypeError, match="Cannot instantiate Battery directly"):
        Battery(
            id=component_id,
            microgrid_id=microgrid_id,
            name="test_battery",
            manufacturer="test_manufacturer",
            model_name="test_model",
            type=BatteryType.LI_ION,
        )


@pytest.mark.parametrize(
    "case",
    [
        BatteryTestCase(
            cls=UnspecifiedBattery,
            expected_type=BatteryType.UNSPECIFIED,
            name="unspecified",
        ),
        BatteryTestCase(
            cls=LiIonBattery, expected_type=BatteryType.LI_ION, name="li_ion"
        ),
        BatteryTestCase(
            cls=NaIonBattery, expected_type=BatteryType.NA_ION, name="na_ion"
        ),
    ],
    ids=lambda case: case.name,
)
def test_recognized_battery_types(
    case: BatteryTestCase, component_id: ComponentId, microgrid_id: MicrogridId
) -> None:
    """Test initialization and properties of different battery types."""
    battery = case.cls(
        id=component_id,
        microgrid_id=microgrid_id,
        name=case.name,
        manufacturer="test_manufacturer",
        model_name="test_model",
    )

    assert battery.id == component_id
    assert battery.microgrid_id == microgrid_id
    assert battery.name == case.name
    assert battery.manufacturer == "test_manufacturer"
    assert battery.model_name == "test_model"
    assert battery.category == ComponentCategory.BATTERY
    assert battery.type == case.expected_type


def test_unrecognized_battery_type(
    component_id: ComponentId, microgrid_id: MicrogridId
) -> None:
    """Test initialization and properties of different battery types."""
    battery = UnrecognizedBattery(
        id=component_id,
        microgrid_id=microgrid_id,
        name="unrecognized_battery",
        manufacturer="test_manufacturer",
        model_name="test_model",
        type=999,
    )

    assert battery.id == component_id
    assert battery.microgrid_id == microgrid_id
    assert battery.name == "unrecognized_battery"
    assert battery.manufacturer == "test_manufacturer"
    assert battery.model_name == "test_model"
    assert battery.category == ComponentCategory.BATTERY
    assert battery.type == 999
