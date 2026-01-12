import json
import os

import dotenv

from highflame import Highflame, Config

dotenv.load_dotenv()

# Retrieve environment variables
api_key = os.getenv("HIGHFLAME_API_KEY")
virtual_api_key = os.getenv("HIGHFLAME_VIRTUALAPIKEY")
llm_api_key = os.getenv("LLM_API_KEY")


def pretty_print(obj):
    """
    Pretty-prints an object that has a JSON representation.
    """
    if hasattr(obj, "dict"):
        obj = obj.dict()
    try:
        print(json.dumps(obj, indent=4))
    except TypeError:
        print(obj)


def main():
    config = Config(
        base_url=os.getenv("HIGHFLAME_BASE_URL"),
        api_key=api_key,
        virtual_api_key=virtual_api_key,
        llm_api_key=llm_api_key,
    )
    client = Highflame(config)

    chat_completion_routes = [
        {"route_name": "myusers"},
    ]

    text_completion_routes = [
        {"route_name": "bedrockllama"},
        {"route_name": "bedrocktitan"},
    ]

    # Chat completion examples
    for route in chat_completion_routes:
        print(f"\nQuerying chat completion route: {route['route_name']}")
        chat_response = client.chat.completions.create(
            route=route["route_name"],
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! What can you do?"},
            ],
            temperature=0.7,
        )
        print("Chat Completion Response:")
        pretty_print(chat_response)

    # Text completion examples
    for route in text_completion_routes:
        print(f"\nQuerying text completion route: {route['route_name']}")
        completion_response = client.completions.create(
            route=route["route_name"],
            prompt="Complete this sentence: The quick brown fox",
            max_tokens=50,
            temperature=0.7,
        )
        print("Text Completion Response:")
        pretty_print(completion_response)


if __name__ == "__main__":
    main()
