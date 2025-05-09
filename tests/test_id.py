# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the microgrid and component IDs."""

from dataclasses import dataclass

import pytest

from frequenz.client.microgrid import ComponentId, MicrogridId, SensorId


@dataclass(frozen=True)
class IdTypeInfo:
    """Information about an ID type for testing."""

    id_class: type
    str_prefix: str
    error_prefix: str


# Define all ID types to test here
ID_TYPES: list[IdTypeInfo] = [
    IdTypeInfo(MicrogridId, "MID", "Microgrid"),
    IdTypeInfo(ComponentId, "CID", "Component"),
    IdTypeInfo(SensorId, "SID", "Sensor"),
]


@pytest.mark.parametrize(
    "type_info",
    ID_TYPES,
    ids=lambda type_info: type_info.id_class.__name__,
)
class TestIds:
    """Tests for ID classes."""

    def test_valid_id(self, type_info: IdTypeInfo) -> None:
        """Test creating a valid ID."""
        id_obj = type_info.id_class(42)
        assert int(id_obj) == 42

    def test_negative_id_raises(self, type_info: IdTypeInfo) -> None:
        """Test that creating a negative ID raises ValueError."""
        error_msg = f"{type_info.error_prefix} ID can't be negative"
        with pytest.raises(ValueError, match=error_msg):
            type_info.id_class(-1)

    def test_equality(self, type_info: IdTypeInfo) -> None:
        """Test equality comparison."""
        assert type_info.id_class(1) == type_info.id_class(1)
        assert type_info.id_class(1) != type_info.id_class(2)

        # Test against all other types
        for other_type in ID_TYPES:
            if other_type != type_info:
                assert type_info.id_class(1) != other_type.id_class(1)

    def test_ordering(self, type_info: IdTypeInfo) -> None:
        """Test ordering comparison."""
        assert type_info.id_class(1) < type_info.id_class(2)
        assert not type_info.id_class(2) < type_info.id_class(1)

        # Test against all other types
        for other_type in ID_TYPES:
            if other_type != type_info:
                with pytest.raises(TypeError):
                    _ = type_info.id_class(1) < other_type.id_class(2)

    def test_hash(self, type_info: IdTypeInfo) -> None:
        """Test hash behavior."""
        # Same IDs should hash to same value
        assert hash(type_info.id_class(1)) == hash(type_info.id_class(1))
        # Different IDs should hash to different values
        assert hash(type_info.id_class(1)) != hash(type_info.id_class(2))

        # Test against all other types
        for other_type in ID_TYPES:
            if other_type != type_info:
                # Same ID but different types should hash to different values
                assert hash(type_info.id_class(1)) != hash(other_type.id_class(1))

    def test_str_and_repr(self, type_info: IdTypeInfo) -> None:
        """Test string representations."""
        id_obj = type_info.id_class(42)
        assert str(id_obj) == f"{type_info.str_prefix}42"
        assert repr(id_obj) == f"{type_info.id_class.__name__}(42)"

    def test_invalid_creation(self, type_info: IdTypeInfo) -> None:
        """Test that creating an ID with a non-integer raises TypeError."""
        with pytest.raises(TypeError):
            type_info.id_class("not-an-int")
