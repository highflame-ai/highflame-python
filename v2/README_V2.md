# Highflame Python SDK v2

Welcome to the Highflame Python SDK v2! This is a complete refactoring of the former Javelin SDK, now branded and optimized for Highflame.

## What's New in v2

### Key Changes

1. **Rebranding**: All "Javelin" references have been replaced with "Highflame" for company-specific elements (API keys, configuration, headers)

2. **Generic Class Names**: Code-level abstractions no longer reference the company name:
   - `JavelinClient` → `Client`
   - `JavelinConfig` → `Config`
   - `JavelinClientError` → `ClientError`
   - `JavelinRequestWrapper` → `RequestWrapper`

3. **Simplified Package Structure**:
   - Package directory: `highflame/` (was `javelin_sdk/`)
   - CLI directory: `highflame_cli/` (was `javelin_cli/`)

4. **Updated Configuration**:
   - Environment variables: `JAVELIN_*` → `HIGHFLAME_*`
   - Config field names: `javelin_api_key` → `api_key`, `javelin_virtualapikey` → `virtual_api_key`
   - Default URL: `https://api-dev.javelin.live` → `https://api.highflame.app`

5. **HTTP Headers**: All custom headers updated:
   - `x-javelin-apikey` → `x-highflame-apikey`
   - `x-javelin-route` → `x-highflame-route`
   - And all other `x-javelin-*` → `x-highflame-*`

## Directory Structure

```
v2/
├── highflame/              # Core SDK package
│   ├── __init__.py             # Public API exports
│   ├── client.py               # Highflame class (was JavelinClient)
│   ├── models.py               # Config & data models
│   ├── exceptions.py           # Exception classes
│   ├── chat_completions.py     # Chat/Completions/Embeddings
│   ├── model_adapters.py       # Provider adapters
│   ├── tracing_setup.py        # OpenTelemetry configuration
│   └── services/               # Service classes
│       ├── route_service.py
│       ├── provider_service.py
│       ├── gateway_service.py
│       ├── secret_service.py
│       ├── template_service.py
│       ├── trace_service.py
│       ├── modelspec_service.py
│       ├── guardrails_service.py
│       └── aispm_service.py
│
├── highflame_cli/              # Command-line interface
│   ├── __init__.py
│   ├── cli.py                  # Main CLI entry point
│   └── _internal/
│       └── commands.py         # CLI commands
│
├── examples/                   # Integration examples
│   ├── openai/                 # OpenAI examples (renamed from javelin_*)
│   ├── azure-openai/           # Azure OpenAI examples
│   ├── bedrock/                # AWS Bedrock examples
│   ├── gemini/                 # Google Gemini examples
│   ├── anthropic/              # Anthropic examples
│   ├── mistral/                # Mistral examples
│   ├── agents/                 # Agent examples (CrewAI, LangGraph, etc.)
│   ├── rag/                    # RAG examples
│   ├── guardrails/             # Guardrails examples
│   ├── customer_support_agent/ # Customer support use case
│   └── route_examples/         # Route configuration examples
│
├── swagger/                    # OpenAPI/Swagger tools
│   ├── sync_models.py          # Model synchronization utility
│   └── swagger.yaml            # API specification
│
├── MIGRATION_GUIDE.md          # Complete migration guide from v1
└── README_V2.md               # This file
```

## Quick Start

### Installation

```bash
pip install highflame
```

### Basic Usage

```python
from highflame import Highflame, Config
import os

# Get your API key from environment
api_key = os.getenv("HIGHFLAME_API_KEY")

# Create configuration
config = Config(
    api_key=api_key,
    base_url="https://api.highflame.app"  # Or your custom URL
)

# Initialize client
client = Highflame(config)

# Query a route
response = client.query_route(
    route_name="my_route",
    query_body={
        "messages": [{"role": "user", "content": "Hello"}],
        "model": "gpt-4"
    }
)

print(response)

# Don't forget to close
client.close()
```

### Async Usage

```python
from highflame import Highflame, Config

async with Highflame(config) as client:
    response = await client.aquery_route(
        route_name="my_route",
        query_body={...}
    )
```

### Using with External Clients

```python
from openai import OpenAI
from highflame import Highflame, Config

# Initialize your OpenAI client
openai_client = OpenAI(api_key=openai_api_key)

# Register it with Highflame for monitoring/routing
client = Highflame(config)
client.register_openai(openai_client, route_name="my_openai_route")

# Now requests go through Highflame
response = openai_client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
```

## API Services

The SDK provides access to multiple services:

