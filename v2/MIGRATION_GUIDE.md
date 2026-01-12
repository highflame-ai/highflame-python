# Migration Guide: Javelin SDK v1 to Highflame SDK v2

This guide helps you migrate your code from the Javelin SDK v1 to the Highflame SDK v2.

## Overview

The v2 release is a complete refactoring of the Javelin SDK for Highflame. While the functionality remains largely the same, many names and references have changed to be more generic and properly branded for Highflame.

## Breaking Changes

### 1. Import Statements

**v1:**
```python
from javelin_sdk import JavelinClient, JavelinConfig
from javelin_sdk.exceptions import JavelinClientError
```

**v2:**
```python
from highflame import Highflame, Config
from highflame.exceptions import ClientError
```

### 2. Environment Variables

All environment variable names have changed from `JAVELIN_*` to `HIGHFLAME_*`:

| v1 | v2 |
|----|-----|
| `JAVELIN_API_KEY` | `HIGHFLAME_API_KEY` |
| `JAVELIN_VIRTUALAPIKEY` | `HIGHFLAME_VIRTUALAPIKEY` |
| `JAVELIN_BASE_URL` | `HIGHFLAME_BASE_URL` |

**v1:**
```python
import os
api_key = os.getenv("JAVELIN_API_KEY")
```

**v2:**
```python
import os
api_key = os.getenv("HIGHFLAME_API_KEY")
```

### 3. Configuration Class

**v1:**
```python
from javelin_sdk import JavelinConfig

config = JavelinConfig(
    javelin_api_key=api_key,
    javelin_virtualapikey=virtual_api_key,
    base_url="https://api-dev.javelin.live"
)
```

**v2:**
```python
from highflame import Config

config = Config(
    api_key=api_key,
    virtual_api_key=virtual_api_key,
    base_url="https://api.highflame.app"
)
```

**Configuration Field Changes:**
- `javelin_api_key` → `api_key`
- `javelin_virtualapikey` → `virtual_api_key`

### 4. Client Class

**v1:**
```python
from javelin_sdk import JavelinClient

client = JavelinClient(config)
```

**v2:**
```python
from highflame import Highflame

client = Highflame(config)
```

### 5. Exception Classes

**v1:**
```python
from javelin_sdk.exceptions import (
    JavelinClientError,
    RouteNotFoundError,
    ProviderNotFoundError,
)

try:
    client.query_route(...)
except JavelinClientError as e:
    print(f"Error: {e}")
```

**v2:**
```python
from highflame.exceptions import (
    ClientError,
    RouteNotFoundError,
    ProviderNotFoundError,
)

try:
    client.query_route(...)
except ClientError as e:
    print(f"Error: {e}")
```

### 6. HTTP Headers

Custom headers passed to external clients have been renamed:

| v1 | v2 |
|----|-----|
| `x-javelin-apikey` | `x-highflame-apikey` |
| `x-javelin-virtualapikey` | `x-highflame-virtualapikey` |
| `x-javelin-route` | `x-highflame-route` |
| `x-javelin-model` | `x-highflame-model` |
| `x-javelin-provider` | `x-highflame-provider` |

### 7. Base URL Change

The default API endpoint URL has changed:

| v1 | v2 |
|----|-----|
| `https://api-dev.javelin.live` | `https://api.highflame.app` |

### 8. Cache Directory

The CLI cache directory has moved:

| v1 | v2 |
|----|-----|
| `~/.javelin/` | `~/.highflame/` |

### 9. CLI Command

When authenticating via CLI:

**v1:**
```bash
javelin auth
```

**v2:**
```bash
highflame auth
```

### 10. Span/Telemetry Attributes

OpenTelemetry span attributes have been updated:

| v1 | v2 |
|----|-----|
| `javelin.response.body` | `highflame.response.body` |
| `javelin.error` | `highflame.error` |

Tracer and service names:
- Tracer name: `"javelin"` → `"highflame"`
- Service name: `"javelin-sdk"` → `"highflame"`

## Complete Migration Example

### v1 Code:
```python
import os
from javelin_sdk import JavelinClient, JavelinConfig
from javelin_sdk.exceptions import RouteNotFoundError

# Get API key from environment
api_key = os.getenv("JAVELIN_API_KEY")

# Create configuration
config = JavelinConfig(
    javelin_api_key=api_key,
    base_url="https://api-dev.javelin.live"
)

# Create client
client = JavelinClient(config)

# Query a route
try:
    response = client.query_route(
        route_name="my_route",
        query_body={
            "messages": [{"role": "user", "content": "Hello"}],
            "model": "gpt-4"
        }
    )
    print(response)
except RouteNotFoundError as e:
    print(f"Route not found: {e}")
finally:
    client.close()
```

### v2 Code:
```python
import os
from highflame import Highflame, Config
from highflame.exceptions import RouteNotFoundError

# Get API key from environment
api_key = os.getenv("HIGHFLAME_API_KEY")

# Create configuration
config = Config(
    api_key=api_key,
    base_url="https://api.highflame.app"
)

# Create client
client = Highflame(config)

# Query a route
try:
    response = client.query_route(
        route_name="my_route",
        query_body={
            "messages": [{"role": "user", "content": "Hello"}],
            "model": "gpt-4"
        }
    )
    print(response)
except RouteNotFoundError as e:
    print(f"Route not found: {e}")
finally:
    client.close()
```

## API Compatibility

The v2 SDK maintains **full API compatibility** with v1 in terms of functionality. All methods, parameters, and responses remain the same - only the naming conventions have changed.

## Services and Operations

All services remain the same with no API changes:
- `route_service`
- `provider_service`
- `gateway_service`
- `secret_service`
- `template_service`
- `trace_service`
- `modelspec_service`
- `guardrails_service`
- `aispm` (AISPM service)
- `chat`
- `completions`
- `embeddings`

Example (no change in usage):
```python
# v1 and v2 are identical
routes = client.route_service.list_routes()
gateway = client.gateway_service.get_gateway("my_gateway")
```

## Async/Await Support

Async support remains unchanged in v2:

```python
async with Highflame(config) as client:
    response = await client.aquery_route(
        route_name="my_route",
        query_body={...}
    )
```

## Documentation

For more information, see:
- [Highflame Documentation](https://docs.highflame.com)
- [Python SDK Documentation](https://docs.highflame.com/docs/python-sdk)

## Support

If you encounter any issues during migration, please report them to the Highflame team.
