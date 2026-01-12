# Customer Support Agent with LangGraph and MCP

An AI-powered customer support agent built with LangGraph and Model Context Protocol (MCP) that handles customer service scenarios including order inquiries, technical support, billing issues, and general questions. The agent uses Highflame as a unified LLM provider supporting both OpenAI and Google Gemini models.

## Features

- **Highflame LLM Integration**: Unified provider for OpenAI and Google Gemini models
- **MCP Architecture**: Database operations isolated in MCP server for scalability and separation of concerns
- **Intelligent Conversation Flow**: LangGraph manages complex conversation states and routing
- **Conversation Memory**: Maintains context across multiple turns using LangGraph's MemorySaver
- **11 Database Tools**: Via MCP server (orders, customers, tickets, knowledge base)
- **Direct Tools**: Web search and email capabilities
- **REST API**: FastAPI server with `/chat` and `/generate` endpoints
- **Streamlit UI**: Interactive chat interface with conversation history and debug views
- **Comprehensive Logging**: Timestamped logs saved to `logs/` directory

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Application                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           LangGraph Agent (State Machine)            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │  │
│  │  │  Start   │→ │Understand │→ │ Call     │          │  │
│  │  │  Node    │  │  Intent   │  │  Tools   │          │  │
│  │  └──────────┘  └──────────┘  └──────────┘          │  │
│  │                              ↓                       │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │  │
│  │  │ Synthesize│← │  Tools   │← │ Tool     │          │  │
│  │  │ Response  │  │  Node    │  │  Calls   │          │  │
│  │  └──────────┘  └──────────┘  └──────────┘          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Highflame LLM (Unified Provider)            │  │
│  │  • OpenAI Route (gpt-4o-mini, etc.)                 │  │
│  │  • Google Route (gemini-2.5-flash-lite, etc.)      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  Tool Router                         │  │
│  │  ├── MCP Client → MCP Server (11 DB tools)         │  │
│  │  └── Direct Tools (web search, email)               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              MCP Server (Port 9000)                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Knowledge Base Tools (2)                            │  │
│  │  • search_knowledge_base_tool                        │  │
│  │  • get_knowledge_base_by_category_tool               │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Order Tools (3)                                     │  │
│  │  • lookup_order_tool                                 │  │
│  │  • get_order_status_tool                             │  │
│  │  • get_order_history_tool                            │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Customer Tools (3)                                  │  │
│  │  • lookup_customer_tool                              │  │
│  │  • get_customer_profile_tool                         │  │
│  │  • create_customer_tool                              │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Ticket Tools (3)                                    │  │
│  │  • create_ticket_tool                                │  │
│  │  • update_ticket_tool                                │  │
│  │  • get_ticket_tool                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↓                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         SQLite Database                              │  │
│  │  • customers, orders, tickets, knowledge_base        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Highflame API key
- OpenAI API key (for `openai` route) or Google Gemini API key (for `google` route)

### Step 1: Install Dependencies

```bash
# Clone or navigate to the project directory
cd agent

# Install all required packages
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

Create a `.env` file in the project root directory:

```env
# Highflame Configuration (Required)
HIGHFLAME_API_KEY=your_highflame_api_key_here
HIGHFLAME_ROUTE=google  # or 'openai'
MODEL=gemini-2.5-flash-lite  # or 'gpt-4o-mini' for OpenAI route
LLM_API_KEY=your_openai_or_gemini_api_key_here

# MCP Server Configuration
MCP_SERVER_URL=http://localhost:9000/mcp
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=9000

# Database Configuration
DATABASE_PATH=./src/db/support_agent.db

# API Server Configuration (Optional)
PORT=8000

# Email Configuration (Optional - for email tool)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=your_email@gmail.com

# Logging Configuration (Optional)
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

**Important Notes:**
- `HIGHFLAME_ROUTE` must be either `openai` or `google`
- For `openai` route: `LLM_API_KEY` should be your OpenAI API key, `MODEL` should be an OpenAI model (e.g., `gpt-4o-mini`)
- For `google` route: `LLM_API_KEY` should be your Google Gemini API key, `MODEL` should be a Gemini model (e.g., `gemini-2.5-flash-lite`)

### Step 3: Start All Services

**Option A: Using the Startup Script (Recommended)**

```bash
# Make the script executable
chmod +x start.sh

# Start all services
./start.sh
```

This will start:
1. MCP Server on port 9000
2. FastAPI Server on port 8000
3. Streamlit UI on port 8501

**Option B: Manual Startup**

Terminal 1 - MCP Server:
```bash
python -m src.mcp_server.server
```

