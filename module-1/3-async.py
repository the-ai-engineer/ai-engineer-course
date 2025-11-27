import asyncio

# Uncomment if running in a notebook
# import nest_asyncio

from openai import AsyncOpenAI

# Allow nested event loops inside notebooks
# nest_asyncio.apply()

client = AsyncOpenAI()


# Example 1: Basic async client call
async def call_llm(message: str):
    return await client.responses.create(model="gpt-5-mini", input=message)


response = asyncio.run(call_llm("Who won the world series in 2020?"))

