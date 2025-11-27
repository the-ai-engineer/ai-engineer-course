from openai import OpenAI
from pydantic import BaseModel
from enum import Enum

client = OpenAI()


class QueryType(str, Enum):
    BILLING = "billing"
    TECHNICAL = "technical"
    OTHER = "other"


class SupportQuery(BaseModel):
    query_type: QueryType
    summary: str


response = client.responses.parse(
    model="gpt-4o",
    input=[
        {
            "role": "user",
            "content": "I was charged twice for my subscription this month. Can you help me get a refund?",
        },
    ],
    text_format=SupportQuery,
)

# query = response.output_parsed
# query.query_type  # QueryType.BILLING
# query.summary  # 'Customer charged twice for subscription, requesting refund'
