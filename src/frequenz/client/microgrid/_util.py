# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Utility functions."""

import enum
from typing import TypeVar

EnumT = TypeVar("EnumT", bound=enum.Enum)
"""A type variable that is bound to an enum."""


def enum_from_proto(value: int, enum_type: type[EnumT]) -> EnumT | int:
    """Convert a protobuf int enum value to a python enum.

    Example:
        ```python
        import enum

        from proto import proto_pb2  # Just an example. pylint: disable=import-error

        @enum.unique
        class SomeEnum(enum.Enum):
            # These values should match the protobuf enum values.
            UNSPECIFIED = 0
            SOME_VALUE = 1

        enum_value = enum_from_proto(proto_pb2.SomeEnum.SOME_ENUM_SOME_VALUE, SomeEnum)
        # -> SomeEnum.SOME_VALUE

        enum_value = enum_from_proto(42, SomeEnum)
        # -> 42
        ```

    Args:
        value: The protobuf int enum value.
        enum_type: The python enum type to convert to,
            typically an enum class.

    Returns:
        The resulting python enum value if the protobuf value is known, otherwise
            the input value converted to a plain `int`.
    """
    # A protobuf enum value is a NewType of int, so we make sure we have a pure int at
    # this point.
    value = int(value)
    try:
        return enum_type(value)
    except ValueError:
        return value
