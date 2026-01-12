from highflame import Highflame, Config
import os
from typing import Dict, Any
import json
import dotenv

dotenv.load_dotenv()


# Helper function to pretty print responses
def print_response(provider: str, response: Dict[str, Any]) -> None:
    print(f"=== Response from {provider} ===")
    print(json.dumps(response, indent=2))


# Setup client configuration
config = Config(
    base_url=os.getenv("HIGHFLAME_BASE_URL"),
    api_key=os.getenv("HIGHFLAME_API_KEY"),
    timeout=120,
)

client = Highflame(config)
custom_headers = {
    "Content-Type": "application/json",
    "x-highflame-route": "claude_univ",
    "x-api-key": os.getenv("ANTHROPIC_API_KEY"),
    "x-highflame-model": "claude-3-5-sonnet-20240620",
    "x-highflame-provider": "https://api.anthropic.com/v1",
}
client.set_headers(custom_headers)

# Example messages in OpenAI format
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What are the three primary colors?"},
]

try:
    openai_response = client.chat.completions.create(
        messages=messages,
        temperature=0.7,
        max_tokens=150,
        model="claude-3-5-sonnet-20240620",
        stream=True,
        endpoint_type="messages",
        anthropic_version="bedrock-2023-05-31",
    )
    for chunk in openai_response:
        print(chunk, end="", flush=True)
    print()  # Add a newline at the end
except Exception as e:
    print(f"Anthropic query failed: {str(e)}")
