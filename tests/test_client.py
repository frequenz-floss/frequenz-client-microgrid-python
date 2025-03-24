# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Tests for the microgrid client thin wrapper."""

import logging
from collections.abc import AsyncIterator
from contextlib import AsyncExitStack
from typing import Any
from unittest import mock

import grpc.aio
import pytest
from frequenz.api.common import components_pb2, metrics_pb2
from frequenz.api.microgrid import grid_pb2, inverter_pb2, microgrid_pb2
from frequenz.client.base import retry

from frequenz.client.microgrid import (
    ApiClientError,
    BatteryData,
    Component,
    ComponentCategory,
    ComponentData,
    ComponentId,
    Connection,
    EVChargerData,
    Fuse,
    GridMetadata,
    InverterData,
    InverterType,
    MeterData,
    MicrogridApiClient,
)


class _TestClient(MicrogridApiClient):
    def __init__(self, *, retry_strategy: retry.Strategy | None = None) -> None:
        # Here we sadly can't use spec=MicrogridStub because the generated stub typing
        # is a mess, and for some reason inspection of gRPC methods doesn't work.
        # This is also why we need to explicitly create the AsyncMock objects for every
        # call.
        mock_stub = mock.MagicMock(name="stub")
        mock_stub.ListComponents = mock.AsyncMock("ListComponents")
        mock_stub.ListConnections = mock.AsyncMock("ListConnections")
        mock_stub.SetPowerActive = mock.AsyncMock("SetPowerActive")
        mock_stub.SetPowerReactive = mock.AsyncMock("SetPowerReactive")
        mock_stub.AddInclusionBounds = mock.AsyncMock("AddInclusionBounds")
        mock_stub.StreamComponentData = mock.Mock("StreamComponentData")
        super().__init__("grpc://mock_host:1234", retry_strategy=retry_strategy)
        self.mock_stub = mock_stub
        self._stub = mock_stub  # pylint: disable=protected-access


async def test_components() -> None:
    """Test the components() method."""
    client = _TestClient()
    server_response = microgrid_pb2.ComponentList()
    client.mock_stub.ListComponents.return_value = server_response
    assert set(await client.components()) == set()

    server_response.components.append(
        microgrid_pb2.Component(
            id=0, category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_METER
        )
    )
    assert set(await client.components()) == {
        Component(ComponentId(0), ComponentCategory.METER)
    }

    server_response.components.append(
        microgrid_pb2.Component(
            id=0, category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_BATTERY
        )
    )
    assert set(await client.components()) == {
        Component(ComponentId(0), ComponentCategory.METER),
        Component(ComponentId(0), ComponentCategory.BATTERY),
    }

    server_response.components.append(
        microgrid_pb2.Component(
            id=0, category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_METER
        )
    )
    assert set(await client.components()) == {
        Component(ComponentId(0), ComponentCategory.METER),
        Component(ComponentId(0), ComponentCategory.BATTERY),
        Component(ComponentId(0), ComponentCategory.METER),
    }

    # sensors are not counted as components by the API client
    server_response.components.append(
        microgrid_pb2.Component(
            id=1, category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_SENSOR
        )
    )
    assert set(await client.components()) == {
        Component(ComponentId(0), ComponentCategory.METER),
        Component(ComponentId(0), ComponentCategory.BATTERY),
        Component(ComponentId(0), ComponentCategory.METER),
    }

    _replace_components(
        server_response,
        [
            microgrid_pb2.Component(
                id=9, category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_METER
            ),
            microgrid_pb2.Component(
                id=99,
                category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_INVERTER,
            ),
            microgrid_pb2.Component(
                id=666,
                category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_SENSOR,
            ),
            microgrid_pb2.Component(
                id=999,
                category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_BATTERY,
            ),
        ],
    )
    assert set(await client.components()) == {
        Component(ComponentId(9), ComponentCategory.METER),
        Component(ComponentId(99), ComponentCategory.INVERTER, InverterType.NONE),
        Component(ComponentId(999), ComponentCategory.BATTERY),
    }

    _replace_components(
        server_response,
        [
            microgrid_pb2.Component(
                id=99,
                category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_SENSOR,
            ),
            microgrid_pb2.Component(
                id=100,
                category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_UNSPECIFIED,
            ),
            microgrid_pb2.Component(
                id=104,
                category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_METER,
            ),
            microgrid_pb2.Component(
                id=105,
                category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_INVERTER,
            ),
            microgrid_pb2.Component(
                id=106,
                category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_BATTERY,
            ),
            microgrid_pb2.Component(
                id=107,
                category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_EV_CHARGER,
            ),
            microgrid_pb2.Component(
                id=999,
                category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_SENSOR,
            ),
            microgrid_pb2.Component(
                id=101,
                category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_GRID,
                grid=grid_pb2.Metadata(rated_fuse_current=int(123.0)),
            ),
        ],
    )

    grid_fuse = Fuse(123.0)

    assert set(await client.components()) == {
        Component(ComponentId(100), ComponentCategory.NONE),
        Component(
            ComponentId(101),
            ComponentCategory.GRID,
            None,
            GridMetadata(fuse=grid_fuse),
        ),
        Component(ComponentId(104), ComponentCategory.METER),
        Component(ComponentId(105), ComponentCategory.INVERTER, InverterType.NONE),
        Component(ComponentId(106), ComponentCategory.BATTERY),
        Component(ComponentId(107), ComponentCategory.EV_CHARGER),
    }

    _replace_components(
        server_response,
        [
            microgrid_pb2.Component(
                id=9, category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_METER
            ),
            microgrid_pb2.Component(
                id=666,
                category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_SENSOR,
            ),
            microgrid_pb2.Component(
                id=999,
                category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_BATTERY,
            ),
            microgrid_pb2.Component(
                id=99,
                category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_INVERTER,
                inverter=inverter_pb2.Metadata(
                    type=components_pb2.InverterType.INVERTER_TYPE_BATTERY
                ),
            ),
        ],
    )

    assert set(await client.components()) == {
        Component(ComponentId(9), ComponentCategory.METER),
        Component(ComponentId(99), ComponentCategory.INVERTER, InverterType.BATTERY),
        Component(ComponentId(999), ComponentCategory.BATTERY),
    }


