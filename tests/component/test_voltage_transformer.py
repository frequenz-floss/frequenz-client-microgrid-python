# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for VoltageTransformer component."""

import pytest
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid.component import (
    ComponentCategory,
    ComponentStatus,
    VoltageTransformer,
)


@pytest.fixture
def component_id() -> ComponentId:
    """Provide a test component ID."""
    return ComponentId(42)


@pytest.fixture
def microgrid_id() -> MicrogridId:
    """Provide a test microgrid ID."""
    return MicrogridId(1)


@pytest.mark.parametrize(
    "primary, secondary", [(400.0, 230.0), (0.0, 0.0), (230.0, 400.0), (-230.0, -400.0)]
)
def test_creation_ok(
    component_id: ComponentId,
    microgrid_id: MicrogridId,
    primary: float,
    secondary: float,
) -> None:
    """Test VoltageTransformer component initialization with different voltages."""
    voltage_transformer = VoltageTransformer(
        id=component_id,
        microgrid_id=microgrid_id,
        name="test_voltage_transformer",
        manufacturer="test_manufacturer",
        model_name="test_model",
        status=ComponentStatus.ACTIVE,
        primary_voltage=primary,
        secondary_voltage=secondary,
    )

    assert voltage_transformer.id == component_id
    assert voltage_transformer.microgrid_id == microgrid_id
    assert voltage_transformer.name == "test_voltage_transformer"
    assert voltage_transformer.manufacturer == "test_manufacturer"
    assert voltage_transformer.model_name == "test_model"
    assert voltage_transformer.status == ComponentStatus.ACTIVE
    assert voltage_transformer.category == ComponentCategory.VOLTAGE_TRANSFORMER
    assert voltage_transformer.primary_voltage == pytest.approx(primary)
    assert voltage_transformer.secondary_voltage == pytest.approx(secondary)
