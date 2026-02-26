# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for protobuf conversion of simple Component objects."""

import logging
from unittest.mock import Mock, patch

import pytest
from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)

from frequenz.client.microgrid.component import (
    Chp,
    Component,
    ComponentCategory,
    Converter,
    CryptoMiner,
    Electrolyzer,
    GridConnectionPoint,
    Hvac,
    Meter,
    MismatchedCategoryComponent,
    Precharger,
    Relay,
    UnrecognizedComponent,
    UnspecifiedComponent,
    VoltageTransformer,
    WindTurbine,
)
from frequenz.client.microgrid.component._component_proto import (
    ComponentBaseData,
    component_from_proto,
    component_from_proto_with_issues,
)

from .conftest import assert_base_data, base_data_as_proto


def test_unspecified(default_component_base_data: ComponentBaseData) -> None:
    """Test Component with unspecified category."""
    major_issues: list[str] = []
    minor_issues: list[str] = []
    proto = base_data_as_proto(default_component_base_data)

    component = component_from_proto_with_issues(
        proto, major_issues=major_issues, minor_issues=minor_issues
    )

    assert major_issues == ["category is unspecified"]
    assert not minor_issues
    assert isinstance(component, UnspecifiedComponent)
    assert_base_data(default_component_base_data, component)
    assert component.category == ComponentCategory.UNSPECIFIED


def test_unrecognized(default_component_base_data: ComponentBaseData) -> None:
    """Test Component with unrecognized category."""
    major_issues: list[str] = []
    minor_issues: list[str] = []
    base_data = default_component_base_data._replace(category=999)
    proto = base_data_as_proto(base_data)

    component = component_from_proto_with_issues(
        proto, major_issues=major_issues, minor_issues=minor_issues
    )

    assert major_issues == ["category 999 is unrecognized"]
    assert not minor_issues
    assert isinstance(component, UnrecognizedComponent)
    assert_base_data(base_data, component)
    assert component.category == 999


def test_category_mismatch(default_component_base_data: ComponentBaseData) -> None:
    """Test MismatchedCategoryComponent for category GRID and battery specific info."""
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

    component = component_from_proto_with_issues(
        proto, major_issues=major_issues, minor_issues=minor_issues
    )
    # The actual message from component_from_proto_with_issues via
    # _component_base_from_proto_with_issues
    assert major_issues == [
        "category_specific_info.kind (battery) does not match the category (grid_connection_point)"
    ]
    assert not minor_issues
    assert isinstance(component, MismatchedCategoryComponent)
    assert_base_data(base_data, component)
    assert component.category == ComponentCategory.GRID_CONNECTION_POINT


@pytest.mark.parametrize(
    "category,component_class",
    [
        pytest.param(ComponentCategory.CHP, Chp, id="Chp"),
        pytest.param(ComponentCategory.CONVERTER, Converter, id="Converter"),
        pytest.param(ComponentCategory.CRYPTO_MINER, CryptoMiner, id="CryptoMiner"),
        pytest.param(ComponentCategory.ELECTROLYZER, Electrolyzer, id="Electrolyzer"),
        pytest.param(ComponentCategory.HVAC, Hvac, id="Hvac"),
        pytest.param(ComponentCategory.METER, Meter, id="Meter"),
        pytest.param(ComponentCategory.PRECHARGER, Precharger, id="Precharger"),
        pytest.param(ComponentCategory.RELAY, Relay, id="Relay"),
        pytest.param(ComponentCategory.WIND_TURBINE, WindTurbine, id="WindTurbine"),
    ],
)
def test_trivial(
    category: ComponentCategory,
    component_class: type[Component],
    default_component_base_data: ComponentBaseData,
) -> None:
    """Test component types that don't need special handling."""
    major_issues: list[str] = []
    minor_issues: list[str] = []
    base_data = default_component_base_data._replace(category=category)
    proto = base_data_as_proto(base_data)

    component = component_from_proto_with_issues(
        proto, major_issues=major_issues, minor_issues=minor_issues
    )

    assert not major_issues
    assert not minor_issues
    assert isinstance(component, component_class)


