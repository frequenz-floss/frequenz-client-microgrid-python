# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Client for requests to the Microgrid API."""

from __future__ import annotations

import asyncio
import itertools
import math
from dataclasses import replace
from datetime import datetime, timedelta
from typing import Any, assert_never

from frequenz.api.microgrid.v1 import microgrid_pb2, microgrid_pb2_grpc
from frequenz.client.base import channel, client, conversion, retry, streaming
from frequenz.client.common.microgrid.components import ComponentId
from google.protobuf.empty_pb2 import Empty
from typing_extensions import override

from ._exception import ClientNotConnected
from ._microgrid_info import MicrogridInfo
from ._microgrid_info_proto import microgrid_info_from_proto
from .component._component import Component

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
        self._broadcasters: dict[
            ComponentId, streaming.GrpcStreamBroadcaster[Any, Any]
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
        microgrid = await client.call_stub_method(
            self,
            lambda: self.stub.GetMicrogridMetadata(
                Empty(),
                timeout=DEFAULT_GRPC_CALL_TIMEOUT,
            ),
            method_name="GetMicrogridMetadata",
        )

        return microgrid_info_from_proto(microgrid.microgrid)

    async def set_component_power_active(  # noqa: DOC502 (raises ApiClientError indirectly)
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

        response = await client.call_stub_method(
            self,
            lambda: self.stub.SetComponentPowerActive(
                microgrid_pb2.SetComponentPowerActiveRequest(
                    component_id=_get_component_id(component),
                    power=power,
                    request_lifetime=lifetime_seconds,
                ),
                timeout=DEFAULT_GRPC_CALL_TIMEOUT,
            ),
            method_name="SetComponentPowerActive",
        )

        if response.HasField("valid_until"):
            return conversion.to_datetime(response.valid_until)

        return None

    async def set_component_power_reactive(  # noqa: DOC502 (raises ApiClientError indirectly)
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

        response = await client.call_stub_method(
            self,
            lambda: self.stub.SetComponentPowerReactive(
                microgrid_pb2.SetComponentPowerReactiveRequest(
                    component_id=_get_component_id(component),
                    power=power,
                    request_lifetime=lifetime_seconds,
                ),
                timeout=DEFAULT_GRPC_CALL_TIMEOUT,
            ),
            method_name="SetComponentPowerReactive",
        )

        if response.HasField("valid_until"):
            return conversion.to_datetime(response.valid_until)

        return None


def _get_component_id(component: ComponentId | Component) -> int:
    """Get the component ID from a component or component ID."""
    match component:
        case ComponentId():
            return int(component)
        case Component():
            return int(component.id)
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
