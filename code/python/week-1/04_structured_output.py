"""
Structured Outputs

Get type-safe responses using Pydantic models with the Gemini API.
"""

from enum import Enum
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

client = genai.Client()

# =============================================================================
# Basic Structured Output
# =============================================================================


class ContactInfo(BaseModel):
    name: str
    email: str
    phone: str | None = None
    company: str | None = None


email_text = "Hi! I'm John Smith from Acme Corp. Reach me at john@acme.com or 555-0123."

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=f"Extract contact information:\n{email_text}",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=ContactInfo,
    ),
)

contact = ContactInfo.model_validate_json(response.text)
contact

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


response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Create a task for fixing the login bug that's blocking users",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=Task,
    ),
)

task = Task.model_validate_json(response.text)
task

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

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=f"Extract person information:\n{text}",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=Person,
    ),
)

person = Person.model_validate_json(response.text)
person

# =============================================================================
# List of Objects
# =============================================================================


class Product(BaseModel):
    name: str
    price: float


class ProductList(BaseModel):
    products: list[Product]


response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Generate 3 products for a tech store",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=ProductList,
    ),
)

catalog = ProductList.model_validate_json(response.text)
catalog.products
