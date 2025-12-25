"""
Human-in-the-Loop Agent

An agent that requires human approval before executing dangerous tools.
"""

import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


# =============================================================================
# Dangerous Tool: Bash Commands
# =============================================================================


def run_bash(command: str) -> str:
    """Run a bash command and return the output.

    Args:
        command: The bash command to execute
    """
    import subprocess

    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return f"Error: {result.stderr}"
    return result.stdout or "Command completed successfully"


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_bash",
            "description": "Run a bash command and return the output",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to execute",
                    }
                },
                "required": ["command"],
            },
        },
    },
]

TOOL_MAP = {"run_bash": run_bash}


# =============================================================================
# Agent with Human Approval
# =============================================================================


class AgentWithApproval:
    """
    An agent that requires human approval before executing tools.

    Use this pattern for dangerous operations like:
    - Running shell commands
    - Sending emails
    - Making purchases
    - Modifying databases
    """

    def __init__(
        self,
        tools: list = None,
        tool_map: dict = None,
        model: str = "gpt-5-mini",
        system_prompt: str = None,
    ):
        self.tools = tools or []
        self.tool_map = tool_map or {}
        self.model = model
        self.system_prompt = system_prompt or self._default_prompt()

    def _default_prompt(self) -> str:
        return """You are a helpful assistant that can run bash commands.

Only use the run_bash tool when the user asks you to perform system operations.
Be careful with destructive commands."""

    def _get_approval(self, tool_name: str, args: dict) -> bool:
        """Ask user for approval before running a tool."""
        print(f"\nTool: {tool_name}")
        print(f"Args: {args}")
        response = input("Approve? [y/n]: ").strip().lower()
        return response == "y"

    def run(self, goal: str, max_iterations: int = 5) -> str:
        """Run agent with human approval for each tool call."""
        print(f"Goal: {goal}\n")

        response = client.responses.create(
            model=self.model,
            input=goal,
            instructions=self.system_prompt,
            tools=self.tools,
        )

        for i in range(max_iterations):
            print(f"--- Step {i + 1} ---")

            # Check for tool calls
            tool_calls = [item for item in response.output if item.type == "function_call"]

            if not tool_calls:
                print(f"Answer: {response.output_text}\n")
                return response.output_text

            # Execute tools WITH APPROVAL
            tool_results = []
            for call in tool_calls:
                func = self.tool_map.get(call.name)

                if func:
                    args = json.loads(call.arguments) if call.arguments else {}

                    # Ask for approval
                    if self._get_approval(call.name, args):
                        result = func(**args)
                        print(f"Result: {result[:200]}..." if len(str(result)) > 200 else f"Result: {result}")
                    else:
                        result = "Tool execution denied by user"
                        print("Denied")
                else:
                    result = f"Unknown tool: {call.name}"

                tool_results.append({
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": str(result),
                })

            # Continue with tool results
            response = client.responses.create(
                model=self.model,
                input=tool_results,
                previous_response_id=response.id,
                tools=self.tools,
            )

        return "Max iterations reached"


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    agent = AgentWithApproval(tools=TOOLS, tool_map=TOOL_MAP)

    # Uncomment to run examples:
    # agent.run("List the files in the current directory")
    # agent.run("What processes are running on this machine?")
    # agent.run("How much disk space is available?")
