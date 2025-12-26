"""
Tool Calling

Give the model the ability to call functions using the OpenAI Responses API.
"""

import json
from datetime import datetime
from zoneinfo import ZoneInfo
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

# =============================================================================
# Define Tools
# =============================================================================


def get_current_time(timezone: str = "UTC") -> str:
    """Get the current time in a specific timezone.

    Args:
        timezone: IANA timezone name (e.g., 'America/New_York', 'Europe/London')
    """
    try:
        tz = ZoneInfo(timezone)
        return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        return f"Invalid timezone: {timezone}"


def calculate(expression: str) -> str:
    """Evaluate a mathematical expression.

    Args:
        expression: Math expression (e.g., '2 + 2', '10 * 5')
    """
    try:
        allowed = set("0123456789+-*/.() ")
        if not all(c in allowed for c in expression):
            return "Invalid characters in expression"
        return str(eval(expression))
    except Exception:
        return f"Could not evaluate: {expression}"


# =============================================================================
# Tool Definitions for OpenAI
# =============================================================================

# OpenAI requires JSON schema definitions for tools

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current time in a specific timezone",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "IANA timezone name (e.g., 'America/New_York', 'Europe/London')",
                    }
                },
                "required": ["timezone"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a mathematical expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression (e.g., '2 + 2', '10 * 5')",
                    }
                },
                "required": ["expression"],
            },
        },
    },
]

# Map function names to actual functions
tool_map = {
    "get_current_time": get_current_time,
    "calculate": calculate,
}

# =============================================================================
# Basic Tool Calling
# =============================================================================

response = client.responses.create(
    model="gpt-5-mini",
    input="What time is it in Tokyo?",
    tools=tools,
)

# Check for tool calls in the response output
for item in response.output:
    if item.type == "function_call":
        print(f"Function: {item.name}")
        print(f"Arguments: {item.arguments}")

        # Execute the function
        func = tool_map.get(item.name)
        if func:
            args = json.loads(item.arguments)
            result = func(**args)
            print(f"Result: {result}")

# =============================================================================
# Tool Calling Loop (Agent Pattern)
# =============================================================================


def chat_with_tools(user_message: str, max_iterations: int = 5) -> str:
    """Complete a request that may require multiple tool calls."""
    response = client.responses.create(
        model="gpt-5-mini",
        input=user_message,
        tools=tools,
    )

    for _ in range(max_iterations):
        # Check if there are any tool calls
        tool_calls = [item for item in response.output if item.type == "function_call"]

        if not tool_calls:
            # No tool calls, return the text response
            return response.output_text

        # Execute all tool calls and collect results
        tool_results = []
        for call in tool_calls:
            func = tool_map.get(call.name)
            if func:
                args = json.loads(call.arguments)
                result = func(**args)
                tool_results.append({
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": result,
                })

        # Continue the conversation with tool results
        response = client.responses.create(
            model="gpt-5-mini",
            input=tool_results,
            previous_response_id=response.id,
            tools=tools,
        )

    return response.output_text


# Single tool call
result = chat_with_tools("What time is it in Tokyo?")
print(result)

# Multiple tool calls
result = chat_with_tools("What's 15% of 200, and what time is it in London?")
print(result)
