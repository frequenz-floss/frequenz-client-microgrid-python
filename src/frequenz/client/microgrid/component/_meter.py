# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Meter component."""

import dataclasses
from typing import Literal

from ._category import ComponentCategory
from ._component import Component


@dataclasses.dataclass(frozen=True, kw_only=True)
class Meter(Component):
    """A measuring meter component."""

    category: Literal[ComponentCategory.METER] = ComponentCategory.METER
    """The category of this component."""
