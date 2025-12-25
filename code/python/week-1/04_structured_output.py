"""
Structured Outputs

Get type-safe responses using Pydantic models with the OpenAI Responses API.
The responses.parse method provides a cleaner way to get structured data,
automatically parsing the response into your Pydantic model.
"""

from enum import Enum
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

client = OpenAI()

# =============================================================================
# Basic Structured Output
# =============================================================================


class ContactInfo(BaseModel):
    name: str
    email: str
    phone: str | None = None
    company: str | None = None


email_text = "Hi! I'm John Smith from Acme Corp. Reach me at john@acme.com or 555-0123."

response = client.responses.parse(
    model="gpt-5-mini",
    input=[
        {"role": "system", "content": "Extract contact information from the text."},
        {"role": "user", "content": email_text},
    ],
    text_format=ContactInfo,
)

contact = response.output_parsed
print(contact)

# =============================================================================
# Enums for Constrained Values
# =============================================================================


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(BaseModel):
    title: str
    description: str
    priority: Priority


response = client.responses.parse(
    model="gpt-5-mini",
    input=[
        {"role": "system", "content": "Create a task from the user's request."},
        {"role": "user", "content": "Fix the login bug that's blocking users"},
    ],
    text_format=Task,
)

task = response.output_parsed
print(task)

# =============================================================================
# Nested Objects
# =============================================================================


class Address(BaseModel):
    city: str
    country: str


class Person(BaseModel):
    name: str
    age: int
    address: Address
    skills: list[str]


text = "John Doe is a 32-year-old developer in San Francisco, USA. He knows Python and JavaScript."

response = client.responses.parse(
    model="gpt-5-mini",
    input=[
        {"role": "system", "content": "Extract person information from the text."},
        {"role": "user", "content": text},
    ],
    text_format=Person,
)

person = response.output_parsed
print(person)

# =============================================================================
# List of Objects
# =============================================================================


class Product(BaseModel):
    name: str
    price: float


class ProductList(BaseModel):
    products: list[Product]


response = client.responses.parse(
    model="gpt-5-mini",
    input=[
        {"role": "system", "content": "Generate products for a tech store."},
        {"role": "user", "content": "Generate 3 products"},
    ],
    text_format=ProductList,
)

catalog = response.output_parsed
print(catalog.products)
