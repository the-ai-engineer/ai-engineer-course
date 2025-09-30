from openai import OpenAI
from pydantic import BaseModel

from datetime import datetime

client = OpenAI()


class CalendarEvent(BaseModel):
    name: str
    date: datetime
    participants: list[str]


PROMPT = f"""You are a helpful calendar assistant.

Today is {datetime.now().isoformat()}
"""

response = client.responses.parse(
    model="gpt-4o",
    input=[
        {"role": "system", "content": PROMPT},
        {
            "role": "user",
            "content": "Schedule a meeting with Jack at 2pm next Friday.",
        },
    ],
    text_format=CalendarEvent,
)

# event = response.output_parsed
# event.name  # 'Meeting with Jack'
# event.date.isoformat()  # '2025-08-22T14:00:00+00:00'
# event.participants  # ['Jack']
