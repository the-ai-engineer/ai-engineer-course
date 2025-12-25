"""
Timezone Agent

A terminal-based chat assistant for timezone questions.
Run with: uv run python agent.py
"""

import json
from datetime import datetime
from zoneinfo import ZoneInfo
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

# =============================================================================
# Tools
# =============================================================================


def get_current_time(timezone: str = "UTC") -> str:
    """Get the current time in a specific timezone.

    Args:
        timezone: IANA timezone name (e.g., 'America/New_York', 'Asia/Tokyo')
    """
    try:
        tz = ZoneInfo(timezone)
        return datetime.now(tz).strftime("%H:%M %Z")
    except Exception:
        return f"Invalid timezone: {timezone}"


def convert_time(time_str: str, from_tz: str, to_tz: str) -> str:
    """Convert a time from one timezone to another.

    Args:
        time_str: Time in HH:MM format (24-hour)
        from_tz: Source timezone (IANA format)
        to_tz: Target timezone (IANA format)
    """
    try:
        hour, minute = map(int, time_str.split(":"))
        dt = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        dt = dt.replace(tzinfo=ZoneInfo(from_tz))
        converted = dt.astimezone(ZoneInfo(to_tz))
        return f"{time_str} {from_tz} = {converted.strftime('%H:%M')} {to_tz}"
    except Exception as e:
        return f"Error converting time: {e}"


# Tool definitions for OpenAI
TOOLS = [
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
                        "description": "IANA timezone name (e.g., 'America/New_York', 'Asia/Tokyo')",
                    }
                },
                "required": ["timezone"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "convert_time",
            "description": "Convert a time from one timezone to another",
            "parameters": {
                "type": "object",
                "properties": {
                    "time_str": {
                        "type": "string",
                        "description": "Time in HH:MM format (24-hour)",
                    },
                    "from_tz": {
                        "type": "string",
                        "description": "Source timezone (IANA format)",
                    },
                    "to_tz": {
                        "type": "string",
                        "description": "Target timezone (IANA format)",
                    },
                },
                "required": ["time_str", "from_tz", "to_tz"],
            },
        },
    },
]

TOOL_MAP = {
    "get_current_time": get_current_time,
    "convert_time": convert_time,
}

SYSTEM_PROMPT = """You are a helpful timezone assistant.

You can:
- Get the current time in any timezone
- Convert times between timezones

Be concise and helpful. When users ask about times in cities, use the appropriate IANA timezone (e.g., 'Asia/Tokyo' for Tokyo, 'America/New_York' for New York)."""


# =============================================================================
# Chat Function
# =============================================================================


def chat(user_input: str, previous_id: str = None) -> tuple[str, str]:
    """Send a message and get a response with tool handling."""
    response = client.responses.create(
        model="gpt-5-mini",
        input=user_input,
        instructions=SYSTEM_PROMPT,
        tools=TOOLS,
        previous_response_id=previous_id,
    )

    # Handle tool calls in a loop
    while True:
        tool_calls = [item for item in response.output if item.type == "function_call"]

        if not tool_calls:
            return response.output_text, response.id

        # Execute tools
        tool_results = []
        for call in tool_calls:
            func = TOOL_MAP.get(call.name)
            args = json.loads(call.arguments) if call.arguments else {}
            result = func(**args) if func else f"Unknown tool: {call.name}"
            tool_results.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": str(result),
            })

        # Continue with results
        response = client.responses.create(
            model="gpt-5-mini",
            input=tool_results,
            previous_response_id=response.id,
            tools=TOOLS,
        )


# =============================================================================
# Main
# =============================================================================


def main():
    print("Timezone Agent")
    print("Type 'quit' to exit\n")

    previous_id = None

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        response_text, previous_id = chat(user_input, previous_id)
        print(f"Assistant: {response_text}\n")


if __name__ == "__main__":
    main()
