# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Client for requests to the Microgrid API."""

from __future__ import annotations

import asyncio
import enum
import itertools
import math
from collections.abc import Iterable
from dataclasses import replace
from datetime import datetime, timedelta
from typing import Any, assert_never

from frequenz.api.common.v1alpha8.metrics import bounds_pb2, metrics_pb2
from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.api.microgrid.v1alpha18 import microgrid_pb2, microgrid_pb2_grpc
from frequenz.channels import Receiver
from frequenz.client.base import channel, client, conversion, retry, streaming
from frequenz.client.base.exception import ApiClientError
from frequenz.client.common.microgrid.components import ComponentId
from google.protobuf.empty_pb2 import Empty
from grpc.aio import AioRpcError
from typing_extensions import override

from ._exception import ClientNotConnected
from ._microgrid_info import MicrogridInfo
from ._microgrid_info_proto import microgrid_info_from_proto
from .component._category import ComponentCategory
from .component._component import Component
from .component._component_proto import component_from_proto
from .component._connection import ComponentConnection
from .component._connection_proto import component_connection_from_proto
from .component._data_samples import ComponentDataSamples
from .component._data_samples_proto import component_data_samples_from_proto
from .component._types import ComponentTypes
from .metrics._bounds import Bounds
from .metrics._metric import Metric

