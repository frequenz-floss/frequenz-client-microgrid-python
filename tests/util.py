# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

# pylint: disable=too-many-lines

r'''Utilities for testing client implementations.

This module provides utilities to create and structure test case files for
testing gRPC client methods. These utilities are designed to simplify the
process of testing client-side gRPC logic by mocking gRPC stub interactions and
providing a framework for asserting client behavior.

The primary tools you'll use from this module are:

* [`get_test_specs()`][tests.util.get_test_specs]: Discovers and prepares test
  cases based on files you create in a conventional directory structure.
* [`ApiClientTestCaseSpec`][tests.util.ApiClientTestCaseSpec]: Objects returned
  by `get_test_specs()`. You'll call methods like `test_unary_unary_call()` or
  `test_unary_stream_call()` on these objects to run individual test scenarios.

While these are the main interfaces for test definitions, the framework also
utilizes other helpers you probably want to use:

* [`patch_client_class()`][tests.util.patch_client_class]: For setting up client
  mocks, often used within `pytest` fixtures to prepare a client instance for
  testing.
* [`make_grpc_error()`][tests.util.make_grpc_error]: For creating mock gRPC
  error objects to simulate API failures.

# Quick Start Guide

This section provides a fast track to writing your first client tests using this
framework.

## Directory Structure

Organize your test case files as follows:

```text
tests/
├── test_some_client.py       # Your main pytest file for the client
└── client_test_cases/        # Root directory for all client method test cases
    └── some_unary_method/    # Subdirectory for a specific unary client method
    |   ├── success_case.py
    |   └── error_case.py
    └── some_stream_method/   # Subdirectory for a specific streaming client method
        ├── success_case.py
        ├── call_error_case.py
        └── stream_error_case.py
```

## Main Test File (`test_some_client.py`)

```python title="test_some_client.py"
from collections.abc import AsyncIterator
from pathlib import Path

import pytest

# Replace with your actual client and stub
from some_protobuf_generated_files import some_api_pb2_grpc  # type: ignore
from some_client_module import SomeApiClient  # type: ignore
# Replace with your retry strategy if needed
from frequenz.client.base.retry import LinearBackoff

from tests.util import ApiClientTestCaseSpec, get_test_specs, patch_client_class

# Define the directory where your test case files are stored
TESTS_DIR = Path(__file__).parent / "client_test_cases"

@pytest.fixture
async def client(mocker: pytest_mock.MockerFixture) -> AsyncIterator[SomeApiClient]:
    """Fixture that provides a SomeApiClient with a mock gRPC stub."""
    # The patch_client_class utility replaces the client's `connect` method
    # to inject a mock stub, avoiding real network calls.
    with patch_client_class(
        SomeApiClient, some_api_pb2_grpc.SomeApiStub
    ) as patched_client_class:
        # Initialize your client, potentially with a fast retry strategy for tests
        instance = patched_client_class(
            "grpc://localhost:1234", # Mock server URL, not really used
            retry_strategy=LinearBackoff(interval=0.0, jitter=0.0, limit=3),
        )
        async with instance:
            yield instance

@pytest.mark.parametrize(
    "spec",
    # "some_unary_method" must match your SomeApiClient method name, and also
    # the subdirectory name in client_test_cases/.
    get_test_specs("some_unary_method", tests_dir=TESTS_DIR),
    ids=str,  # Use the test case file name as the test ID
)
async def test_some_unary_method(
    client: SomeApiClient, spec: ApiClientTestCaseSpec
) -> None:
    """Test the some_unary_method client call."""
    # "ActualGrpcMethodName" is the name of the method on the gRPC stub.
    await spec.test_unary_unary_call(client, "ActualGrpcMethodName")

@pytest.mark.parametrize(
    "spec", get_test_specs("some_stream_method", tests_dir=TESTS_DIR), ids=str,
)
async def test_some_stream_method(
    client: SomeApiClient, spec: ApiClientTestCaseSpec
) -> None:
    """Test the some_stream_method client call."""
    # "ActualGrpcStreamMethodName" is the name of the streaming method on the
    # gRPC stub.
    await spec.test_unary_stream_call(client, "ActualGrpcStreamMethodName")
```

## Test Case File Examples

### Unary Method Test Cases

Example: Success test case
    ```python title="client_test_cases/some_unary_method/success_case.py"
    # Replace with your actual protobuf message types
    from some_api_pb2 import SomeRequest, SomeResponse  # type: ignore
    # If client transforms the response
    from some_client_module import SomeClientReturnType  # type: ignore

    # Arguments to pass to your client.some_unary_method()
    client_args = ("some_id",)
    client_kwargs = {"param": True}

    # Function to assert the gRPC request sent by the client
    def assert_stub_method_call(request: SomeRequest) -> None:
        assert isinstance(request, SomeRequest)
        assert request.id == "some_id"
        assert request.parameter is True

    # Expected gRPC response from the stub
    grpc_response = SomeResponse(data="mocked_data")

    # Function to assert the result returned by your client method
    def assert_client_result(result: SomeClientReturnType) -> None:
        # If your client method returns the raw gRPC response:
        # assert result == grpc_response
        # If your client method processes the response:
        assert isinstance(result, SomeClientReturnType)
        assert result.processed_data == "mocked_data_processed"
    ```

Example: Error test case
    ```python title="client_test_cases/some_unary_method/error_case.py"
    from grpc import StatusCode
    from some_api_pb2 import SomeRequest  # type: ignore
    from some_client_module import ClientSpecificError # type: ignore
    from grpc.aio import AioRpcError

    from tests.util import make_grpc_error

    client_args = ("non_existent_id",)
    client_kwargs = {}

    def assert_stub_method_call(request: SomeRequest) -> None:
        assert request.id == "non_existent_id"

    # Simulate a gRPC error
    grpc_response = make_grpc_error(StatusCode.NOT_FOUND, details="Item not found")

    # Assert that the client raises a specific exception
    def assert_client_exception(exception: Exception) -> None:
        assert isinstance(exception, ClientSpecificError)
        assert "not found" in str(exception).lower()
        assert isinstance(exception.__cause__, AioRpcError)
        assert exception.__cause__.code() == StatusCode.NOT_FOUND
    ```

### Streaming Method Test Cases

Example: Success test case
    ```python title="client_test_cases/some_stream_method/success_case.py"
    from frequenz.channels import Receiver, ReceiverStoppedError
    import pytest # For pytest.raises

    from some_api_pb2 import SomeStreamRequest, SomeStreamResponse  # type: ignore
    # Type of items from client stream
    from some_client_module import SomeClientStreamItemType  # type: ignore

    client_args = (10,) # e.g., client.some_stream_method(10)
    client_kwargs = {}

    def assert_stub_method_call(request: SomeStreamRequest) -> None:
        assert isinstance(request, SomeStreamRequest)
        assert request.count == 10

    # For streams, grpc_response can be an iterable of response messages
    grpc_response = [
        SomeStreamResponse(item_id=1, value="first"),
        SomeStreamResponse(item_id=2, value="second"),
    ]
    # Alternatively, it can be a generator function, async iterable, etc.
    # (see detailed guide below).

    async def assert_client_result(
        receiver: Receiver[SomeClientStreamItemType]
    ) -> None:
        result = await receiver.receive()
        assert isinstance(result, SomeClientStreamItemType)
        assert result.id == 1 and result.val == "first_processed"

        result = await receiver.receive()
        assert result.id == 2 and result.val == "second_processed"

        with pytest.raises(ReceiverStoppedError):
            await receiver.receive()
    ```

Example: Error on stream initiation
    ```python title="client_test_cases/some_stream_method/call_error_case.py"
    # Replace with your actual protobuf message types and client error
    from some_api_pb2 import SomeStreamRequest  # type: ignore
    from some_client_module import ClientSpecificError # type: ignore
    from grpc import StatusCode
    from grpc.aio import AioRpcError

    from tests.util import make_grpc_error

    # Arguments to pass to your client.some_stream_method()
    client_args = (10,) # e.g., client.some_stream_method(10)
    client_kwargs = {}

    # Function to assert the gRPC request sent by the client
    def assert_stub_method_call(request: SomeStreamRequest) -> None:
        assert isinstance(request, SomeStreamRequest)
        assert request.count == 10  # Example assertion

    # Simulate a gRPC error when the stream is initiated
    grpc_response = make_grpc_error(StatusCode.UNAVAILABLE, details="Service temporarily down")

    # Assert that the client method itself raises an exception immediately
    def assert_client_exception(exception: Exception) -> None:
        assert isinstance(exception, ClientSpecificError) # Or the specific error you expect
        assert "unavailable" in str(exception).lower() or \
               "service temporarily down" in str(exception).lower()
        assert isinstance(exception.__cause__, AioRpcError)
        assert exception.__cause__.code() == StatusCode.UNAVAILABLE
    ```

Example: Error during the stream
    ```python title="client_test_cases/some_stream_method/stream_error_case.py"
    from collections.abc import AsyncIterator
    import pytest # For pytest.raises

    # Replace with your actual protobuf message types and client error
    from some_api_pb2 import SomeStreamRequest, SomeStreamResponse  # type: ignore
    from some_client_module import ClientSpecificError, SomeClientStreamItemType # type: ignore
    from grpc import StatusCode
    from grpc.aio import AioRpcError
    from frequenz.channels import Receiver # If client returns a receiver

    from tests.util import make_grpc_error

    # Arguments to pass to your client.some_stream_method()
    client_args = (10,) # e.g., client.some_stream_method(10)
    client_kwargs = {}

    # Function to assert the gRPC request sent by the client
    def assert_stub_method_call(request: SomeStreamRequest) -> None:
        assert isinstance(request, SomeStreamRequest)
        assert request.count == 10  # Example assertion

    # This example simulates an error after the first item is received.
    _iterations = 0
    async def grpc_response() -> AsyncIterator[Any]:
        global _iterations  # pylint: disable=global-statement
        _iterations += 1
        if _iterations == 1:
            raise make_grpc_error(StatusCode.INTERNAL)
        yield microgrid_pb2.ReceiveComponentDataStreamResponse(
            data=components_pb2.ComponentData(component_id=1, metric_samples=[], states=[]),
        )


    # Assert that the client handles the error as expected.
    async def assert_client_result(
        receiver: Receiver[SomeClientStreamItemType] # Or your client's return type
    ) -> None:
        # Check for the first successfully received item
        result = await receiver.receive()
        assert isinstance(result, SomeClientStreamItemType)
        assert result.id == 1 and result.val == "first_ok_processed" # Example processing

        # Expect an error when trying to receive the next item
        with pytest.raises(ClientSpecificError) as exc_info:
            await receiver.receive()

        assert "internal" in str(exc_info.value).lower() # Check error message
        assert isinstance(exc_info.value.__cause__, AioRpcError)
        assert exc_info.value.__cause__.code() == StatusCode.INTERNAL
    ```

# In-Depth Guide to Writing Test Cases

This guide walks you through the process of setting up and writing test cases
for your gRPC client methods.

## Set Up Your Main Test File

Start by creating a Python file for your client tests, typically named
`test_<your_client_name>.py` (e.g., `test_some_client.py`) in your `tests/`
directory.

In this file:

1. **Import necessary modules**: `pytest`, your client class (e.g.,
   `SomeApiClient`), and from this `tests.util` module:
   [`ApiClientTestCaseSpec`][tests.util.ApiClientTestCaseSpec],
   [`get_test_specs()`][tests.util.get_test_specs], and usually
   [`patch_client_class()`][tests.util.patch_client_class].
2. **Define `TESTS_DIR`**: Create a `pathlib.Path` object pointing to the
   directory where your test case definition files will reside. A common
   convention is `Path(__file__).parent / "client_test_cases"`.
3. **Create a `client` fixture**: This `pytest` fixture should provide an
   instance of your client, properly mocked to prevent actual network calls.
   Use the [`patch_client_class()`][tests.util.patch_client_class] utility as
   shown in the Quick Start Guide. This fixture will be injected into your test
   functions.

## Write Test Functions for Each Client Method

For each client method you want to test (e.g., `get_component_info`), create a
corresponding asynchronous test function in your main test file (e.g.,
`async def test_get_component_info(...)`).

1. Parameterize with `get_test_specs`:
    * Use the `@pytest.mark.parametrize("spec", ...)` decorator.

    * Call `get_test_specs("client_method_name", tests_dir=TESTS_DIR)`.

        * `"client_method_name"`: This string should match the name of the
            subdirectory you'll create under `TESTS_DIR` for this method's test
            cases. It often corresponds to the Python name of your client method
            (e.g., `"get_component_info"`).
        * `tests_dir=TESTS_DIR`: Pass the path defined in Step 1.

    * Optionally, use `ids=str` in `parametrize` to get clearer test names in
        `pytest` output, based on the test case filenames.

2.  **Call the appropriate `spec` method**:
    * The `spec` parameter injected into your test function is an instance of
        `ApiClientTestCaseSpec`.
    * If the client method performs a **unary-unary** gRPC call (single request,
        single response), call:
        `await spec.test_unary_unary_call(client, "ActualGrpcMethodName")`
    * If the client method performs a **unary-stream** gRPC call (single
        request, stream of responses), call:
        `await spec.test_unary_stream_call(client, "ActualGrpcStreamMethodName")`
    * `client`: The client instance from your fixture.
    * `"ActualGrpcMethodName"`: This is a string representing the **exact name
        of the method on the gRPC stub** that your client method calls
        internally (e.g., `"GetComponentInfo"` if the stub has a method
        `Stub.GetComponentInfo(...)`).

## Authoring Test Case Files

For each client method, you'll create multiple test case files, each
representing a specific scenario (e.g., successful call, specific error,
particular input leading to unique behavior).

### Directory Structure

Under your `TESTS_DIR` (e.g., `tests/client_test_cases/`), create a
subdirectory named exactly as the first argument you passed to
`get_test_specs` (e.g., `get_component_info/`).

### Test Case Files

Inside this method-specific subdirectory, create Python files (`.py`) for each
test scenario. The filenames should be descriptive (e.g., `success_case.py`,
`not_found_error_case.py`, `empty_list_response_case.py`). By default,
`get_test_specs` looks for files ending in `_case.py`.

### Variables in a Test Case File

Each test case `.py` file is a module that defines several top-level variables.
These variables instruct the test framework on how to mock the gRPC call and
what to assert.

#### `client_args` (Optional)

* **Type**: `tuple[Any, ...]`
* **Default**: `()` (empty tuple)
* **Purpose**: Positional arguments to pass to your client method when it's
  called during the test.
  Example:
    ```python
    client_args = (12345, "component_type_filter")
    ```

#### `client_kwargs` (Optional)

* **Type**: `dict[str, Any]`
* **Default**: `{}` (empty dictionary)
* **Purpose**: Keyword arguments to pass to your client method.
  Example:
    ```python
    client_kwargs = {"timeout_sec": 10, "include_details": True}
    ```

#### `assert_stub_method_call` (Required)

* **Type**: `Callable[[RequestProto], None]` where `RequestProto` is the type
  of the gRPC request message for the stub method being called.
* **Purpose**: A function that validates the request object sent by your client
  method to the gRPC stub. This function receives the actual gRPC request
  object (as prepared by your client code) as its sole argument. Use `assert`
  statements within this function to check its fields and values.
  Example:
    ```python
    from some_api_pb2 import GetComponentInfoRequest # Your request protobuf type

    def assert_stub_method_call(request: GetComponentInfoRequest) -> None:
        assert isinstance(request, GetComponentInfoRequest)
        assert request.component_id == 12345
        assert request.type_filter == "component_type_filter"
    ```

#### `grpc_response` (Required)

This variable defines the mock response or error the gRPC stub should produce.

* **Type**: Varies based on call type (unary/stream) and expected outcome
  (success/error).
* **Purpose**: To simulate the gRPC service's behavior.

* **For Unary-Unary Calls**:
    * **Successful Response**: The `grpc_response` should be an instance of the
      expected gRPC response protobuf message.
      Example:
        ```python
        from some_api_pb2 import ComponentInfoResponse
        grpc_response = ComponentInfoResponse(name="Test Component", status="ACTIVE")
        ```
    * **gRPC Error**: If the gRPC call itself is expected to fail (e.g.,
      `StatusCode.NOT_FOUND`), `grpc_response` should be an exception
      instance, typically `grpc.aio.AioRpcError`. Use the
      [`make_grpc_error`][tests.util.make_grpc_error] utility for this.
      Example:
        ```python
        from grpc import StatusCode
        from tests.util import make_grpc_error
        grpc_response = make_grpc_error(StatusCode.NOT_FOUND, details="Component not found")
        ```

* **For Unary-Stream Calls**:
    * **Successful Stream**: `grpc_response` can be any of the following to
      represent the stream of messages from the server:
        * An **iterable** of response protobuf messages (e.g., a `list` or
          `tuple`).
        * A **synchronous generator function** that yields response messages.
        * An **asynchronous iterable** of response protobuf messages.
        * An **asynchronous generator function** that yields response messages.
        * A **callable** that, when called, returns any of the above
          (iterable, generator, etc.).
      Examples:
        ```python
        from some_api_pb2 import StreamDataItem
        # List of messages
        grpc_response = [
            StreamDataItem(value=1.0, timestamp=100),
            StreamDataItem(value=1.1, timestamp=101),
        ]

        # Generator function
        def generate_responses():
            yield StreamDataItem(value=2.0, timestamp=200)
            yield StreamDataItem(value=2.1, timestamp=201)
        grpc_response = generate_responses

        # Async generator function
        async def generate_async_responses():
            yield StreamDataItem(value=3.0, timestamp=300)
            # Simulate async work if needed: await asyncio.sleep(0.01)
            yield StreamDataItem(value=3.1, timestamp=301)
        grpc_response = generate_async_responses
        ```
    * **gRPC Error (for the stream call itself)**: If the initial gRPC call to
      start the stream is expected to fail, `grpc_response` should be an
      exception instance (e.g., `AioRpcError` from `make_grpc_error`).
      Example:
        ```python
        from grpc import StatusCode
        from tests.util import make_grpc_error
        grpc_response = make_grpc_error(StatusCode.UNAUTHENTICATED, details="Missing auth token")
        ```
      *Note*: If an error is expected *during* an otherwise successful stream
      (i.e., the stream starts, sends some items, then an error occurs that the
      client should handle via the stream itself), this should typically be
      modeled by having your iterable/generator raise the error at the
      appropriate point, or by having the client method itself catch and
      transform this into a client-level exception that
      `assert_client_exception` can check.

#### Asserting Client Behavior (Choose ONE)

You must define *exactly one* of the following two variables to assert the
final outcome of your client method call.

##### `assert_client_result` (Conditional)

* **Type**: `Callable[[ClientResultType], None | Awaitable[None]]` where
  `ClientResultType` is the type of the value returned by your client method.
* **Purpose**: To validate the result returned by your client method if it's
  expected to complete successfully. This function receives the client
  method's return value as its argument. It can be a synchronous or an
  asynchronous function (e.g., if you need to `await` something while
  asserting, or if the client returns an async iterator that needs to be
  consumed).
* **When to use**: When `grpc_response` is configured for a successful gRPC
  call (not an exception), and you expect your client method to process this
  and return a value or an async iterator.
  Example (Unary):
    ```python
    from some_client_module import ProcessedComponentInfo
    def assert_client_result(result: ProcessedComponentInfo) -> None:
        assert isinstance(result, ProcessedComponentInfo)
        assert result.name_upper == "TEST COMPONENT"
    ```
  Example (Stream - consuming an async iterator):
    ```python
    from some_client_module import ClientStreamItem
    async def assert_client_result(stream: AsyncIterator[ClientStreamItem]) -> None:
        items = [item async for item in stream]
        assert len(items) == 2
        assert items[0].value_plus_one == 2.0
    ```

##### `assert_client_exception` (Conditional)

* **Type**: `Callable[[Exception], None]`
* **Purpose**: To validate an exception that you expect your client method to
  raise. This function receives the actual exception object raised by the
  client method as its argument.
* **When to use**: When `grpc_response` is an exception (simulating a gRPC
  error), or when your client method's internal logic is expected to raise an
  exception based on the gRPC response or other conditions.
  Example:
    ```python
    from some_client_module import ClientSpecificError
    from grpc import StatusCode
    from grpc.aio import AioRpcError

    def assert_client_exception(exception: Exception) -> None:
        assert isinstance(exception, ClientSpecificError)
        assert "Component could not be found" in str(exception)
        # Optionally, check the cause if your client wraps gRPC errors
        assert isinstance(exception.__cause__, AioRpcError)
        assert exception.__cause__.code() == StatusCode.NOT_FOUND
    ```

## Understanding Test Execution

When you run `pytest`, here's how your test cases are processed:

1. **Discovery**: `pytest` discovers your `test_...()` functions.
2. **Parameterization**: For each such function, `get_test_specs()` is called.
   It scans the specified subdirectory in `TESTS_DIR` for `*_case.py` files.
3. **Spec Creation**: For each found file, an `ApiClientTestCaseSpec` object is
   created. This object holds metadata about the test case file.
4. **Test Invocation**: `pytest` calls your test function once for each
   `ApiClientTestCaseSpec` object.
5. **Execution via `spec` methods**:
    * Inside your test function, when you call
      `await spec.test_unary_unary_call(...)` or
      `await spec.test_unary_stream_call(...)`:
        a. **Loading**: The `spec` object loads the Python module corresponding
           to the current test case file (e.g., `success_case.py`).
        b. **Parsing**: It reads the variables (`client_args`, `grpc_response`,
           etc.) you defined in that file.
        c. **Mocking**: The gRPC stub method (e.g.,
           `client.stub.ActualGrpcMethodName`) on your client instance is
           patched with a mock.
        d. **Stub Behavior**: This mock is configured to behave according to
           your `grpc_response` variable (i.e., return the specified value(s),
           stream items, or raise the specified exception).
        e. **Client Call**: Your actual client method (e.g.,
           `client.get_component_info()`) is called using the `client_args` and
           `client_kwargs` from the test case file.
        f. **Request Assertion**: After your client method calls the (now
           mocked) stub method, your `assert_stub_method_call` function is
           invoked with the gRPC request object that your client constructed and
           sent to the stub.
        g. **Outcome Assertion**:
            * If the client method call resulted in an exception: If
              `assert_client_exception` is defined in your test case file, it's
              called with the raised exception. If `assert_client_result` was
              defined instead, the test fails (and vice-versa).
            * If the client method call returned a result: If
              `assert_client_result` is defined, it's called with the returned
              result. If `assert_client_exception` was defined instead, the
              test fails.
6. **Pass/Fail**: If all assertions within `assert_stub_method_call` and the
   relevant `assert_client_result`/`assert_client_exception` pass, and no
   unexpected exceptions occur, the individual test scenario passes.

This structured approach allows for clear separation of test logic (in your
main test file) from test data and specific scenario definitions (in your test
case files), promoting maintainability and readability.
'''

