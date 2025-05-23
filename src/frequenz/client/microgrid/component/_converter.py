# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Converter component."""

import dataclasses
from typing import Literal

from ._category import ComponentCategory
from ._component import Component


@dataclasses.dataclass(frozen=True, kw_only=True)
class Converter(Component):
    """An AC-DC converter component."""

    category: Literal[ComponentCategory.CONVERTER] = ComponentCategory.CONVERTER
    """The category of this component."""
