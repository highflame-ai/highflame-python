# Customer Support Agent API Documentation

## Overview

The Customer Support Agent provides a RESTful API for interacting with an AI-powered customer support system. The API supports both stateful conversations (maintaining context) and stateless queries.

## Base URL

```
http://localhost:8000
```

For production deployments, replace `localhost:8000` with your server address.

## Authentication

Currently, the API does not require authentication. For production use, implement authentication middleware.

## Endpoints

### 1. Health Check

Check if the API is running and healthy.

**Endpoint:** `GET /health`

**Request:**
```bash
curl -X GET http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "customer-support-agent"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

### 2. Root Endpoint

Get API information and available endpoints.

**Endpoint:** `GET /`

**Request:**
```bash
curl -X GET http://localhost:8000/
```

**Response:**
```json
{
  "message": "Customer Support Agent API",
  "version": "1.0.0",
  "endpoints": {
    "/chat": "POST - Chat with the agent (maintains conversation state)",
    "/generate": "POST - Generate a single response (no state)",
    "/health": "GET - Health check"
  }
}
```

**Status Codes:**
- `200 OK` - Success

---

### 3. Chat Endpoint

Chat with the agent while maintaining conversation state. The agent remembers previous messages in the conversation thread, allowing for natural multi-turn conversations.

**Endpoint:** `POST /chat`

**Request Body:**
```json
{
  "message": "What is the status of my order ORD-001?",
  "thread_id": "user-123",
  "customer_id": 1
}
```

**Request Fields:**
- `message` (string, required): The user's message or question
- `thread_id` (string, optional): Unique identifier for the conversation thread. Defaults to `"default"` if not provided. Use the same `thread_id` across multiple requests to maintain conversation context.
- `customer_id` (integer, optional): Customer ID if known. Helps the agent access customer-specific information.

**Example Request:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the status of my order ORD-001?",
    "thread_id": "user-123",
    "customer_id": 1
  }'
```

**Response:**
```json
{
  "response": "Your order ORD-001 is currently shipped and should arrive within 2-3 business days. You can track it using the tracking number provided in your confirmation email.",
  "thread_id": "user-123",
  "tool_calls": [
    {
      "tool": "lookup_order_tool",
      "args": {
        "order_number": "ORD-001"
      },
      "id": "call_abc123"
    }
  ],
  "intent": "order_inquiry",
  "confidence": 0.95
}
```

**Response Fields:**
- `response` (string): The agent's response message
- `thread_id` (string): The conversation thread identifier (same as provided or default)
- `tool_calls` (array, optional): List of tools that were called during processing. Each tool call includes:
  - `tool` (string): Name of the tool that was called
  - `args` (object): Arguments passed to the tool
  - `id` (string): Unique identifier for the tool call
- `intent` (string, optional): Detected intent of the user's message (e.g., `order_inquiry`, `technical_support`, `billing`, `general`)
- `confidence` (float, optional): Confidence score of the response (0.0 to 1.0)

**Status Codes:**
- `200 OK` - Request processed successfully
- `400 Bad Request` - Invalid request body
- `500 Internal Server Error` - Server error processing request

**Multi-turn Conversation Example:**

**First Message:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need help with my order",
    "thread_id": "user-123"
  }'
```

**Response:**
```json
{
  "response": "I'd be happy to help you with your order! Could you please provide your order number?",
  "thread_id": "user-123",
  "intent": "order_inquiry",
  "confidence": 0.85
}
```

**Follow-up Message (using same thread_id):**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My order number is ORD-001",
    "thread_id": "user-123"
  }'
```

**Response:**
```json
{
  "response": "Thank you! I've looked up your order ORD-001. It's currently shipped and should arrive within 2-3 business days. The tracking number is TRACK123456.",
  "thread_id": "user-123",
  "tool_calls": [
    {
      "tool": "lookup_order_tool",
      "args": {
        "order_number": "ORD-001"
      },
      "id": "call_xyz789"
    }
  ],
  "intent": "order_inquiry",
  "confidence": 0.95
}
```

---

### 4. Generate Endpoint

Generate a single response without maintaining conversation state. Each request is treated as a new, independent conversation.

**Endpoint:** `POST /generate`

**Request Body:**
```json
{
  "message": "What is your return policy?",
  "thread_id": "optional-unique-id",
  "customer_id": 1
}
```

**Request Fields:**
- `message` (string, required): The user's message or question
- `thread_id` (string, optional): If not provided, a unique ID is generated automatically. Note: Unlike `/chat`, this endpoint does not maintain state between requests.
- `customer_id` (integer, optional): Customer ID if known

**Example Request:**
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is your return policy?"
  }'