from __future__ import annotations

import asyncio
import functools
import gc
import importlib
import inspect
import itertools
import logging
import sys
from collections.abc import AsyncIterable, AsyncIterator, Awaitable, Callable, Iterable
from contextlib import AsyncExitStack, ContextDecorator, aclosing
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generic, Protocol, TypeVar, get_args, get_origin
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from frequenz.client.base.client import BaseApiClient
from grpc import StatusCode
from grpc.aio import AioRpcError, Channel, Metadata

_logger = logging.getLogger(__name__)

StubT = TypeVar("StubT")
"""Type variable for the gRPC stub type."""

ClientT = TypeVar("ClientT", bound=BaseApiClient[Any])
"""Type variable for the client type."""


@dataclass(frozen=True, kw_only=True)
class ApiClientTestCase:
    """A single test case for a gRPC client method."""

    client_args: tuple[Any, ...]
    """The positional arguments to use when calling the client method being tested."""

    client_kwargs: dict[str, Any]
    """The keyword arguments to use when calling the client method being tested."""

    assert_stub_method_call: Callable[[Any], None]
    """The assertion function to validate the gRPC request done by the client.

    The assertion function takes the actual gRPC request that was done, and should
    make assertions on it to validate that it matches the expected request.
    """

    grpc_response: Any
    """The response or exception to use to mock the gRPC call.

    If this is an exception, it will be raised when the gRPC call is made.
    If this is a value, it will be returned as the response.
    """

    assert_client_result: (
        Callable[[Any], None] | Callable[[Any], Awaitable[None]] | None
    ) = None
    """The assertion function to validate the result returned by the client.

    The assertion function takes the actual result returned by the client method,
    and it should make assertions on it to validate that it matches the expected
    result.

    This is only used if the gRPC call does not raise an exception.
    """

    assert_client_exception: Callable[[Exception], None] | None = None
    """The assertion function to validate the exception raised by the client.

    The assertion function takes the actual exception raised by the client method,
    and it should make assertions on it to validate that it matches the expected
    exception.

    This is only used if the gRPC call raises an exception.
    """

    def __post_init__(self) -> None:
        """Post-initialization checks for the TestCase class."""
        if self.assert_client_result is None and self.assert_client_exception is None:
            raise ValueError(
                "Either assert_client_result or assert_client_exception must be provided."
            )
        if (
            self.assert_client_result is not None
            and self.assert_client_exception is not None
        ):
            raise ValueError(
                "Only one of assert_client_result or assert_client_exception must be provided."
            )


