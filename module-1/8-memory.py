"""
Conversation Memory

As conversations grow, you face two problems:
1. Context window limits - models have maximum token limits
2. Cost - longer conversations cost more per request

Memory strategies:
1. Full history - send everything (simple, but doesn't scale)
2. Sliding window - keep only the last N messages
3. Summarization - compress old messages into a summary

This lesson shows practical patterns for managing conversation memory.
"""

from openai import OpenAI

client = OpenAI()


# =============================================================================
# Strategy 1: Sliding Window Memory
# =============================================================================


class SlidingWindowMemory:
    """Keep only the last N messages."""

    def __init__(self, max_messages: int = 10):
        self.messages: list = []
        self.max_messages = max_messages

    def add_user_message(self, content: str):
        self.messages.append({"role": "user", "content": content})
        self._trim()

    def add_assistant_message(self, content: str):
        self.messages.append({"role": "assistant", "content": content})
        self._trim()

    def _trim(self):
        """Keep only the last N messages."""
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages :]

    def get_messages(self) -> list:
        return self.messages.copy()


# =============================================================================
# Strategy 2: Summary Memory
# =============================================================================


class SummaryMemory:
    """Summarize old messages to save context space."""

    def __init__(self, summarize_after: int = 6):
        self.messages: list = []
        self.summary: str = ""
        self.summarize_after = summarize_after

    def add_user_message(self, content: str):
        self.messages.append({"role": "user", "content": content})
        self._maybe_summarize()

    def add_assistant_message(self, content: str):
        self.messages.append({"role": "assistant", "content": content})
        self._maybe_summarize()

    def _maybe_summarize(self):
        """Summarize if we have too many messages."""
        if len(self.messages) > self.summarize_after:
            # Summarize the older messages
            old_messages = self.messages[:-2]  # Keep last 2
            self.summary = self._create_summary(old_messages)
            self.messages = self.messages[-2:]  # Keep only recent

    def _create_summary(self, messages: list) -> str:
        """Use the LLM to summarize the conversation so far."""
        conversation_text = "\n".join(f"{m['role']}: {m['content']}" for m in messages)

        response = client.responses.create(
            model="gpt-5-mini",
            instructions="Summarize this conversation in 2-3 sentences. Focus on key facts and context.",
            input=conversation_text,
        )

        return response.output_text

    def get_messages(self) -> list:
        """Return messages with summary context if available."""
        if self.summary:
            # Prepend summary as context
            summary_msg = {
                "role": "user",
                "content": f"[Previous conversation summary: {self.summary}]",
            }
            return [summary_msg] + self.messages.copy()
        return self.messages.copy()


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Sliding Window Memory Demo")
    print("=" * 60)

    memory = SlidingWindowMemory(max_messages=4)

    # Simulate a conversation
    exchanges = [
        ("Hi, I'm Bob.", "Hello Bob! Nice to meet you."),
        ("I live in Paris.", "Paris is a beautiful city!"),
        ("I work as a chef.", "That's a great profession!"),
        ("What do you know about me?", ""),  # Test if it remembers
    ]

    for user_msg, assistant_msg in exchanges:
        memory.add_user_message(user_msg)
        if assistant_msg:
            memory.add_assistant_message(assistant_msg)

    print(f"Messages in memory: {len(memory.get_messages())}")
    print(f"Window size: {memory.max_messages}")
    print()

    # Get response using memory
    response = client.responses.create(
        model="gpt-5-mini",
        instructions="You are a helpful assistant.",
        input=memory.get_messages(),
    )

    print("User: What do you know about me?")
    print(f"Assistant: {response.output_text}")
    print()
    print("Note: With sliding window, early messages may be forgotten.")

    print()
    print("=" * 60)
    print("Summary Memory Demo")
    print("=" * 60)

    summary_memory = SummaryMemory(summarize_after=4)

    # Add messages
    for user_msg, assistant_msg in exchanges[:-1]:
        summary_memory.add_user_message(user_msg)
        summary_memory.add_assistant_message(assistant_msg)

    if summary_memory.summary:
        print(f"Summary created: {summary_memory.summary}")
    else:
        print("No summary needed yet.")

    print(f"Recent messages: {len(summary_memory.messages)}")

