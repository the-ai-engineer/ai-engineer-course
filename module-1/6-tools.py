"""
Tool Calling Basics

This example shows how to:
1. Define a tool schema
2. Make an API call with tools
3. Handle the tool call response
4. Execute the tool and return results
"""

from openai import OpenAI
import json

client = OpenAI()

# =============================================================================
# Step 1: Define the tool schema
# =============================================================================

tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get the current weather for a specific location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and country, e.g. 'London, UK'",
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit preference",
                },
            },
            "required": ["location"],
        },
    },
]


# =============================================================================
# Step 2: Implement the actual function
# =============================================================================


def get_weather(location, unit="celsius"):
    """Simulated weather API."""
    temp = 22
    if unit == "fahrenheit":
        temp = round(temp * 9 / 5 + 32)
    unit_symbol = "°C" if unit == "celsius" else "°F"
    return {
        "location": location,
        "temperature": f"{temp}{unit_symbol}",
        "condition": "Sunny",
    }


# =============================================================================
# Step 3: Make the API call with tools
# =============================================================================

# Start with the user message
messages: list = [{"role": "user", "content": "What's the weather like in Tokyo?"}]

response = client.responses.create(
    model="gpt-5-mini",
    tools=tools,  # type: ignore[arg-type]
    input=messages,
)

# =============================================================================
# Step 4: Check if a tool was called
# =============================================================================

# The response might be a direct answer OR a tool call request
for item in response.output:
    if item.type == "function_call":
        print(f"Tool requested: {item.name}")
        print(f"Arguments: {item.arguments}")

        # =============================================================================
        # Step 5: Execute the tool and return result to LLM
        # =============================================================================

        args = json.loads(item.arguments)
        result = get_weather(**args)
        print(f"Tool result: {result}")

        # Add the model's output and our tool result to the conversation
        messages += response.output
        messages.append(
            {
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps(result),
            }
        )

        # Send result back to get final answer
        final_response = client.responses.create(
            model="gpt-5-mini",
            tools=tools,  # type: ignore[arg-type]
            input=messages,  # type: ignore[arg-type]
        )

        print(f"\nFinal answer: {final_response.output_text}")

    elif item.type == "message":
        # LLM answered directly without using tools
        print(f"Direct answer: {item.content}")