async def test_components_grpc_error() -> None:
    """Test the components() method when the gRPC call fails."""
    client = _TestClient()
    client.mock_stub.ListComponents.side_effect = grpc.aio.AioRpcError(
        mock.MagicMock(name="mock_status"),
        mock.MagicMock(name="mock_initial_metadata"),
        mock.MagicMock(name="mock_trailing_metadata"),
        "fake grpc details",
        "fake grpc debug_error_string",
    )
    with pytest.raises(
        ApiClientError,
        match=r"Failed calling 'ListComponents' on 'grpc://mock_host:1234': .* "
        r"<status=<MagicMock name='mock_status\.name' id='.*'>>: fake grpc details "
        r"\(fake grpc debug_error_string\)",
    ):
        await client.components()


async def test_connections() -> None:
    """Test the connections() method."""
    client = _TestClient()

    def assert_filter(*, starts: set[int], ends: set[int]) -> None:
        client.mock_stub.ListConnections.assert_called_once()
        filter_ = client.mock_stub.ListConnections.call_args[0][0]
        assert isinstance(filter_, microgrid_pb2.ConnectionFilter)
        assert set(filter_.starts) == starts
        assert set(filter_.ends) == ends

    components_response = microgrid_pb2.ComponentList()
    connections_response = microgrid_pb2.ConnectionList()
    client.mock_stub.ListComponents.return_value = components_response
    client.mock_stub.ListConnections.return_value = connections_response
    assert set(await client.connections()) == set()
    assert_filter(starts=set(), ends=set())

    connections_response.connections.append(microgrid_pb2.Connection(start=0, end=0))
    assert set(await client.connections()) == {
        Connection(ComponentId(0), ComponentId(0))
    }

    components_response.components.extend(
        [
            microgrid_pb2.Component(
                id=7,
                category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_BATTERY,
            ),
            microgrid_pb2.Component(
                id=9,
                category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_INVERTER,
            ),
        ]
    )
    connections_response.connections.append(microgrid_pb2.Connection(start=7, end=9))
    assert set(await client.connections()) == {
        Connection(ComponentId(0), ComponentId(0)),
        Connection(ComponentId(7), ComponentId(9)),
    }

    connections_response.connections.append(microgrid_pb2.Connection(start=0, end=0))
    assert set(await client.connections()) == {
        Connection(ComponentId(0), ComponentId(0)),
        Connection(ComponentId(7), ComponentId(9)),
        Connection(ComponentId(0), ComponentId(0)),
    }

    _replace_connections(
        connections_response,
        [
            microgrid_pb2.Connection(start=999, end=9),
            microgrid_pb2.Connection(start=99, end=19),
            microgrid_pb2.Connection(start=909, end=101),
            microgrid_pb2.Connection(start=99, end=91),
        ],
    )
    for component_id in [999, 99, 19, 909, 101, 91]:
        components_response.components.append(
            microgrid_pb2.Component(
                id=component_id,
                category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_BATTERY,
            )
        )
    assert set(await client.connections()) == {
        Connection(ComponentId(999), ComponentId(9)),
        Connection(ComponentId(99), ComponentId(19)),
        Connection(ComponentId(909), ComponentId(101)),
        Connection(ComponentId(99), ComponentId(91)),
    }

    for component_id in [1, 2, 3, 4, 5, 6, 7, 8]:
        components_response.components.append(
            microgrid_pb2.Component(
                id=component_id,
                category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_BATTERY,
            )
        )
    _replace_connections(
        connections_response,
        [
            microgrid_pb2.Connection(start=1, end=2),
            microgrid_pb2.Connection(start=2, end=3),
            microgrid_pb2.Connection(start=2, end=4),
            microgrid_pb2.Connection(start=2, end=5),
            microgrid_pb2.Connection(start=4, end=3),
            microgrid_pb2.Connection(start=4, end=5),
            microgrid_pb2.Connection(start=4, end=6),
            microgrid_pb2.Connection(start=5, end=4),
            microgrid_pb2.Connection(start=5, end=7),
            microgrid_pb2.Connection(start=5, end=8),
        ],
    )
    assert set(await client.connections()) == {
        Connection(ComponentId(1), ComponentId(2)),
        Connection(ComponentId(2), ComponentId(3)),
        Connection(ComponentId(2), ComponentId(4)),
        Connection(ComponentId(2), ComponentId(5)),
        Connection(ComponentId(4), ComponentId(3)),
        Connection(ComponentId(4), ComponentId(5)),
        Connection(ComponentId(4), ComponentId(6)),
        Connection(ComponentId(5), ComponentId(4)),
        Connection(ComponentId(5), ComponentId(7)),
        Connection(ComponentId(5), ComponentId(8)),
    }

    # passing empty sets is the same as passing `None`,
    # filter is ignored
    client.mock_stub.reset_mock()
    await client.connections(starts=set(), ends=set())
    assert_filter(starts=set(), ends=set())

    # include filter for connection start
    client.mock_stub.reset_mock()
    await client.connections(starts={ComponentId(1), ComponentId(2)})
    assert_filter(starts={1, 2}, ends=set())

    client.mock_stub.reset_mock()
    await client.connections(starts={ComponentId(2)})
    assert_filter(starts={2}, ends=set())

    # include filter for connection end
    client.mock_stub.reset_mock()
    await client.connections(ends={ComponentId(1)})
    assert_filter(starts=set(), ends={1})

    client.mock_stub.reset_mock()
    await client.connections(ends={ComponentId(2), ComponentId(4), ComponentId(5)})
    assert_filter(starts=set(), ends={2, 4, 5})

    # different filters combine with AND logic
    client.mock_stub.reset_mock()
    await client.connections(
        starts={ComponentId(1), ComponentId(2), ComponentId(4)},
        ends={ComponentId(4), ComponentId(5), ComponentId(6)},
    )
    assert_filter(starts={1, 2, 4}, ends={4, 5, 6})


