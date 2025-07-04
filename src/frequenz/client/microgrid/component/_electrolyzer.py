# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Electrolyzer component."""

import dataclasses
from typing import Literal

from ._category import ComponentCategory
from ._component import Component


@dataclasses.dataclass(frozen=True, kw_only=True)
class Electrolyzer(Component):
    """An electrolyzer component."""

    category: Literal[ComponentCategory.ELECTROLYZER] = ComponentCategory.ELECTROLYZER
    """The category of this component."""