@dataclass(frozen=True, kw_only=True)
class ApiClientTestCaseSpec:
    """A specification for a test case.

    This is used to load the test case data from a file and run the test.
    """

    name: str
    """The name of the test case."""

    client_method_name: str
    """The name of the gRPC client method being tested."""

    path: Path
    """The absolute path to the test case file."""

    relative_path: Path
    """The test case file path relative to current working directory."""

    def __str__(self) -> str:
        """Return a string representation of the test case specification."""
        return self.name

    def load_test_module(self) -> Any:
        """Return the loaded test case module from the test case file."""
        module_name = self.path.stem
        if module_name in sys.modules:
            raise ValueError(
                f"The module name for test case {self.name} is already in use"
            )

        # Register the module name with pytest to allow for better error reporting
        # when the test case fails.
        pytest.register_assert_rewrite(module_name)

        # We load the module as a top-level module to avoid requiring adding
        # `__init__.py` files to the test directories. We make sure to unload
        # the module (and other modules that might have been loaded by the test
        # case) after the test case is run to avoid polluting the module namespace.
        original_modules = sys.modules.copy()
        original_sys_path = sys.path.copy()
        sys.path.insert(0, str(self.path.parent))
        try:
            module = importlib.import_module(module_name)
        except ImportError as exc:
            raise ImportError(
                f"Test case {self.name} could not be imported from {self.relative_path}, "
                f"make sure the file exists and is a valid Python module: {exc}"
            ) from exc
        finally:
            sys.path = original_sys_path
            sys.modules = original_modules
            importlib.invalidate_caches()
            gc.collect()

        return module

    def load_test_case(self) -> ApiClientTestCase:
        """Return the loaded test case from the test case file."""
        module = self.load_test_module()

        required_attrs = ["assert_stub_method_call", "grpc_response"]
        if missing_attrs := [
            attr for attr in required_attrs if not hasattr(module, attr)
        ]:
            raise AttributeError(
                f"Test case file {self.relative_path} is missing required attributes: "
                + ", ".join(missing_attrs)
            )

        try:
            test_case = ApiClientTestCase(
                client_args=getattr(module, "client_args", ()),
                client_kwargs=getattr(module, "client_kwargs", {}),
                assert_stub_method_call=module.assert_stub_method_call,
                grpc_response=module.grpc_response,
                assert_client_result=getattr(module, "assert_client_result", None),
                assert_client_exception=getattr(
                    module, "assert_client_exception", None
                ),
            )
        except ValueError as exc:
            raise ValueError(
                f"Test case file {self.relative_path} is invalid: {exc}"
            ) from exc

        return test_case

    async def test_call(
        self,
        *,
        client: ClientProtocol,
        stub_method_name: str,
        call_client_method: Callable[
            [ClientProtocol, str, ApiClientTestCase, AsyncExitStack],
            Awaitable[tuple[MagicMock, Any, Exception | None]],
        ],
        exit_stack: AsyncExitStack,
    ) -> None:
        """Run a test for a unary-unary gRPC call."""
        _logger.debug(
            "Running test case %r for `%s()` (%s)",
            self.name,
            self.client_method_name,
            stub_method_name,
        )
        test_case = self.load_test_case()
        _logger.debug("Loaded test case %r from %s", self.name, self.relative_path)
        client_should_raise = test_case.assert_client_exception is not None

        # Call the client method and collect the result/exception
        stub_method_mock, client_result, client_raised_exception = (
            await call_client_method(client, stub_method_name, test_case, exit_stack)
        )

        if client_raised_exception is not None:
            if not client_should_raise:
                # Expected a result, but got an exception. Test premise failed.
                # We raise an AssertionError here to indicate that the test case
                # failed, but we chain it to the original exception to keep the
                # original traceback.
                # We need to check this before running the assert_stub_method_call() because
                # if an exception was raised, the stub method might not have been
                # called at all.
                _logger.debug(
                    "Raising AssertionError because the client raised an unexpected exception: %r",
                    client_raised_exception,
                )
                raise AssertionError(
                    f"{self.relative_path}: The client call to method {self.client_method_name}() "
                    f"raised an exception {client_raised_exception!r}, but a result was expected "
                    "(the test case provided a assert_client_result() function and not a "
                    "assert_client_exception() function)"
                ) from client_raised_exception

            _logger.debug(
                "The client raised an expected exception, calling `assert_client_exception(%r)`",
                client_raised_exception,
            )
            # Expected an exception, and got one, so run the user's
            # assertion function on the exception before we validate the
            # gRPC call, because if the wrong exception was raised, the stub
            # method might not have been called at all.
            # We also chain the exception to the original exception to keep the
            # original traceback for a better debugging experience.
            assert test_case.assert_client_exception is not None
            try:
                test_case.assert_client_exception(client_raised_exception)
            except AssertionError as err:
                raise err from client_raised_exception

        # Validate the gRPC stub call was made correctly
        # This will report any failed assertions as a test FAIL, and any other
        # unexpected exception as a test ERROR, always pointing to the exact
        # location where the issue originated.
        test_case.assert_stub_method_call(stub_method_mock)

        if client_raised_exception is None:
            if client_should_raise:
                # Expected an exception, but got a result. Test premise failed.
                pytest.fail(
                    f"{self.relative_path}: The client call to method "
                    f"{self.client_method_name}() didn't raise the expected exception "
                    f"{test_case.grpc_response!r}, instead it returned {client_result!r}",
                    pytrace=False,
                )

            # Expected a result, and got one, so run the user's assertion
            # function on the result.
            elif test_case.assert_client_result is None:
                pytest.fail(
                    f"{self.relative_path}: The client method "
                    f"{self.client_method_name}() returned a result, but an "
                    "exception was expected (the test case provided a "
                    "assert_client_exception() function and not a "
                    "assert_client_result() function)",
                    pytrace=False,
                )

            if inspect.iscoroutinefunction(test_case.assert_client_result):
                _logger.debug("Awaiting `assert_client_result(%r)`", client_result)
                async with asyncio.timeout(60):
                    await test_case.assert_client_result(client_result)
            else:
                _logger.debug("Calling `assert_client_result(%r)`", client_result)
                test_case.assert_client_result(client_result)

    async def test_unary_unary_call(
        self,
        client: ClientProtocol,
        stub_method_name: str,
    ) -> None:
        """Run a test for a unary-unary gRPC call."""
        async with AsyncExitStack() as exit_stack:
            await self.test_call(
                client=client,
                stub_method_name=stub_method_name,
                call_client_method=self.call_unary_method,
                exit_stack=exit_stack,
            )

    async def test_unary_stream_call(
        self,
        client: ClientProtocol,
        stub_method_name: str,
    ) -> None:
        """Run a test for a unary-stream gRPC call."""
        async with AsyncExitStack() as exit_stack:
            await self.test_call(
                client=client,
                stub_method_name=stub_method_name,
                call_client_method=self.call_stream_method,
                exit_stack=exit_stack,
            )

    async def call_unary_method(
        self,
        client: ClientProtocol,
        stub_method_name: str,
        test_case: ApiClientTestCase,
        _: AsyncExitStack,
    ) -> tuple[AsyncMock, Any, Exception | None]:
        """Call a unary method on the client."""
        _logger.debug("Preparing stub gRPC unary call `%s()`", stub_method_name)
        # Prepare the mock for the gRPC stub method
        stub_method_mock = AsyncMock(name=stub_method_name)
        if isinstance(test_case.grpc_response, Exception):
            stub_method_mock.side_effect = test_case.grpc_response
        else:
            stub_method_mock.return_value = test_case.grpc_response
        _logger.debug(
            "Patching %s.%s with %s", client.stub, stub_method_name, stub_method_mock
        )
        setattr(client.stub, stub_method_name, stub_method_mock)

        # Call the client method and collect the result/exception
        client_method = getattr(client, self.client_method_name)
        # We use a separate variable for the result if it is an exception to be able
        # to support weird cases where the method actually returns an exception
        # instead of raising it.
        client_result: Any = None
        client_raised_exception: Exception | None = None
        try:
            _logger.debug(
                "Calling client method `%s(*%r, **%r)`",
                self.client_method_name,
                test_case.client_args,
                test_case.client_kwargs,
            )
            client_result = await client_method(
                *test_case.client_args, **test_case.client_kwargs
            )
            _logger.debug("Client method result: %r", client_result)
        except Exception as err:  # pylint: disable=broad-exception-caught
            _logger.debug("Client method raised an exception: %r", err)
            client_raised_exception = err

        return (stub_method_mock, client_result, client_raised_exception)

    async def call_stream_method(
        self,
        client: ClientProtocol,
        stub_method_name: str,
        test_case: ApiClientTestCase,
        exit_stack: AsyncExitStack,
    ) -> tuple[MagicMock, Any, Exception | None]:
        """Call a stream method on the client."""
        _logger.debug("Preparing stub gRPC stream call `%s()`", stub_method_name)
        stub_method_mock = MagicMock(name=stub_method_name)

        if isinstance(test_case.grpc_response, Exception):
            _logger.debug(
                "`grpc_response` is an exception, setting as side_effect: %r",
                test_case.grpc_response,
            )
            stub_method_mock.side_effect = test_case.grpc_response
        else:

            def create_response_wrapper(*_: Any, **__: Any) -> AsyncIterator[Any]:
                """Create a response wrapper for the gRPC response."""
                wrapper = _IterableResponseWrapper(test_case.grpc_response)
                exit_stack.push_async_exit(aclosing(wrapper))
                return wrapper

            stub_method_mock.side_effect = create_response_wrapper
        _logger.debug(
            "Patching %s.%s with %s", client.stub, stub_method_name, stub_method_mock
        )
        setattr(client.stub, stub_method_name, stub_method_mock)

        # Call the client method and collect the result/exception
        client_method = getattr(client, self.client_method_name)
        # We use a separate variable for the result if it is an exception to be able
        # to support weird cases where the method actually returns an exception
        # instead of raising it.
        client_result: Any = None
        client_raised_exception: Exception | None = None
        try:
            _logger.debug(
                "Calling client method `%s(*%r, **%r)`",
                self.client_method_name,
                test_case.client_args,
                test_case.client_kwargs,
            )
            client_result = client_method(
                *test_case.client_args, **test_case.client_kwargs
            )
            if asyncio.iscoroutine(client_result):
                _logger.debug("The client method is a coroutine, awaiting it...")
                async with asyncio.timeout(60):
                    client_result = await client_result
            _logger.debug("Client method result: %r", client_result)
        except Exception as err:  # pylint: disable=broad-exception-caught
            _logger.debug("Client method raised an exception: %r", err)
            client_raised_exception = err

        # Yield control to allow the gRPC streamer to start running
        await asyncio.sleep(0)

        return (stub_method_mock, client_result, client_raised_exception)