async def test_connections_grpc_error() -> None:
    """Test the components() method when the gRPC call fails."""
    client = _TestClient()
    client.mock_stub.ListConnections.side_effect = grpc.aio.AioRpcError(
        mock.MagicMock(name="mock_status"),
        mock.MagicMock(name="mock_initial_metadata"),
        mock.MagicMock(name="mock_trailing_metadata"),
        "fake grpc details",
        "fake grpc debug_error_string",
    )
    with pytest.raises(
        ApiClientError,
        match=r"Failed calling 'ListConnections' on 'grpc://mock_host:1234': .* "
        r"<status=<MagicMock name='mock_status\.name' id='.*'>>: fake grpc details "
        r"\(fake grpc debug_error_string\)",
    ):
        await client.connections()


@pytest.fixture
def meter83() -> microgrid_pb2.Component:
    """Return a test meter component."""
    return microgrid_pb2.Component(
        id=83, category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_METER
    )


@pytest.fixture
def battery38() -> microgrid_pb2.Component:
    """Return a test battery component."""
    return microgrid_pb2.Component(
        id=38, category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_BATTERY
    )


@pytest.fixture
def inverter99() -> microgrid_pb2.Component:
    """Return a test inverter component."""
    return microgrid_pb2.Component(
        id=99, category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_INVERTER
    )


