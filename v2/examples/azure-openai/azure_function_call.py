#!/usr/bin/env python
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from highflame import Highflame, Config

load_dotenv()


def init_azure_client_with_javelin():
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_key = os.getenv("HIGHFLAME_API_KEY")

    if not azure_api_key or not api_key:
        raise ValueError("Missing AZURE_OPENAI_API_KEY or HIGHFLAME_API_KEY")

    # Azure OpenAI setup
    azure_client = AzureOpenAI(
        api_version="2023-07-01-preview",
        azure_endpoint="https://javelinpreview.openai.azure.com",
        api_key=azure_api_key,
    )

    # Register with Highflame
    config = Config(api_key=api_key)
    client = Highflame(config)
    client.register_azureopenai(azure_client, route_name="azureopenai_univ")

    return azure_client


def run_function_call_test(azure_client):
    print("\n==== Azure OpenAI Function Calling via Highflame ====")

    try:
        response = azure_client.chat.completions.create(
            model="gpt35",  # Your Azure model deployment name
            messages=[{"role": "user", "content": "Get weather in Tokyo in Celsius."}],
            functions=[
                {
                    "name": "get_weather",
                    "description": "Provides weather information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {"type": "string", "description": "City name"},
                            "unit": {
                                "type": "string",
                                "enum": ["celsius", "fahrenheit"],
                                "description": "Temperature unit",
                            },
                        },
                        "required": ["city"],
                    },
                }
            ],
            function_call="auto",
        )
        print("Function Call Output:")
        print(response.to_json(indent=2))
    except Exception as e:
        print("Azure Function Calling Error:", e)


def run_tool_call_test(azure_client):
    print("\n==== Azure OpenAI Tool Calling via Highflame ====")

    try:
        response = azure_client.chat.completions.create(
            model="gpt35",  # Your Azure deployment name
            messages=[{"role": "user", "content": "Get a random motivational quote."}],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "get_motivation",
                        "description": "Returns a motivational quote",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "category": {
                                    "type": "string",
                                    "description": "e.g. success, life",
                                }
                            },
                            "required": [],
                        },
                    },
                }
            ],
            tool_choice="auto",
        )
        print("Tool Call Output:")
        print(response.to_json(indent=2))
    except Exception as e:
        print("Azure Tool Calling Error:", e)


def main():
    client = init_azure_client_with_javelin()
    run_function_call_test(client)
    run_tool_call_test(client)


if __name__ == "__main__":
    main()