```

**Response:**
```json
{
  "response": "Our return policy allows returns within 30 days of purchase. Items must be in original condition with tags attached. Electronics can be returned for a full refund or exchange. To initiate a return, log into your account and go to the Orders section.",
  "thread_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response Fields:**
- `response` (string): The agent's response message
- `thread_id` (string): The thread identifier used for this request (generated if not provided)

**Status Codes:**
- `200 OK` - Request processed successfully
- `400 Bad Request` - Invalid request body
- `500 Internal Server Error` - Server error processing request

---

## Example Use Cases

### Order Inquiry

**Check order status:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Where is my order ORD-001?",
    "thread_id": "customer-456"
  }'
```

**Get order history:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me my order history",
    "thread_id": "customer-456",
    "customer_id": 5
  }'
```

### Customer Information

**Lookup customer:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about customer ID 10",
    "thread_id": "support-agent-1"
  }'
```

**Get customer profile:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Get the full profile for customer with email john@example.com",
    "thread_id": "support-agent-1"
  }'
```

### Technical Support

**Create support ticket:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My product is not working. It won't turn on. Please create a support ticket.",
    "thread_id": "customer-789",
    "customer_id": 3
  }'
```

**Update ticket status:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Update ticket 123 to resolved status",
    "thread_id": "support-agent-2"
  }'
```

### Billing Question

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I was charged twice for my order. Can you help?",
    "thread_id": "customer-101",
    "customer_id": 7
  }'
```

### Knowledge Base Search

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I track my order?"
  }'
```

### Web Search

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the current weather in New York?",
    "thread_id": "user-weather"
  }'
```

---

## Error Responses

### 400 Bad Request

Invalid request body or missing required fields.

**Response:**
```json
{
  "detail": "Invalid request body"
}
```

**Common Causes:**
- Missing `message` field
- Invalid JSON format
- Wrong data types for fields

### 500 Internal Server Error

Server error while processing the request.

**Response:**
```json
{
  "detail": "Error processing chat request: [error message]"
}
```

**Common Causes:**
- MCP server not running or unreachable
- Database connection issues
- LLM API errors
- Missing environment variables

---

## Response Fields Reference

### Chat Response

| Field | Type | Description |
|-------|------|-------------|
| `response` | string | The agent's response message |
| `thread_id` | string | The conversation thread identifier |
| `tool_calls` | array (optional) | List of tools that were called during processing |
| `intent` | string (optional) | Detected intent of the user's message |
| `confidence` | float (optional) | Confidence score of the response (0.0 to 1.0) |

### Generate Response

| Field | Type | Description |
|-------|------|-------------|
| `response` | string | The agent's response message |
| `thread_id` | string | The thread identifier used for this request |

### Tool Call Object

| Field | Type | Description |
|-------|------|-------------|
| `tool` | string | Name of the tool that was called |
| `args` | object | Arguments passed to the tool |
| `id` | string | Unique identifier for the tool call |

---

## Intent Classification

The agent automatically classifies user queries into the following intent categories:

- `order_inquiry` - Questions about orders, shipping, delivery
- `technical_support` - Product issues, troubleshooting
- `billing` - Payment, charges, refunds
- `customer_inquiry` - Customer information requests
- `ticket_management` - Creating or updating support tickets
- `knowledge_base` - FAQ and help article searches
- `general` - General questions or unclear intent

---

## Notes

1. **Memory/State**: The `/chat` endpoint maintains conversation state using the `thread_id`. Use the same `thread_id` across multiple requests to maintain context. The agent remembers previous messages in the conversation.

2. **Thread IDs**: For `/chat`, use a unique `thread_id` per user/session. For `/generate`, each request is independent and thread IDs are not used for state management.

3. **Customer ID**: Providing `customer_id` helps the agent access customer-specific information like order history, profile details, and create tickets associated with the customer.

4. **Tool Calls**: The agent automatically selects and uses appropriate tools based on the user's query. Tool calls are included in the response for transparency and debugging.

5. **Intent Classification**: The agent automatically classifies user queries to better understand context and route to appropriate tools.

6. **Confidence Scores**: Higher confidence scores (closer to 1.0) indicate the agent is more certain about its response. Lower scores may indicate ambiguous queries.

7. **Rate Limiting**: Currently, there is no rate limiting. For production use, implement rate limiting middleware.

8. **Timeout**: Requests may take several seconds depending on tool calls and LLM response time. Set appropriate timeout values in your HTTP client.

---

## API Versioning

Current API version: `1.0.0`

API version information is available at the root endpoint (`GET /`).

---

## Support

For API issues:

1. Check server logs in `logs/` directory
2. Verify all services are running (MCP server, API server)
3. Test health endpoint: `GET /health`
4. Review environment variable configuration
