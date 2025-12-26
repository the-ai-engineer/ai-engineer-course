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
    """Get the current date, time, and timezone."""
    from datetime import datetime
    import time

    now = datetime.now()
    timezone = time.tzname[time.daylight]
    return f"Date: {now.strftime('%Y-%m-%d')}, Time: {now.strftime('%H:%M:%S')}, Timezone: {timezone}"


def read_file(path: str) -> str:
    """Read the contents of a local file."""
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
            "name": "read_file",
            "description": "Read the contents of a local file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file"}
                },
                "required": ["path"],
            },
        },
    },
]

TOOL_MAP = {
    "get_current_datetime": get_current_datetime,
    "read_file": read_file,
}

DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant that can use tools to answer questions.

Think step by step:
1. Understand what the user is asking
2. Use tools if needed to gather information
3. Provide a clear answer

When you have the final answer, respond directly without calling more tools."""


# =============================================================================
# Agent Class
# =============================================================================


class Agent:
    """A simple ReAct agent using the OpenAI Responses API."""

    def __init__(
        self,
        tools: list,
        tool_map: dict,
        model: str = "gpt-5-mini",
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ):
        self.tools = tools
        self.tool_map = tool_map
        self.model = model
        self.system_prompt = system_prompt

    def run(self, goal: str, max_iterations: int = 5) -> str:
        """Run the agent until the goal is achieved."""
        response = client.responses.create(
            model=self.model,
            input=goal,
            instructions=self.system_prompt,
            tools=self.tools,
        )

        for _ in range(max_iterations):
            # Check for tool calls
            tool_calls = [item for item in response.output if item.type == "function_call"]

            if not tool_calls:
                return response.output_text

            # Execute tools and collect results
            tool_results = []
            for call in tool_calls:
                func = self.tool_map.get(call.name)
                if func:
                    args = json.loads(call.arguments) if call.arguments else {}
                    result = func(**args)
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
# Usage
# =============================================================================

agent = Agent(tools=TOOLS, tool_map=TOOL_MAP)

# agent.run("What is the current date and time?")
# agent.run("Read the README.md file and summarize it")
