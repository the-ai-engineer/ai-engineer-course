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


# =============================================================================
# Tools
# =============================================================================


def get_current_time(timezone: str = "UTC") -> str:
    """Get the current time in a specific timezone."""
    try:
        tz = ZoneInfo(timezone)
        return datetime.now(tz).strftime("%H:%M %Z")
    except Exception:
        return f"Invalid timezone: {timezone}"


def convert_time(time_str: str, from_tz: str, to_tz: str) -> str:
    """Convert a time from one timezone to another."""
    try:
        hour, minute = map(int, time_str.split(":"))
        dt = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        dt = dt.replace(tzinfo=ZoneInfo(from_tz))
        converted = dt.astimezone(ZoneInfo(to_tz))
        return f"{time_str} {from_tz} = {converted.strftime('%H:%M')} {to_tz}"
    except Exception as e:
        return f"Error converting time: {e}"


TOOLS = [
    {
        "type": "function",
        "name": "get_current_time",
        "description": "Get the current time in a specific timezone",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "IANA timezone (e.g., 'America/New_York')",
                }
            },
            "required": ["timezone"],
        },
    },
    {
        "type": "function",
        "name": "convert_time",
        "description": "Convert a time from one timezone to another",
        "parameters": {
            "type": "object",
            "properties": {
                "time_str": {"type": "string", "description": "Time in HH:MM format"},
                "from_tz": {"type": "string", "description": "Source timezone"},
                "to_tz": {"type": "string", "description": "Target timezone"},
            },
            "required": ["time_str", "from_tz", "to_tz"],
        },
    },
]

TOOL_MAP = {"get_current_time": get_current_time, "convert_time": convert_time}


# =============================================================================
# Agent
# =============================================================================


class TimezoneAgent:
    """A simple agent that answers timezone questions."""

    def __init__(self):
        self.client = OpenAI()
        self.last_response_id = None

    def chat(self, user_input: str) -> str:
        """Send a message and get a response."""
        response = self.client.responses.create(
            model="gpt-4.1-mini",
            input=user_input,
            instructions="You are a helpful timezone assistant. Be concise.",
            tools=TOOLS,
            previous_response_id=self.last_response_id,
        )

        # Handle tool calls
        while response.output:
            tool_calls = [item for item in response.output if item.type == "function_call"]
            if not tool_calls:
                break

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

            response = self.client.responses.create(
                model="gpt-4.1-mini",
                input=tool_results,
                previous_response_id=response.id,
                tools=TOOLS,
            )

        self.last_response_id = response.id
        return response.output_text


# =============================================================================
# Main
# =============================================================================


def main():
    print("Timezone Agent (type 'quit' to exit)\n")
    agent = TimezoneAgent()

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

        response = agent.chat(user_input)
        print(f"Assistant: {response}\n")


if __name__ == "__main__":
    main()