@pytest.mark.parametrize("primary", [None, -10.0, 0.0, 230.0])
@pytest.mark.parametrize("secondary", [None, -34.5, 0.0, 400.0])
def test_voltage_transformer(
    default_component_base_data: ComponentBaseData,
    primary: float | None,
    secondary: float | None,
) -> None:
    """Test VoltageTransformer component."""
    major_issues: list[str] = []
    minor_issues: list[str] = []
    base_data = default_component_base_data._replace(
        category=ComponentCategory.POWER_TRANSFORMER
    )

    proto = base_data_as_proto(base_data)
    if primary is not None:
        proto.category_specific_info.power_transformer.primary = primary
    if secondary is not None:
        proto.category_specific_info.power_transformer.secondary = secondary

    component = component_from_proto_with_issues(
        proto, major_issues=major_issues, minor_issues=minor_issues
    )

    assert not major_issues
    assert not minor_issues
    assert isinstance(component, VoltageTransformer)
    assert_base_data(base_data, component)
    assert component.primary_voltage == (
        pytest.approx(primary if primary is not None else 0.0)
    )
    assert component.secondary_voltage == (
        pytest.approx(secondary if secondary is not None else 0.0)
    )


@pytest.mark.parametrize("rated_fuse_current", [None, 0, 23])
def test_grid(
    default_component_base_data: ComponentBaseData,
    rated_fuse_current: int | None,
) -> None:
    """Test GridConnectionPoint component with default values."""
    major_issues: list[str] = []
    minor_issues: list[str] = []
    base_data = default_component_base_data._replace(
        category=ComponentCategory.GRID_CONNECTION_POINT
    )

    proto = base_data_as_proto(base_data)
    if rated_fuse_current is not None:
        proto.category_specific_info.grid_connection_point.rated_fuse_current = (
            rated_fuse_current
        )

    component = component_from_proto_with_issues(
        proto, major_issues=major_issues, minor_issues=minor_issues
    )

    assert not major_issues
    assert not minor_issues
    assert isinstance(component, GridConnectionPoint)
    assert_base_data(base_data, component)
    assert component.rated_fuse_current == (
        rated_fuse_current if rated_fuse_current is not None else 0
    )


@patch(
    "frequenz.client.microgrid.component._component_proto."
    "component_from_proto_with_issues",
    autospec=True,
)
def test_issues_logging(
    mock_from_proto_with_issues: Mock, caplog: pytest.LogCaptureFixture
) -> None:
    """Test collection and logging of issues during proto conversion."""
    caplog.set_level("DEBUG")  # Ensure we capture DEBUG level messages

    mock_component = Mock(name="component", spec=Component)

    def _fake_from_proto_with_issues(
        _: electrical_components_pb2.ElectricalComponent,
        *,
        major_issues: list[str],
        minor_issues: list[str],
    ) -> Component:
        """Fake function to simulate conversion and logging."""
        major_issues.append("fake major issue")
        minor_issues.append("fake minor issue")
        return mock_component

    mock_from_proto_with_issues.side_effect = _fake_from_proto_with_issues

    mock_proto = Mock(name="proto", spec=electrical_components_pb2.ElectricalComponent)
    component = component_from_proto(mock_proto)

    assert component is mock_component
    assert caplog.record_tuples == [
        (
            "frequenz.client.microgrid.component._component_proto",
            logging.WARNING,
            "Found issues in component: fake major issue | "
            f"Protobuf message:\n{mock_proto}",
        ),
        (
            "frequenz.client.microgrid.component._component_proto",
            logging.DEBUG,
            "Found minor issues in component: fake minor issue | "
            f"Protobuf message:\n{mock_proto}",
        ),
    ]