DEFAULT_GRPC_CALL_TIMEOUT = 60.0
"""The default timeout for gRPC calls made by this client (in seconds)."""


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
        self._component_data_broadcasters: dict[
            str,
            streaming.GrpcStreamBroadcaster[
                microgrid_pb2.ReceiveElectricalComponentTelemetryStreamResponse,
                ComponentDataSamples,
            ],
        ] = {}
        self._sensor_data_broadcasters: dict[
            str,
            streaming.GrpcStreamBroadcaster[Any, Any],
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
                        self._component_data_broadcasters.values(),
                        self._sensor_data_broadcasters.values(),
                    )
                ),
                return_exceptions=True,
            )
            if isinstance(exc, BaseException)
        )
        self._component_data_broadcasters.clear()
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

    async def get_microgrid_info(  # noqa: DOC502 (raises ApiClientError indirectly)
        self,
    ) -> MicrogridInfo:
        """Retrieve information about the local microgrid.

        This consists of information about the overall microgrid, for example, the
        microgrid ID and its location.  It does not include information about the
        electrical components or sensors in the microgrid.

        Returns:
            The information about the local microgrid.

        Raises:
            ApiClientError: If there are any errors communicating with the Microgrid API,
                most likely a subclass of
                [GrpcError][frequenz.client.microgrid.GrpcError].
        """
        response = await client.call_stub_method(
            self,
            lambda: self.stub.GetMicrogrid(Empty(), timeout=DEFAULT_GRPC_CALL_TIMEOUT),
            method_name="GetMicrogridMetadata",
        )

        return microgrid_info_from_proto(response.microgrid)

    async def list_components(  # noqa: DOC502 (raises ApiClientError indirectly)
        self,
        *,
        components: Iterable[ComponentId | Component] = (),
        categories: Iterable[ComponentCategory | int] = (),
    ) -> Iterable[ComponentTypes]:
        """Fetch all the components present in the local microgrid.

        Electrical components are a part of a microgrid's electrical infrastructure
        are can be connected to each other to form an electrical circuit, which can
        then be represented as a graph.

        If provided, the filters for component and categories have an `AND`
        relationship with one another, meaning that they are applied serially,
        but the elements within a single filter list have an `OR` relationship with
        each other.

        Example:
            If `ids = {1, 2, 3}`, and `categories = {ComponentCategory.INVERTER,
            ComponentCategory.BATTERY}`, then the results will consist of elements that
            have:

            * The IDs 1, `OR` 2, `OR` 3; `AND`
            * Are of the categories `ComponentCategory.INVERTER` `OR`
              `ComponentCategory.BATTERY`.

        If a filter list is empty, then that filter is not applied.

        Args:
            components: The components to fetch. See the method description for details.
            categories: The categories of the components to fetch. See the method
                description for details.

        Returns:
            Iterator whose elements are all the components in the local microgrid.

        Raises:
            ApiClientError: If the are any errors communicating with the Microgrid API,
                most likely a subclass of
                [GrpcError][frequenz.client.microgrid.GrpcError].
        """
        response = await client.call_stub_method(
            self,
            lambda: self.stub.ListElectricalComponents(
                microgrid_pb2.ListElectricalComponentsRequest(
                    electrical_component_ids=map(_get_component_id, components),
                    electrical_component_categories=map(
                        _get_category_value, categories
                    ),
                ),
                timeout=DEFAULT_GRPC_CALL_TIMEOUT,
            ),
            method_name="ListComponents",
        )

        return map(component_from_proto, response.electrical_components)

    async def list_connections(  # noqa: DOC502 (raises ApiClientError indirectly)
        self,
        *,
        sources: Iterable[ComponentId | Component] = (),
        destinations: Iterable[ComponentId | Component] = (),
    ) -> Iterable[ComponentConnection]:
        """Fetch all the connections present in the local microgrid.

        Electrical components are a part of a microgrid's electrical infrastructure
        are can be connected to each other to form an electrical circuit, which can
        then be represented as a graph.

        The direction of a connection is always away from the grid endpoint, i.e.
        aligned with the direction of positive current according to the passive sign
        convention: https://en.wikipedia.org/wiki/Passive_sign_convention

        The request may be filtered by `source`/`destination` component(s) of individual
        connections.  If provided, the `sources` and `destinations` filters have an
        `AND` relationship between each other, meaning that they are applied serially,
        but an `OR` relationship with other elements in the same list.

        Example:
            If `sources = {1, 2, 3}`, and `destinations = {4,
            5, 6}`, then the result should have all the connections where:

            * Each `source` component ID is either `1`, `2`, OR `3`; **AND**
            * Each `destination` component ID is either `4`, `5`, OR `6`.

        Args:
            sources: The component from which the connections originate.
            destinations: The component at which the connections terminate.

        Returns:
            Iterator whose elements are all the connections in the local microgrid.

        Raises:
            ApiClientError: If the are any errors communicating with the Microgrid API,
                most likely a subclass of
                [GrpcError][frequenz.client.microgrid.GrpcError].
        """
        response = await client.call_stub_method(
            self,
            lambda: self.stub.ListElectricalComponentConnections(
                microgrid_pb2.ListElectricalComponentConnectionsRequest(
                    source_electrical_component_ids=map(_get_component_id, sources),
                    destination_electrical_component_ids=map(
                        _get_component_id, destinations
                    ),
                ),
                timeout=DEFAULT_GRPC_CALL_TIMEOUT,
            ),
            method_name="ListConnections",
        )

        return (
            conn
            for conn in map(
                component_connection_from_proto,
                response.electrical_component_connections,
            )
            if conn is not None
        )

    # pylint: disable-next=fixme
    # TODO: Unifi set_component_power_active and set_component_power_reactive, or at
    #       least use a common implementation.
    #       Return an iterator or receiver with the streamed responses instead of
    #       returning just the first one
    async def set_component_power_active(  # noqa: DOC503
        self,
        component: ComponentId | Component,
        power: float,
        *,
        request_lifetime: timedelta | None = None,
        validate_arguments: bool = True,
    ) -> datetime | None:
        """Set the active power output of a component.

        The power output can be negative or positive, depending on whether the component
        is supposed to be discharging or charging, respectively.

        The power output is specified in watts.

        The return value is the timestamp until which the given power command will
        stay in effect. After this timestamp, the component's active power will be
        set to 0, if the API receives no further command to change it before then.
        By default, this timestamp will be set to the current time plus 60 seconds.

        Note:
            The target component may have a resolution of more than 1 W. E.g., an
            inverter may have a resolution of 88 W. In such cases, the magnitude of
            power will be floored to the nearest multiple of the resolution.

        Args:
            component: The component to set the output active power of.
            power: The output active power level, in watts. Negative values are for
                discharging, and positive values are for charging.
            request_lifetime: The duration, until which the request will stay in effect.
                This duration has to be between 10 seconds and 15 minutes (including
                both limits), otherwise the request will be rejected. It has
                a resolution of a second, so fractions of a second will be rounded for
                `timedelta` objects, and it is interpreted as seconds for `int` objects.
                If not provided, it usually defaults to 60 seconds.
            validate_arguments: Whether to validate the arguments before sending the
                request. If `True` a `ValueError` will be raised if an argument is
                invalid without even sending the request to the server, if `False`, the
                request will be sent without validation.

        Returns:
            The timestamp until which the given power command will stay in effect, or
                `None` if it was not provided by the server.

        Raises:
            ApiClientError: If there are any errors communicating with the Microgrid API,
                most likely a subclass of
                [GrpcError][frequenz.client.microgrid.GrpcError].
        """
        lifetime_seconds = _delta_to_seconds(request_lifetime)

        if validate_arguments:
            _validate_set_power_args(power=power, request_lifetime=lifetime_seconds)

        method_name = "SetElectricalComponentPower"
        if not self.is_connected:
            raise ClientNotConnected(server_url=self.server_url, operation=method_name)

        try:
            response = await anext(
                aiter(
                    self.stub.SetElectricalComponentPower(
                        microgrid_pb2.SetElectricalComponentPowerRequest(
                            electrical_component_id=_get_component_id(component),
                            power_type=microgrid_pb2.POWER_TYPE_ACTIVE,
                            power=power,
                            request_lifetime=lifetime_seconds,
                        ),
                        timeout=DEFAULT_GRPC_CALL_TIMEOUT,
                    )
                )
            )
        except AioRpcError as grpc_error:
            raise ApiClientError.from_grpc_error(
                server_url=self.server_url,
                operation=method_name,
                grpc_error=grpc_error,
            ) from grpc_error

        if response.HasField("valid_until_time"):
            return conversion.to_datetime(response.valid_until_time)

        return None

    async def set_component_power_reactive(  # noqa: DOC503
        self,
        component: ComponentId | Component,
        power: float,
        *,
        request_lifetime: timedelta | None = None,
        validate_arguments: bool = True,
    ) -> datetime | None:
        """Set the reactive power output of a component.

        We follow the polarity specified in the IEEE 1459-2010 standard
        definitions, where:

        - Positive reactive is inductive (current is lagging the voltage)
        - Negative reactive is capacitive (current is leading the voltage)

        The power output is specified in VAr.

        The return value is the timestamp until which the given power command will
        stay in effect. After this timestamp, the component's reactive power will
        be set to 0, if the API receives no further command to change it before
        then. By default, this timestamp will be set to the current time plus 60
        seconds.

        Note:
            The target component may have a resolution of more than 1 VAr. E.g., an
            inverter may have a resolution of 88 VAr. In such cases, the magnitude of
            power will be floored to the nearest multiple of the resolution.

        Args:
            component: The component to set the output reactive power of.
            power: The output reactive power level, in VAr. The standard of polarity is
                as per the IEEE 1459-2010 standard definitions: positive reactive is
                inductive (current is lagging the voltage); negative reactive is
                capacitive (current is leading the voltage).
            request_lifetime: The duration, until which the request will stay in effect.
                This duration has to be between 10 seconds and 15 minutes (including
                both limits), otherwise the request will be rejected. It has
                a resolution of a second, so fractions of a second will be rounded for
                `timedelta` objects, and it is interpreted as seconds for `int` objects.
                If not provided, it usually defaults to 60 seconds.
            validate_arguments: Whether to validate the arguments before sending the
                request. If `True` a `ValueError` will be raised if an argument is
                invalid without even sending the request to the server, if `False`, the
                request will be sent without validation.

        Returns:
            The timestamp until which the given power command will stay in effect, or
                `None` if it was not provided by the server.

        Raises:
            ApiClientError: If there are any errors communicating with the Microgrid API,
                most likely a subclass of
                [GrpcError][frequenz.client.microgrid.GrpcError].
        """
        lifetime_seconds = _delta_to_seconds(request_lifetime)

        if validate_arguments:
            _validate_set_power_args(power=power, request_lifetime=lifetime_seconds)

        method_name = "SetElectricalComponentPower"
        if not self.is_connected:
            raise ClientNotConnected(server_url=self.server_url, operation=method_name)

        try:
            response = await anext(
                aiter(
                    self.stub.SetElectricalComponentPower(
                        microgrid_pb2.SetElectricalComponentPowerRequest(
                            electrical_component_id=_get_component_id(component),
                            power_type=microgrid_pb2.POWER_TYPE_REACTIVE,
                            power=power,
                            request_lifetime=lifetime_seconds,
                        ),
                        timeout=DEFAULT_GRPC_CALL_TIMEOUT,
                    )
                )
            )
        except AioRpcError as grpc_error:
            raise ApiClientError.from_grpc_error(
                server_url=self.server_url,
                operation=method_name,
                grpc_error=grpc_error,
            ) from grpc_error

        if response.HasField("valid_until_time"):
            return conversion.to_datetime(response.valid_until_time)

        return None

    async def add_component_bounds(  # noqa: DOC502 (Raises ApiClientError indirectly)
        self,
        component: ComponentId | Component,
        target: Metric | int,
        bounds: Iterable[Bounds],
        *,
        validity: Validity | None = None,
    ) -> datetime | None:
        """Add inclusion bounds for a given metric of a given component.

        The bounds are used to define the acceptable range of values for a metric
        of a component. The added bounds are kept only temporarily, and removed
        automatically after some expiry time.

        Inclusion bounds give the range that the system will try to keep the
        metric within. If the metric goes outside of these bounds, the system will
        try to bring it back within the bounds.
        If the bounds for a metric are `[[lower_1, upper_1], [lower_2, upper_2]]`,
        then this metric's `value` needs to comply with the constraints `lower_1 <=
        value <= upper_1` OR `lower_2 <= value <= upper_2`.

        If multiple inclusion bounds have been provided for a metric, then the
        overlapping bounds are merged into a single bound, and non-overlapping
        bounds are kept separate.

        Example:
            If the bounds are [[0, 10], [5, 15], [20, 30]], then the resulting bounds
            will be [[0, 15], [20, 30]].

            The following diagram illustrates how bounds are applied:

            ```
              lower_1  upper_1
            <----|========|--------|========|-------->
                                lower_2  upper_2
            ```

            The bounds in this example are `[[lower_1, upper_1], [lower_2, upper_2]]`.

            ```
            ---- values here are considered out of range.
            ==== values here are considered within range.
            ```

        Note:
            For power metrics, regardless of the bounds, 0W is always allowed.

        Args:
            component: The component to add bounds to.
            target: The target metric whose bounds have to be added.
            bounds: The bounds to add to the target metric. Overlapping pairs of bounds
                are merged into a single pair of bounds, and non-overlapping ones are
                kept separated.
            validity: The duration for which the given bounds will stay in effect.
                If `None`, then the bounds will be removed after some default time
                decided by the server, typically 5 seconds.

                The duration for which the bounds are valid. If not provided, the
                bounds are considered to be valid indefinitely.

        Returns:
            The timestamp until which the given bounds will stay in effect, or `None` if
                if it was not provided by the server.

        Raises:
            ApiClientError: If there are any errors communicating with the Microgrid API,
                most likely a subclass of
                [GrpcError][frequenz.client.microgrid.GrpcError].
        """
        response = await client.call_stub_method(
            self,
            lambda: self.stub.AugmentElectricalComponentBounds(
                microgrid_pb2.AugmentElectricalComponentBoundsRequest(
                    electrical_component_id=_get_component_id(component),
                    target_metric=_get_metric_value(target),
                    bounds=(
                        bounds_pb2.Bounds(
                            lower=bound.lower,
                            upper=bound.upper,
                        )
                        for bound in bounds
                    ),
                    request_lifetime=validity.value if validity else None,
                ),
                timeout=DEFAULT_GRPC_CALL_TIMEOUT,
            ),
            method_name="AddComponentBounds",
        )

        if response.HasField("valid_until_time"):
            return conversion.to_datetime(response.valid_until_time)

        return None

    # noqa: DOC502 (Raises ApiClientError indirectly)
    def receive_component_data_samples_stream(
        self,
        component: ComponentId | Component,
        metrics: Iterable[Metric | int],
        *,
        buffer_size: int = 50,
    ) -> Receiver[ComponentDataSamples]:
        """Stream data samples from a component.

        At least one metric must be specified. If no metric is specified, then the
        stream will raise an error.

        Warning:
            Components may not support all metrics. If a component does not support
            a given metric, then the returned data stream will not contain that metric.

            There is no way to tell if a metric is not being received because the
            component does not support it or because there is a transient issue when
            retrieving the metric from the component.

            The supported metrics by a component can even change with time, for example,
            if a component is updated with new firmware.

        Args:
            component: The component to stream data from.
            metrics: List of metrics to return. Only the specified metrics will be
                returned.
            buffer_size: The maximum number of messages to buffer in the returned
                receiver. After this limit is reached, the oldest messages will be
                dropped.

        Returns:
            The data stream from the component.
        """
        component_id = _get_component_id(component)
        metrics_set = frozenset([_get_metric_value(m) for m in metrics])
        key = f"{component_id}-{hash(metrics_set)}"
        broadcaster = self._component_data_broadcasters.get(key)
        if broadcaster is None:
            client_id = hex(id(self))[2:]
            stream_name = f"microgrid-client-{client_id}-component-data-{key}"
            # Alias to avoid too long lines linter errors
            # pylint: disable-next=invalid-name
            Request = microgrid_pb2.ReceiveElectricalComponentTelemetryStreamRequest
            broadcaster = streaming.GrpcStreamBroadcaster(
                stream_name,
                lambda: aiter(
                    self.stub.ReceiveElectricalComponentTelemetryStream(
                        Request(
                            electrical_component_id=_get_component_id(component),
                            filter=Request.ComponentTelemetryStreamFilter(
                                metrics=metrics_set
                            ),
                        ),
                    )
                ),
                lambda msg: component_data_samples_from_proto(msg.telemetry),
                retry_strategy=self._retry_strategy,
            )
            self._component_data_broadcasters[key] = broadcaster
        return broadcaster.new_receiver(maxsize=buffer_size)