@pytest.fixture
def ev_charger101() -> microgrid_pb2.Component:
    """Return a test EV charger component."""
    return microgrid_pb2.Component(
        id=101, category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_EV_CHARGER
    )


@pytest.fixture
def component_list(
    meter83: microgrid_pb2.Component,
    battery38: microgrid_pb2.Component,
    inverter99: microgrid_pb2.Component,
    ev_charger101: microgrid_pb2.Component,
) -> list[microgrid_pb2.Component]:
    """Return a list of test components."""
    return [meter83, battery38, inverter99, ev_charger101]


@pytest.mark.parametrize("method", ["meter_data", "battery_data", "inverter_data"])
async def test_data_component_not_found(method: str) -> None:
    """Test the meter_data() method."""
    client = _TestClient()
    client.mock_stub.ListComponents.return_value = microgrid_pb2.ComponentList()

    # It should raise a ValueError for a missing component_id
    with pytest.raises(ValueError, match="Unable to find CID20"):
        await getattr(client, method)(ComponentId(20))


@pytest.mark.parametrize(
    "method, component_id",
    [
        ("meter_data", ComponentId(38)),
        ("battery_data", ComponentId(83)),
        ("inverter_data", ComponentId(83)),
        ("ev_charger_data", ComponentId(99)),
    ],
)
async def test_data_bad_category(
    method: str,
    component_id: ComponentId,
    component_list: list[microgrid_pb2.Component],
) -> None:
    """Test the meter_data() method."""
    client = _TestClient()
    client.mock_stub.ListComponents.return_value = microgrid_pb2.ComponentList(
        components=component_list
    )

    # It should raise a ValueError for a wrong component category
    with pytest.raises(
        ValueError, match=f"{component_id} is a .*, not a {method[:-5]}"
    ):
        await getattr(client, method)(component_id)


@pytest.mark.parametrize(
    "method, component_id, component_class",
    [
        ("meter_data", ComponentId(83), MeterData),
        ("battery_data", ComponentId(38), BatteryData),
        ("inverter_data", ComponentId(99), InverterData),
        ("ev_charger_data", ComponentId(101), EVChargerData),
    ],
)
async def test_component_data(
    method: str,
    component_id: ComponentId,
    component_class: type[ComponentData],
    component_list: list[microgrid_pb2.Component],
) -> None:
    """Test the meter_data() method."""
    client = _TestClient()
    client.mock_stub.ListComponents.return_value = microgrid_pb2.ComponentList(
        components=component_list
    )

    async def stream_data(
        *args: Any, **kwargs: Any  # pylint: disable=unused-argument
    ) -> AsyncIterator[microgrid_pb2.ComponentData]:
        yield microgrid_pb2.ComponentData(id=int(component_id))

    client.mock_stub.StreamComponentData.side_effect = stream_data
    receiver = await getattr(client, method)(component_id)
    async with AsyncExitStack() as stack:
        stack.push_async_callback(
            client._broadcasters[component_id].stop  # pylint: disable=protected-access
        )
        latest = await receiver.receive()
        assert isinstance(latest, component_class)
        assert latest.component_id == component_id


