# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Client for requests to the Microgrid API."""

from __future__ import annotations

import asyncio
import itertools
import logging
from collections.abc import Callable, Iterable, Set
from dataclasses import replace
from functools import partial
from typing import Any, NotRequired, TypedDict, TypeVar, assert_never

from frequenz.api.common import components_pb2, metrics_pb2
from frequenz.api.microgrid import microgrid_pb2, microgrid_pb2_grpc, sensor_pb2
from frequenz.channels import Receiver
from frequenz.client.base import channel, client, retry, streaming
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.components import ComponentId
from frequenz.client.common.microgrid.sensors import SensorId
from google.protobuf.empty_pb2 import Empty
from typing_extensions import override

from ._component import (
    Component,
    ComponentCategory,
    component_category_from_protobuf,
    component_metadata_from_protobuf,
    component_type_from_protobuf,
)
from ._component_data import (
    BatteryData,
    ComponentData,
    EVChargerData,
    InverterData,
    MeterData,
)
from ._connection import Connection
from ._constants import RECEIVER_MAX_SIZE
from ._exception import ApiClientError, ClientNotConnected
from ._metadata import Location, Metadata
from ._sensor_proto import sensor_data_samples_from_proto, sensor_from_proto
from .sensor import Sensor, SensorDataSamples, SensorMetric

DEFAULT_GRPC_CALL_TIMEOUT = 60.0
"""The default timeout for gRPC calls made by this client (in seconds)."""

_ComponentDataT = TypeVar("_ComponentDataT", bound=ComponentData)
"""Type variable resolving to any ComponentData sub-class."""

_logger = logging.getLogger(__name__)


DEFAULT_CHANNEL_OPTIONS = replace(
    channel.ChannelOptions(), ssl=channel.SslOptions(enabled=False)
)
"""The default channel options for the microgrid API client.

These are the same defaults as the common default options but with SSL disabled, as the
microgrid API does not use SSL by default.
"""


