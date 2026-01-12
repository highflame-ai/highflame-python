from highflame import Highflame, Config
import os
from typing import Dict, Any
import json


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
    "x-highflame-route": "univ_bedrock",
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
        model="amazon.titan-text-express-v1",
    )
    print_response("OpenAI", openai_response)
except Exception as e:
    print(f"OpenAI query failed: {str(e)}")