Terminal 2 - FastAPI Server:
```bash
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

Terminal 3 - Streamlit UI:
```bash
streamlit run src/ui/app.py
```

### Step 4: Access the Services

- **Streamlit UI**: http://localhost:8501
- **FastAPI Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MCP Server**: http://localhost:9000/mcp

## Project Structure

```
agent/
├── src/
│   ├── agent/
│   │   ├── database/          # Database models and queries
│   │   │   ├── models.py      # SQLAlchemy ORM models
│   │   │   ├── queries.py     # Database query functions
│   │   │   └── setup.py       # Database initialization
│   │   ├── tools/             # Direct tools (no DB access)
│   │   │   ├── web_search.py  # DuckDuckGo search
│   │   │   └── email.py       # SMTP email sending
│   │   ├── graph.py           # LangGraph agent definition
│   │   ├── llm.py             # Highflame LLM integration
│   │   ├── mcp_tools.py       # MCP client wrapper
│   │   └── state.py           # Agent state schema
│   ├── mcp_server/
│   │   └── server.py          # MCP server with 11 DB tools
│   ├── ui/
│   │   ├── app.py             # Streamlit chat UI
│   │   └── db_viewer.py       # Database viewer
│   ├── utils/
│   │   └── logger.py          # Centralized logging
│   ├── api.py                 # FastAPI server
│   └── main.py                # CLI interface
├── tests/
│   ├── test_agent.py          # Agent tests
│   └── test_mcp_server.py     # MCP server tests
├── docs/
│   └── API.md                 # API documentation
├── logs/                      # Application logs (auto-generated)
├── requirements.txt
├── start.sh                   # Startup script
└── README.md
```

## Available Tools

### MCP Server Tools (Database Operations)

All database operations are handled through the MCP server for better scalability and separation of concerns.

**Knowledge Base (2 tools)**
- `search_knowledge_base_tool` - Search help articles by query string
- `get_knowledge_base_by_category_tool` - Get articles filtered by category

**Orders (3 tools)**
- `lookup_order_tool` - Get detailed order information by order number
- `get_order_status_tool` - Check current status of an order
- `get_order_history_tool` - Get complete order history for a customer

**Customers (3 tools)**
- `lookup_customer_tool` - Find customer by email, phone, or ID
- `get_customer_profile_tool` - Get full customer profile with all details
- `create_customer_tool` - Create a new customer record

**Tickets (3 tools)**
- `create_ticket_tool` - Create a new support ticket
- `update_ticket_tool` - Update ticket status, priority, or assignee
- `get_ticket_tool` - Get ticket details by ID

### Direct Tools (No Database)

These tools run directly in the agent without going through the MCP server.

- `web_search_tool` - Search the web using DuckDuckGo
- `web_search_news_tool` - Search for news articles
- `send_email_tool` - Send emails via SMTP (requires SMTP configuration)

## Configuration Details

### Highflame LLM Configuration

The agent uses Highflame as a unified provider. Configure it using these environment variables:

**For OpenAI Route:**
```env
HIGHFLAME_API_KEY=your_highflame_key
HIGHFLAME_ROUTE=openai
MODEL=gpt-4o-mini
LLM_API_KEY=sk-your_openai_key_here
```

**For Google Route:**
```env
HIGHFLAME_API_KEY=your_highflame_key
HIGHFLAME_ROUTE=google
MODEL=gemini-2.5-flash-lite
LLM_API_KEY=your_gemini_api_key_here
```

### MCP Server Configuration

The MCP server can run locally or remotely:

**Local Deployment:**
```env
MCP_SERVER_URL=http://localhost:9000/mcp
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=9000
```

**Remote Deployment:**
```env
MCP_SERVER_URL=http://your-server-ip:9000/mcp
```

### Database Configuration

The SQLite database is automatically initialized on first run:

```env
DATABASE_PATH=./src/db/support_agent.db
```

The database includes mock data for testing. To reset the database, delete the `.db` file and restart the services.

## Usage Examples

### Using the Streamlit UI

1. Start all services using `./start.sh` or manually
2. Open http://localhost:8501 in your browser
3. Start a new conversation or continue an existing one
4. Ask questions like:
   - "What is the status of order ORD-001?"
   - "Tell me about customer ID 10"
   - "Create a support ticket for a damaged item"
   - "Search the web for current weather in New York"

### Using the REST API

**Stateful Chat (maintains conversation context):**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the status of order ORD-001?",
    "thread_id": "user-123",
    "customer_id": 1
  }'
```

**Stateless Query (no context):**
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I reset my password?"
  }'
```

See `docs/API.md` for complete API documentation.

### Using the CLI

**Interactive Mode:**
```bash
python src/main.py
```

**Test Suite:**
```bash
python src/main.py test
```

**Single Query:**
```bash
python src/main.py "What is the status of order ORD-001?"
```

## Testing

### Run All Tests

```bash
pytest
```

### Test MCP Server

```bash
# Start server first (in one terminal)
python -m src.mcp_server.server

# Run tests (in another terminal)
pytest tests/test_mcp_server.py -v
```

### Test Agent

```bash
pytest tests/test_agent.py -v
```

### Manual Testing

```bash
# Run comprehensive test suite
python src/main.py test
```

## API Endpoints

### FastAPI Server Endpoints

**GET /health** - Health check
```bash
curl http://localhost:8000/health
```

**GET /** - API information
```bash
curl http://localhost:8000/
```

**POST /chat** - Stateful conversation
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "thread_id": "test-123"}'
```

