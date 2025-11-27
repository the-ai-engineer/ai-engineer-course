"""
Conversations and Message Roles

LLM APIs are stateless - each call is independent. To have a conversation,
you must send the full history with each request. Messages have roles that
tell the model who said what.

Message Roles:
- "user": The human's messages
- "assistant": The model's previous responses
- System prompt: Set via `instructions` parameter (not a message role)
"""

from openai import OpenAI

client = OpenAI()

# =============================================================================
# Example 1: Single turn (no conversation history)
# =============================================================================

response = client.responses.create(
    model="gpt-5-mini",
    instructions="You are a helpful assistant.",
    input="What is the capital of France?",
)

print("Single turn:")
print(f"  Assistant: {response.output_text}")
print()

# =============================================================================
# Example 2: Multi-turn conversation
# =============================================================================

# Build conversation history as a list of messages
conversation = [
    {"role": "user", "content": "My name is Alice."},
]

# First turn
response = client.responses.create(
    model="gpt-5-mini",
    instructions="You are a helpful assistant.",
    input=conversation,  # type: ignore[arg-type]
)

# Add the assistant's response to history
conversation.append({"role": "assistant", "content": response.output_text})

print("Multi-turn conversation:")
print(f"  User: {conversation[0]['content']}")
print(f"  Assistant: {response.output_text}")

# Second turn - the model remembers the context
conversation.append({"role": "user", "content": "What is my name?"})

response = client.responses.create(
    model="gpt-5-mini",
    instructions="You are a helpful assistant.",
    input=conversation,  # type: ignore[arg-type]
)

print(f"  User: {conversation[-1]['content']}")
print(f"  Assistant: {response.output_text}")
print()

# =============================================================================
# Example 3: Simple chat loop
# =============================================================================


def chat(system_prompt: str = "You are a helpful assistant."):
    """Simple interactive chat loop."""
    conversation: list = []

    print("Chat started. Type 'quit' to exit.")
    print("-" * 40)

    while True:
        user_input = input("You: ")

        if user_input.lower() == "quit":
            break

        # Add user message to history
        conversation.append({"role": "user", "content": user_input})

        # Get response
        response = client.responses.create(
            model="gpt-5-mini",
            instructions=system_prompt,
            input=conversation,  # type: ignore[arg-type]
        )

        # Add assistant response to history
        assistant_message = response.output_text
        conversation.append({"role": "assistant", "content": assistant_message})

        print(f"Assistant: {assistant_message}")

    print(f"\nConversation had {len(conversation)} messages.")


if __name__ == "__main__":
    # Uncomment to run interactive chat:
    # chat()
    pass
