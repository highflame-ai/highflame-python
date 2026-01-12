[![Ask DeepWiki](https://deepwiki.com/badge.svg "DeepWiki Documentation")](https://deepwiki.com/getjavelin/javelin-python)

## Highflame: Enterprise-Scale LLM Gateway

This is the Python SDK for Highflame - an enterprise-scale, fast LLM gateway that provides unified access to multiple LLM providers with advanced routing, monitoring, and management capabilities.

**Package Name:** `highflame` (v2.0.0)  
**Previous Package:** `javelin_sdk`

For more information about Highflame, see [https://highflame.com](https://highflame.com)

Highflame Documentation: [https://docs.highflame.ai/](https://docs.highflame.ai/)

---

## Quick Start

### Installation

**SDK:**

```bash
pip install highflame
```

**CLI:**

```bash
pip install highflame-cli
```

> **Note:** The CLI package (`highflame-cli`) depends on the SDK package (`highflame`), so installing the CLI will automatically install the SDK as well.

### Basic Usage

**Using the SDK:**

```python
from highflame import Highflame, Config
import os

# Initialize client
config = Config(api_key=os.getenv("HIGHFLAME_API_KEY"))
client = Highflame(config)

# Query a route
response = client.query_route(
    route_name="my_route",
    query_body={"messages": [{"role": "user", "content": "Hello!"}], "model": "gpt-4"}
)
```

**Using the CLI:**

```bash
# Authenticate
highflame auth

# List routes
highflame routes list

# Create a route
highflame routes create --name my_route --file route.json

# Get route details
highflame routes get --name my_route
```

---

## What Changed

### Package & Import Changes

**v1:**

```python
from javelin_sdk import JavelinClient, JavelinConfig
```

**v2:**

```python
from highflame import Highflame, Config
```

### Class Name Changes

| v1                   | v2            |
| -------------------- | ------------- |
| `JavelinClient`      | `Highflame`   |
| `JavelinConfig`      | `Config`      |
| `JavelinClientError` | `ClientError` |

### Configuration Changes

**Environment Variables:**
All environment variable names have changed from `JAVELIN_*` to `HIGHFLAME_*`:

| v1                      | v2                        |
| ----------------------- | ------------------------- |
| `JAVELIN_API_KEY`       | `HIGHFLAME_API_KEY`       |
| `JAVELIN_VIRTUALAPIKEY` | `HIGHFLAME_VIRTUALAPIKEY` |
| `JAVELIN_BASE_URL`      | `HIGHFLAME_BASE_URL`      |

**Configuration Fields:**

- `javelin_api_key` → `api_key`
- `javelin_virtualapikey` → `virtual_api_key`
- Default `base_url`: `https://api-dev.javelin.live` → `https://api.highflame.app`

**Example:**

**v1:**

```python
from javelin_sdk import JavelinConfig

config = JavelinConfig(javelin_api_key="your-key")
```

**v2:**

```python
from highflame import Config

config = Config(api_key="your-key")
```

### HTTP Headers (Backward Compatible)

v2 sends **both** old and new headers for backward compatibility during the transition period:

| Header Type     | v1                        | v2 (Primary)                | v2 (Backward Compat)      |
| --------------- | ------------------------- | --------------------------- | ------------------------- |
| API Key         | `x-javelin-apikey`        | `x-highflame-apikey`        | `x-javelin-apikey`        |
| Virtual API Key | `x-javelin-virtualapikey` | `x-highflame-virtualapikey` | `x-javelin-virtualapikey` |
| Route           | `x-javelin-route`         | `x-highflame-route`         | `x-javelin-route`         |
| Model           | `x-javelin-model`         | `x-highflame-model`         | `x-javelin-model`         |
| Provider        | `x-javelin-provider`      | `x-highflame-provider`      | `x-javelin-provider`      |
| Account ID      | `x-javelin-accountid`     | `x-highflame-accountid`     | `x-javelin-accountid`     |
| User            | `x-javelin-user`          | `x-highflame-user`          | `x-javelin-user`          |
| User Role       | `x-javelin-userrole`      | `x-highflame-userrole`      | `x-javelin-userrole`      |

**Note:** Both header formats are sent simultaneously to ensure compatibility with existing backends.

### API Endpoint Changes

| v1                             | v2                          |
| ------------------------------ | --------------------------- |
| `https://api-dev.javelin.live` | `https://api.highflame.app` |

### Exception Handling

**v1:**

```python
from javelin_sdk.exceptions import (
    JavelinClientError,
    GatewayNotFoundError,
    RouteNotFoundError,
    # ... etc
)
```

**v2:**

```python
from highflame.exceptions import (
    ClientError,
    GatewayNotFoundError,
    RouteNotFoundError,
    # ... etc
)
```

All exception classes now inherit from `ClientError` instead of `JavelinClientError`.

### OpenTelemetry Tracing

**Service & Tracer Names:**

- Service name: `"javelin-sdk"` → `"highflame"`
- Tracer name: `"javelin"` → `"highflame"`

**Span Attributes:**

- `javelin.response.body` → `highflame.response.body`
- `javelin.error` → `highflame.error`

### CLI Changes

**Command Name:**

- `javelin` → `highflame`

**Cache Directory:**

- `~/.javelin/` → `~/.highflame/`

**Example:**

**v1:**

```bash
javelin auth
javelin routes list
```

**v2:**

```bash
highflame auth
highflame routes list
```

### Exception Handling Changes

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

### Complete Migration Example

**v1 Code:**

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

**v2 Code:**

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

### Async/Await Support

Async support remains unchanged in v2:

```python
async with Highflame(config) as client:
    response = await client.aquery_route(
        route_name="my_route",
        query_body={...}
    )
```

### Migration Checklist

1. ✅ Update package installation: `pip install highflame` (instead of `javelin_sdk` or `highflame-sdk`)
2. ✅ Update imports: `from highflame import Highflame, Config`
3. ✅ Update class names: `JavelinClient` → `Highflame`, `JavelinConfig` → `Config`
4. ✅ Update environment variables: `JAVELIN_*` → `HIGHFLAME_*`
5. ✅ Update configuration field names: `javelin_api_key` → `api_key`
6. ✅ Update API endpoint if using custom base URL
7. ✅ Update exception imports: `JavelinClientError` → `ClientError`
8. ✅ Update CLI commands: `javelin` → `highflame`
9. ✅ Update cache directory references if any

**Note:** HTTP headers are backward compatible - both old and new headers are sent automatically, so no immediate changes needed for header handling. The v2 SDK maintains **full API compatibility** with v1 in terms of functionality - all methods, parameters, and responses remain the same, only naming conventions have changed.

---

## Development Setup

### Setting up Virtual Environment

#### Windows

```batch
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install poetry
poetry install
```

#### macOS/Linux

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install poetry
poetry install
```

### Building and Installing the SDK

```bash
# Uninstall any existing version
pip uninstall highflame highflame-sdk javelin_sdk -y

# Build the package
poetry build

# Install the newly built package
pip install dist/highflame-<version>-py3-none-any.whl
```

### Development Notes

For local development, change `version = "RELEASE_VERSION"` with any semantic version (e.g., `version = "2.0.1"`) in `pyproject.toml`.

**⚠️ Important:** Make sure to revert `pyproject.toml` before committing to main.

---

## Universal Endpoints

Highflame provides universal endpoints that allow you to use a consistent interface across different LLM providers. Here are the main patterns:

### Azure OpenAI

- [Basic Azure OpenAI integration](https://github.com/highflame-ai/highflame-python/blob/main/examples/azure-openai/azure-universal.py)
- [Universal endpoint implementation](https://github.com/highflame-ai/highflame-python/blob/main/examples/azure-openai/highflame_azureopenai_univ_endpoint.py)
- [OpenAI-compatible interface](https://github.com/highflame-ai/highflame-python/blob/main/examples/azure-openai/openai_compatible_univ_azure.py)

### Bedrock

- [Basic Bedrock integration](https://github.com/highflame-ai/highflame-python/blob/main/examples/bedrock/bedrock_client_universal.py)
- [Universal endpoint implementation](https://github.com/highflame-ai/highflame-python/blob/main/examples/bedrock/highflame_bedrock_univ_endpoint.py)
- [OpenAI-compatible interface](https://github.com/highflame-ai/highflame-python/blob/main/examples/bedrock/openai_compatible_univ_bedrock.py)

### Gemini

- [Basic Gemini integration](https://github.com/highflame-ai/highflame-python/blob/main/examples/gemini/gemini-universal.py)
- [Universal endpoint implementation](https://github.com/highflame-ai/highflame-python/blob/main/examples/gemini/highflame_gemini_univ_endpoint.py)
- [OpenAI-compatible interface](https://github.com/highflame-ai/highflame-python/blob/main/examples/gemini/openai_compatible_univ_gemini.py)

### Agent Examples

- [CrewAI integration](https://github.com/highflame-ai/highflame-python/blob/main/examples/agents/crewai_highflame.ipynb)
- [LangGraph integration](https://github.com/highflame-ai/highflame-python/blob/main/examples/agents/langgraph_highflame.ipynb)

### Basic Examples

- [Asynchronous example](https://github.com/highflame-ai/highflame-python/blob/main/examples/route_examples/aexample.py)
- [Synchronous example](https://github.com/highflame-ai/highflame-python/blob/main/examples/route_examples/example.py)
- [Drop-in replacement example](https://github.com/highflame-ai/highflame-python/blob/main/examples/route_examples/drop_in_replacement.py)

### Advanced Examples

- [Document processing](https://github.com/highflame-ai/highflame-python/blob/main/examples/gemini/document_processing.py)
- [RAG implementation](https://github.com/highflame-ai/highflame-python/blob/main/examples/rag/highflame_rag_embeddings_demo.ipynb)

---

## Additional Integration Patterns

For more detailed examples and integration patterns, check out:

- [Azure OpenAI Integration](https://docs.highflame.ai/documentation/getting-started/gateway-integration-examples#id-2-azure-openai-api-endpoints)
- [AWS Bedrock Integration](https://docs.highflame.ai/documentation/getting-started/gateway-integration-examples#id-3-aws-bedrock-api-endpoints)
- [CLI Reference](https://docs.highflame.ai/api-reference/cli)

---

## Type Hints & py.typed Marker

This package includes a `py.typed` marker file, which indicates to type checkers (like `mypy`, `pyright`, `pylance`) that the package supports type checking. This allows IDEs and static analysis tools to provide better autocomplete, type checking, and refactoring support.

**Usage:**

```python
# With py.typed, type checkers can validate this:
from highflame import Highflame, Config

config: Config = Config(api_key="your-key")
client: Highflame = Highflame(config)
```

---

## Logging

The SDK includes logging support for debugging and observability. Logging is configured at the module level using Python's standard `logging` module.

### Basic Configuration

```python
import logging

# Enable debug logging for the SDK
logging.basicConfig(level=logging.DEBUG)

# Or set logging for specific modules
logging.getLogger("highflame").setLevel(logging.DEBUG)
logging.getLogger("highflame.services").setLevel(logging.DEBUG)
```

### Logging Levels

- **DEBUG** - Detailed information for diagnosing problems
  - Client initialization
  - Route queries
  - Service operations
  - Tracing configuration
- **INFO** - General informational messages
- **WARNING** - Warning messages for potentially problematic situations
- **ERROR** - Error messages for failures

### Example: Full Debug Logging

```python
import logging
from highflame import Highflame, Config

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize client
config = Config(api_key="your-key")
client = Highflame(config)

# Debug logs will show:
# - Client initialization with base URL
# - Route queries with route names
# - Tracing configuration (if enabled)
response = client.query_route(
    route_name="my_route",
    query_body={...}
)
```

### Production Configuration

For production, use structured logging:

```python
import logging
import json
from datetime import datetime

# Use JSON logging for better observability
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

# Configure handler
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())

logger = logging.getLogger("highflame")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Available Loggers

| Logger                               | Purpose                             |
| ------------------------------------ | ----------------------------------- |
| `highflame.client`                   | Main Highflame client operations    |
| `highflame.services.route_service`   | Route querying and management       |
| `highflame.services.gateway_service` | Gateway operations                  |
| `highflame.tracing_setup`            | OpenTelemetry tracing configuration |

---

## TODO

### Code Quality Improvements

- [ ] **Type Hints Coverage**: Add comprehensive type hints to all methods. Many internal methods currently return `Any` or lack return type annotations. Properties like `client`, `aclient`, `close()`, and helper methods need type hints.

- [ ] **Error Handling**: Replace broad `except Exception` blocks (27+ locations) with specific exception types. This will improve debugging and error context.

- [ ] **Backward Compatibility**: Phase out dual header support (`x-javelin-*` and `x-highflame-*`) after transition period. Create deprecation timeline and migration path.

- [ ] **Request/Response Validation**: Add validation layer for requests and responses to catch errors early.

- [ ] **HTTP Connection Pooling**: Add configuration options for HTTP connection pooling to improve performance.

### CLI Improvements

- [x] **CLI Separation**: Separate CLI into its own `highflame-cli` package. Package structure separated, ready for independent distribution.

- [ ] **CLI Error Messages**: Improve CLI error messages with troubleshooting hints and actionable guidance.

- [ ] **CLI Testing**: Add comprehensive test suite for CLI commands and edge cases.

- [ ] **CLI Documentation**: Update CLI documentation to reflect current bundled state vs. future separated state.

### Reliability & Performance

- [ ] **Automatic Retry Logic**: Implement retry logic with exponential backoff for transient failures.

- [ ] **Rate Limit Detection**: Add automatic rate limit detection and backoff handling.

- [ ] **Performance Metrics**: Add performance metrics tracking for requests, latency, and throughput.

- [ ] **Circuit Breaker Pattern**: Implement circuit breaker pattern for resilience against failing services.

- [ ] **Request Caching**: Add optional request caching layer for frequently accessed resources.

### Developer Experience

- [ ] **Deprecation Warnings**: Add deprecation warning module for v1 → v2 migration to help users transition.

- [ ] **Structured Logging**: Enhance structured JSON logging implementation for production environments.

- [ ] **Custom Middleware**: Add support for custom middleware to allow users to extend SDK functionality.

- [ ] **Better Error Messages**: Implement error messages with troubleshooting steps and links to documentation.

### Testing & Release

- [ ] **Full Test Suite**: Run and expand comprehensive test suite covering all SDK functionality.

- [ ] **Build & Distribution**: Test building distribution packages and verify installation process.

- [ ] **Installation Testing**: Test `pip install highflame` and verify all imports work correctly.

- [ ] **CLI Functionality Testing**: Test all CLI commands and verify they work as expected.

- [ ] **Performance Testing**: Conduct performance testing and optimization.

- [ ] **PyPI Publishing**: Publish `highflame` v2.0.0 to PyPI with proper release notes.

- [ ] **Documentation Updates**: Update GitHub release notes and publish migration guide on docs site.

### Architecture

- [ ] **Client Class Refactoring**: Refactor large `Highflame` class (1645 lines) into smaller, focused classes for better maintainability.

- [ ] **Constants Module**: Create centralized constants module for HTTP headers and configuration values.

- [ ] **Service Layer Improvements**: Enhance service layer with better error handling and type safety.
