import asyncio
import json
import os
from typing import Any, Dict

from highflame import Highflame, Config

import dotenv

dotenv.load_dotenv()


# Helper function to pretty print responses
def print_response(provider: str, response: Dict[str, Any]) -> None:
    print(f"=== Response from {provider} ===")
    print(json.dumps(response, indent=2))


# Setup client configuration for Bedrock
config = Config(
    base_url=os.getenv("HIGHFLAME_BASE_URL"),
    api_key=os.getenv("HIGHFLAME_API_KEY"),
)
client = Highflame(config)
headers = {
    "Content-Type": "application/json",
    "x-highflame-route": "claude_univ",
    "x-highflame-model": "claude-3-5-sonnet-20240620",
    "x-api-key": os.getenv("ANTHROPIC_API_KEY"),
}

messages = [{"role": "user", "content": "what is the capital of india?"}]


async def main():
    try:
        query_body = {
            "messages": messages,
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 200,
            "temperature": 0.7,
        }
        bedrock_response = client.query_unified_endpoint(
            provider_name="anthropic",
            endpoint_type="messages",
            query_body=query_body,
            headers=headers,
        )
        print(bedrock_response)
    except Exception as e:
        print(f"Anthropic query failed: {str(e)}")


# Run the async function
asyncio.run(main())
