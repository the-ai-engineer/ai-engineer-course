"""
Structured Output with Pydantic

Get typed, validated responses instead of raw text.
"""

from openai import OpenAI
from pydantic import BaseModel, Field
from enum import Enum

client = OpenAI()


# =============================================================================
# Example 1: Basic Classification
# =============================================================================


class QueryType(str, Enum):
    BILLING = "billing"
    TECHNICAL = "technical"
    GENERAL = "general"


class SupportQuery(BaseModel):
    query_type: QueryType
    summary: str


response = client.responses.parse(
    model="gpt-5-mini",
    input="I was charged twice for my subscription. Can you help me get a refund?",
    text_format=SupportQuery,
)

result = response.output_parsed
print("Classification:")
print(f"  Type: {result.query_type}")
print(f"  Summary: {result.summary}")


# =============================================================================
# Example 2: Data Extraction with Nested Models
# =============================================================================


class Address(BaseModel):
    city: str
    country: str


class Company(BaseModel):
    name: str
    address: Address
    employee_count: int = Field(gt=0)


text = """
TechCorp is a software company with 150 employees.
They're located in San Francisco, USA.
"""

response = client.responses.parse(
    model="gpt-5-mini",
    input=f"Extract company info:\n{text}",
    text_format=Company,
)

company = response.output_parsed
print("\nExtracted Company:")
print(f"  Name: {company.name}")
print(f"  Location: {company.address.city}, {company.address.country}")
print(f"  Employees: {company.employee_count}")


# =============================================================================
# Example 3: Optional Fields
# =============================================================================


class JobPosting(BaseModel):
    title: str
    company: str
    salary_min: int | None = None
    salary_max: int | None = None
    remote: bool


posting = """
Senior Python Developer at TechStartup
Remote position. $150k-$180k.
"""

response = client.responses.parse(
    model="gpt-5-mini",
    input=f"Extract job details:\n{posting}",
    text_format=JobPosting,
)

job = response.output_parsed
print("\nJob Posting:")
print(f"  {job.title} at {job.company}")
print(f"  Remote: {job.remote}")
if job.salary_min and job.salary_max:
    print(f"  Salary: ${job.salary_min:,} - ${job.salary_max:,}")
