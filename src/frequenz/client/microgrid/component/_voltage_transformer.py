# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Voltage transformer component."""

import dataclasses
from typing import Literal

from ._category import ComponentCategory
from ._component import Component


@dataclasses.dataclass(frozen=True, kw_only=True)
class VoltageTransformer(Component):
    """A voltage transformer component.

    Voltage transformers are used to step up or step down the voltage, keeping
    the power somewhat constant by increasing or decreasing the current.

    If voltage is stepped up, current is stepped down, and vice versa.

    Note:
        Voltage transformers have efficiency losses, so the output power is always less
        than the input power.
    """

    category: Literal[ComponentCategory.POWER_TRANSFORMER] = (
        ComponentCategory.POWER_TRANSFORMER
    )
    """The category of this component."""

    primary_voltage: float
    """The primary voltage of the transformer, in volts.

    This is the input voltage that is stepped up or down.
    """

    secondary_voltage: float
    """The secondary voltage of the transformer, in volts.

    This is the output voltage that is the result of stepping the primary
    voltage up or down.
    """
