"""
Terminal Agent

An interactive command-line AI assistant that can read files,
execute commands, and have conversations.

Run: python agent.py
"""

from openai import OpenAI
import json

from tools import TOOLS, TOOL_REGISTRY

client = OpenAI()

SYSTEM_PROMPT = """You are a helpful terminal assistant. You can help users explore 
their file system, read files, run commands, and answer questions.

Be concise and helpful. When using tools, explain what you're doing and summarize 
the results in a useful way.

If a tool returns an error, explain what went wrong and suggest alternatives."""


def print_banner():
    """Print a welcome banner."""
    print()
    print("╭─────────────────────────────────────────╮")
    print("│  Terminal Agent                         │")
    print("│  Type 'quit' to exit, 'help' for help  │")
    print("╰─────────────────────────────────────────╯")
    print()


def print_tool_call(name: str, args: dict, result: str):
    """Print a formatted tool call."""
    # TODO: Format this nicely
    # Show the tool name and arguments
    # Show a truncated result if it's too long
    pass


def run_agent(max_iterations: int = 10):
    """Main agent loop."""
    messages: list = []

    print_banner()

    while True:
        # Get user input
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        # Handle special commands
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        if user_input.lower() == "help":
            print("Available commands:")
            print("  quit - Exit the agent")
            print("  help - Show this message")
            print("  Or just ask me anything!")
            continue
        if not user_input:
            continue

        # Add user message to history
        messages.append({"role": "user", "content": user_input})

        # TODO: Implement the agent loop
        #
        # For each iteration:
        # 1. Call the LLM with messages and tools
        # 2. Check if there are tool calls in the response
        # 3. If yes: execute tools, add results to messages, continue loop
        # 4. If no: print the response (with streaming!) and break
        #
        # Don't forget:
        # - Add response.output to messages after LLM call
        # - Handle tool execution errors gracefully
        # - Use streaming for the final text response
        # - Respect max_iterations to prevent infinite loops

        print()  # Spacing after response


if __name__ == "__main__":
    run_agent()
