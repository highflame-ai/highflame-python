# OTEL Traces Example

This example demonstrates how to push OpenTelemetry traces from your AI application to Highflame Workbench for analysis and monitoring.

## Overview

The `generate_traces.py` script shows how to:

- Configure OpenTelemetry to send traces to Highflame's OTEL endpoint
- Create spans for LLM operations (OpenAI in this example)
- Add custom attributes to track model, prompts, responses, and usage metrics
- View and analyze traces in the Highflame Workbench UI

## Prerequisites

- Python 3.9 or higher
- OpenAI API key (for this example)
- Highflame authorization credentials

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Set up your environment variables (see Configuration section below)

## Configuration

### Required Environment Variables

**OTEL_EXPORTER_OTLP_HEADERS** (Required)

- Authorization header for Highflame Workbench
- Example:
  ```bash
  export OTEL_EXPORTER_OTLP_HEADERS="your-otel-header"
  ```

**OPENAI_API_KEY** (Required for this example)

- Your OpenAI API key
- Example:
  ```bash
  export OPENAI_API_KEY="sk-your-openai-api-key"
  ```

### Optional Environment Variables

**OTLP_ENDPOINT**

- OTEL endpoint URL
- Example:
  ```bash
  export OTLP_ENDPOINT="https://cerberus-http.api-dev.highflame.dev/v1/traces"
  ```

**OTEL_SERVICE_NAME** (Optional)

- Name of your service for identification in Workbench
- Default: `"trace-generator"`
- Example:
  ```bash
  export OTEL_SERVICE_NAME="my-ai-application"
  ```

## Usage

1. Set your environment variables:

```bash
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Basic%20<your-credentials>"
export OPENAI_API_KEY="sk-your-openai-api-key"
```

2. Run the script:

```bash
python generate_traces.py
```

3. Expected output:

```
2
```

The script will:

- Make an OpenAI API call (calculating "1 + 1")
- Create an OpenTelemetry span for the operation
- Add attributes including model, prompt, response, and token usage
- Send the trace to Highflame Workbench
- Print the answer

## Viewing Traces in Workbench

After running the script:

1. **Access Workbench UI**: Navigate to your Highflame Workbench dashboard
2. **View Traces**: Look for traces with:
   - Service name: `trace-generator` (or your custom `OTEL_SERVICE_NAME`)
   - Span name: `openai.chat.completions.create`
3. **Analyze Data**: You can view:
   - Trace timeline and duration
   - Model information (`llm.model`)
   - Prompt and response data (`input`, `output`, `prompt.user_question`)
   - Token usage metrics (`llm.usage.prompt_tokens`, `llm.usage.completion_tokens`, `llm.usage.total_tokens`)
   - Response ID and preview

## Trace Attributes

The script adds the following attributes to each span:

| Attribute                     | Description                 | Example          |
| ----------------------------- | --------------------------- | ---------------- |
| `llm.model`                   | LLM model used              | `"gpt-4o"`       |
| `prompt.user_question`        | User's question/prompt      | `"1 + 1 = "`     |
| `response.id`                 | Unique response ID          | `"chatcmpl-..."` |
| `response.preview`            | Response preview            | `"2"`            |
| `input`                       | Full input text             | `"1 + 1 = "`     |
| `output`                      | Full output text            | `"2"`            |
| `llm.usage.prompt_tokens`     | Number of prompt tokens     | `10`             |
| `llm.usage.completion_tokens` | Number of completion tokens | `1`              |
| `llm.usage.total_tokens`      | Total tokens used           | `11`             |

## Customization

### Using a Different LLM Provider

You can adapt this script for other LLM providers:

1. Replace the OpenAI client with your provider's SDK
2. Update the span attributes to match your provider's response format
3. Keep the OTEL configuration the same

### Custom Service Name

Set a custom service name to identify your application:

```bash
export OTEL_SERVICE_NAME="my-custom-service"
python generate_traces.py
```

### Custom Endpoint

Use a different OTEL endpoint:

```bash
export OTLP_ENDPOINT="https://your-custom-endpoint.com/v1/traces"
python generate_traces.py
```

## Troubleshooting

### Connection Errors

If you get connection errors when sending traces:

1. **Verify endpoint URL**: Check that `OTLP_ENDPOINT` is correct
2. **Check authorization header**: Ensure `OTEL_EXPORTER_OTLP_HEADERS` is properly formatted
3. **Network connectivity**: Verify you can reach the endpoint

### OpenAI API Errors

If you encounter OpenAI API errors:

1. **Check API key**: Verify `OPENAI_API_KEY` is set and valid
2. **Check quota**: Ensure your OpenAI account has available quota
3. **Verify model**: Ensure the model name (`gpt-4o`) is correct and available

### Traces Not Appearing in Workbench

If traces don't appear in Workbench:

1. **Check authorization**: Verify your `OTEL_EXPORTER_OTLP_HEADERS` credentials are correct
2. **Wait a few seconds**: Traces may take a moment to appear
3. **Check service name**: Look for traces with your `OTEL_SERVICE_NAME` (default: `trace-generator`)
4. **Verify endpoint**: Ensure you're using the correct endpoint for your environment

## Related Documentation

- [Highflame Workbench Documentation](https://docs.highflame.ai/)
- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/instrumentation/python/)
- [OpenTelemetry OTLP Protocol](https://opentelemetry.io/docs/specs/otlp/)