**POST /generate** - Stateless query
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"message": "What can you help me with?"}'
```

See `docs/API.md` for complete API documentation with request/response examples.

## Database Schema

The SQLite database includes the following tables:

- **customers** - Customer information (name, email, phone, address)
- **orders** - Order details (order number, status, items, dates)
- **tickets** - Support tickets (status, priority, description, assignments)
- **knowledge_base** - Help articles and FAQs (title, content, category)
- **conversations** - Chat history (messages, customer associations)

The database is automatically initialized with mock data on first run. You can view the database using:

```bash
streamlit run src/ui/db_viewer.py
```

## Logging

All application logs are saved to the `logs/` directory with timestamped filenames:

```
logs/
├── app_20251230_093000.log
├── app_20251230_094500.log
└── ...
```

Log levels can be configured via `LOG_LEVEL` environment variable:
- `DEBUG` - Detailed debugging information
- `INFO` - General informational messages
- `WARNING` - Warning messages
- `ERROR` - Error messages only

## Development

### Adding New Tools

**For database tools** - Add to `src/mcp_server/server.py`:

```python
@mcp.tool()
def my_new_tool(arg1: str, arg2: int) -> str:
    """Tool description for the LLM."""
    db = get_session()
    try:
        # Your database logic here
        result = perform_query(db, arg1, arg2)
        return result
    finally:
        db.close()
```

Then add wrapper in `src/agent/mcp_tools.py`:

```python
class MyNewToolInput(BaseModel):
    arg1: str = Field(description="First argument")
    arg2: int = Field(description="Second argument")

my_new_tool = StructuredTool(
    name="my_new_tool",
    description="Tool description",
    args_schema=MyNewToolInput,
    func=lambda arg1, arg2: call_mcp_tool("my_new_tool", arg1=arg1, arg2=arg2),
)
```

**For direct tools** - Add to `src/agent/tools/`:

```python
from langchain_core.tools import tool

@tool
def my_direct_tool(query: str) -> str:
    """Tool description for the LLM."""
    # Your logic here
    return result
```

Then import and add to `get_tools()` in `src/agent/graph.py`.

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/
```

## Troubleshooting

### MCP Server Not Starting

**Check if port 9000 is available:**
```bash
lsof -i :9000
```

**Kill process if needed:**
```bash
kill -9 <PID>
```

**Check MCP server logs:**
```bash
tail -f logs/app_*.log
```

### API Server Not Starting

**Check if port 8000 is available:**
```bash
lsof -i :8000
```

**Verify environment variables:**
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('HIGHFLAME_API_KEY:', bool(os.getenv('HIGHFLAME_API_KEY')))"
```

### Connection Refused to MCP Server

1. Verify MCP server is running: `curl http://localhost:9000/mcp`
2. Check `MCP_SERVER_URL` in `.env` matches server address
3. Review MCP server logs in `logs/` directory

### Tools Not Working

1. Verify MCP server is running and accessible
2. Check `MCP_SERVER_URL` in `.env` is correct
3. Review agent logs for tool call errors
4. Test MCP server directly: `pytest tests/test_mcp_server.py`

### API Key Errors

Ensure all required API keys are set in `.env`:

```bash
# Check if keys are loaded
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('HIGHFLAME_API_KEY:', bool(os.getenv('HIGHFLAME_API_KEY')))
print('HIGHFLAME_ROUTE:', os.getenv('HIGHFLAME_ROUTE'))
print('MODEL:', os.getenv('MODEL'))
print('LLM_API_KEY:', bool(os.getenv('LLM_API_KEY')))
"
```

### Database Errors

**Reset database:**
```bash
rm src/db/support_agent.db
# Restart services - database will be recreated with mock data
```

**View database:**
```bash
streamlit run src/ui/db_viewer.py
```

## Security Considerations

- API keys stored in `.env` (not committed to git)
- Database operations isolated in MCP server
- Input validation on all tool parameters
- CORS enabled for API endpoints (configure as needed)
- Logs may contain sensitive information - secure the `logs/` directory

## Performance

- **MCP Server**: Handles database operations efficiently with connection pooling
- **Agent**: Uses LangGraph's optimized state management
- **Memory**: Conversation state persisted using LangGraph's MemorySaver
- **Logging**: Rotating file handler (10MB per file, 5 backups)

## Requirements

- Python 3.11+
- Highflame API key
- OpenAI API key (for `openai` route) or Google Gemini API key (for `google` route)
- 100MB disk space for database and logs
- Network access for MCP server communication

## Support

For issues or questions:

1. Check logs in `logs/` directory
2. Run test suite: `python src/main.py test`
3. View database: `streamlit run src/ui/db_viewer.py`
4. Review API documentation: `docs/API.md`

## License

Apache 2.0
