"""
Agent Architectures

Two ways to build agents, determined by one question:
Does the user wait for the result?

1. Interactive Agents - User sends request, waits for response
   Examples: ChatGPT, Claude Code, customer support bots
   Pattern: Request -> Process -> Response

2. Event-Driven Agents - Run independently, triggered by external events
   Examples: Email assistants, PR review bots, monitoring systems
   Pattern: Event -> Queue -> Process -> Action (-> Human Review)

Event-Driven Architecture (EDA) is essential for AI systems because:
- LLM calls are slow (seconds, not milliseconds)
- Workloads fluctuate unpredictably
- Components need to scale independently
- Failures need graceful handling

This lesson covers:
- State management (tracking agent progress)
- Human-in-the-loop patterns (notify, question, review)
- When to use each architecture
"""

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# =============================================================================
# State Management
# =============================================================================

# State = where we are + what we've done + what we're waiting for


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    WAITING_FOR_HUMAN = "waiting_for_human"  # Key for event-driven agents
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentState:
    """
    Tracks agent execution. Critical for event-driven agents that must
    persist state across process restarts and human review cycles.
    """

    status: AgentStatus = AgentStatus.IDLE
    current_step: int = 0
    total_steps: int = 0
    intermediate_results: list[Any] = field(default_factory=list)
    pending_human_input: str | None = None  # What we're waiting for

    def checkpoint(self) -> dict:
        """Serialize state for persistence."""
        return {
            "status": self.status.value,
            "step": self.current_step,
            "results": self.intermediate_results,
            "pending": self.pending_human_input,
        }


# =============================================================================
# Human-in-the-Loop Patterns
# =============================================================================

# Event-driven agents need guardrails. Three patterns for human involvement:


class HumanInteraction(Enum):
    NOTIFY = "notify"  # Inform human, no response needed
    QUESTION = "question"  # Need clarification to proceed
    REVIEW = "review"  # Need approval before action


@dataclass
class HumanRequest:
    """A request for human involvement."""

    interaction_type: HumanInteraction
    message: str
    context: dict = field(default_factory=dict)
    options: list[str] | None = None  # For QUESTION type


def request_human_input(
    interaction: HumanInteraction,
    message: str,
    **kwargs,
) -> HumanRequest:
    """
    Create a human-in-the-loop request.

    Examples:
        # Just inform - agent continues
        request_human_input(NOTIFY, "Processed 50 emails")

        # Need clarification - agent pauses
        request_human_input(QUESTION, "Which account?", options=["work", "personal"])

        # Need approval - agent pauses
        request_human_input(REVIEW, "Send this reply?", context={"draft": "..."})
    """
    return HumanRequest(interaction, message, kwargs.get("context", {}), kwargs.get("options"))


# =============================================================================
# Interactive Agent
# =============================================================================


class InteractiveAgent:
    """
    User waits for response. State lives in memory.

    Use for: Chat interfaces, coding assistants, real-time tools
    """

    def __init__(self):
        self.state = AgentState()
        self.messages: list[dict] = []

    def chat(self, user_message: str) -> str:
        self.messages.append({"role": "user", "content": user_message})
        # In practice: LLM call + tools
        response = f"[Response to: {user_message}]"
        self.messages.append({"role": "assistant", "content": response})
        return response


# =============================================================================
# Event-Driven Agent
# =============================================================================


@dataclass
class Event:
    """Something that happened in the outside world."""

    id: str
    type: str  # e.g., "new_email", "pr_opened", "file_changed"
    payload: dict


class EventDrivenAgent:
    """
    Runs independently. Triggered by events. May pause for human input.

    Use for: Email triage, code review, monitoring, scheduled tasks
    """

    def __init__(self):
        self.state = AgentState()
        self.queue: asyncio.Queue[Event] = asyncio.Queue()
        self.running = False

    async def on_event(self, event: Event) -> HumanRequest | dict:
        """
        Process an event. Override in subclass.

        Return either:
        - HumanRequest: Agent pauses, waits for human
        - dict: Result, agent continues
        """
        # Example: flag important emails for review
        if event.type == "new_email" and "urgent" in str(event.payload):
            return request_human_input(
                HumanInteraction.REVIEW,
                "Urgent email received. Draft reply?",
                context=event.payload,
            )
        return {"processed": event.id}

    async def run(self):
        """Main event loop."""
        self.running = True
        while self.running:
            try:
                event = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                self.state.status = AgentStatus.RUNNING

                result = await self.on_event(event)

                if isinstance(result, HumanRequest):
                    self.state.status = AgentStatus.WAITING_FOR_HUMAN
                    self.state.pending_human_input = result.message
                    print(f"[{result.interaction_type.value.upper()}] {result.message}")
                else:
                    print(f"Processed: {event.id}")

            except asyncio.TimeoutError:
                continue

    def stop(self):
        self.running = False


# =============================================================================
# Demo
# =============================================================================

async def main():
    print("=" * 60)
    print("AGENT ARCHITECTURES")
    print("=" * 60)

    # Interactive
    print("\n1. INTERACTIVE AGENT")
    print("-" * 40)
    agent = InteractiveAgent()
    print(f"User: Hello")
    print(f"Agent: {agent.chat('Hello')}")

    # Event-driven
    print("\n2. EVENT-DRIVEN AGENT")
    print("-" * 40)
    ed_agent = EventDrivenAgent()
    task = asyncio.create_task(ed_agent.run())

    # Simulate events
    await ed_agent.queue.put(Event("e1", "new_email", {"subject": "Meeting"}))
    await ed_agent.queue.put(Event("e2", "new_email", {"subject": "urgent: Server down!"}))

    await asyncio.sleep(0.3)
    ed_agent.stop()
    await task

    # Human-in-the-loop patterns
    print("\n3. HUMAN-IN-THE-LOOP PATTERNS")
    print("-" * 40)
    print("NOTIFY   - Inform human, agent continues")
    print("QUESTION - Ask for clarification, agent pauses")
    print("REVIEW   - Request approval, agent pauses")

    print("\n" + "=" * 60)
    print("WHEN TO USE EACH")
    print("=" * 60)
    print("""
Interactive:
  - Chat interfaces, customer support
  - Coding assistants (Claude Code)
  - Search and research tools

Event-Driven:
  - Email triage and drafting
  - Code review bots
  - Monitoring and alerting
  - Scheduled report generation
  - Document processing pipelines
""")


if __name__ == "__main__":
    asyncio.run(main())
