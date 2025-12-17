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


def calculate(expression: str) -> str:
    """Evaluate a mathematical expression.

    Args:
        expression: A math expression like '2 + 2' or '15 * 9/5 + 32'
    """
    try:
        allowed = set("0123456789+-*/.() ")
        if not all(c in allowed for c in expression):
            return "Error: Invalid characters"
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"


def search(query: str) -> str:
    """Search for information (simulated).

    Args:
        query: The search query
    """
    # Simulated search results
    results = {
        "weather london": "London: 15°C, cloudy, 60% humidity",
        "weather paris": "Paris: 18°C, sunny, 45% humidity",
        "population france": "France has a population of 67.5 million",
        "capital japan": "The capital of Japan is Tokyo",
    }

    query_lower = query.lower()
    for key, value in results.items():
        if key in query_lower:
            return value

    return f"No results found for: {query}"


def get_current_date() -> str:
    """Get the current date."""
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d")


TOOLS = [calculate, search, get_current_date]
TOOL_MAP = {f.__name__: f for f in TOOLS}

# =============================================================================
# Agent System Prompt
# =============================================================================

AGENT_PROMPT = """You are a helpful assistant that can use tools to answer questions.

Available tools:
- calculate(expression): Evaluate math expressions
- search(query): Search for information
- get_current_date(): Get today's date

Process:
1. Think about what you need to do
2. Use a tool if needed
3. Observe the result
4. Repeat until you have the answer

When you have the final answer, just provide it directly without calling any more tools.
"""

# =============================================================================
# The Agent Loop
# =============================================================================


def run_agent(goal: str, max_iterations: int = 5, verbose: bool = True) -> str:
    """
    Run the agent loop until goal is achieved or max iterations reached.
    """
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=AGENT_PROMPT,
            tools=TOOLS,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True  # We'll handle tool calls manually for visibility
            ),
        ),
    )

    if verbose:
        print(f"Goal: {goal}\n")

    for iteration in range(max_iterations):
        if verbose:
            print(f"--- Iteration {iteration + 1} ---")

        response = chat.send_message(goal if iteration == 0 else "Continue.")

        # Check for tool calls
        parts = response.candidates[0].content.parts
        tool_calls = [p for p in parts if p.function_call]

        if not tool_calls:
            # No tool call means agent is done
            if verbose:
                print(f"Final Answer: {response.text}\n")
            return response.text

        # Execute each tool call
        tool_results = []
        for part in tool_calls:
            fc = part.function_call
            func = TOOL_MAP.get(fc.name)

            if func:
                result = func(**fc.args)
                if verbose:
                    print(f"Tool: {fc.name}({fc.args})")
                    print(f"Result: {result}")
            else:
                result = f"Unknown tool: {fc.name}"

            tool_results.append(
                types.Part.from_function_response(
                    name=fc.name,
                    response={"result": result},
                )
            )

        # Send results back
        response = chat.send_message(tool_results)

        # Check if this response is the final answer
        parts = response.candidates[0].content.parts
        if not any(p.function_call for p in parts):
            if verbose:
                print(f"\nFinal Answer: {response.text}")
            return response.text

    return "Max iterations reached without an answer"


# =============================================================================
# Example Usage
# =============================================================================

# Simple calculation
run_agent("What is 15% of 200?")

# Search + calculation
run_agent("What's the weather in London? Convert the temperature to Fahrenheit.")

# Multi-step reasoning
run_agent("What is the population of France divided by 1000?")