class MicrogridApiClient(client.BaseApiClient[microgrid_pb2_grpc.MicrogridStub]):
    """A microgrid API client."""

    def __init__(
        self,
        server_url: str,
        *,
        channel_defaults: channel.ChannelOptions = DEFAULT_CHANNEL_OPTIONS,
        connect: bool = True,
        retry_strategy: retry.Strategy | None = None,
    ) -> None:
        """Initialize the class instance.

        Args:
            server_url: The location of the microgrid API server in the form of a URL.
                The following format is expected:
                "grpc://hostname{:`port`}{?ssl=`ssl`}",
                where the `port` should be an int between 0 and 65535 (defaulting to
                9090) and `ssl` should be a boolean (defaulting to `false`).
                For example: `grpc://localhost:1090?ssl=true`.
            channel_defaults: The default options use to create the channel when not
                specified in the URL.
            connect: Whether to connect to the server as soon as a client instance is
                created. If `False`, the client will not connect to the server until
                [connect()][frequenz.client.base.client.BaseApiClient.connect] is
                called.
            retry_strategy: The retry strategy to use to reconnect when the connection
                to the streaming method is lost. By default a linear backoff strategy
                is used.
        """
        super().__init__(
            server_url,
            microgrid_pb2_grpc.MicrogridStub,
            connect=connect,
            channel_defaults=channel_defaults,
        )
        self._broadcasters: dict[
            ComponentId, streaming.GrpcStreamBroadcaster[Any, Any]
        ] = {}
        self._sensor_data_broadcasters: dict[
            str,
            streaming.GrpcStreamBroadcaster[
                microgrid_pb2.ComponentData, SensorDataSamples
            ],
        ] = {}
        self._retry_strategy = retry_strategy

    @property
    def stub(self) -> microgrid_pb2_grpc.MicrogridAsyncStub:
        """The gRPC stub for the API."""
        if self.channel is None or self._stub is None:
            raise ClientNotConnected(server_url=self.server_url, operation="stub")
        # This type: ignore is needed because we need to cast the sync stub to
        # the async stub, but we can't use cast because the async stub doesn't
        # actually exists to the eyes of the interpreter, it only exists for the
        # type-checker, so it can only be used for type hints.
        return self._stub  # type: ignore

    @override
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> bool | None:
        """Close the gRPC channel and stop all broadcasters."""
        exceptions = list(
            exc
            for exc in await asyncio.gather(
                *(
                    broadcaster.stop()
                    for broadcaster in itertools.chain(
                        self._broadcasters.values(),
                        self._sensor_data_broadcasters.values(),
                    )
                ),
                return_exceptions=True,
            )
            if isinstance(exc, BaseException)
        )
        self._broadcasters.clear()
        self._sensor_data_broadcasters.clear()

        result = None
        try:
            result = await super().__aexit__(exc_type, exc_val, exc_tb)
        except Exception as exc:  # pylint: disable=broad-except
            exceptions.append(exc)
        if exceptions:
            raise BaseExceptionGroup(
                "Error while disconnecting from the microgrid API", exceptions
            )
        return result

    async def components(  # noqa: DOC502 (raises ApiClientError indirectly)
        self,
    ) -> Iterable[Component]:
        """Fetch all the components present in the microgrid.

        Returns:
            Iterator whose elements are all the components in the microgrid.

        Raises:
            ApiClientError: If the are any errors communicating with the Microgrid API,
                most likely a subclass of
                [GrpcError][frequenz.client.microgrid.GrpcError].
        """
        component_list = await client.call_stub_method(
            self,
            lambda: self.stub.ListComponents(
                microgrid_pb2.ComponentFilter(),
                timeout=int(DEFAULT_GRPC_CALL_TIMEOUT),
            ),
            method_name="ListComponents",
        )

        components_only = filter(
            lambda c: c.category
            is not components_pb2.ComponentCategory.COMPONENT_CATEGORY_SENSOR,
            component_list.components,
        )
        result: Iterable[Component] = map(
            lambda c: Component(
                ComponentId(c.id),
                component_category_from_protobuf(c.category),
                component_type_from_protobuf(c.category, c.inverter),
                component_metadata_from_protobuf(c.category, c.grid),
            ),
            components_only,
        )

        return result

    async def list_sensors(  # noqa: DOC502 (raises ApiClientError indirectly)
        self,
    ) -> Iterable[Sensor]:
        """Fetch all the sensors present in the microgrid.

        Returns:
            Iterator whose elements are all the sensors in the microgrid.

        Raises:
            ApiClientError: If the are any errors communicating with the Microgrid API,
                most likely a subclass of
                [GrpcError][frequenz.client.microgrid.GrpcError].
        """
        component_list = await client.call_stub_method(
            self,
            lambda: self.stub.ListComponents(
                microgrid_pb2.ComponentFilter(
                    categories=[
                        components_pb2.ComponentCategory.COMPONENT_CATEGORY_SENSOR
                    ]
                ),
                timeout=int(DEFAULT_GRPC_CALL_TIMEOUT),
            ),
            method_name="ListComponents",
        )
        return map(sensor_from_proto, component_list.components)

    async def metadata(self) -> Metadata:
        """Fetch the microgrid metadata.

        If there is an error fetching the metadata, the microgrid ID and
        location will be set to None.

        Returns:
            the microgrid metadata.
        """
        microgrid_metadata: microgrid_pb2.MicrogridMetadata | None = None
        try:
            microgrid_metadata = await client.call_stub_method(
                self,
                lambda: self.stub.GetMicrogridMetadata(
                    Empty(),
                    timeout=int(DEFAULT_GRPC_CALL_TIMEOUT),
                ),
                method_name="GetMicrogridMetadata",
            )
        except ApiClientError:
            _logger.exception("The microgrid metadata is not available.")

        if not microgrid_metadata:
            return Metadata()

        location: Location | None = None
        if microgrid_metadata.HasField("location"):
            location = Location(
                latitude=microgrid_metadata.location.latitude,
                longitude=microgrid_metadata.location.longitude,
            )

        return Metadata(
            microgrid_id=MicrogridId(microgrid_metadata.microgrid_id), location=location
        )

    async def connections(  # noqa: DOC502 (raises ApiClientError indirectly)
        self,
        starts: Set[ComponentId] = frozenset(),
        ends: Set[ComponentId] = frozenset(),
    ) -> Iterable[Connection]:
        """Fetch the connections between components in the microgrid.

        Args:
            starts: if set and non-empty, only include connections whose start
                value matches one of the provided component IDs
            ends: if set and non-empty, only include connections whose end value
                matches one of the provided component IDs

        Returns:
            Microgrid connections matching the provided start and end filters.

        Raises:
            ApiClientError: If the are any errors communicating with the Microgrid API,
                most likely a subclass of
                [GrpcError][frequenz.client.microgrid.GrpcError].
        """
        # Convert ComponentId to raw int for the API call
        start_ids = {int(start) for start in starts}
        end_ids = {int(end) for end in ends}

        connection_filter = microgrid_pb2.ConnectionFilter(
            starts=start_ids, ends=end_ids
        )
        valid_components, all_connections = await asyncio.gather(
            self.components(),
            client.call_stub_method(
                self,
                lambda: self.stub.ListConnections(
                    connection_filter,
                    timeout=int(DEFAULT_GRPC_CALL_TIMEOUT),
                ),
                method_name="ListConnections",
            ),
        )

        # Filter out the components filtered in `components` method.
        # id=0 is an exception indicating grid component.
        valid_ids = {int(c.component_id) for c in valid_components}
        valid_ids.add(0)

        connections = filter(
            lambda c: (c.start in valid_ids and c.end in valid_ids),
            all_connections.connections,
        )

        result: Iterable[Connection] = map(
            lambda c: Connection(ComponentId(c.start), ComponentId(c.end)), connections
        )

        return result

    async def _new_component_data_receiver(
        self,
        *,
        component_id: ComponentId,
        expected_category: ComponentCategory,
        transform: Callable[[microgrid_pb2.ComponentData], _ComponentDataT],
        maxsize: int,
    ) -> Receiver[_ComponentDataT]:
        """Return a new broadcaster receiver for a given `component_id`.

        If a broadcaster for the given `component_id` doesn't exist, it creates a new
        one.

        Args:
            component_id: id of the component to get data for.
            expected_category: Category of the component to get data for.
            transform: A method for transforming raw component data into the
                desired output type.
            maxsize: Size of the receiver's buffer.

        Returns:
            The new receiver for the given `component_id`.
        """
        await self._expect_category(
            component_id,
            expected_category,
        )

        broadcaster = self._broadcasters.get(component_id)
        if broadcaster is None:
            broadcaster = streaming.GrpcStreamBroadcaster(
                f"raw-component-data-{component_id}",
                lambda: aiter(
                    self.stub.StreamComponentData(
                        microgrid_pb2.ComponentIdParam(id=int(component_id))
                    )
                ),
                transform,
                retry_strategy=self._retry_strategy,
                # We don't expect any data stream to end, so if it is exhausted for any
                # reason we want to keep retrying
                retry_on_exhausted_stream=True,
            )
            self._broadcasters[component_id] = broadcaster
        return broadcaster.new_receiver(maxsize=maxsize)

    async def _expect_category(
        self,
        component_id: ComponentId,
        expected_category: ComponentCategory,
    ) -> None:
        """Check if the given component_id is of the expected type.

        Raises:
            ValueError: if the given id is unknown or has a different type.

        Args:
            component_id: Component id to check.
            expected_category: Component category that the given id is expected
                to have.
        """
        try:
            comp = next(
                comp
                for comp in await self.components()
                if comp.component_id == component_id
            )
        except StopIteration as exc:
            raise ValueError(f"Unable to find {component_id}") from exc

        if comp.category != expected_category:
            raise ValueError(
                f"{component_id} is a {comp.category.name.lower()}"
                f", not a {expected_category.name.lower()}."
            )

    async def meter_data(  # noqa: DOC502 (ValueError is raised indirectly by _expect_category)
        self,
        component_id: ComponentId,
        maxsize: int = RECEIVER_MAX_SIZE,
    ) -> Receiver[MeterData]:
        """Return a channel receiver that provides a `MeterData` stream.

        Raises:
            ValueError: if the given id is unknown or has a different type.

        Args:
            component_id: id of the meter to get data for.
            maxsize: Size of the receiver's buffer.

        Returns:
            A channel receiver that provides realtime meter data.
        """
        return await self._new_component_data_receiver(
            component_id=component_id,
            expected_category=ComponentCategory.METER,
            transform=MeterData.from_proto,
            maxsize=maxsize,
        )

    async def battery_data(  # noqa: DOC502 (ValueError is raised indirectly by _expect_category)
        self,
        component_id: ComponentId,
        maxsize: int = RECEIVER_MAX_SIZE,
    ) -> Receiver[BatteryData]:
        """Return a channel receiver that provides a `BatteryData` stream.

        Raises:
            ValueError: if the given id is unknown or has a different type.

        Args:
            component_id: id of the battery to get data for.
            maxsize: Size of the receiver's buffer.

        Returns:
            A channel receiver that provides realtime battery data.
        """
        return await self._new_component_data_receiver(
            component_id=component_id,
            expected_category=ComponentCategory.BATTERY,
            transform=BatteryData.from_proto,
            maxsize=maxsize,
        )

    async def inverter_data(  # noqa: DOC502 (ValueError is raised indirectly by _expect_category)
        self,
        component_id: ComponentId,
        maxsize: int = RECEIVER_MAX_SIZE,
    ) -> Receiver[InverterData]:
        """Return a channel receiver that provides an `InverterData` stream.

        Raises:
            ValueError: if the given id is unknown or has a different type.

        Args:
            component_id: id of the inverter to get data for.
            maxsize: Size of the receiver's buffer.

        Returns:
            A channel receiver that provides realtime inverter data.
        """
        return await self._new_component_data_receiver(
            component_id=component_id,
            expected_category=ComponentCategory.INVERTER,
            transform=InverterData.from_proto,
            maxsize=maxsize,
        )

    async def ev_charger_data(  # noqa: DOC502 (ValueError is raised indirectly by _expect_category)
        self,
        component_id: ComponentId,
        maxsize: int = RECEIVER_MAX_SIZE,
    ) -> Receiver[EVChargerData]:
        """Return a channel receiver that provides an `EvChargeData` stream.

        Raises:
            ValueError: if the given id is unknown or has a different type.

        Args:
            component_id: id of the ev charger to get data for.
            maxsize: Size of the receiver's buffer.

        Returns:
            A channel receiver that provides realtime ev charger data.
        """
        return await self._new_component_data_receiver(
            component_id=component_id,
            expected_category=ComponentCategory.EV_CHARGER,
            transform=EVChargerData.from_proto,
            maxsize=maxsize,
        )

    async def set_power(  # noqa: DOC502 (raises ApiClientError indirectly)
        self, component_id: ComponentId, power_w: float
    ) -> None:
        """Send request to the Microgrid to set power for component.

        If power > 0, then component will be charged with this power.
        If power < 0, then component will be discharged with this power.
        If power == 0, then stop charging or discharging component.


        Args:
            component_id: id of the component to set power.
            power_w: power to set for the component.

        Raises:
            ApiClientError: If the are any errors communicating with the Microgrid API,
                most likely a subclass of
                [GrpcError][frequenz.client.microgrid.GrpcError].
        """
        await client.call_stub_method(
            self,
            lambda: self.stub.SetPowerActive(
                microgrid_pb2.SetPowerActiveParam(
                    component_id=int(component_id), power=power_w
                ),
                timeout=int(DEFAULT_GRPC_CALL_TIMEOUT),
            ),
            method_name="SetPowerActive",
        )

    async def set_reactive_power(  # noqa: DOC502 (raises ApiClientError indirectly)
        self, component_id: ComponentId, reactive_power_var: float
    ) -> None:
        """Send request to the Microgrid to set reactive power for component.

        Negative values are for inductive (lagging) power , and positive values are for
        capacitive (leading) power.

        Args:
            component_id: id of the component to set power.
            reactive_power_var: reactive power to set for the component.

        Raises:
            ApiClientError: If the are any errors communicating with the Microgrid API,
                most likely a subclass of
                [GrpcError][frequenz.client.microgrid.GrpcError].
        """
        await client.call_stub_method(
            self,
            lambda: self.stub.SetPowerReactive(
                microgrid_pb2.SetPowerReactiveParam(
                    component_id=int(component_id), power=reactive_power_var
                ),
                timeout=int(DEFAULT_GRPC_CALL_TIMEOUT),
            ),
            method_name="SetPowerReactive",
        )

    async def set_bounds(  # noqa: DOC503 (raises ApiClientError indirectly)
        self,
        component_id: ComponentId,
        lower: float,
        upper: float,
    ) -> None:
        """Send `SetBoundsParam`s received from a channel to the Microgrid service.

        Args:
            component_id: ID of the component to set bounds for.
            lower: Lower bound to be set for the component.
            upper: Upper bound to be set for the component.

        Raises:
            ValueError: when upper bound is less than 0, or when lower bound is
                greater than 0.
            ApiClientError: If the are any errors communicating with the Microgrid API,
                most likely a subclass of
                [GrpcError][frequenz.client.microgrid.GrpcError].
        """
        if upper < 0:
            raise ValueError(f"Upper bound {upper} must be greater than or equal to 0.")
        if lower > 0:
            raise ValueError(f"Lower bound {lower} must be less than or equal to 0.")

        target_metric = (
            microgrid_pb2.SetBoundsParam.TargetMetric.TARGET_METRIC_POWER_ACTIVE
        )
        await client.call_stub_method(
            self,
            lambda: self.stub.AddInclusionBounds(
                microgrid_pb2.SetBoundsParam(
                    component_id=int(component_id),
                    target_metric=target_metric,
                    bounds=metrics_pb2.Bounds(lower=lower, upper=upper),
                ),
                timeout=int(DEFAULT_GRPC_CALL_TIMEOUT),
            ),
            method_name="AddInclusionBounds",
        )

    # noqa: DOC502 (Raises ApiClientError indirectly)
    def stream_sensor_data(
        self,
        sensor: SensorId | Sensor,
        metrics: Iterable[SensorMetric | int] | None = None,
        *,
        buffer_size: int = 50,
    ) -> Receiver[SensorDataSamples]:
        """Stream data samples from a sensor.

        Warning:
            Sensors may not support all metrics. If a sensor does not support
            a given metric, then the returned data stream will not contain that metric.

            There is no way to tell if a metric is not being received because the
            sensor does not support it or because there is a transient issue when
            retrieving the metric from the sensor.

            The supported metrics by a sensor can even change with time, for example,
            if a sensor is updated with new firmware.

        Args:
            sensor: The sensor to stream data from.
            metrics: If not `None`, only the specified metrics will be retrieved.
                Otherwise all available metrics will be retrieved.
            buffer_size: The maximum number of messages to buffer in the returned
                receiver. After this limit is reached, the oldest messages will be
                dropped.

        Returns:
            A receiver to retrieve data from the sensor.
        """
        sensor_id = _get_sensor_id(sensor)
        key = str(sensor_id)

        class _ExtraArgs(TypedDict):
            metrics: NotRequired[frozenset[sensor_pb2.SensorMetric.ValueType]]

        extra_args: _ExtraArgs = {}
        if metrics is not None:
            extra_args["metrics"] = frozenset(
                [_get_sensor_metric_value(m) for m in metrics]
            )
            # We use the frozenset because iterables are not hashable
            key += f"{hash(extra_args['metrics'])}"

        broadcaster = self._sensor_data_broadcasters.get(key)
        if broadcaster is None:
            client_id = hex(id(self))[2:]
            stream_name = f"microgrid-client-{client_id}-sensor-data-{key}"
            broadcaster = streaming.GrpcStreamBroadcaster(
                stream_name,
                lambda: aiter(
                    self.stub.StreamComponentData(
                        microgrid_pb2.ComponentIdParam(id=sensor_id),
                        timeout=DEFAULT_GRPC_CALL_TIMEOUT,
                    )
                ),
                partial(sensor_data_samples_from_proto, **extra_args),
                retry_strategy=self._retry_strategy,
            )
            self._sensor_data_broadcasters[key] = broadcaster
        return broadcaster.new_receiver(maxsize=buffer_size)


def _get_sensor_id(sensor: SensorId | Sensor) -> int:
    """Get the sensor ID from a sensor or sensor ID."""
    match sensor:
        case SensorId():
            return int(sensor)
        case Sensor():
            return int(sensor.id)
        case unexpected:
            assert_never(unexpected)


def _get_sensor_metric_value(
    metric: SensorMetric | int,
) -> sensor_pb2.SensorMetric.ValueType:
    """Get the sensor metric ID from a sensor metric or sensor metric ID."""
    match metric:
        case SensorMetric():
            return sensor_pb2.SensorMetric.ValueType(metric.value)
        case int():
            return sensor_pb2.SensorMetric.ValueType(metric)
        case unexpected:
            assert_never(unexpected)
