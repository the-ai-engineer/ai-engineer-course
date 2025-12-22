"""
The Agent Loop

A simple ReAct agent built from scratch.
"""

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()


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
# Agent Class
# =============================================================================


class Agent:
    """
    A simple ReAct agent.

    Usage:
        agent = Agent(tools=[get_current_datetime, fetch_url])
        answer = agent.run("What time is it?")
    """

    def __init__(
        self,
        tools: list = None,
        model: str = "gemini-3-flash-preview",
        system_prompt: str = None,
    ):
        self.tools = tools or []
        self.tool_map = {f.__name__: f for f in self.tools}
        self.model = model
        self.system_prompt = system_prompt or self._default_prompt()
        self.messages = []  # Conversation history

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
        # Reset messages for new run
        self.messages = []

        if verbose:
            print(f"Goal: {goal}\n")

        # Add user goal to messages
        self.messages.append(
            types.Content(role="user", parts=[types.Part.from_text(goal)])
        )

        for i in range(max_iterations):
            if verbose:
                print(f"--- Step {i + 1} ---")

            # Call model with full message history
            response = client.models.generate_content(
                model=self.model,
                contents=self.messages,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    tools=self.tools,
                ),
            )

            # Add assistant response to messages
            self.messages.append(response.candidates[0].content)

            # Check for tool calls
            parts = response.candidates[0].content.parts
            tool_calls = [p for p in parts if p.function_call]

            if not tool_calls:
                # No tool calls = final answer
                if verbose:
                    print(f"Answer: {response.text}\n")
                return response.text

            # Execute tools and collect results
            tool_results = []
            for part in tool_calls:
                fc = part.function_call
                func = self.tool_map.get(fc.name)

                if func:
                    result = func(**fc.args)
                    if verbose:
                        print(f"Tool: {fc.name}({fc.args})")
                        print(f"Result: {result[:200]}..." if len(result) > 200 else f"Result: {result}")
                else:
                    result = f"Unknown tool: {fc.name}"

                tool_results.append(
                    types.Part.from_function_response(
                        name=fc.name,
                        response={"result": result},
                    )
                )

            # Add tool results to messages
            self.messages.append(types.Content(role="user", parts=tool_results))

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
        model: str = "gemini-3-flash-preview",
        system_prompt: str = None,
    ):
        self.tools = tools or []
        self.tool_map = {f.__name__: f for f in self.tools}
        self.model = model
        self.system_prompt = system_prompt or self._default_prompt()
        self.messages = []

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
        self.messages = []

        print(f"Goal: {goal}\n")

        self.messages.append(
            types.Content(role="user", parts=[types.Part.from_text(goal)])
        )

        for i in range(max_iterations):
            print(f"--- Step {i + 1} ---")

            response = client.models.generate_content(
                model=self.model,
                contents=self.messages,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    tools=self.tools,
                ),
            )

            self.messages.append(response.candidates[0].content)

            parts = response.candidates[0].content.parts
            tool_calls = [p for p in parts if p.function_call]

            if not tool_calls:
                print(f"Answer: {response.text}\n")
                return response.text

            # Execute tools WITH APPROVAL
            tool_results = []
            for part in tool_calls:
                fc = part.function_call
                func = self.tool_map.get(fc.name)

                if func:
                    # Ask for approval
                    if self._get_approval(fc.name, fc.args):
                        result = func(**fc.args)
                        print(f"Result: {result[:200]}..." if len(result) > 200 else f"Result: {result}")
                    else:
                        result = "Tool execution denied by user"
                        print("Denied")
                else:
                    result = f"Unknown tool: {fc.name}"

                tool_results.append(
                    types.Part.from_function_response(
                        name=fc.name,
                        response={"result": result},
                    )
                )

            self.messages.append(types.Content(role="user", parts=tool_results))

        return "Max iterations reached"


# =============================================================================
# Example Usage
# =============================================================================

# Basic agent with tools
agent = Agent(tools=[get_current_datetime, fetch_url, read_file])

# agent.run("What is the current date and time?")
# agent.run("Fetch the Python homepage and tell me what Python is")
# agent.run("Read the README.md file and summarize it")


# Agent with approval for dangerous tools
bash_agent = AgentWithApproval(tools=[run_bash])

# bash_agent.run("List the files in the current directory")
# bash_agent.run("What processes are running on this machine?")
# bash_agent.run("How much disk space is available?")
