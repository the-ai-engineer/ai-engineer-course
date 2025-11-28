"""
Basic Agent Loop

An agent is an LLM that can call tools in a loop until it has enough
information to answer the user's question. This is the core pattern
that powers AI assistants.

The key difference from basic tool calling:
- We loop until the LLM stops requesting tools
- The LLM can call multiple tools in sequence
- Results from one tool can inform the next tool call
"""

from openai import OpenAI
import json

client = OpenAI()

# =============================================================================
# Tools - define what the agent can do
# =============================================================================

tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name, e.g. 'Paris', 'London'",
                },
            },
            "required": ["city"],
        },
    },
    {
        "type": "function",
        "name": "calculate",
        "description": "Perform a mathematical calculation.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression to evaluate, e.g. '2 + 2'",
                },
            },
            "required": ["expression"],
        },
    },
]


# =============================================================================
# Tool implementations
# =============================================================================


def get_weather(city: str) -> str:
    """Simulated weather API."""
    weather_data = {
        "paris": "Sunny, 22°C",
        "london": "Cloudy, 15°C",
        "tokyo": "Rainy, 18°C",
        "new york": "Clear, 20°C",
    }
    return weather_data.get(city.lower(), f"No weather data for {city}")


def calculate(expression: str) -> str:
    """Safe calculator - only allows basic math."""
    try:
        # Only allow safe math operations
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error: {e}"


# Tool registry - maps names to functions
tool_registry = {
    "get_weather": get_weather,
    "calculate": calculate,
}


# =============================================================================
# The Agent Loop
# =============================================================================


def run_agent(
    user_message: str,
    system_prompt: str = "You are a helpful assistant.",
    max_iterations: int = 10,
) -> str:
    """
    Run the agent loop until we get a final answer.

    The agent will:
    1. Send the message to the LLM with available tools
    2. If the LLM requests tool calls, execute them
    3. Send results back to the LLM
    4. Repeat until the LLM gives a final text response

    Args:
        user_message: The user's question
        system_prompt: Instructions for the agent's behavior
        max_iterations: Maximum tool call rounds to prevent infinite loops
    """
    messages: list = [{"role": "user", "content": user_message}]

    for iteration in range(max_iterations):
        # Call the LLM
        response = client.responses.create(
            model="gpt-5-mini",
            instructions=system_prompt,
            tools=tools,  # type: ignore[arg-type]
            input=messages,  # type: ignore[arg-type]
        )

        # Check for tool calls
        tool_calls = [item for item in response.output if item.type == "function_call"]

        # No tool calls = we have our final answer
        if not tool_calls:
            return response.output_text

        # Add the model's response to conversation
        messages += response.output

        # Execute each tool call
        for call in tool_calls:
            print(f"  [{iteration + 1}] Tool: {call.name}")

            # Handle unknown tools gracefully
            if call.name not in tool_registry:
                result = f"Error: Unknown tool '{call.name}'"
            else:
                try:
                    func = tool_registry[call.name]
                    args = json.loads(call.arguments)
                    result = func(**args)
                except Exception as e:
                    result = f"Error: {e}"

            print(f"       Result: {result}")

            # Add result to conversation
            messages.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": result,
                }
            )

        # Loop continues - LLM will process tool results

    # If we hit max iterations, return what we have
    return f"Max iterations ({max_iterations}) reached."


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    # Test questions that exercise the agent
    questions = [
        "What's the weather in Paris?",
        "What is 25 * 4 + 10?",
        "What's 2 + 2? Also, what's the weather in London?",
        "What's the capital of France?",  # No tools needed
    ]

    for question in questions:
        print(f"\n{'=' * 60}")
        print(f"User: {question}")
        print("-" * 60)
        answer = run_agent(question)
        print(f"\nAgent: {answer}")