def get_test_specs(
    client_method_name: str,
    *,
    tests_dir: str | Path,
    suffixes: Iterable[str] = ("_case",),
) -> Iterable[ApiClientTestCaseSpec]:
    """Get all test names for a specific stub call.

    Args:
        client_method_name: The name of the client method being tested.
        tests_dir: The directory where the test cases are located (inside the
            `client_method_name` sub-directory).
        suffixes: The file suffixes to look for.

    Returns:
        A iterable of test case specs.

    Raises:
        ValueError: If the test directory does not exist or is not a directory,
            the `test_cases_subdir` is not a relative path, or if no test files
            are found in the test directory.
    """
    tests_dir = Path(tests_dir)
    if not tests_dir.is_absolute():
        raise ValueError(f"{tests_dir} must be an absolute path")

    test_dir = tests_dir / client_method_name
    if not test_dir.exists():
        raise ValueError(f"Tests directory {test_dir} does not exist")
    if not test_dir.is_dir():
        raise ValueError(f"Tests directory {test_dir} is not a directory")

    specs = list(
        itertools.chain(
            (
                ApiClientTestCaseSpec(
                    name=p.stem[: -len(suffix)],
                    client_method_name=client_method_name,
                    path=p.resolve(),
                    relative_path=p.relative_to(Path.cwd()),
                )
                for suffix in suffixes
                for p in test_dir.glob(f"*{suffix}.py")
            )
        )
    )
    if not specs:
        globs = [f"*{suffix}.py" for suffix in suffixes]
        raise ValueError(
            f"No test files found in {test_dir} matching {', '.join(globs)}"
        )

    return specs


