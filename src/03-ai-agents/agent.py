#!/usr/bin/env python3
"""
AI Agents 101: Building Intelligent Agents with Tool Calling

This example demonstrates:
1. Basic agent structure with conversation memory
2. Tool calling loop (agent decides when to use tools)
3. Type-safe tool definitions using Pydantic
"""

import json
import inspect
from typing import Callable
from openai import OpenAI


# Tool implementation
def get_weather(location: str) -> str:
    """Get the current weather for a location.

    Args:
        location: The city and state, e.g. San Francisco, CA
    """
    return f"The weather in {location} is sunny and 72°F"


# Simple Tool class
class Tool:
    def __init__(self, func: Callable):
        self.func = func
        self.name = func.__name__
        self.description = func.__doc__ or ""

    def to_openai_format(self) -> dict:
        """Convert to OpenAI function calling format."""
        # Create schema from function signature
        sig = inspect.signature(self.func)

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            properties[param_name] = {
                "type": "string",
                "description": f"The {param_name} parameter",
            }
            required.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    def run(self, args: dict) -> str:
        """Execute the tool."""
        return str(self.func(**args))


# Register tool
TOOLS = {
    "get_weather": Tool(get_weather),
}


class Agent:
    def __init__(self, system_prompt: str = "You are a helpful AI agent."):
        self.client = OpenAI()
        self.messages = [{"role": "system", "content": system_prompt}]
        self.max_iterations = 10

    def run(self, user_prompt: str) -> str:
        """Run the agent with a tool calling loop."""
        self.messages.append({"role": "user", "content": user_prompt})

        for _ in range(self.max_iterations):
            # Call LLM with GPT-5
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=self.messages,
                tools=[tool.to_openai_format() for tool in TOOLS.values()],
                tool_choice="auto",
            )

            message = response.choices[0].message

            # If no tool calls, we're done
            if not message.tool_calls:
                self.messages.append({"role": "assistant", "content": message.content})
                return message.content

            # Add assistant message
            self.messages.append(
                {
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": message.tool_calls,
                }
            )

            # Execute tool calls
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                print(f"🔧 {tool_name}({tool_args})")
                result = TOOLS[tool_name].run(tool_args)
                print(f"✅ {result}")

                self.messages.append(
                    {"role": "tool", "tool_call_id": tool_call.id, "content": result}
                )


# Example usage
if __name__ == "__main__":
    agent = Agent()

    print("Example 1: No tools needed")
    print(agent.run("What is the capital of France?"))
    print()

    print("Example 2: Using weather tool")
    print(agent.run("What's the weather in Tokyo?"))
    print()

    print("Example 3: Multiple locations")
    print(agent.run("What's the weather in Seattle and Paris?"))
