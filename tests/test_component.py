# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Tests for the microgrid component wrapper."""

import pytest
from frequenz.client.common.microgrid.components import ComponentCategory, ComponentId

from frequenz.client.microgrid import Component


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

    invalid_type = Component(ComponentId(666), -1)
    assert not invalid_type.is_valid()

    another_invalid_type = Component(ComponentId(666), 666)
    assert not another_invalid_type.is_valid()