@pytest.mark.parametrize(
    "method, component_id, component_class",
    [
        ("meter_data", ComponentId(83), MeterData),
        ("battery_data", ComponentId(38), BatteryData),
        ("inverter_data", ComponentId(99), InverterData),
        ("ev_charger_data", ComponentId(101), EVChargerData),
    ],
)
async def test_component_data_grpc_error(
    method: str,
    component_id: ComponentId,
    component_class: type[ComponentData],
    component_list: list[microgrid_pb2.Component],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the components() method when the gRPC call fails."""
    caplog.set_level(logging.WARNING)
    client = _TestClient(
        retry_strategy=retry.LinearBackoff(interval=0.0, jitter=0.0, limit=6)
    )
    client.mock_stub.ListComponents.return_value = microgrid_pb2.ComponentList(
        components=component_list
    )

    num_calls = 0

    async def stream_data(
        *args: Any, **kwargs: Any  # pylint: disable=unused-argument
    ) -> AsyncIterator[microgrid_pb2.ComponentData]:
        nonlocal num_calls
        num_calls += 1
        if num_calls % 2:
            raise grpc.aio.AioRpcError(
                mock.MagicMock(name="mock_status"),
                mock.MagicMock(name="mock_initial_metadata"),
                mock.MagicMock(name="mock_trailing_metadata"),
                f"fake grpc details num_calls={num_calls}",
                "fake grpc debug_error_string",
            )
        yield microgrid_pb2.ComponentData(id=int(component_id))

    client.mock_stub.StreamComponentData.side_effect = stream_data
    receiver = await getattr(client, method)(component_id)
    async with AsyncExitStack() as stack:
        stack.push_async_callback(
            client._broadcasters[component_id].stop  # pylint: disable=protected-access
        )
        latest = await receiver.receive()
        assert isinstance(latest, component_class)
        assert latest.component_id == component_id

        latest = await receiver.receive()
        assert isinstance(latest, component_class)
        assert latest.component_id == component_id

        latest = await receiver.receive()
        assert isinstance(latest, component_class)
        assert latest.component_id == component_id

    # This is not super portable, it will change if the GrpcStreamBroadcaster changes,
    # but without this there isn't much to check by this test.
    assert len(caplog.record_tuples) == 6
    for n, log_tuple in enumerate(caplog.record_tuples):
        assert log_tuple[0] == "frequenz.client.base.streaming"
        assert log_tuple[1] == logging.WARNING
        assert (
            f"raw-component-data-{component_id}: connection ended, retrying"
            in log_tuple[2]
        )
        if n % 2:
            assert "Stream exhausted" in log_tuple[2]
        else:
            assert f"fake grpc details num_calls={n+1}" in log_tuple[2]


@pytest.mark.parametrize("power_w", [0, 0.0, 12, -75, 0.1, -0.0001, 134.0])
async def test_set_power_ok(power_w: float, meter83: microgrid_pb2.Component) -> None:
    """Test if charge is able to charge component."""
    client = _TestClient()
    client.mock_stub.ListComponents.return_value = microgrid_pb2.ComponentList(
        components=[meter83]
    )

    component_id = ComponentId(83)
    await client.set_power(component_id=component_id, power_w=power_w)
    client.mock_stub.SetPowerActive.assert_called_once()
    call_args = client.mock_stub.SetPowerActive.call_args[0]
    assert call_args[0] == microgrid_pb2.SetPowerActiveParam(
        component_id=int(component_id), power=power_w
    )


async def test_set_power_grpc_error() -> None:
    """Test set_power() raises ApiClientError when the gRPC call fails."""
    client = _TestClient()
    client.mock_stub.SetPowerActive.side_effect = grpc.aio.AioRpcError(
        mock.MagicMock(name="mock_status"),
        mock.MagicMock(name="mock_initial_metadata"),
        mock.MagicMock(name="mock_trailing_metadata"),
        "fake grpc details",
        "fake grpc debug_error_string",
    )
    with pytest.raises(
        ApiClientError,
        match=r"Failed calling 'SetPowerActive' on 'grpc://mock_host:1234': .* "
        r"<status=<MagicMock name='mock_status\.name' id='.*'>>: fake grpc details "
        r"\(fake grpc debug_error_string\)",
    ):
        await client.set_power(component_id=ComponentId(83), power_w=100.0)


@pytest.mark.parametrize(
    "reactive_power_var",
    [0, 0.0, 12, -75, 0.1, -0.0001, 134.0],
)
async def test_set_reactive_power_ok(
    reactive_power_var: float, meter83: microgrid_pb2.Component
) -> None:
    """Test if charge is able to charge component."""
    client = _TestClient()
    client.mock_stub.ListComponents.return_value = microgrid_pb2.ComponentList(
        components=[meter83]
    )

    component_id = ComponentId(83)
    await client.set_reactive_power(
        component_id=component_id, reactive_power_var=reactive_power_var
    )
    client.mock_stub.SetPowerReactive.assert_called_once()
    call_args = client.mock_stub.SetPowerReactive.call_args[0]
    assert call_args[0] == microgrid_pb2.SetPowerReactiveParam(
        component_id=int(component_id), power=reactive_power_var
    )


async def test_set_reactive_power_grpc_error() -> None:
    """Test set_power() raises ApiClientError when the gRPC call fails."""
    client = _TestClient()
    client.mock_stub.SetPowerReactive.side_effect = grpc.aio.AioRpcError(
        mock.MagicMock(name="mock_status"),
        mock.MagicMock(name="mock_initial_metadata"),
        mock.MagicMock(name="mock_trailing_metadata"),
        "fake grpc details",
        "fake grpc debug_error_string",
    )
    with pytest.raises(
        ApiClientError,
        match=r"Failed calling 'SetPowerReactive' on 'grpc://mock_host:1234': .* "
        r"<status=<MagicMock name='mock_status\.name' id='.*'>>: fake grpc details "
        r"\(fake grpc debug_error_string\)",
    ):
        await client.set_reactive_power(
            component_id=ComponentId(83), reactive_power_var=100.0
        )


@pytest.mark.parametrize(
    "bounds",
    [
        metrics_pb2.Bounds(lower=0.0, upper=0.0),
        metrics_pb2.Bounds(lower=0.0, upper=2.0),
        metrics_pb2.Bounds(lower=-10.0, upper=0.0),
        metrics_pb2.Bounds(lower=-10.0, upper=2.0),
    ],
    ids=str,
)
async def test_set_bounds_ok(
    bounds: metrics_pb2.Bounds, inverter99: microgrid_pb2.Component
) -> None:
    """Test if charge is able to charge component."""
    client = _TestClient()
    client.mock_stub.ListComponents.return_value = microgrid_pb2.ComponentList(
        components=[inverter99]
    )

    component_id = ComponentId(99)
    await client.set_bounds(component_id, bounds.lower, bounds.upper)
    client.mock_stub.AddInclusionBounds.assert_called_once()
    call_args = client.mock_stub.AddInclusionBounds.call_args[0]
    assert call_args[0] == microgrid_pb2.SetBoundsParam(
        component_id=int(component_id),
        target_metric=microgrid_pb2.SetBoundsParam.TargetMetric.TARGET_METRIC_POWER_ACTIVE,
        bounds=bounds,
    )


@pytest.mark.parametrize(
    "bounds",
    [
        metrics_pb2.Bounds(lower=0.0, upper=-2.0),
        metrics_pb2.Bounds(lower=10.0, upper=-2.0),
        metrics_pb2.Bounds(lower=10.0, upper=0.0),
    ],
    ids=str,
)
async def test_set_bounds_fail(
    bounds: metrics_pb2.Bounds, inverter99: microgrid_pb2.Component
) -> None:
    """Test if charge is able to charge component."""
    client = _TestClient()
    client.mock_stub.ListComponents.return_value = microgrid_pb2.ComponentList(
        components=[inverter99]
    )

    with pytest.raises(ValueError):
        await client.set_bounds(ComponentId(99), bounds.lower, bounds.upper)
    client.mock_stub.AddInclusionBounds.assert_not_called()


async def test_set_bounds_grpc_error() -> None:
    """Test the components() method when the gRPC call fails."""
    client = _TestClient()
    client.mock_stub.AddInclusionBounds.side_effect = grpc.aio.AioRpcError(
        mock.MagicMock(name="mock_status"),
        mock.MagicMock(name="mock_initial_metadata"),
        mock.MagicMock(name="mock_trailing_metadata"),
        "fake grpc details",
        "fake grpc debug_error_string",
    )
    with pytest.raises(
        ApiClientError,
        match=r"Failed calling 'AddInclusionBounds' on 'grpc://mock_host:1234': .* "
        r"<status=<MagicMock name='mock_status\.name' id='.*'>>: fake grpc details "
        r"\(fake grpc debug_error_string\)",
    ):
        await client.set_bounds(ComponentId(99), 0.0, 100.0)


def _clear_components(component_list: microgrid_pb2.ComponentList) -> None:
    while component_list.components:
        component_list.components.pop()


def _replace_components(
    component_list: microgrid_pb2.ComponentList,
    components: list[microgrid_pb2.Component],
) -> None:
    _clear_components(component_list)
    component_list.components.extend(components)


def _clear_connections(connection_list: microgrid_pb2.ConnectionList) -> None:
    while connection_list.connections:
        connection_list.connections.pop()


def _replace_connections(
    connection_list: microgrid_pb2.ConnectionList,
    connections: list[microgrid_pb2.Connection],
) -> None:
    _clear_connections(connection_list)
    connection_list.connections.extend(connections)
