# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Unknown component."""

import dataclasses
from typing import Any, Literal, Self

from ._category import ComponentCategory
from ._component import Component


@dataclasses.dataclass(frozen=True, kw_only=True)
class ProblematicComponent(Component):
    """An abstract component with a problem."""

    # pylint: disable-next=unused-argument
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        """Prevent instantiation of this class."""
        if cls is ProblematicComponent:
            raise TypeError(f"Cannot instantiate {cls.__name__} directly")
        return super().__new__(cls)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedComponent(ProblematicComponent):
    """A component of unspecified type."""

    category: Literal[ComponentCategory.UNSPECIFIED] = ComponentCategory.UNSPECIFIED
    """The category of this component."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnrecognizedComponent(ProblematicComponent):
    """A component of an unrecognized type."""

    category: int
    """The category of this component."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class MismatchedCategoryComponent(ProblematicComponent):
    """A component with a mismatch in the category.

    This component declared a category but carries category specific metadata that
    doesn't match the declared category.
    """

    category: ComponentCategory | int
    """The category of this component."""