### Route Management
```python
# Create, read, update, delete routes
route = client.route_service.create_route(route)
routes = client.route_service.list_routes()
route = client.route_service.get_route("route_name")
client.route_service.update_route("route_name", updated_route)
client.route_service.delete_route("route_name")
```

### Provider Management
```python
providers = client.provider_service.list_providers()
provider = client.provider_service.get_provider("provider_name")
```

### Gateway Management
```python
gateways = client.gateway_service.list_gateways()
gateway = client.gateway_service.get_gateway("gateway_name")
```

### Secrets Management
```python
secret = client.secret_service.create_secret(secret)
secrets = client.secret_service.list_secrets()
```

### Templates Management
```python
templates = client.template_service.list_templates()
template = client.template_service.get_template("template_name")
```

### AI Spend & Performance Management (AISPM)
```python
usage = client.aispm.get_usage()
alerts = client.aispm.get_alerts()
customers = client.aispm.list_customers()
```

### Guardrails
```python
guardrails = client.guardrails_service.list_guardrails()
```

### Tracing
```python
traces = client.trace_service.get_traces()
```

## Configuration

### Environment Variables

Set these environment variables to configure the SDK:

```bash
# Required
export HIGHFLAME_API_KEY="your-api-key"

# Optional
export HIGHFLAME_BASE_URL="https://api.highflame.app"
export HIGHFLAME_VIRTUALAPIKEY="your-virtual-api-key"

# OpenTelemetry configuration (optional)
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="https://your-otel-endpoint/v1/traces"
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer token"
```

### Programmatic Configuration

```python
from highflame import Config

config = Config(
    api_key="your-api-key",
    base_url="https://api.highflame.app",
    virtual_api_key="optional-virtual-key",  # For multi-tenancy
    llm_api_key="optional-llm-key",          # For LLM providers
    api_version="/v1",                        # API version
    timeout=30,                               # Request timeout in seconds
    default_headers={"X-Custom": "value"}    # Custom headers
)
```

## CLI Usage

The Highflame CLI is available for managing resources:

```bash
# Authenticate
highflame auth

# Manage routes
highflame routes list
highflame routes create --name my_route --file route.json

# Manage providers
highflame providers list

# Manage gateways
highflame gateways list

# AISPM commands
highflame aispm usage
highflame aispm alerts
highflame aispm customer create --name "My Customer"
```

## Error Handling

```python
from highflame.exceptions import (
    ClientError,
    RouteNotFoundError,
    ProviderNotFoundError,
    UnauthorizedError,
    RateLimitExceededError,
)

try:
    response = client.query_route(route_name="my_route", query_body={...})
except RouteNotFoundError as e:
    print(f"Route not found: {e}")
except UnauthorizedError as e:
    print(f"Authentication failed: {e}")
except RateLimitExceededError as e:
    print(f"Rate limit exceeded: {e}")
except ClientError as e:
    print(f"Error: {e}")
```

## OpenTelemetry Integration

The SDK includes built-in OpenTelemetry tracing:

```python
import os

# Configure trace endpoint
os.environ["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"] = "https://your-otel-endpoint/v1/traces"

# Traces are automatically captured for all operations
client = Highflame(config)
response = client.query_route(...)  # Trace automatically created
```

Span attributes include:
- `gen_ai.system`: LLM provider (e.g., "openai", "aws.bedrock")
- `gen_ai.operation.name`: Operation type (e.g., "chat", "embeddings")
- `gen_ai.request.model`: Model name
- `gen_ai.usage.input_tokens`: Input token count
- `gen_ai.usage.output_tokens`: Output token count
- `highflame.response.body`: Response body
- `highflame.error`: Error information

## Examples

See the `examples/` directory for complete examples:

- **OpenAI Integration**: `examples/openai/highflame_openai_univ_endpoint.py`
- **Azure OpenAI**: `examples/azure-openai/highflame_azureopenai_univ_endpoint.py`
- **AWS Bedrock**: `examples/bedrock/highflame_bedrock_univ_endpoint.py`
- **Google Gemini**: `examples/gemini/highflame_gemini_univ_endpoint.py`
- **Agents**: `examples/agents/` (CrewAI, LangGraph, OpenAI Agents)
- **RAG**: `examples/rag/`
- **Guardrails**: `examples/guardrails/`

## Migration from v1

If you're upgrading from the Javelin SDK v1, please see the [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) for detailed instructions on updating your code.

## Documentation

- [Highflame Documentation](https://docs.highflame.com)
- [Python SDK Reference](https://docs.highflame.com/docs/python-sdk)
- [API Reference](https://docs.highflame.com/docs/api)

## Support

For issues, questions, or feedback:
- Create an issue on GitHub
- Contact the Highflame team

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