class ClientProtocol(Protocol):
    """Protocol for client objects with a stub property."""

    @property
    def stub(self) -> Any:
        """Return the gRPC stub."""
        ...  # pylint: disable=unnecessary-ellipsis


def make_grpc_error(
    code: StatusCode,
    *,
    initial_metadata: Metadata = Metadata(),
    trailing_metadata: Metadata = Metadata(),
    details: str | None = None,
    debug_error_string: str | None = None,
) -> AioRpcError:
    """Create a gRPC error for testing purposes."""
    return AioRpcError(
        code=code,
        initial_metadata=initial_metadata,
        trailing_metadata=trailing_metadata,
        details=details,
        debug_error_string=debug_error_string,
    )


# generic_cls uses Any because it doesn't really take a `type` (which might be
# what looks more intuitive), technically is a `typing._GenericAlias`, but this
# is not a public API and we don't want to depend on it. There is also
# `types.GenericAlias` but this one is only used for built-in generics, like
# `list[int]`, so we can't use it either.
@functools.lru_cache(maxsize=1024)
def is_subclass_of_generic(cls: type[Any], generic_cls: Any) -> bool:
    """Return whether `cls` is a subclass of a parameterized generic `generic_cls`.

    Check at runtime whether `cls` is a subclass of a parameterized generic
    `generic_cls`., e.g. `is_subclass_generic(DerivedInt, GenericBase[int])`.

    Args:
        cls: The class to check.
        generic_cls: The parameterized generic type to check against.

    Returns:
        True if `cls` is a subclass of `generic_cls`, False otherwise.

    Raises:
        TypeError: If `generic_cls` is not a parameterized generic type.
    """
    # Check if 'generic_cls' is actually a parameterized generic type
    # (like list[int], GenericBase[str], etc.).
    # get_origin returns None for non-generics or non-parameterized generics.
    origin = get_origin(generic_cls)
    if origin is None:
        raise TypeError(f"generic_cls {generic_cls!r} must be a parameterized generic")

    # First check the raw generic relationship (e.g., is DerivedInt a subclass
    # of GenericBase?).
    if not issubclass(cls, origin):
        return False

    # Inspect __orig_bases__ throughout the MRO (Method Resolution Order).
    # This handles inheritance chains correctly (sub-sub classes).
    # We iterate through getmro(cls) to check not just direct parents, but all
    # ancestors.
    for base in inspect.getmro(cls):
        # __orig_bases__ stores the base classes *as they were written*,
        # including type parameters. Might not exist on all classes (like 'object').
        # getattr avoids an AttributeError if __orig_bases__ is missing.
        # Python3.12 provides types.get_original_bases(cls) to get __orig_bases__,
        # this can be updated when we drop support for older versions.
        for orig_base in getattr(base, "__orig_bases__", ()):
            # Check if the origin of this specific original base matches our
            # target origin AND if the arguments match our target arguments.
            # get_args returns a tuple, so this correctly handles multi-generic
            # bases by comparing tuples element-wise (e.g., (str, int) == (str,
            # int)).
            if get_origin(orig_base) is origin and get_args(orig_base) == get_args(
                generic_cls
            ):
                return True

    return False


