from openai import OpenAI

client = OpenAI()

# Example 1: Basic client call
response = client.responses.create(
    model="gpt-5", input="What is the capital of the UK?"
)

response.model_dump()

response.output_text

# Example 2: System prompt
response2 = client.responses.create(
    model="gpt-5",
    instructions="Speak like a pirate and respponse in Japenese",
    input="Who won the world series in 2020?",
)

response2.output_text
