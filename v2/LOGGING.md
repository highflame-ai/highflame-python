# Logging Guide for Highflame SDK

The Highflame SDK includes built-in logging support to help debug issues and monitor application behavior in production.

## Setup

### Basic Configuration

Logging is configured using Python's standard `logging` module. To enable debug logging:

```python
import logging

# Enable debug logging for the SDK
logging.basicConfig(level=logging.DEBUG)

# Or set logging for specific modules
logging.getLogger("highflame").setLevel(logging.DEBUG)
logging.getLogger("highflame.services").setLevel(logging.DEBUG)
```

### Production Configuration

For production, use a structured logging approach:

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

## Log Levels

The SDK uses standard Python logging levels:

- **DEBUG** - Detailed information for diagnosing problems
  - Client initialization
  - Route queries
  - Service operations
  - Tracing configuration

- **INFO** - General informational messages (not currently used)

- **WARNING** - Warning messages for potentially problematic situations

- **ERROR** - Error messages for failures

- **CRITICAL** - Critical messages for severe failures

## Available Loggers

### Main Loggers

| Logger | Purpose |
|--------|---------|
| `highflame.client` | Main Highflame client operations |
| `highflame.services.route_service` | Route querying and management |
| `highflame.services.gateway_service` | Gateway operations |
| `highflame.services.provider_service` | Provider operations |
| `highflame.services.secret_service` | Secret management |
| `highflame.services.template_service` | Template operations |
| `highflame.tracing_setup` | OpenTelemetry tracing configuration |

## Example: Full Debug Logging

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

Output:
```
2024-01-11 12:34:56,789 - highflame.client - DEBUG - Initializing Highflame client with base_url=https://api.highflame.app/v1
2024-01-11 12:34:56,791 - highflame.tracing_setup - DEBUG - Configuring OTLP span exporter with endpoint=https://...
2024-01-11 12:34:56,792 - highflame.tracing_setup - DEBUG - OTLP span exporter configured successfully
2024-01-11 12:34:56,850 - highflame.services.route_service - DEBUG - Querying route: my_route, stream=False
```

## Troubleshooting

### Enable logging to debug initialization issues:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

from highflame import Highflame, Config
config = Config(api_key="...")
client = Highflame(config)
```

### Check tracing configuration:
```python
import logging
logging.getLogger("highflame.tracing_setup").setLevel(logging.DEBUG)
```

### Monitor service operations:
```python
logging.getLogger("highflame.services").setLevel(logging.DEBUG)
```

## Best Practices

1. **Use DEBUG level during development** to understand SDK behavior
2. **Use INFO level in production** to minimize log volume
3. **Implement structured logging** for better analysis in production
4. **Set up log aggregation** to collect logs from multiple instances
5. **Configure log rotation** to manage disk space
6. **Avoid logging sensitive data** - the SDK avoids logging API keys

## Integration with Observability Tools

### CloudWatch
```python
import logging
from watchtower import CloudWatchLogHandler

handler = CloudWatchLogHandler(
    log_group="/aws/highflame",
    stream_name="sdk-logs"
)
logging.getLogger("highflame").addHandler(handler)
```

### Datadog
```python
from datadog import api
from datadog.logger import DatadogHandler

handler = DatadogHandler(
    api_key="your-datadog-key"
)
logging.getLogger("highflame").addHandler(handler)
```

### ELK Stack
```python
from pythonjsonlogger import jsonlogger
import logging

handler = logging.FileHandler("highflame.json")
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logging.getLogger("highflame").addHandler(handler)
```
