"""
The Agent Loop

A simple ReAct agent built from scratch using the OpenAI Responses API.
"""

import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


# =============================================================================
# Tools
# =============================================================================


def get_current_datetime() -> str:
    """Get the current date, time, and timezone.

    Returns:
        Current datetime information
    """
    from datetime import datetime
    import time

    now = datetime.now()
    timezone = time.tzname[time.daylight]

    return f"Date: {now.strftime('%Y-%m-%d')}, Time: {now.strftime('%H:%M:%S')}, Timezone: {timezone}"


def fetch_url(url: str) -> str:
    """Fetch the content of a webpage.

    Args:
        url: The URL to fetch (must start with https://)

    Returns:
        The text content of the page (truncated to 5000 chars)
    """
    import urllib.request
    import urllib.error

    if not url.startswith("https://"):
        return "Error: URL must start with https://"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            content = response.read().decode("utf-8", errors="ignore")
            # Return truncated content
            if len(content) > 5000:
                return content[:5000] + "\n... (truncated)"
            return content
    except urllib.error.URLError as e:
        return f"Error fetching URL: {e}"
    except Exception as e:
        return f"Error: {e}"


def read_file(path: str) -> str:
    """Read the contents of a local file.

    Args:
        path: Path to the file to read

    Returns:
        The file contents (truncated to 5000 chars)
    """
    try:
        with open(path, "r") as f:
            content = f.read()
            if len(content) > 5000:
                return content[:5000] + "\n... (truncated)"
            return content
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except Exception as e:
        return f"Error reading file: {e}"


# =============================================================================
# Tool Definitions
# =============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Get the current date, time, and timezone",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Fetch the content of a webpage",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to fetch (must start with https://)",
                    }
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a local file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read",
                    }
                },
                "required": ["path"],
            },
        },
    },
]

TOOL_MAP = {
    "get_current_datetime": get_current_datetime,
    "fetch_url": fetch_url,
    "read_file": read_file,
}


# =============================================================================
# Agent Class
# =============================================================================


class Agent:
    """
    A simple ReAct agent using the OpenAI Responses API.

    Usage:
        agent = Agent(tools=TOOLS, tool_map=TOOL_MAP)
        answer = agent.run("What time is it?")
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
        return """You are a helpful assistant that can use tools to answer questions.

Think step by step:
1. Understand what the user is asking
2. Use tools if needed to gather information
3. Provide a clear answer

When you have the final answer, respond directly without calling more tools."""

    def run(self, goal: str, max_iterations: int = 5, verbose: bool = True) -> str:
        """
        Run the agent until the goal is achieved.

        Args:
            goal: What you want the agent to accomplish
            max_iterations: Safety limit to prevent infinite loops
            verbose: Print progress

        Returns:
            The agent's final answer
        """
        if verbose:
            print(f"Goal: {goal}\n")

        # Initial request
        response = client.responses.create(
            model=self.model,
            input=goal,
            instructions=self.system_prompt,
            tools=self.tools,
        )

        for i in range(max_iterations):
            if verbose:
                print(f"--- Step {i + 1} ---")

            # Check for tool calls
            tool_calls = [item for item in response.output if item.type == "function_call"]

            if not tool_calls:
                # No tool calls = final answer
                if verbose:
                    print(f"Answer: {response.output_text}\n")
                return response.output_text

            # Execute tools and collect results
            tool_results = []
            for call in tool_calls:
                func = self.tool_map.get(call.name)

                if func:
                    args = json.loads(call.arguments) if call.arguments else {}
                    result = func(**args)
                    if verbose:
                        print(f"Tool: {call.name}({args})")
                        print(f"Result: {result[:200]}..." if len(str(result)) > 200 else f"Result: {result}")
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
# Human-in-the-Loop Agent
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


BASH_TOOLS = [
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

BASH_TOOL_MAP = {"run_bash": run_bash}


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

# Basic agent with tools
agent = Agent(tools=TOOLS, tool_map=TOOL_MAP)

# agent.run("What is the current date and time?")
# agent.run("Fetch the Python homepage and tell me what Python is")
# agent.run("Read the README.md file and summarize it")


# Agent with approval for dangerous tools
bash_agent = AgentWithApproval(tools=BASH_TOOLS, tool_map=BASH_TOOL_MAP)

# bash_agent.run("List the files in the current directory")
# bash_agent.run("What processes are running on this machine?")
# bash_agent.run("How much disk space is available?")
