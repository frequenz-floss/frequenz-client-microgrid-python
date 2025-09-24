# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for protobuf conversion of components with a type."""

import pytest
from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)

from frequenz.client.microgrid.component import (
    AcEvCharger,
    Battery,
    BatteryInverter,
    BatteryType,
    ComponentCategory,
    DcEvCharger,
    EvCharger,
    EvChargerType,
    HybridEvCharger,
    HybridInverter,
    Inverter,
    InverterType,
    LiIonBattery,
    NaIonBattery,
    SolarInverter,
    UnrecognizedBattery,
    UnrecognizedEvCharger,
    UnrecognizedInverter,
    UnspecifiedBattery,
    UnspecifiedEvCharger,
    UnspecifiedInverter,
)
from frequenz.client.microgrid.component._component_proto import (
    ComponentBaseData,
    component_from_proto_with_issues,
)

from .conftest import assert_base_data, base_data_as_proto


@pytest.mark.parametrize(
    "battery_class, battery_type, pb_battery_type, expected_major_issues",
    [
        pytest.param(
            LiIonBattery,
            BatteryType.LI_ION,
            electrical_components_pb2.BATTERY_TYPE_LI_ION,
            [],
            id="LI_ION",
        ),
        pytest.param(
            NaIonBattery,
            BatteryType.NA_ION,
            electrical_components_pb2.BATTERY_TYPE_NA_ION,
            [],
            id="NA_ION",
        ),
        pytest.param(
            UnspecifiedBattery,
            BatteryType.UNSPECIFIED,
            electrical_components_pb2.BATTERY_TYPE_UNSPECIFIED,
            ["battery type is unspecified"],
            id="UNSPECIFIED",
        ),
        pytest.param(
            UnrecognizedBattery,
            999,
            999,
            ["battery type 999 is unrecognized"],
            id="UNRECOGNIZED",
        ),
    ],
)
def test_battery(
    default_component_base_data: ComponentBaseData,
    battery_class: type[Battery],
    battery_type: BatteryType | int,
    pb_battery_type: int,
    expected_major_issues: list[str],
) -> None:
    """Test battery component."""
    major_issues: list[str] = []
    minor_issues: list[str] = []
    base_data = default_component_base_data._replace(category=ComponentCategory.BATTERY)
    proto = base_data_as_proto(base_data)
    proto.category_specific_info.battery.type = pb_battery_type  # type: ignore[assignment]

    component = component_from_proto_with_issues(
        proto, major_issues=major_issues, minor_issues=minor_issues
    )
    assert major_issues == expected_major_issues
    assert not minor_issues
    assert isinstance(component, Battery)
    assert isinstance(component, battery_class)
    assert_base_data(base_data, component)
    assert component.type == battery_type


@pytest.mark.parametrize(
    "ev_charger_class, ev_charger_type, pb_ev_charger_type, expected_major_issues",
    [
        pytest.param(
            AcEvCharger,
            EvChargerType.AC,
            electrical_components_pb2.EV_CHARGER_TYPE_AC,
            [],
            id="AC",
        ),
        pytest.param(
            DcEvCharger,
            EvChargerType.DC,
            electrical_components_pb2.EV_CHARGER_TYPE_DC,
            [],
            id="DC",
        ),
        pytest.param(
            HybridEvCharger,
            EvChargerType.HYBRID,
            electrical_components_pb2.EV_CHARGER_TYPE_HYBRID,
            [],
            id="HYBRID",
        ),
        pytest.param(
            UnspecifiedEvCharger,
            EvChargerType.UNSPECIFIED,
            electrical_components_pb2.EV_CHARGER_TYPE_UNSPECIFIED,
            ["ev_charger type is unspecified"],
            id="UNSPECIFIED",
        ),
        pytest.param(
            UnrecognizedEvCharger,
            999,
            999,
            ["ev_charger type 999 is unrecognized"],
            id="UNRECOGNIZED",
        ),
    ],
)
def test_ev_charger(
    default_component_base_data: ComponentBaseData,
    ev_charger_class: type[EvCharger],
    ev_charger_type: EvChargerType | int,
    pb_ev_charger_type: int,
    expected_major_issues: list[str],
) -> None:
    """Test EV Charger component."""
    major_issues: list[str] = []
    minor_issues: list[str] = []
    base_data = default_component_base_data._replace(
        category=ComponentCategory.EV_CHARGER
    )
    proto = base_data_as_proto(base_data)
    proto.category_specific_info.ev_charger.type = pb_ev_charger_type  # type: ignore[assignment]

    component = component_from_proto_with_issues(
        proto, major_issues=major_issues, minor_issues=minor_issues
    )
    assert major_issues == expected_major_issues
    assert not minor_issues
    assert isinstance(component, EvCharger)
    assert isinstance(component, ev_charger_class)
    assert_base_data(base_data, component)
    assert component.type == ev_charger_type


@pytest.mark.parametrize(
    "inverter_class, inverter_type, pb_inverter_type, expected_major_issues",
    [
        pytest.param(
            BatteryInverter,
            InverterType.BATTERY,
            electrical_components_pb2.INVERTER_TYPE_BATTERY,
            [],
            id="BATTERY",
        ),
        pytest.param(
            SolarInverter,
            InverterType.SOLAR,
            electrical_components_pb2.INVERTER_TYPE_PV,
            [],
            id="SOLAR",
        ),
        pytest.param(
            HybridInverter,
            InverterType.HYBRID,
            electrical_components_pb2.INVERTER_TYPE_HYBRID,
            [],
            id="HYBRID",
        ),
        pytest.param(
            UnspecifiedInverter,
            InverterType.UNSPECIFIED,
            electrical_components_pb2.INVERTER_TYPE_UNSPECIFIED,
            ["inverter type is unspecified"],
            id="UNSPECIFIED",
        ),
        pytest.param(
            UnrecognizedInverter,
            999,
            999,
            ["inverter type 999 is unrecognized"],
            id="UNRECOGNIZED",
        ),
    ],
)
def test_inverter(
    default_component_base_data: ComponentBaseData,
    inverter_class: type[Inverter],
    inverter_type: InverterType | int,
    pb_inverter_type: int,
    expected_major_issues: list[str],
) -> None:
    """Test inverter component."""
    major_issues: list[str] = []
    minor_issues: list[str] = []
    base_data = default_component_base_data._replace(
        category=ComponentCategory.INVERTER
    )
    proto = base_data_as_proto(base_data)
    proto.category_specific_info.inverter.type = pb_inverter_type  # type: ignore[assignment]

    component = component_from_proto_with_issues(
        proto, major_issues=major_issues, minor_issues=minor_issues
    )
    assert major_issues == expected_major_issues
    assert not minor_issues
    assert isinstance(component, Inverter)
    assert isinstance(component, inverter_class)
    assert_base_data(base_data, component)
    assert component.type == inverter_type