class patch_client_class(  # pylint: disable=invalid-name
    ContextDecorator, Generic[ClientT, StubT]
):
    """Patches the client class for testing.

    This avoids the class to really connect anywhere, and creates a mock
    channel and stub instead.

    It can be used as a context manager or decorator.

    Example: Usage as a context manager

        ```python
        @patch_client_class(SomeApiClient, SomeApiStub)
        def test_some_function(client_class: SomeApiClient):
            client = client_class(...)
            client.stub.some_method.return_value = ...
            # Your test code here
        ```

    Example: Usage as a decorator
        ```python
        def test_some_function():
            with patch_client_class(SomeApiClient, SomeApiStub) as client_class:
                client = client_class(...)
                client.stub.some_method.return_value = ...
                # Your test code here
        ```
    """

    def __init__(self, client_class: type[ClientT], stub_class: type[StubT]) -> None:
        """Context manager that patches the client for testing.

        Args:
            client_class: The client class to patch.
            stub_class: The stub class to patch.
        """
        # We need the type ignores here because:
        # 1. mypy doesn't consider types hashable (needed for the
        #    is_subclass_of_generic cache), but they are, based on their memory
        #    address, which is enough for us.
        # 2. mypy expect classes, TypeVar or other type expressions, but we are
        #    using a *regular variable* here. In general this is wrong, and
        #    can't be properly type checked, but it does what it should at
        #    runtime.
        assert is_subclass_of_generic(
            client_class, BaseApiClient[stub_class]  # type: ignore[valid-type]
        )
        self._client_class: type[ClientT] = client_class
        self._patched_client_class = patch.object(
            client_class, "connect", autospec=True, side_effect=self._fake_connect
        )

    def __enter__(self) -> type[ClientT]:
        """Enter the context manager."""
        self._patched_client_class.__enter__()
        return self._client_class

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        """Exit the context manager."""
        self._patched_client_class.__exit__(*args, **kwargs)

    def _fake_connect(
        self,
        client: ClientT,
        server_url: str | None = None,
        auth_key: str | None = None,  # pylint: disable=unused-argument
        sign_secret: str | None = None,  # pylint: disable=unused-argument
    ) -> None:
        """Fake connect method that does nothing."""
        # pylint: disable=protected-access
        if server_url is not None and server_url != client._server_url:  # URL changed
            client._server_url = server_url
        elif client.is_connected:
            return
        client._channel = MagicMock(name="_channel", spec=Channel)
        # We don't spec the stub because we would need the `AsyncStub` for that,
        # but it only exists for type hints, so it can't be used at runtime.
        client._stub = MagicMock(name="_stub")
        # pylint: enable=protected-access


