# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Base component from which all other components inherit."""

import dataclasses
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any, Self

from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.components import ComponentId

from .._lifetime import Lifetime
from ..metrics._bounds import Bounds
from ..metrics._metric import Metric
from ._category import ComponentCategory


@dataclasses.dataclass(frozen=True, kw_only=True)
class Component:  # pylint: disable=too-many-instance-attributes
    """A base class for all components."""

    id: ComponentId
    """This component's ID."""

    microgrid_id: MicrogridId
    """The ID of the microgrid this component belongs to."""

    category: ComponentCategory | int
    """The category of this component.

    Note:
        This should not be used normally, you should test if a component
        [`isinstance`][] of a concrete component class instead.

        It is only provided for using with a newer version of the API where the client
        doesn't know about a new category yet (i.e. for use with
        [`UnrecognizedComponent`][frequenz.client.microgrid.component.UnrecognizedComponent])
        and in case some low level code needs to know the category of a component.
        """

    name: str | None = None
    """The name of this component."""

    manufacturer: str | None = None
    """The manufacturer of this component."""

    model_name: str | None = None
    """The model name of this component."""

    operational_lifetime: Lifetime = dataclasses.field(default_factory=Lifetime)
    """The operational lifetime of this component."""

    rated_bounds: Mapping[Metric | int, Bounds] = dataclasses.field(
        default_factory=dict,
        # dict is not hashable, so we don't use this field to calculate the hash. This
        # shouldn't be a problem since it is very unlikely that two components with all
        # other attributes being equal would have different category specific metadata,
        # so hash collisions should be still very unlikely.
        hash=False,
    )
    """List of rated bounds present for the component identified by Metric."""

    category_specific_metadata: Mapping[str, Any] = dataclasses.field(
        default_factory=dict,
        # dict is not hashable, so we don't use this field to calculate the hash. This
        # shouldn't be a problem since it is very unlikely that two components with all
        # other attributes being equal would have different category specific metadata,
        # so hash collisions should be still very unlikely.
        hash=False,
    )
    """The category specific metadata of this component.

    Note:
        This should not be used normally, it is only useful when accessing a newer
        version of the API where the client doesn't know about the new metadata fields
        yet (i.e. for use with
        [`UnrecognizedComponent`][frequenz.client.microgrid.component.UnrecognizedComponent]).
    """

    def __new__(cls, *_: Any, **__: Any) -> Self:
        """Prevent instantiation of this class."""
        if cls is Component:
            raise TypeError(f"Cannot instantiate {cls.__name__} directly")
        return super().__new__(cls)

    def is_operational_at(self, timestamp: datetime) -> bool:
        """Check whether this component is operational at a specific timestamp.

        Args:
            timestamp: The timestamp to check.

        Returns:
            Whether this component is operational at the given timestamp.
        """
        return self.operational_lifetime.is_operational_at(timestamp)

    def is_operational_now(self) -> bool:
        """Check whether this component is currently operational.

        Returns:
            Whether this component is operational at the current time.
        """
        return self.is_operational_at(datetime.now(timezone.utc))

    @property
    def identity(self) -> tuple[ComponentId, MicrogridId]:
        """The identity of this component.

        This uses the component ID and microgrid ID to identify a component
        without considering the other attributes, so even if a component state
        changed, the identity remains the same.
        """
        return (self.id, self.microgrid_id)

    def __str__(self) -> str:
        """Return a human-readable string representation of this instance."""
        name = f":{self.name}" if self.name else ""
        return f"{self.id}<{type(self).__name__}>{name}"
