"""
Tool Calling Basics

This example shows how to:
1. Define a tool schema
2. Make an API call with tools
3. Handle the tool call response
4. Execute the tool and return results

We use `read_file` as our example — a practical tool you'll use
in the Terminal Agent project.
"""

from openai import OpenAI
import json
import os

client = OpenAI()

# =============================================================================
# Step 1: Define the tool schema
# =============================================================================

# The schema tells the LLM what the tool does and what arguments it accepts.
# This is JSON Schema format — the same format used for structured output.

tools = [
    {
        "type": "function",
        "name": "read_file",
        "description": "Read the contents of a file at the given path.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file to read",
                },
            },
            "required": ["path"],
        },
    },
]


# =============================================================================
# Step 2: Implement the actual function
# =============================================================================


def read_file(path: str) -> dict:
    """Read a file and return its contents."""
    try:
        # Expand ~ to home directory
        expanded_path = os.path.expanduser(path)

        with open(expanded_path, "r") as f:
            content = f.read()

        return {"path": path, "content": content}

    except FileNotFoundError:
        return {"error": f"File not found: {path}"}
    except PermissionError:
        return {"error": f"Permission denied: {path}"}
    except Exception as e:
        return {"error": str(e)}


# =============================================================================
# Step 3: Make the API call with tools
# =============================================================================

# Create a test file for the demo
test_file = "/tmp/demo.txt"
with open(test_file, "w") as f:
    f.write("Hello from the demo file!\nThis is line 2.")

# Ask the LLM to read the file
messages: list = [{"role": "user", "content": f"What's in the file {test_file}?"}]

response = client.responses.create(
    model="gpt-5-mini",
    tools=tools,  # type: ignore[arg-type]
    input=messages,
)

# =============================================================================
# Step 4: Check if a tool was called
# =============================================================================

# The response might be a direct answer OR a tool call request
for item in response.output:
    if item.type == "function_call":
        print(f"Tool requested: {item.name}")
        print(f"Arguments: {item.arguments}")

        # =============================================================================
        # Step 5: Execute the tool and return result to LLM
        # =============================================================================

        try:
            args = json.loads(item.arguments)
            result = read_file(**args)
        except json.JSONDecodeError:
            result = {"error": "Invalid JSON in tool arguments"}

        print(f"Tool result: {result}")

        # Add the model's output and our tool result to the conversation
        messages += response.output
        messages.append(
            {
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps(result),
            }
        )

        # Send result back to get final answer
        final_response = client.responses.create(
            model="gpt-5-mini",
            tools=tools,  # type: ignore[arg-type]
            input=messages,  # type: ignore[arg-type]
        )

        print(f"\nFinal answer: {final_response.output_text}")

    elif item.type == "message":
        # LLM answered directly without using tools
        print(f"Direct answer: {item.content}")