# pylint: disable-next=fixme
# TODO: Remove this enum, now AugmentElectricalComponentBounds takes a simple timeout as
# an int.
class Validity(enum.Enum):
    """The duration for which a given list of bounds will stay in effect."""

    FIVE_SECONDS = 5
    """The bounds will stay in effect for 5 seconds."""

    ONE_MINUTE = 60
    """The bounds will stay in effect for 1 minute."""

    FIVE_MINUTES = 60 * 5
    """The bounds will stay in effect for 5 minutes."""

    FIFTEEN_MINUTES = 60 * 15
    """The bounds will stay in effect for 15 minutes."""


def _get_component_id(component: ComponentId | Component) -> int:
    """Get the component ID from a component or component ID."""
    match component:
        case ComponentId():
            return int(component)
        case Component():
            return int(component.id)
        case unexpected:
            assert_never(unexpected)


def _get_metric_value(metric: Metric | int) -> metrics_pb2.Metric.ValueType:
    """Get the metric ID from a metric or metric ID."""
    match metric:
        case Metric():
            return metrics_pb2.Metric.ValueType(metric.value)
        case int():
            return metrics_pb2.Metric.ValueType(metric)
        case unexpected:
            assert_never(unexpected)


def _get_category_value(
    category: ComponentCategory | int,
) -> electrical_components_pb2.ElectricalComponentCategory.ValueType:
    """Get the category value from a component or component category."""
    match category:
        case ComponentCategory():
            return electrical_components_pb2.ElectricalComponentCategory.ValueType(
                category.value
            )
        case int():
            return electrical_components_pb2.ElectricalComponentCategory.ValueType(
                category
            )
        case unexpected:
            assert_never(unexpected)


def _delta_to_seconds(delta: timedelta | None) -> int | None:
    """Convert a `timedelta` to seconds (or `None` if `None`)."""
    return round(delta.total_seconds()) if delta is not None else None


def _validate_set_power_args(*, power: float, request_lifetime: int | None) -> None:
    """Validate the request lifetime."""
    if math.isnan(power):
        raise ValueError("power cannot be NaN")
    if request_lifetime is not None:
        minimum_lifetime = 10  # 10 seconds
        maximum_lifetime = 900  # 15 minutes
        if not minimum_lifetime <= request_lifetime <= maximum_lifetime:
            raise ValueError(
                "request_lifetime must be between 10 seconds and 15 minutes"
            )
