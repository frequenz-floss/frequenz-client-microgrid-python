# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

r'''Provides strongly-typed unique identifiers for entities.

This module offers a base class,
[`BaseId`][frequenz.client.microgrid.id.BaseId], which can be subclassed to
create distinct ID types for different components or concepts within a system.
These IDs ensure type safety, meaning that an ID for one type of entity (e.g., a
sensor) cannot be mistakenly used where an ID for another type (e.g., a
microgrid) is expected.

# Creating Custom ID Types

To define a new ID type, create a class that inherits from
[`BaseId`][frequenz.client.microgrid.id.BaseId] and provide a unique
`str_prefix` as a keyword argument in the class definition. This prefix is used
in the string representation of the ID and must be unique across all ID types.

Note:
    The `str_prefix` must be unique across all ID types. If you try to use a
    prefix that is already registered, a `ValueError` will be raised when defining
    the class.

To encourage consistency, the class name must end with the suffix "Id" (e.g.,
`MyNewId`). This check can be bypassed by passing `allow_custom_name=True` when
defining the class (e.g., `class MyCustomName(BaseId, str_prefix="MCN",
allow_custom_name=True):`).

Tip:
    Use the [`@typing.final`][typing.final] decorator to prevent subclassing of
    ID classes.

Example: Creating a standard ID type
    ```python
    from typing import final
    from frequenz.client.microgrid.id import BaseId

    @final
    class InverterId(BaseId, str_prefix="INV"):
        """A unique identifier for an inverter."""

    inv_id = InverterId(123)
    print(inv_id)       # Output: INV123
    print(int(inv_id))  # Output: 123
    ```

Example: Creating an ID type with a non-standard name
    ```python
    from typing import final
    from frequenz.client.microgrid.id import BaseId

    @final
    class CustomNameForId(BaseId, str_prefix="CST", allow_custom_name=True):
        """An ID with a custom name, not ending in 'Id'."""

    custom_id = CustomNameForId(456)
    print(custom_id)       # Output: CST456
    print(int(custom_id))  # Output: 456
    ```

# Predefined ID Types

This module predefines the following ID types:

- [`ComponentId`][frequenz.client.microgrid.id.ComponentId]: For identifying
    generic components.
- [`MicrogridId`][frequenz.client.microgrid.id.MicrogridId]: For identifying
    microgrids.
- [`SensorId`][frequenz.client.microgrid.id.SensorId]: For identifying sensors.
'''


from typing import Any, ClassVar, Self, cast, final


class BaseId:
    """A base class for unique identifiers.

    Subclasses must provide a unique `str_prefix` keyword argument during
    definition, which is used in the string representation of the ID.

    By default, subclass names must end with "Id". This can be overridden by
    passing `allow_custom_name=True` during class definition.

    For more information and examples, see the [module's
    documentation][frequenz.client.microgrid.id].
    """

    _id: int
    _str_prefix: ClassVar[str]
    _registered_prefixes: ClassVar[set[str]] = set()

    def __new__(cls, *_: Any, **__: Any) -> Self:
        """Create a new instance of the ID class, only if it is a subclass of BaseId."""
        if cls is BaseId:
            raise TypeError("BaseId cannot be instantiated directly. Use a subclass.")
        return super().__new__(cls)

    def __init_subclass__(
        cls,
        *,
        str_prefix: str,
        allow_custom_name: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize a subclass, set its string prefix, and perform checks.

        Args:
            str_prefix: The string prefix for the ID type (e.g., "MID").
                Must be unique across all ID types.
            allow_custom_name: If True, bypasses the check that the class name
                must end with "Id". Defaults to False.
            **kwargs: Forwarded to the parent's __init_subclass__.

        Raises:
            ValueError: If the `str_prefix` is already registered by another
                ID type.
            TypeError: If `allow_custom_name` is False and the class name
                does not end with "Id".
        """
        super().__init_subclass__(**kwargs)

        if str_prefix in BaseId._registered_prefixes:
            raise ValueError(
                f"Prefix '{str_prefix}' is already registered. "
                "ID prefixes must be unique."
            )
        BaseId._registered_prefixes.add(str_prefix)

        if not allow_custom_name and not cls.__name__.endswith("Id"):
            raise TypeError(
                f"Class name '{cls.__name__}' for an ID class must end with 'Id' "
                "(e.g., 'SomeId'), or use `allow_custom_name=True`."
            )

        cls._str_prefix = str_prefix

    def __init__(self, id_: int, /) -> None:
        """Initialize this instance.

        Args:
            id_: The numeric unique identifier.

        Raises:
            ValueError: If the ID is negative.
        """
        if id_ < 0:
            raise ValueError(f"{type(self).__name__} can't be negative.")
        self._id = id_

    @property
    def str_prefix(self) -> str:
        """The prefix used for the string representation of this ID."""
        return self._str_prefix

    def __int__(self) -> int:
        """Return the numeric ID of this instance."""
        return self._id

    def __eq__(self, other: object) -> bool:
        """Check if this instance is equal to another object.

        Equality is defined as being of the exact same type and having the same
        underlying ID.
        """
        # pylint thinks this is not an unidiomatic typecheck, but in this case
        # it is not. isinstance() returns True for subclasses, which is not
        # what we want here, as different ID types should never be equal.
        # pylint: disable-next=unidiomatic-typecheck
        if type(other) is not type(self):
            return NotImplemented
        # We already checked type(other) is type(self), but mypy doesn't
        # understand that, so we need to cast it to Self.
        other_id = cast(Self, other)
        return self._id == other_id._id

    def __lt__(self, other: object) -> bool:
        """Check if this instance is less than another object.

        Comparison is only defined between instances of the exact same type.
        """
        # pylint: disable-next=unidiomatic-typecheck
        if type(other) is not type(self):
            return NotImplemented
        other_id = cast(Self, other)
        return self._id < other_id._id

    def __hash__(self) -> int:
        """Return the hash of this instance.

        The hash is based on the exact type and the underlying ID to ensure
        that IDs of different types but with the same numeric value have different hashes.
        """
        return hash((type(self), self._id))

    def __repr__(self) -> str:
        """Return the string representation of this instance."""
        return f"{type(self).__name__}({self._id!r})"

    def __str__(self) -> str:
        """Return the short string representation of this instance."""
        return f"{type(self)._str_prefix}{self._id}"


@final
class MicrogridId(BaseId, str_prefix="MID"):
    """A unique identifier for a microgrid."""


@final
class ComponentId(BaseId, str_prefix="CID"):
    """A unique identifier for a microgrid component."""


@final
class SensorId(BaseId, str_prefix="SID"):
    """A unique identifier for a microgrid sensor."""
