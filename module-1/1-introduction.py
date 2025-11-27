from openai import OpenAI

# Ensure you have set an OPENAI_API_KEY environment variable set.
client = OpenAI()

response = client.responses.create(
    model="gpt-5-mini",
    input="What is the capital of the UK?",
)

print(response.output_text)

# Example 2: Using instructions (system prompt)
response2 = client.responses.create(
    model="gpt-5-mini",
    instructions="Speak like a pirate",
    input="What is the capital of the UK?",
)

print(response2.output_text)
