"""
Workflow Patterns

Five patterns for orchestrating multiple LLM calls:
1. Prompt Chaining - Sequential steps
2. Routing - Classify and route
3. Parallelization - Process concurrently
4. Orchestrator-Workers - Dynamic decomposition
5. Evaluator-Optimizer - Generate-evaluate-refine
"""

import asyncio
from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import Literal

client = AsyncOpenAI()


async def llm(prompt: str) -> str:
    """Simple async LLM call."""
    response = await client.responses.create(
        model="gpt-5-mini",
        input=prompt,
    )
    return response.output_text


# =============================================================================
# Pattern 1: Prompt Chaining
# =============================================================================


async def prompt_chaining():
    """Sequential steps where each builds on the previous."""
    print("\n1. PROMPT CHAINING")
    print("-" * 40)

    # Step 1: Create outline
    outline = await llm("Create a 3-point outline for: why testing matters")
    print(f"Outline:\n{outline[:200]}...")

    # Step 2: Write based on outline
    draft = await llm(f"Write a short paragraph based on:\n{outline}")
    print(f"\nDraft:\n{draft[:200]}...")


# =============================================================================
# Pattern 2: Routing
# =============================================================================


class Category(BaseModel):
    category: Literal["billing", "technical", "general"]


async def routing():
    """Classify input and route to specialized handler."""
    print("\n2. ROUTING")
    print("-" * 40)

    query = "I was charged twice!"

    # Step 1: Classify
    result = await client.responses.parse(
        model="gpt-5-mini",
        input=f"Classify: {query}",
        text_format=Category,
    )
    category = result.output_parsed.category
    print(f"Query: {query}")
    print(f"Category: {category}")

    # Step 2: Route to specialist
    prompts = {
        "billing": "You are a billing specialist. Help with: ",
        "technical": "You are tech support. Help with: ",
        "general": "You are a general assistant. Help with: ",
    }
    response = await llm(prompts[category] + query)
    print(f"Response: {response[:150]}...")


# =============================================================================
# Pattern 3: Parallelization
# =============================================================================


async def parallelization():
    """Process multiple items concurrently."""
    print("\n3. PARALLELIZATION")
    print("-" * 40)

    items = ["Python", "JavaScript", "Rust"]

    # All at once with asyncio.gather
    results = await asyncio.gather(
        *[llm(f"Describe {item} in one sentence.") for item in items]
    )

    for item, result in zip(items, results):
        print(f"{item}: {result[:80]}...")


# =============================================================================
# Pattern 4: Orchestrator-Workers
# =============================================================================


class Plan(BaseModel):
    subtasks: list[str]


async def orchestrator_workers():
    """Dynamically decompose task and delegate to workers."""
    print("\n4. ORCHESTRATOR-WORKERS")
    print("-" * 40)

    task = "Explain the benefits of code review"

    # Orchestrator plans
    plan = await client.responses.parse(
        model="gpt-5-mini",
        input=f"Break into 2 subtasks: {task}",
        text_format=Plan,
    )
    print(f"Subtasks: {plan.output_parsed.subtasks}")

    # Workers execute in parallel
    results = await asyncio.gather(
        *[llm(f"Complete: {st}") for st in plan.output_parsed.subtasks]
    )

    for i, result in enumerate(results):
        print(f"Worker {i + 1}: {result[:80]}...")


# =============================================================================
# Pattern 5: Evaluator-Optimizer
# =============================================================================


class Evaluation(BaseModel):
    score: int
    feedback: str


async def evaluator_optimizer():
    """Generate-evaluate-refine loop."""
    print("\n5. EVALUATOR-OPTIMIZER")
    print("-" * 40)

    # Generate
    draft = await llm("Write a tagline for a coffee shop.")
    print(f"Draft: {draft}")

    # Evaluate
    evaluation = await client.responses.parse(
        model="gpt-5-mini",
        input=f"Rate 1-10 with feedback:\n{draft}",
        text_format=Evaluation,
    )
    print(f"Score: {evaluation.output_parsed.score}/10")
    print(f"Feedback: {evaluation.output_parsed.feedback}")

    # Refine (if needed)
    if evaluation.output_parsed.score < 8:
        improved = await llm(
            f"Improve based on feedback:\n{draft}\nFeedback: {evaluation.output_parsed.feedback}"
        )
        print(f"Improved: {improved}")


# =============================================================================
# Run all patterns
# =============================================================================


async def main():
    print("=" * 50)
    print("WORKFLOW PATTERNS")
    print("=" * 50)

    await prompt_chaining()
    await routing()
    await parallelization()
    await orchestrator_workers()
    await evaluator_optimizer()

    print("\n" + "=" * 50)
    print("All patterns complete!")


if __name__ == "__main__":
    asyncio.run(main())
