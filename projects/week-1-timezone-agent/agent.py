"""
Timezone Agent

A terminal-based chat assistant for timezone questions.
Run with: uv run python agent.py
"""

from datetime import datetime
from zoneinfo import ZoneInfo
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

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


SYSTEM_PROMPT = """You are a helpful timezone assistant.

You can:
- Get the current time in any timezone
- Convert times between timezones

Be concise and helpful. When users ask about times in cities, use the appropriate IANA timezone (e.g., 'Asia/Tokyo' for Tokyo, 'America/New_York' for New York)."""

# =============================================================================
# Main
# =============================================================================


def main():
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[get_current_time, convert_time],
        ),
    )

    print("Timezone Agent")
    print("Type 'quit' to exit\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if not user_input:
            continue
        if user_input.lower() in ["quit", "exit", "q"]:
            break

        response = chat.send_message(user_input)
        print(f"Assistant: {response.text}\n")


if __name__ == "__main__":
    main()
