"""
Tool Calling

Give the model the ability to call functions.
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
# Automatic Function Calling (Simple)
# =============================================================================

# Pass Python functions directly. Gemini calls them automatically and returns
# the final response. This is the simplest approach.

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What time is it in Tokyo?",
    config=types.GenerateContentConfig(
        tools=[get_current_time, calculate],
    ),
)
response.text

# Multiple tools in one query
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What's 15% of 200, and what time is it in London?",
    config=types.GenerateContentConfig(
        tools=[get_current_time, calculate],
    ),
)
response.text

# =============================================================================
# Manual Function Calling
# =============================================================================

# Sometimes you need control over function execution: logging, error handling,
# async execution, or approval workflows. Disable automatic calling.

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What time is it in Tokyo?",
    config=types.GenerateContentConfig(
        tools=[get_current_time],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
    ),
)

# Now you get the function call instead of the result
part = response.candidates[0].content.parts[0]
fc = part.function_call
fc.name, fc.args

# Execute manually
result = get_current_time(**fc.args)
result

# Send result back to get final response
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Part.from_text("What time is it in Tokyo?"),
        part,
        types.Part.from_function_response(
            name=fc.name,
            response={"result": result},
        ),
    ],
    config=types.GenerateContentConfig(
        tools=[get_current_time],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
    ),
)
response.text
