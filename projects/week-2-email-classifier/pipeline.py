"""
Email Classifier Pipeline

Fetch emails, classify them, route to appropriate handlers, generate draft responses.
"""

from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv
from gmail import get_gmail_service, fetch_emails

load_dotenv()

client = genai.Client()

# =============================================================================
# State Models
# =============================================================================


class EmailState(BaseModel):
    """State for a single email being processed."""

    id: str
    subject: str
    sender: str
    snippet: str
    body: str
    category: str | None = None
    draft_response: str | None = None
    action: str | None = None


class ProcessedBatch(BaseModel):
    """State for a batch of processed emails."""

    emails: list[EmailState]
    total: int = 0
    by_category: dict[str, int] = {}


# =============================================================================
# Classification Step
# =============================================================================


def classify_email(state: EmailState) -> EmailState:
    """Classify email into a category."""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""Classify this email as exactly one of: support, sales, spam, newsletter

From: {state.sender}
Subject: {state.subject}

{state.body[:1000]}

Category:""",
        config=types.GenerateContentConfig(temperature=0.0),
    )

    category = response.text.strip().lower()

    # Normalize category
    valid_categories = {"support", "sales", "spam", "newsletter"}
    if category not in valid_categories:
        category = "spam"  # Default for unrecognized

    return state.model_copy(update={"category": category})


# =============================================================================
# Response Generation Steps
# =============================================================================


def generate_support_response(state: EmailState) -> EmailState:
    """Generate a draft support response."""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""Draft a helpful support response for this email.
Be professional and empathetic. Acknowledge the issue and offer to help.

From: {state.sender}
Subject: {state.subject}

{state.body[:1000]}

Draft response:""",
        config=types.GenerateContentConfig(temperature=0.7),
    )

    return state.model_copy(
        update={"draft_response": response.text, "action": "respond"}
    )


def generate_sales_response(state: EmailState) -> EmailState:
    """Generate a draft sales follow-up."""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""Draft a friendly sales follow-up response for this email.
Be helpful, not pushy. Focus on addressing their interest.

From: {state.sender}
Subject: {state.subject}

{state.body[:1000]}

Draft response:""",
        config=types.GenerateContentConfig(temperature=0.7),
    )

    return state.model_copy(
        update={"draft_response": response.text, "action": "forward_to_sales"}
    )


# =============================================================================
# Routing Step
# =============================================================================


def route_email(state: EmailState) -> EmailState:
    """Route email to appropriate handler based on classification."""
    if state.category == "support":
        return generate_support_response(state)
    elif state.category == "sales":
        return generate_sales_response(state)
    elif state.category == "newsletter":
        return state.model_copy(update={"action": "archive"})
    else:  # spam
        return state.model_copy(update={"action": "discard"})


# =============================================================================
# Main Pipeline
# =============================================================================


def process_email(email: dict) -> EmailState:
    """Process a single email through the pipeline."""
    state = EmailState(
        id=email["id"],
        subject=email["subject"],
        sender=email["sender"],
        snippet=email["snippet"],
        body=email["body"],
    )

    # Step 1: Classify
    state = classify_email(state)

    # Step 2: Route and generate response if needed
    state = route_email(state)

    return state


def run_pipeline(max_emails: int = 10) -> ProcessedBatch:
    """Run the full email classification pipeline."""
    # Fetch emails from Gmail
    print("Connecting to Gmail...")
    service = get_gmail_service()
    emails = fetch_emails(service, max_results=max_emails)
    print(f"Fetched {len(emails)} emails\n")

    # Process each email
    processed = []
    for i, email in enumerate(emails, 1):
        print(f"Processing {i}/{len(emails)}: {email['subject'][:50]}...")
        state = process_email(email)
        processed.append(state)
        print(f"  -> {state.category} ({state.action})")

    # Build batch summary
    by_category = {}
    for email in processed:
        by_category[email.category] = by_category.get(email.category, 0) + 1

    batch = ProcessedBatch(
        emails=processed, total=len(processed), by_category=by_category
    )

    return batch


def print_summary(batch: ProcessedBatch):
    """Print a summary of processed emails."""
    print("\n" + "=" * 60)
    print("PROCESSING SUMMARY")
    print("=" * 60)
    print(f"\nTotal emails processed: {batch.total}")
    print("\nBy category:")
    for category, count in sorted(batch.by_category.items()):
        print(f"  {category}: {count}")

    print("\n" + "-" * 60)
    print("DRAFT RESPONSES")
    print("-" * 60)

    for email in batch.emails:
        if email.draft_response:
            print(f"\nTo: {email.sender}")
            print(f"Re: {email.subject}")
            print(f"\n{email.draft_response[:500]}...")
            print("-" * 40)


def save_results(batch: ProcessedBatch, path: str = "results.json"):
    """Save processed batch to JSON."""
    with open(path, "w") as f:
        f.write(batch.model_dump_json(indent=2))
    print(f"\nResults saved to {path}")


# =============================================================================
# Entry Point
# =============================================================================


def main():
    """Run the pipeline."""
    batch = run_pipeline(max_emails=10)
    print_summary(batch)
    save_results(batch)


if __name__ == "__main__":
    main()