async def _iter_to_async_iter(it: Iterable[Any]) -> AsyncIterator[Any]:
    """Return an async iterator from an iterable."""
    for item in it:
        yield item


class _IterableResponseWrapper(AsyncIterator[Any]):
    """Wrap a response to make it an async iterator.

    Supports the following types of `response`:

    * Async generator function
    * Generator function
    * Async generator
    * Generator
    * Async iterable
    * Iterable
    * Single value (`str`, `bytes` and non-iterables)
    """

    def __init__(self, response: Any) -> None:
        """Initialize the wrapper with the response."""
        self._response = response
        self._iter_is_async = False
        self._iter_is_generator = False
        self._iter: Any

        if inspect.isasyncgenfunction(response):
            _logger.debug(
                "`grpc_response` is an async generator function: %r", response
            )
            self._iter_is_async = True
            self._iter_is_generator = True
            self._iter = response()
        elif inspect.isgeneratorfunction(response):
            _logger.debug("`grpc_response` is a generator function: %r", response)
            self._iter_is_generator = True
            self._iter = response()
        elif inspect.isasyncgen(response):
            _logger.debug("`grpc_response` is an async generator: %r", response)
            self._iter_is_async = True
            self._iter_is_generator = True
            self._iter = response
        elif inspect.isgenerator(response):
            _logger.debug("`grpc_response` is a generator: %r", response)
            self._iter_is_generator = True
            self._iter = response
        elif isinstance(response, AsyncIterable):
            _logger.debug("`grpc_response` is an async iterable: %r", response)
            self._iter_is_async = True
            self._iter = aiter(response)
        # We check for str and bytes here because they are iterable, but it
        # would be very unlikely that users want to use them as iterator.
        # If they do, they can just use grpc_response = iter([...]) to explicitly
        # create an iterator from it.
        elif isinstance(response, (str, bytes)):
            _logger.debug(
                "`grpc_response` is a string or bytes, wrapping in a list as an iterator: %r",
                response,
            )
            self._iter = iter([response])
        elif isinstance(response, Iterable):
            _logger.debug("`grpc_response` is an iterable: %r", response)
            self._iter = iter(response)
        else:
            _logger.debug(
                "`grpc_response` is not iterable, wrapping in a list as an iterator: %r",
                response,
            )
            self._iter = iter([response])

    def __aiter__(self) -> _IterableResponseWrapper:
        """Return the iterator."""
        return self

    async def __anext__(self) -> Any:
        """Return the next item from the iterator."""
        if self._iter_is_async:
            _logger.debug("`grpc_response` is async, awaiting next item")
            return await anext(self._iter)

        try:
            _logger.debug("`grpc_response` is sync, getting next item without await")
            return next(self._iter)
        except StopIteration as exc:
            raise StopAsyncIteration from exc

    async def aclose(self) -> None:
        """Close the iterator."""
        if self._iter_is_generator:
            if self._iter_is_async:
                _logger.debug(
                    "`grpc_response` is async generator, awaiting for `aclose()`"
                )
                await self._iter.aclose()
            else:
                _logger.debug("`grpc_response` is generator, calling `close()`")
                self._iter.close()
