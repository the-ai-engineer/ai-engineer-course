"""
Tool Calling

Give the model the ability to call functions using the Gemini API.
Gemini supports automatic function calling - just pass Python functions directly.
"""

from datetime import datetime
from zoneinfo import ZoneInfo
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

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
# Automatic Tool Calling
# =============================================================================

# Gemini handles the tool calling loop automatically.
# Just pass Python functions directly - no JSON schema needed.


def chat_with_tools(user_message: str) -> str:
    """Complete a request that may require tool calls."""
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=user_message,
        config=types.GenerateContentConfig(
            tools=[get_current_time, calculate],
        ),
    )
    return response.text


# Single tool call
chat_with_tools("What time is it in Tokyo?")

# Multiple tool calls
chat_with_tools("What's 15% of 200, and what time is it in London?")

# =============================================================================
# Manual Tool Handling (When Needed)
# =============================================================================

# For custom control (logging, approval workflows, etc.), you can disable
# automatic function calling and handle tools manually.

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="What time is it in Tokyo?",
    config=types.GenerateContentConfig(
        tools=[get_current_time, calculate],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True,
        ),
    ),
)

# Check if there are tool calls in the response
for part in response.candidates[0].content.parts:
    if part.function_call:
        print(f"Function: {part.function_call.name}")
        print(f"Arguments: {part.function_call.args}")

        # Execute manually if needed
        if part.function_call.name == "get_current_time":
            result = get_current_time(**part.function_call.args)
            print(f"Result: {result}")
