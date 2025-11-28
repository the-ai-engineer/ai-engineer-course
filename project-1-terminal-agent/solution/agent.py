"""
Terminal Agent - Solution

A complete interactive command-line AI assistant.

Run: python agent.py
"""

from openai import OpenAI
import json

from tools import TOOLS, TOOL_REGISTRY

client = OpenAI()

SYSTEM_PROMPT = """You are a helpful terminal assistant. You can help users explore 
their file system, read files, run commands, and answer questions.

Be concise and helpful. When using tools, explain what you're doing briefly.
After getting tool results, summarize them in a useful way for the user.

If a tool returns an error, explain what went wrong and suggest alternatives.

Available tools:
- list_directory: List files in a directory
- read_file: Read file contents
- write_file: Write to a file
- run_command: Execute shell commands
- get_file_info: Get file metadata"""


def print_banner():
    """Print a welcome banner."""
    print()
    print("╭─────────────────────────────────────────╮")
    print("│  Terminal Agent                         │")
    print("│  Type 'quit' to exit, 'help' for help  │")
    print("╰─────────────────────────────────────────╯")
    print()


def print_tool_call(iteration: int, name: str, args: dict, result: str):
    """Print a formatted tool call."""
    # Format arguments nicely
    args_str = ", ".join(f"{k}={repr(v)}" for k, v in args.items())

    print(f"\n  [{iteration}] Tool: {name}({args_str})")

    # Truncate long results
    result_preview = result
    if len(result_preview) > 200:
        result_preview = result_preview[:200] + "..."

    # Indent result lines
    for line in result_preview.split("\n")[:5]:  # Max 5 lines
        print(f"      → {line}")

    if result.count("\n") > 5:
        print(f"      ... ({result.count(chr(10)) + 1} lines total)")
    print()


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
            print("\nI can help you with:")
            print("  • Exploring files and directories")
            print("  • Reading and writing files")
            print("  • Running shell commands")
            print("  • Answering questions about your project")
            print("\nCommands:")
            print("  quit - Exit the agent")
            print("  help - Show this message")
            print()
            continue
        if not user_input:
            continue

        # Add user message to history
        messages.append({"role": "user", "content": user_input})

        # Agent loop
        for iteration in range(max_iterations):
            # Call the LLM
            response = client.responses.create(
                model="gpt-5-mini",
                instructions=SYSTEM_PROMPT,
                tools=TOOLS,  # type: ignore[arg-type]
                input=messages,  # type: ignore[arg-type]
            )

            # Check for tool calls
            tool_calls = [
                item for item in response.output if item.type == "function_call"
            ]

            # No tool calls = we have our final answer
            if not tool_calls:
                # Stream the final response
                print()
                stream = client.responses.create(
                    model="gpt-5-mini",
                    instructions=SYSTEM_PROMPT,
                    tools=TOOLS,  # type: ignore[arg-type]
                    input=messages,  # type: ignore[arg-type]
                    stream=True,
                )

                full_response = ""
                for event in stream:
                    if hasattr(event, "delta") and event.delta:
                        print(event.delta, end="", flush=True)
                        full_response += event.delta

                print()  # Newline after response

                # Add assistant response to history
                messages.append({"role": "assistant", "content": full_response})
                break

            # Add the model's response to conversation
            messages += response.output

            # Execute each tool call
            for call in tool_calls:
                # Get the function
                if call.name not in TOOL_REGISTRY:
                    result = f"Error: Unknown tool '{call.name}'"
                else:
                    try:
                        func = TOOL_REGISTRY[call.name]
                        args = json.loads(call.arguments)
                        result = func(**args)
                    except json.JSONDecodeError:
                        result = f"Error: Invalid arguments"
                    except Exception as e:
                        result = f"Error: {e}"

                # Print the tool call
                args = json.loads(call.arguments) if call.arguments else {}
                print_tool_call(iteration + 1, call.name, args, result)

                # Add result to conversation
                messages.append(
                    {
                        "type": "function_call_output",
                        "call_id": call.call_id,
                        "output": result,
                    }
                )

        else:
            # Hit max iterations
            print(f"\n⚠️  Reached maximum iterations ({max_iterations})")

        print()  # Spacing after response


if __name__ == "__main__":
    run_agent()
