"""
Human-in-the-Loop Agent

An agent that requires human approval before executing tools.
Use this pattern for dangerous operations like file writes, API calls, or database changes.
"""

import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


# =============================================================================
# Tool that requires approval
# =============================================================================


def write_file(path: str, content: str) -> str:
    """Write content to a file."""
    try:
        with open(path, "w") as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {e}"


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file"},
                    "content": {"type": "string", "description": "Content to write"},
                },
                "required": ["path", "content"],
            },
        },
    },
]

TOOL_MAP = {"write_file": write_file}


# =============================================================================
# Approval Function
# =============================================================================


def get_approval(tool_name: str, args: dict) -> bool:
    """Ask user for approval before running a tool."""
    print(f"\nTool: {tool_name}")
    print(f"Args: {args}")
    response = input("Approve? [y/n]: ").strip().lower()
    return response == "y"


# =============================================================================
# Agent with Approval
# =============================================================================


def run_with_approval(goal: str, max_iterations: int = 5) -> str:
    """Run an agent loop that requires approval for each tool call."""
    response = client.responses.create(
        model="gpt-5-mini",
        input=goal,
        instructions="You can write files when asked. Be helpful.",
        tools=TOOLS,
    )

    for _ in range(max_iterations):
        tool_calls = [item for item in response.output if item.type == "function_call"]

        if not tool_calls:
            return response.output_text

        tool_results = []
        for call in tool_calls:
            func = TOOL_MAP.get(call.name)
            args = json.loads(call.arguments) if call.arguments else {}

            # Ask for approval before executing
            if get_approval(call.name, args):
                result = func(**args) if func else f"Unknown tool: {call.name}"
            else:
                result = "Tool execution denied by user"

            tool_results.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": str(result),
            })

        response = client.responses.create(
            model="gpt-5-mini",
            input=tool_results,
            previous_response_id=response.id,
            tools=TOOLS,
        )

    return "Max iterations reached"


# Usage:
# run_with_approval("Create a file called hello.txt with the content 'Hello, World!'")
