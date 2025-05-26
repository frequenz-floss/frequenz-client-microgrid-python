# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for EV charger components."""

import dataclasses

import pytest
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid.component import (
    AcEvCharger,
    ComponentCategory,
    ComponentStatus,
    DcEvCharger,
    EvCharger,
    EvChargerType,
    HybridEvCharger,
    UnrecognizedEvCharger,
    UnspecifiedEvCharger,
)


@dataclasses.dataclass(frozen=True, kw_only=True)
class EvChargerTestCase:
    """Test case for EV charger components."""

    cls: type[UnspecifiedEvCharger | AcEvCharger | DcEvCharger | HybridEvCharger]
    expected_type: EvChargerType
    name: str


@pytest.fixture
def component_id() -> ComponentId:
    """Provide a test component ID."""
    return ComponentId(42)


@pytest.fixture
def microgrid_id() -> MicrogridId:
    """Provide a test microgrid ID."""
    return MicrogridId(1)


def test_abstract_ev_charger_cannot_be_instantiated(
    component_id: ComponentId, microgrid_id: MicrogridId
) -> None:
    """Test that EvCharger base class cannot be instantiated."""
    with pytest.raises(TypeError, match="Cannot instantiate EvCharger directly"):
        EvCharger(
            id=component_id,
            microgrid_id=microgrid_id,
            name="test_charger",
            manufacturer="test_manufacturer",
            model_name="test_model",
            status=ComponentStatus.ACTIVE,
            type=EvChargerType.AC,
        )


@pytest.mark.parametrize(
    "case",
    [
        EvChargerTestCase(
            cls=UnspecifiedEvCharger,
            expected_type=EvChargerType.UNSPECIFIED,
            name="unspecified",
        ),
        EvChargerTestCase(cls=AcEvCharger, expected_type=EvChargerType.AC, name="ac"),
        EvChargerTestCase(cls=DcEvCharger, expected_type=EvChargerType.DC, name="dc"),
        EvChargerTestCase(
            cls=HybridEvCharger,
            expected_type=EvChargerType.HYBRID,
            name="hybrid",
        ),
    ],
    ids=lambda case: case.name,
)
def test_recognized_ev_charger_types(  # Renamed from test_ev_charger_types
    case: EvChargerTestCase, component_id: ComponentId, microgrid_id: MicrogridId
) -> None:
    """Test initialization and properties of different recognized EV charger types."""
    charger = case.cls(
        id=component_id,
        microgrid_id=microgrid_id,
        name=case.name,
        manufacturer="test_manufacturer",
        model_name="test_model",
        status=ComponentStatus.ACTIVE,
    )

    assert charger.id == component_id
    assert charger.microgrid_id == microgrid_id
    assert charger.name == case.name
    assert charger.manufacturer == "test_manufacturer"
    assert charger.model_name == "test_model"
    assert charger.status == ComponentStatus.ACTIVE
    assert charger.category == ComponentCategory.EV_CHARGER
    assert charger.type == case.expected_type


def test_unrecognized_ev_charger_type(
    component_id: ComponentId, microgrid_id: MicrogridId
) -> None:
    """Test initialization and properties of unrecognized EV charger type."""
    charger = UnrecognizedEvCharger(
        id=component_id,
        microgrid_id=microgrid_id,
        name="unrecognized_charger",
        manufacturer="test_manufacturer",
        model_name="test_model",
        status=ComponentStatus.ACTIVE,
        type=999,  # type is passed here for UnrecognizedEvCharger
    )

    assert charger.id == component_id
    assert charger.microgrid_id == microgrid_id
    assert charger.name == "unrecognized_charger"
    assert charger.manufacturer == "test_manufacturer"
    assert charger.model_name == "test_model"
    assert charger.status == ComponentStatus.ACTIVE
    assert charger.category == ComponentCategory.EV_CHARGER
    assert charger.type == 999
